import json
from typing import Optional, Tuple

from sentence_transformers import SentenceTransformer, util
from ocr_utils import extract_text_from_image 

# LOAD MODEL
# --------------------------------------------------
intent_model = SentenceTransformer("all-MiniLM-L6-v2")

# LOAD AUTO-GENERATED INTENTS
# --------------------------------------------------
with open("auto_intents.json", "r", encoding="utf-8") as f:
    INTENT_MAP = json.load(f)

# PRECOMPUTE INTENT EMBEDDINGS
# --------------------------------------------------
INTENT_EMBEDDINGS = {
    intent: intent_model.encode(texts, convert_to_tensor=True)
    for intent, texts in INTENT_MAP.items()
}

# INTENT DETECTION (CORE)
# --------------------------------------------------
def _detect_from_text(text: str, threshold: float) -> Tuple[Optional[str], float]:
    if not text:
        return None, 0.0

    query_emb = intent_model.encode(text, convert_to_tensor=True)

    best_intent = None
    best_score = 0.0

    for intent, emb in INTENT_EMBEDDINGS.items():
        score = util.cos_sim(query_emb, emb).max().item()
        if score > best_score:
            best_score = score
            best_intent = intent

    if best_score < threshold:
        return None, best_score

    return best_intent, best_score

# PUBLIC API (TEXT OR IMAGE)
# --------------------------------------------------
def detect_intent(
    query: Optional[str] = None,
    image_path: Optional[str] = None,
    threshold: float = 0.45
) -> Tuple[Optional[str], float, str]:

    extracted_text = ""

    # Image-based intent
    if image_path:
        print(f"📷 Image received: {image_path}")
        extracted_text = extract_text_from_image(image_path)
        print(f"📝 OCR extracted text: {extracted_text}")

        intent, score = _detect_from_text(extracted_text, threshold)
        return intent, score, extracted_text

    # Text-based intent
    if query:
        intent, score = _detect_from_text(query, threshold)
        return intent, score, query

    return None, 0.0, ""
