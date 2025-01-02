from fastapi import APIRouter, HTTPException,Depends
from app.services.ai_app_config_srvc import get_ai_app_config,get_ai_apps
from app.routers.auth import get_current_user
router = APIRouter()

@router.get("/get-ai-app-config")
def get_profile(application_id: str,current_user: str = Depends(get_current_user)):
    try:
        response = get_ai_app_config(application_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ge-ai-apps")
def get_apps(current_user: str = Depends(get_current_user)):
    try:
        response = get_ai_apps()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

