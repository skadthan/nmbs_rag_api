from fastapi import APIRouter, HTTPException
from app.services.get_user_chat_sessions_srvc import get_user_sessions
from pydantic import BaseModel
from app.routers.auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends

class User(BaseModel):
    userid: str

class UserChatSessionsResponse(BaseModel):
    userId: str
    sessionId: str
    createdAt: str
    lastAccessedAt: str
    isActive: bool

router = APIRouter()

@router.post("/getuserchatsessions")
async def get_user_chat_sessions(request: User,current_user: str = Depends(get_current_user)):
    try:
        response = get_user_sessions(request.userid)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
