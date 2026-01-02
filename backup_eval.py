import json
import time
import numpy as np
from datasets import Dataset
from ragas import evaluate


from rag_engine import rag_search  # Graph + Vector RAG

# -----------------------------
# Config
# -----------------------------
EVAL_FILE = "eval_questions.json"
TOP_K = 6

# -----------------------------
# Utility Functions
# -----------------------------
def dcg(scores):
    return sum(score / np.log2(idx + 2) for idx, score in enumerate(scores))


def normalize_text(x):
    if x is None:
        return ""
    if isinstance(x, list):
        return " ".join(map(str, x))
    return str(x)


# -----------------------------
# Graph-Specific Metrics
# -----------------------------
def subgraph_relevance(retrieved_nodes, expected_nodes):
    if not expected_nodes:
        return 1.0  # Out-of-scope handled as correct
    overlap = set(retrieved_nodes) & set(expected_nodes)
    return len(overlap) / len(expected_nodes)


def subgraph_size(retrieved_nodes):
    return len(set(retrieved_nodes))



# -----------------------------
# Main Evaluation
# -----------------------------
def evaluate_graph_rag():

    with open(EVAL_FILE, "r") as f:
        eval_data = json.load(f)

    precision_scores, recall_scores = [], []
    mrr_scores, ndcg_scores = [], []
    subgraph_relevance_scores, subgraph_sizes = [], []
    latencies = []
    ragas_rows = []

    print("\n🔍 GRAPH RAG EVALUATION STARTED\n")

    for idx, item in enumerate(eval_data, 1):
        question = normalize_text(item.get("question"))
        expected_entities = set(item.get("expected_entities", []))
        ground_truth = normalize_text(item.get("answer_expected"))

        print(f"Q{idx}: {question}")

        start = time.time()
        retrieved_docs = rag_search(question, top_k=TOP_K) or []
        latency = time.time() - start
        latencies.append(latency)

        retrieved_docs = [normalize_text(d) for d in retrieved_docs]
        retrieved_set = set(retrieved_docs)

        # -----------------------------
        # Retrieval Metrics
        # -----------------------------
        true_positives = {
            ent for ent in expected_entities
            for doc in retrieved_docs
            if ent.lower() in doc.lower()
        }

        precision = len(true_positives) / len(retrieved_set) if retrieved_set else 0
        recall = len(true_positives) / len(expected_entities) if expected_entities else 1

        precision_scores.append(precision)
        recall_scores.append(recall)

        rr = 0
        for rank, doc in enumerate(retrieved_docs, 1):
            if any(ent.lower() in doc.lower() for ent in expected_entities):
                rr = 1 / rank
                break
        mrr_scores.append(rr)

        relevance_scores = [
            1 if any(ent.lower() in doc.lower() for ent in expected_entities) else 0
            for doc in retrieved_docs
        ]
        ideal_scores = sorted(relevance_scores, reverse=True)
        ndcg = dcg(relevance_scores) / dcg(ideal_scores) if dcg(ideal_scores) else 1
        ndcg_scores.append(ndcg)

        # -----------------------------
        # Graph Metrics
        # -----------------------------
        subgraph_relevance_scores.append(
            subgraph_relevance(retrieved_docs, expected_entities)
        )
        subgraph_sizes.append(subgraph_size(retrieved_docs))

        # -----------------------------
        # RAGAS Row
        # -----------------------------
        ragas_rows.append({
            "question": question,
            "answer": " ".join(retrieved_docs),
            "contexts": retrieved_docs,
            "ground_truth": ground_truth
        })

        print(f"Latency: {latency:.2f}s")
        print("-" * 50)



    # -----------------------------
    # Final Metrics Object (FOR UI)
    # -----------------------------
    metrics_output = {
        "precision_at_k": round(np.mean(precision_scores), 3),
        "recall_at_k": round(np.mean(recall_scores), 3),
        "mrr": round(np.mean(mrr_scores), 3),
        "ndcg_at_k": round(np.mean(ndcg_scores), 3),
        "subgraph_relevance": round(np.mean(subgraph_relevance_scores), 3),
        "avg_subgraph_size": round(np.mean(subgraph_sizes), 2),
        "avg_latency_sec": round(np.mean(latencies), 2),
        "generation_evaluation": "Skipped (LLM-based evaluation disabled to avoid API rate limits)"

    }

    print("\n📊 EVALUATION SUMMARY\n")
    for k, v in metrics_output.items():
        print(f"{k}: {v}")

    return metrics_output


if __name__ == "__main__":
    evaluate_graph_rag()
























