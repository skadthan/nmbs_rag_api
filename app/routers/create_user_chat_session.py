from fastapi import APIRouter, HTTPException
from app.services.get_user_chat_sessions_srvc import insert_user_session
from pydantic import BaseModel
from app.routers.auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends

class User(BaseModel):
    userid: str
    sessionId: str

router = APIRouter()

@router.post("/create")
async def get_user_chat_sessions(request: User,current_user: str = Depends(get_current_user)):
    try:
        response = insert_user_session(request.userid, request.sessionId)
        print(response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
