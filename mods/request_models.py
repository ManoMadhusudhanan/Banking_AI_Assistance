# models/request_models.py

from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    customer_id: str | None = None
