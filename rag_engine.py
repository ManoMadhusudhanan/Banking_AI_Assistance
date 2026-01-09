import os
import uuid
from typing import List
from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from neo4j import GraphDatabase

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np

# --------------------------------------------------
# LOAD ENV
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
COLLECTION = "banking_rag"
EMBED_DIM = 384

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# --------------------------------------------------
# MODE FLAGS
# --------------------------------------------------
GRAPH_AVAILABLE = True

# --------------------------------------------------
# EMBEDDING MODEL
# --------------------------------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------------
# QDRANT CLIENT
# --------------------------------------------------
qdrant_client = QdrantClient(
    url="Your QDRANT_URL ",
    api_key=QDRANT_API_KEY,
    check_compatibility=False
)

# --------------------------------------------------
# NEO4J DRIVER
# --------------------------------------------------
neo4j_driver = None

if all([NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD]):
    try:
        neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        print("✅ Neo4j driver initialized")
    except Exception:
        GRAPH_AVAILABLE = False
else:
    GRAPH_AVAILABLE = False

# --------------------------------------------------
# ENTITY EXTRACTION
# --------------------------------------------------
def extract_entities(text: str) -> List[str]:
    keywords = [
        "account", "loan", "interest", "emi", "kyc",
        "savings", "current", "credit", "debit",
        "charges", "neft", "rtgs", "imps"
    ]
    return list({k for k in keywords if k in text.lower()})

# --------------------------------------------------
# BUILD RAG INDEX
# --------------------------------------------------
def build_rag_index(source_file: str):
    loader = UnstructuredFileLoader(source_file)
    docs = loader.load()

    # chunks 
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)
    texts = [c.page_content.strip() for c in chunks]

    vectors = embedder.encode(texts, batch_size=32)

    points = []

    for i, text in enumerate(texts):
        chunk_id = str(uuid.uuid4())
        entities = extract_entities(text)

        # ---------- Graph Write ----------
        if neo4j_driver and GRAPH_AVAILABLE:
            try:
                with neo4j_driver.session(database=NEO4J_DATABASE) as session:
                    session.run(
                        "CREATE (c:Chunk {id:$id, text:$text})",
                        id=chunk_id,
                        text=text
                    )
                    for ent in entities:
                        session.run(
                            """
                            MERGE (e:Entity {name:$name})
                            MATCH (c:Chunk {id:$cid})
                            MERGE (c)-[:MENTIONS]->(e)
                            """,
                            name=ent,
                            cid=chunk_id
                        )
            except Exception:
                pass

        points.append(
            rest.PointStruct(
                id=i,
                vector=vectors[i].tolist(),
                payload={
                    "chunk_id": chunk_id,
                    "text": text,
                    "entities": entities
                }
            )
        )

    qdrant_client.upsert(collection_name=COLLECTION, points=points)
    print("✅ Vector RAG index built successfully!")

# --------------------------------------------------
# COSINE SIMILARITY
# --------------------------------------------------
def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# --------------------------------------------------
# RAG SEARCH (VECTOR + GRAPH + RE-RANKING)
# --------------------------------------------------
def rag_search(query: str, top_k: int = 4):
    MIN_SCORE = 0.18  # MiniLM-friendly

    query_vec = embedder.encode(query)

    # ---------- Vector Retrieval ----------
    search_results = qdrant_client.query_points(
        collection_name=COLLECTION,
        query=query_vec.tolist(),
        limit=top_k * 4,
        with_payload=True
    )

    if not search_results or not search_results.points:
        return None

    # ---------- Semantic Re-ranking ----------
    scored_chunks = []
    for p in search_results.points:
        doc_text = p.payload["text"]
        doc_vec = embedder.encode(doc_text)
        sim = cosine_similarity(query_vec, doc_vec)
        if sim >= MIN_SCORE:
            scored_chunks.append((sim, doc_text))

    if not scored_chunks:
        return None

    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    # ---------- Graph Boost (optional) ----------
    query_entities = extract_entities(query)
    if neo4j_driver and GRAPH_AVAILABLE and query_entities:
        try:
            with neo4j_driver.session(database=NEO4J_DATABASE) as session:
                graph_ids = set()
                for ent in query_entities:
                    res = session.run(
                        """
                        MATCH (c:Chunk)-[:MENTIONS]->(e:Entity {name:$name})
                        RETURN c.id AS id
                        """,
                        name=ent
                    )
                    graph_ids.update(r["id"] for r in res)

                scored_chunks = sorted(
                    scored_chunks,
                    key=lambda x: 1 if x[1] in graph_ids else 0,
                    reverse=True
                )
        except Exception:
            pass

    return [text for _, text in scored_chunks[:top_k]]
