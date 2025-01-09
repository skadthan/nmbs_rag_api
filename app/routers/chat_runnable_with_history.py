import inspect, uuid
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
        # Initialize session ID
        session_id = request.session_id
        # Prepare user message
        user_message = {
            "Role": "user",
            "Content": request.query,
            "MessageId": str(uuid.uuid4()),
            "ResponseMetadata": {}
        }

        # Format the AI message
        context_documents = []
        if "context" in ai_response:  # Assuming "context" contains document objects
            for doc in ai_response["context"]:
                metadata = getattr(doc, "metadata", {})
                page_content = getattr(doc, "page_content", "")

                # Append document details
                context_documents.append({
                    "page_content": page_content,
                    "source": metadata.get("source", "unknown")
                })

        ai_message = {
            "Role": "ai",
            "Content": ai_response["answer"],
            "MessageId": str(uuid.uuid4()),
            "ResponseMetadata": {
                "sources": context_documents
            }
        }

        # Construct the final response
        response = {
            "status_code": 200,
            "session_id": session_id,
            "messages": [user_message, ai_message]
        }

        return response
    except Exception as e:
        print("Exception: contextualbot",str(e))
        #raise HTTPException(status_code=500, detail=str(e))
        #return {"humanRequest":request.query, "aiResponse": str(e)}
        # General error message
        error_message = {
                "status_code": 500,
                "error_message": str(e)
            }
        
        # Return a JSON response with the custom error message
        return JSONResponse(status_code=200, content={"message": error_message})
