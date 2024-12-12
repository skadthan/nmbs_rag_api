from fastapi import APIRouter, HTTPException
from app.services.chat_service import handle_chat
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    humanRequest: str
    aiResponse: str

router = APIRouter()

@router.post("/ask",response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest):
    try:
        response = handle_chat(request.query)
        return {"humanRequest":request.query, "aiResponse": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
