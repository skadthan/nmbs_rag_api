from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utilities import getiamuserid
from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import get_current_user

router = APIRouter()


class UserIAMInfoRequest(BaseModel):
    user_iam_id: str

@router.get("/getiamuserid")
async def get_iam_user_id(current_user: str = Depends(get_current_user)):
    """
    Retrieve chat messages for the provided user session ID.
    """
    try:
        iamid =  getiamuserid.get_iam_user_id()
        return {"iam_id": iamid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving IAM Information: {str(e)}")

@router.get("/getiamusername")

async def get_iam_user_full_name(current_user: str = Depends(get_current_user)):
    """
    Retrieve chat messages for the provided user session ID.
    """
    try:
        username =  getiamuserid.get_iam_user_full_name()
        return {"iam_username": username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")
