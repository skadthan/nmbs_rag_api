from fastapi import APIRouter, HTTPException
from app.services.batch_embedding_service import process_s3_bucket
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import get_current_user

class S3BucketProcessRequest(BaseModel):
    bucketName: str
    indexName: str

router = APIRouter()

@router.post("/processs3bucket")
async def process_embeddings(request: S3BucketProcessRequest,current_user: str = Depends(get_current_user)):
    try:
        print("request.bucketName, request.indexName", request.bucketName,"-" ,request.indexName)
        process_s3_bucket(request.bucketName, request.indexName)
        return {"status": "success", "message": f"All Files from AWS S3 {request.bucketName} bucket has been processed successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))