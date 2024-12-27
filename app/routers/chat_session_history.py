from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chat_session_history_service import ChatSessionHistory
from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import get_current_user

router = APIRouter()

# Initialize ChatSessionHistory
chat_session = ChatSessionHistory(table_name="UserChatSessionHistoryTable")


class UserChatHistoryRequest(BaseModel):
    user_session_id: str


@router.post("/getchathistory")
async def get_current_user_history(request: UserChatHistoryRequest,current_user: str = Depends(get_current_user)):
    """
    Retrieve chat messages for the provided user session ID.
    """
    try:
        messages = await chat_session.get_session_history(request.user_session_id)
        return {"session_id": request.user_session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")
