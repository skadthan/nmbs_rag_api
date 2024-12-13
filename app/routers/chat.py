from fastapi import APIRouter, HTTPException
from app.services.chat_service import handle_chat
from pydantic import BaseModel
from app.routers.auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    humanRequest: str
    aiResponse: str

router = APIRouter()

@router.post("/ask",response_model=ChatResponse)
async def ask_chatbot(request: ChatRequest,current_user: str = Depends(get_current_user)):
    try:
        response = handle_chat(request.query)
        return {"humanRequest":request.query, "aiResponse": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
