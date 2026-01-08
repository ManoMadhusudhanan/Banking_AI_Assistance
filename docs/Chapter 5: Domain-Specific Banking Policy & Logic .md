# Chapter 5: Domain-Specific Banking Policy & Logic

In Chapter 6: Graph Retrieval-Augmented Generation (RAG) Engine, we will explore how our Banking_AI_Assistance will act as a smart "research assistant," retrieving factual information from official bank documents to answer user questions accurately. This approach will be particularly useful for general inquiries such as "What are the loan eligibility criteria?".

However, banking will involve many actions that require strict adherence to specific rules, procedures, and security protocols. For these sensitive or critical tasks, simply looking up facts or relying on a general AI response will not be sufficient. We will need a system that behaves like a bank’s official rulebook, ensuring that every step is followed precisely.

## What Problem Does It Solve?
Imagine a situation where you want to update your registered mobile number with the bank. You might ask the AI assistant: "I need to change my mobile number."

This will not be a simple question that can be answered with a general fact or a creative AI response. Updating contact details will involve:

- **Security:** Verifying identity to prevent fraud.
- **Compliance:** Following strict regulatory guidelines for such updates.
- **Specific Procedures:** Different processes depending on the situation (for example, losing a phone versus updating to a new number).

If the AI assistant were to provide a generic answer—or worse, invent a procedure—it could lead to serious security risks or regulatory non-compliance. This is where **Domain-Specific Banking Policy & Logic** becomes essential.

This part of the system contains clearly defined, hard-coded rules and policies for handling sensitive or common banking requests. It functions like the bank’s official policy manual built directly into the AI. When the Orchestrator identifies a request that touches these critical areas, it routes the request here. This layer ensures:

- **Safety:** By enforcing strict security procedures.
- **Compliance:** By adhering to all required regulations.
- **Accuracy:** By providing precise, pre-approved steps.
- **Consistency:** By delivering the same correct guidance every time.

Instead of relying solely on the general Large Language Model (LLM) Service, this layer provides structured, secure, and compliant responses, ensuring that critical banking procedures are followed exactly.

## Key Concepts
Let’s break down the core ideas behind this internal "policy manual":

### 1. Hard-Coded Rules
These are explicit *if–then* statements programmed directly into the system. They are not learned by an AI model but are explicitly defined by banking experts.

**Example:**  
IF a user wants to update their mobile number **AND** mentions "lost phone," THEN the policy enforces a *branch visit only*.

### 2. Sensitive Banking Requests
These are actions that have direct implications for a customer’s account security or financial well-being.

**Examples:** Updating contact details, blocking a lost card, applying for sensitive products, or making high-value transfers. For these cases, generic AI responses are too risky.

### 3. Safety & Compliance First
The primary objective of this layer is to ensure that all sensitive interactions are handled with the highest level of security and in full compliance with banking regulations. It prevents the AI from suggesting unsafe or non-standard procedures.

### 4. Predictable, Structured Responses
For critical actions, users require clear and unambiguous instructions. This layer generates pre-approved, consistent messages, eliminating any possibility of a creative (but potentially incorrect) AI response.

| Feature | General LLM Response (Risk) | Domain-Specific Policy (Benefit) |
|------|----------------------------|----------------------------------|
| Accuracy | Might hallucinate procedures | Provides precise, verified banking workflows |
| Security | Could suggest less secure options | Enforces strict security protocols |
| Consistency | Responses may vary by phrasing | Always delivers approved guidance |
| Compliance | Not inherently regulation-aware | Designed for regulatory adherence |

## How to Use It (The Orchestrator’s Role)
The orchestrator in Banking_AI_Assistance determines when to use the general Retrieval-Augmented Generation (RAG) Engine or Large Language Model (LLM) Service, and when to defer to the strict Domain-Specific Banking Policy & Logic layer.

As introduced earlier, when a user requests a mobile number update, the orchestrator checks for specific keywords before deciding the processing path.

```python
# main.py - inside the chatbot function (simplified)

# Check if the query is about updating contact information
contact_update_keywords = [
    "change contact number", "update mobile",
    # ... more keywords ...
]

if final_query and any(k in final_query for k in contact_update_keywords):
    # The orchestrator decides to use a specific policy helper
    mode = decide_contact_update_path(final_query)
    reply = build_contact_update_response(mode)
    follow_up = suggest_follow_up(mode)

    return {
        "reply": reply,
        "follow_up": follow_up,
        "metrics": { "used_rag": False, "latency": latency }
    }

# ... other logic for banking and conversational queries ...
```
The `rag_search` function takes your cleaned-up question (final_query) as input and returns a list of relevant text chunks from the banking knowledge base. These chunks are then used to "augment" the prompt for the[ Large Language Model (LLM) Service](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%207%3A%20Large%20Language%20Model%20(LLM)%20Integration.md), helping it generate a more accurate answer.

| Input (`final_query`) | Output (`context_chunks`) |
|----------------------|---------------------------|
| "what documents do I need to open a savings account" | - To open a savings account, you generally need ID (Aadhaar, Passport) and Address Proof (Utility Bill, Driver's License).<br>- A minimum initial deposit is required for opening new savings accounts as per bank policy. |
| "how to apply for a personal loan" | - Personal loans can be applied online via our website or by visiting any branch.<br>- Eligibility criteria include a stable income, good credit score, and minimum age of 21. |
| "what are the charges for ATM withdrawals" | - First 5 ATM withdrawals per month are free. Subsequent withdrawals incur a charge of Rs. 20 + GST.<br>- International ATM withdrawals have different fee structures. |

## Under the Hood: How the RAG Engine Works
Let's peek behind the curtain to see how the RAG Engine performs its research.

### The Flow of a RAG Search
Here's a simplified sequence of what happens when the Orchestrator asks the RAG Engine for information:
<img width="70%" height="621" alt="image" src="https://github.com/user-attachments/assets/c5c62dfc-e37a-495f-b004-f15501a94c01" />

### 1. Setting Up the Banking "Library" (Building the RAG Index)
Before the RAG Engine can answer questions, it needs to build its knowledge base (the RAG index). This is usually done once, or whenever new documents are added, by calling the `build_rag_index` function in `rag_engine`.py.
```
# rag_engine.py - Simplified `build_rag_index`

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client.http import models as rest
import uuid

embedder = SentenceTransformer("all-MiniLM-L6-v2") # Our embedding model
# qdrant_client is initialized here (not shown for brevity)

def build_rag_index(source_file: str):
    # 1. Load banking documents (e.g., a DOCX file)
    loader = UnstructuredFileLoader(source_file)
    docs = loader.load()

    # 2. Break documents into smaller 'chunks' (pages/paragraphs)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300, # Each piece is around 300 characters
        chunk_overlap=50 # Pieces can slightly overlap for better context
    )
    chunks = splitter.split_documents(docs)
    texts = [c.page_content.strip() for c in chunks]

    # 3. Create numerical 'fingerprints' (embeddings) for each chunk
    vectors = embedder.encode(texts, batch_size=32)

    # 4. Prepare chunks and their fingerprints to be stored in Qdrant
    points = []
    for i, text in enumerate(texts):
        chunk_id = str(uuid.uuid4()) # Unique ID for each chunk
        points.append(
            rest.PointStruct(
                id=i, # An ID for Qdrant
                vector=vectors[i].tolist(), # The numerical fingerprint
                payload={ # Extra info to store with the chunk
                    "chunk_id": chunk_id,
                    "text": text,
                    # "entities": entities (simplified for beginner focus)
                }
            )
        )

    # 5. Store all chunks and their fingerprints in Qdrant
    qdrant_client.upsert(collection_name=COLLECTION, points=points)
    print("✅ Vector RAG index built successfully!")
```
This `build_rag_index` function is essential for preparing the knowledge base:

- `UnstructuredFileLoader`: This helps read various document types, like Word files (.docx), PDF, etc.
- `RecursiveCharacterTextSplitter`: This intelligent tool breaks down long documents into smaller chunks, making retrieval more precise.
- `SentenceTransformer`: This model (all-MiniLM-L6-v2) is our "embedding brain" that converts text into numerical fingerprints.
- `embedder.encode(texts)`: This takes all our text chunks and generates their unique numerical vectors (fingerprints).
- `qdrant_client.upsert(...)`: This command sends all our text chunks along with their numerical fingerprints to the Qdrant Vector Database, making them searchable by meaning.
 
### 2. Performing a Research Query (`rag_search`)
When the Orchestrator calls rag_search with your question, here's a simplified view of what happens inside `rag_engine.py`:
```
# rag_engine.py - Simplified `rag_search`

from sentence_transformers import SentenceTransformer, util
import numpy as np

embedder = SentenceTransformer("all-MiniLM-L6-v2") # Our embedding model
# qdrant_client is initialized here (not shown for brevity)

# Helper function to calculate similarity between two fingerprints
def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def rag_search(query: str, top_k: int = 4):
    # 1. Turn the user's question into a numerical 'fingerprint'
    query_vec = embedder.encode(query)

    # 2. Ask Qdrant to find document chunks with similar fingerprints
    search_results = qdrant_client.query_points(
        collection_name=COLLECTION,
        query=query_vec.tolist(), # The fingerprint of our question
        limit=top_k * 4, # Get more results initially to re-rank
        with_payload=True # Get the actual text back
    )

    if not search_results or not search_results.points:
        return None # No relevant documents found

    # 3. Re-rank the found chunks to ensure the most relevant ones are at the top
    scored_chunks = []
    for p in search_results.points:
        doc_text = p.payload["text"]
        doc_vec = embedder.encode(doc_text) # Get embedding for the retrieved document text
        sim = cosine_similarity(query_vec, doc_vec) # Calculate similarity
        if sim >= 0.18: # Only keep chunks with a good similarity score
            scored_chunks.append((sim, doc_text))

    scored_chunks.sort(reverse=True, key=lambda x: x[0]) # Sort by highest similarity

    # Note: Our project also includes advanced "Graph Boosting" here
    # (using Neo4j) to find even more interconnected context.
    # For simplicity, we are focusing on the core vector search.

    # 4. Return the top 'k' most relevant text chunks
    return [text for _, text in scored_chunks[:top_k]]
```
Here's how `rag_search` works its magic:

- `embedder.encode(query)`: Your question is instantly converted into a numerical fingerprint.
- `qdrant_client.query_points(...)`: This is the crucial step where the RAG Engine sends your question's fingerprint to Qdrant. Qdrant then speedily scans its vast collection of banking document fingerprints and returns the chunks that are semantically (by meaning) most similar.
- `cosine_similarity`: Even after getting initial results from Qdrant, the system performs an extra step called "re-ranking." It calculates the exact similarity of each retrieved chunk against your original query. This ensures that only the very best and most relevant pieces of information are passed on.
return [text for _, text in scored_chunks[:top_k]]: Finally, the function returns a list of the top_k (e.g., 4) most relevant banking text snippets.
These retrieved chunks are the "facts" that will be given to the main AI (Large Language Model (LLM) Service) to help it craft an accurate and specific answer to your banking question.

## Conclusion
We've now seen how the Graph Retrieval-Augmented Generation (RAG) Engine acts as our Banking_AI_Assistance's intelligent "research assistant." It creates a factual foundation by storing banking documents in a specialized Vector Database (Qdrant) as numerical "fingerprints" (embeddings). When you ask a question, the RAG Engine efficiently retrieves the most relevant snippets from this knowledge base, ensuring that the bot's responses are accurate, up-to-date, and grounded in real banking information, preventing "made-up" answers.

With our bot now able to "see" (OCR), "understand" (Intent Detection), and "research" (RAG), the next logical step is to combine all this information to generate a truly helpful and human-like response. That's the job of the Large Language Model (LLM) Service, which we'll explore in detail in a later chapter. First, we'll examine how specific banking rules and logic are handled directly by the orchestrator.

Next Chapter: [Graph Retrieval Augmented Generation (RAG) Engine
](https://github.com/ManoMadhusudhanan/Banking_AI_Assistance/blob/main/docs/Chapter%206%3A%20Graph%20Retrieval%20Augmented%20Generation%20(RAG)%20Engine.md)
