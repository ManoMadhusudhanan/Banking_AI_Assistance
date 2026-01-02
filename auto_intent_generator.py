from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np
import json
import os
def load_rag_chunks(file_path):
    loader = UnstructuredFileLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80
    )

    chunks = splitter.split_documents(documents)

    texts = [chunk.page_content.strip() for chunk in chunks if chunk.page_content.strip()]
    return texts
def embed_chunks(chunks):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)
    return embeddings
def cluster_intents(chunks, embeddings, num_intents=6):
    kmeans = KMeans(
        n_clusters=num_intents,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(embeddings)

    intent_map = {}
    for label, text in zip(labels, chunks):
        intent_map.setdefault(f"intent_{label}", []).append(text)

    return intent_map
def save_intents(intent_map, output_path="auto_intents.json"):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(intent_map, f, indent=2, ensure_ascii=False)
def generate_intents_from_rag(
    rag_file_path,
    num_intents=6,
    output_path="auto_intents.json"
):
    print(" Loading RAG document...")
    chunks = load_rag_chunks(rag_file_path)

    print(f" Total chunks created: {len(chunks)}")

    print(" Generating embeddings...")
    embeddings = embed_chunks(chunks)

    print(" Clustering intents...")
    intent_map = cluster_intents(chunks, embeddings, num_intents)

    save_intents(intent_map, output_path)

    print(f" Auto-generated {num_intents} intents")
    print(f" Saved to {output_path}")

    return intent_map
if __name__ == "__main__":
    intent_map = generate_intents_from_rag(
        rag_file_path="Source_Document.docx",
        num_intents=6
    )

