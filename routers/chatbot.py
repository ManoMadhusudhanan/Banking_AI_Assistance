# routers/chatbot.py

from fastapi import APIRouter
from mods.request_models import ChatRequest
from services.banking_logic import process_banking_query

router = APIRouter(prefix="/chatbot", tags=["Banking Chatbot"])

@router.post("/ask")
def ask_bot(request: ChatRequest):
    response = process_banking_query(request.message, request.customer_id)
    return {"reply": response}
