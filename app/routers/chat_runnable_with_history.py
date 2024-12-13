import inspect
from fastapi import APIRouter, HTTPException
from app.services.chat_runnable_with_history_service import process_rag
from pydantic import BaseModel
from app.services import chat_contextual_service as cc

from fastapi import APIRouter, HTTPException
from app.services.rag_chain_service import get_rag_chain, get_chain_with_history
from app.models.rag_models import RAGRequest, RAGResponse
from fastapi import APIRouter, HTTPException, Depends
from app.routers.auth import get_current_user
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/contextualbot", response_model=RAGResponse)

async def contexctual_chatbot(request: RAGRequest,current_user: str = Depends(get_current_user)):
    try:
        ai_response=cc.contexctual_chat_invoke(request)
        # Extract relevant contextual information
        context_documents = []
        for doc in ai_response.get("context", []):  # Assuming "context" contains a list of documents
            metadata = doc.metadata if hasattr(doc, "metadata") else {}
            page_content = doc.page_content if hasattr(doc, "page_content") else ""
            
            # Construct document details
            context_documents.append({
                "metadata": metadata,
                "page_content": page_content
            })

        # Construct the full response
        response = {
            "status_code": 200,
            "humanRequest": request.query,
            "aiResponse": ai_response["answer"],
            "context": context_documents  # Include metadata and content in the response
        }
        
        return response
    except Exception as e:
        print("Exception: contextualbot",str(e))
        #raise HTTPException(status_code=500, detail=str(e))
        #return {"humanRequest":request.query, "aiResponse": str(e)}
        # General error message
        error_message = {
                "status_code": 500,
                "message": str(e)
            }
        
        # Return a JSON response with the custom error message
        return JSONResponse(status_code=200, content=error_message)
