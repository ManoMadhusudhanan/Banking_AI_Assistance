from fastapi import FastAPI, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import requests
from collections import defaultdict
import time
import shutil
import os
import re
from spellchecker import SpellChecker
from text_utils import normalize_text
from rag_engine import rag_search
from intent_router import detect_intent
import numpy as np
from sentence_transformers import SentenceTransformer

# -----------------------------
# APP SETUP
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ADDED 
embedder = SentenceTransformer("all-MiniLM-L6-v2")
FAITHFULNESS_THRESHOLD = 0.25

# -----------------------------
# SPELL NORMALIZATION
# -----------------------------
spell = SpellChecker()

def normalize_query(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    corrected = []
    for word in text.split():
        if word.isalpha() and len(word) > 2:
            corrected.append(spell.correction(word) or word)
        else:
            corrected.append(word)

    return " ".join(corrected)

# -----------------------------
# CHAT MEMORY
# -----------------------------
CHAT_MEMORY = defaultdict(list)

# -----------------------------
# GROQ CHAT
# -----------------------------
def groq_chat(session_id: str, user_prompt: str):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {
            "role": "system",
           "content": (
                "You are a professional, polite banking assistant. "
                "Respond clearly and formally. "
                "Provide only general and safe guidance for banking-related questions. "
                "Guide users using universally applicable channels such as visiting a bank branch "
                "or contacting official customer care. "
                "Do not assume the availability of specific online or mobile banking features "
                "unless they are explicitly stated in the provided context. "
                "Never request passwords, OTPs, CVV, account numbers, customer IDs, "
                "or any personally identifiable or sensitive information."
            )


        }
    ]

    messages.extend(CHAT_MEMORY[session_id])
    messages.append({"role": "user", "content": user_prompt})

    payload = {
        "model": "llama-3.1-8b-instant",
        "temperature": 0.7,
        "messages": messages
    }

    res = requests.post(url, json=payload, headers=headers).json()

    if "choices" not in res:
        return "Hello! How can I assist you today?"

    reply = res["choices"][0]["message"]["content"].strip()

    CHAT_MEMORY[session_id].append({"role": "user", "content": user_prompt})
    CHAT_MEMORY[session_id].append({"role": "assistant", "content": reply})

    return reply

# -----------------------------
# COSINE SIMILARITY
# -----------------------------
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


#-----------------------------------
def needs_rag(query: str) -> bool:
    rag_triggers = [
        "procedure", "steps", "how to open", "documents required",
        "charges", "fees", "interest rate", "eligibility",
        "indusind", "account opening", "kyc", "minimum balance"
    ]
    return any(trigger in query for trigger in rag_triggers)

#--------NO STARS-----------
def clean_response(text: str) -> str:
    return text.strip()

# POLICY DECISION HELPERS (ADDED)
# -----------------------------
def decide_contact_update_path(query: str) -> str:
    q = query.lower()

    if any(x in q for x in ["lost phone", "sim lost", "number inactive"]):
        return "branch_only"

    if any(x in q for x in ["can't visit", "cannot visit", "far", "busy", "no time"]):
        return "customer_care_first"

    if any(x in q for x in ["app", "net banking", "online"]):
        return "digital_optional"

    return "default"


def build_contact_update_response(mode: str) -> str:
    if mode == "branch_only":
        return (
            "For security reasons, updating the registered mobile number in this case "
            "requires a visit to the nearest IndusInd Bank branch with valid photo identification."
        )

    if mode == "customer_care_first":
        return (
            "If visiting a branch is not convenient, you may contact IndusInd Bank customer care "
            "at 1860 267 7777 for guidance on the required process."
        )

    if mode == "digital_optional":
        return (
            "Customers registered for official digital banking services may check whether a "
            "mobile number update option is available under profile settings. "
            "If unavailable, a branch visit is recommended."
        )

    return (
        "You may update the registered mobile number by visiting a nearby IndusInd Bank branch "
        "or by contacting customer care at 1860 267 7777. "
        "Identity verification is mandatory for such updates."
    )


def suggest_follow_up(mode: str) -> str | None:
    if mode == "branch_only":
        return "Would you like to know the documents required for the branch visit?"

    if mode == "customer_care_first":
        return "Would you like the customer care working hours?"

    if mode == "digital_optional":
        return "Would you like guidance on checking this through digital banking?"

    return "Would you like to know the documents required to update your mobile number?"

# CHATBOT ENDPOINT
# -----------------------------
@app.post("/chatbot/ask")
async def chatbot(
    session_id: str = Form(...),
    message: str = Form(""),
    image: UploadFile = File(None)
):
    start_time = time.time()
    image_path = None

    # IMAGE UPLOAD
    if image:
        image_path = f"{UPLOAD_DIR}/{image.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    raw_query = (message or "").strip()
    normalized_query = normalize_text(raw_query)

    intent, score, detected_text = detect_intent(
        query=normalized_query if normalized_query else None,
        image_path=image_path
    )

    final_query = normalized_query
    latency = round(time.time() - start_time, 2)

        # ---------------- POLICY-GUARDED CONTACT UPDATE ----------------
    contact_update_keywords = [
        "change contact number", "update contact number",
        "change mobile", "update mobile",
        "registered mobile", "passbook update"
    ]

    if final_query and any(k in final_query for k in contact_update_keywords):
        mode = decide_contact_update_path(final_query)
        reply = build_contact_update_response(mode)
        follow_up = suggest_follow_up(mode)

        return {
            "reply": reply,
            "follow_up": follow_up,
            "metrics": {
                "used_rag": False,
                "latency": latency
            }
        }

    BANKING_HINTS = [

    # ---------------- BASIC BANKING ----------------
    "bank", "banking", "indusind", "indusind bank",
    "branch", "bank branch", "registered office", "helpline",
    "customer care", "contact", "contact number",

    # ---------------- ACCOUNTS ----------------
    "account", "savings account", "current account", "salary account",
    "open account", "account opening", "online account",
    "offline account", "account number", "account details",
    "account type", "account variant", "account features",
    "minimum balance", "average balance", "maintenance fee",
    "dormant account", "reactivate account", "close account",

    # ---------------- PASSBOOK & PROFILE ----------------
    "passbook", "passbook update", "update passbook",
    "contact number change", "change contact number",
    "mobile number", "change mobile", "update mobile",
    "update details", "profile update", "personal details",
    "registered mobile", "registered number",

    # ---------------- KYC & DOCUMENTS ----------------
    "kyc", "video kyc", "pan", "pan card",
    "aadhaar", "aadhar", "aadhaar card",
    "id proof", "address proof",
    "documents required", "required documents",
    "eligibility", "age limit", "guardian",
    "minor account",

    # ---------------- NOMINEE ----------------
    "nominee", "add nominee", "change nominee",
    "nomination", "nominee update", "nominee deletion",

    # ---------------- DEPOSITS & WITHDRAWALS ----------------
    "deposit", "cash deposit", "withdraw", "cash withdrawal",
    "atm", "cdm", "cheque", "cheque deposit",

    # ---------------- PAYMENTS & TRANSFERS ----------------
    "neft", "rtgs", "imps", "upi",
    "fund transfer", "money transfer",
    "send money", "receive money",
    "payment", "transaction", "transfer charges",
    "ifsc", "swift", "nach", "auto debit",

    # ---------------- INTEREST & CHARGES ----------------
    "interest", "interest rate", "interest slab",
    "charges", "fees", "service charges",
    "processing fee", "penalty",
    "late fee", "maintenance charges",

    # ---------------- CARDS (GENERAL) ----------------
    "card", "debit card", "credit card",
    "atm card", "rupay", "visa", "mastercard",
    "contactless card",

    # ---------------- CREDIT CARD MANAGEMENT ----------------
    "card application", "apply credit card",
    "card status", "card activation",
    "block card", "unblock card",
    "lost card", "stolen card",
    "add on card", "add-on card",
    "card limit", "increase limit",
    "credit limit", "cash advance",

    # ---------------- CREDIT CARD PAYMENTS ----------------
    "credit card bill", "bill payment",
    "statement", "card statement",
    "outstanding balance", "total due",
    "minimum due", "due date",
    "emi", "convert to emi",
    "apr", "interest on card",

    # ---------------- REWARDS & BENEFITS ----------------
    "reward points", "redeem points",
    "cashback", "offers", "discounts",
    "lounge access", "airport lounge",
    "movie tickets", "bookmyshow",
    "insurance", "golf benefits",
    "forex markup",

    # ---------------- LOANS (GENERAL) ----------------
    "loan", "business loan", "personal loan",
    "quick loan", "instant loan",
    "collateral free loan",
    "loan amount", "loan eligibility",
    "loan tenure", "loan interest",

    # ---------------- LOAN PROCESS ----------------
    "apply loan", "loan application",
    "loan approval", "loan disbursal",
    "emi", "emi date", "missed emi",
    "pre emi", "pre-emi",
    "foreclosure", "prepayment",
    "loan charges",

    # ---------------- CREDIT SCORE ----------------
    "cibil", "credit score",
    "minimum cibil", "credit history",

    # ---------------- BUSINESS LOAN ----------------
    "business vintage", "profitability",
    "business age", "turnover",
    "bank statement", "pdf statement",

    # ---------------- DIGITAL BANKING ----------------
    "net banking", "internet banking",
    "mobile banking", "indie app",
    "indusmobile", "online banking",

    # ---------------- SECURITY & SAFETY ----------------
    "fraud", "phishing", "security",
    "safe banking", "card safety",
    "otp", "pin", "cvv",  # (for detection, not answering)

]

    is_probable_banking = any(hint in final_query for hint in BANKING_HINTS)
    image_uploaded = bool(image)

        # ---------------- BANKING QUERIES ----------------
    if intent is not None or is_probable_banking or image_uploaded:

        use_rag = True

        # Case 1: Needs RAG
        if use_rag:
            context_chunks = rag_search(final_query)
            context = "\n".join(context_chunks) if isinstance(context_chunks, list) else context_chunks

            if not context or len(context.strip()) < 50:

                # Banking-related question → LLM should answer
                if intent is not None or is_probable_banking or image_uploaded:
                    reply = groq_chat(session_id, final_query)
                    return {
                        "reply": reply,
                        "metrics": {
                            "used_rag": False,
                            "latency": latency
                        }
                    }

                #  Non-banking or general knowledge → allow LLM
                reply = clean_response(groq_chat(session_id, final_query))
                return {
                    "reply": reply,
                    "metrics": {
                        "used_rag": False,
                        "latency": latency
                    }
                }



            prompt = f"""
You are a professional banking assistant.

Use the CONTEXT below as a reference when it is relevant.
If the context fully answers the question, base your response on it.

If the context does NOT contain the answer but the question is related to banking,
answer using general banking knowledge and best practices.

Do NOT mention phrases like "the context does not mention" or
"the document does not say".

Do NOT ask for or request personal details such as account number,
customer ID, OTP, or CVV.

Only if the question is NOT related to banking, reply exactly:
"Please contact the bank’s toll-free number 7485 for assistance."

CONTEXT:
{context}

USER QUESTION:
{final_query}
"""

            answer = groq_chat(session_id, prompt)
            answer = clean_response(answer)

            similarity = cosine_similarity(
                embedder.encode(answer),
                embedder.encode(context)
            )

            faithfulness = 1 if similarity >= FAITHFULNESS_THRESHOLD else 0

            return {
                "reply": answer,
                "metrics": {
                    "used_rag": True,
                    "faithfulness": faithfulness,
                    "latency": latency
                }
            }

        #  Case 2: General banking → LLM ONLY
        reply = clean_response(groq_chat(session_id, final_query))
        return {
            "reply": reply,
            "metrics": {
                "used_rag": False,
                "latency": latency
            }
        }

    # ---------------- CONVERSATIONAL ----------------
    if final_query:
       reply = clean_response(groq_chat(session_id, final_query))
       return {
            "reply": reply,
            "metrics": {
                "used_rag": False,
                "latency": latency
            }
        }   

    # ---------------- FALLBACK ----------------
    reply = clean_response(groq_chat(session_id, final_query or "hello"))
    return {
        "reply": reply,
        "metrics": {
            "used_rag": False,
            "latency": latency
        }
    }


# UI
# -----------------------------
@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse("templates/index.html")
