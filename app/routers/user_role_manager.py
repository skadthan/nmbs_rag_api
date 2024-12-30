from fastapi import APIRouter, HTTPException,Depends
from app.models.user_role_models import UserRegistration, RoleApproval
from app.services.user_role_manager_srvc import create_user,approve_roles
from app.routers.auth import get_current_user
router = APIRouter()

@router.post("/register")
def register_user(user: UserRegistration,current_user: str = Depends(get_current_user)):
    try:
        response = create_user(user)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve-role")
def approve_user_roles(approval: RoleApproval,current_user: str = Depends(get_current_user)):
    try:
        response = approve_roles(approval)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

