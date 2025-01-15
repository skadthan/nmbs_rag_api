# Add health check endpoint
from fastapi import APIRouter

router = APIRouter()
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Welcome to Nimbus AI Application APIs"
    }