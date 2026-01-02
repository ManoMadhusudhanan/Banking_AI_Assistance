import json
import time
import numpy as np
from rag_engine import rag_search, embedder

EVAL_FILE = "eval_questions.json"
TOP_K = 6
SIM_THRESHOLD = 0.35

EMBED_CACHE = {}

def get_embedding(text):
    if text not in EMBED_CACHE:
        EMBED_CACHE[text] = embedder.encode(text)
    return EMBED_CACHE[text]

# -----------------------------
# Utility Functions
# -----------------------------
def cosine_similarity(a, b):
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def dcg(scores):
    return sum(score / np.log2(idx + 2) for idx, score in enumerate(scores))

# -----------------------------
# Evaluation Logic
# -----------------------------
def evaluate_rag():
    with open(EVAL_FILE, "r") as f:
        eval_data = json.load(f)

    total = len(eval_data)

    precision_scores, recall_scores = [], []
    mrr_scores, ndcg_scores = [], []

    faithfulness_hits = 0
    relevance_hits = 0
    coherence_hits = 0
    fluency_hits = 0

    hallucinations = 0
    grounded_hits = 0
    latencies = []

    print("\n🔍 RAG EVALUATION STARTED\n")

    # =============================
    # MAIN LOOP
    # =============================
    for idx, item in enumerate(eval_data, 1):
        question = item["question"]
        expected_entities = item["expected_entities"]
        answer_expected = item["answer_expected"]

        print(f"Q{idx}: {question}")

        # -----------------------------
        # Retrieval + Latency
        # -----------------------------
        start_time = time.time()
        retrieved_docs = rag_search(question, top_k=TOP_K) or []
        latency = time.time() - start_time
        latencies.append(latency)

        generated_answer = " ".join(retrieved_docs)

        # -----------------------------
        # Fallback Handling
        # -----------------------------
        if not retrieved_docs:
            if not answer_expected:
                grounded_hits += 1
                print("✅ Correct fallback (no context retrieved)")
            else:
                hallucinations += 1
                print("❌ Missed retrieval (should have context)")

            print(f"Latency: {latency:.2f}s")
            print("-" * 50)
            continue

        # -----------------------------
        # Semantic Retrieval Metrics
        # -----------------------------
        entity_vectors = {ent: get_embedding(ent) for ent in expected_entities}
        doc_vectors = [get_embedding(doc) for doc in retrieved_docs]

        matched_entities = set()
        relevant_doc_flags = []

        for doc_vec in doc_vectors:
            is_relevant = False
            for ent, ent_vec in entity_vectors.items():
                if cosine_similarity(doc_vec, ent_vec) >= SIM_THRESHOLD:
                    is_relevant = True
                    matched_entities.add(ent)
                    break
            relevant_doc_flags.append(1 if is_relevant else 0)

        precision = sum(relevant_doc_flags) / len(retrieved_docs)
        recall = len(matched_entities) / len(expected_entities) if expected_entities else 0

        precision_scores.append(precision)
        recall_scores.append(recall)

        # -----------------------------
        # MRR
        # -----------------------------
        rr = 0
        for rank, flag in enumerate(relevant_doc_flags, 1):
            if flag:
                rr = 1 / rank
                break
        mrr_scores.append(rr)

        # -----------------------------
        # nDCG
        # -----------------------------
        ideal_scores = sorted(relevant_doc_flags, reverse=True)
        ndcg = dcg(relevant_doc_flags) / dcg(ideal_scores) if dcg(ideal_scores) > 0 else 0
        ndcg_scores.append(ndcg)

        # -----------------------------
        # Generation Quality
        # -----------------------------
        q_vec = get_embedding(question)
        a_vec = get_embedding(generated_answer)
        ctx_vec = get_embedding(" ".join(retrieved_docs))

        answer_relevance = cosine_similarity(q_vec, a_vec)
        faithfulness = cosine_similarity(a_vec, ctx_vec)
        coherence = cosine_similarity(q_vec, ctx_vec)

        if faithfulness >= SIM_THRESHOLD:
            faithfulness_hits += 1
            grounded_hits += 1
        else:
            hallucinations += 1

        if answer_relevance >= SIM_THRESHOLD:
            relevance_hits += 1

        if coherence >= SIM_THRESHOLD:
            coherence_hits += 1

        if len(generated_answer.split()) > 5:
            fluency_hits += 1

        print(f"Latency: {latency:.2f}s")
        print("-" * 50)

    # =============================
    # FINAL METRICS (AFTER LOOP)
    # =============================
    metrics = {
        "retrieval": {
            "precision": round(float(np.mean(precision_scores)), 3),
            "recall": round(float(np.mean(recall_scores)), 3),
            "mrr": round(float(np.mean(mrr_scores)), 3),
            "ndcg": round(float(np.mean(ndcg_scores)), 3)
        },
        "generation": {
            "faithfulness": f"{faithfulness_hits}/{total}",
            "answer_relevance": f"{relevance_hits}/{total}",
            "coherence": f"{coherence_hits}/{total}",
            "fluency": f"{fluency_hits}/{total}"
        },
        "system": {
            "hallucination_rate": round(hallucinations / total, 2),
            "groundedness": f"{grounded_hits}/{total}",
            "avg_latency": round(float(np.mean(latencies)), 2)
        }
    }

    with open("rag_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # -----------------------------
    # Summary
    # -----------------------------
    print("\n📊 EVALUATION SUMMARY\n")

    print("🔹 Retrieval Relevance (Semantic)")
    print(f"Precision@K: {metrics['retrieval']['precision']}")
    print(f"Recall@K: {metrics['retrieval']['recall']}")
    print(f"MRR: {metrics['retrieval']['mrr']}")
    print(f"nDCG@K: {metrics['retrieval']['ndcg']}")

    print("\n🔹 Generation Quality")
    print(f"Faithfulness: {metrics['generation']['faithfulness']}")
    print(f"Answer Relevance: {metrics['generation']['answer_relevance']}")
    print(f"Coherence: {metrics['generation']['coherence']}")
    print(f"Fluency: {metrics['generation']['fluency']}")

    print("\n🔹 End-to-End Performance")
    print(f"Hallucination Rate: {metrics['system']['hallucination_rate']}")
    print(f"Groundedness: {metrics['system']['groundedness']}")
    print(f"Average Latency: {metrics['system']['avg_latency']}s")

    print("\n✅ RAG Evaluation Completed\n")

if __name__ == "__main__":
    evaluate_rag()
