import asyncio
import inspect
from fastapi import APIRouter, HTTPException
from app.services.chat_service import handle_chat
from pydantic import BaseModel

from fastapi import APIRouter, HTTPException
from app.services.rag_chain_service import get_rag_chain, get_chain_with_history
from app.utilities import vector_store
from app.models.rag_models import RAGRequest, RAGResponse


# Mock Vectorstore (replace with actual implementation)
#vectorstore = vector_store.get_es_vector_store()  # Initialize your vectorstore here
vectorstore = vector_store.get_aoss_vector_store() 

# Initialize the RAG chain
rag_chain = get_rag_chain(vectorstore)
chain_with_history = get_chain_with_history(rag_chain)

async def process_rag(request: RAGRequest):
    """
    Processes a RAG request and returns the answer.
    """
    #print("before output")
    try:
        #print("request.query: ",request.query )
        #print("request.session_id: ",request.session_id )
        #print("Invoking RAG chain...")
        #print("\ntype(chain_with_history): ",type(chain_with_history))
        #print("chain_with_history 2",chain_with_history)
        async def wait_for_response(future):
            while not future.done():
                await asyncio.sleep(120)
            return future.result()
        try:
            task = asyncio.create_task(chain_with_history.invoke({"input": request.query}, config={"configurable": {"session_id": request.session_id}}))
            output = await asyncio.wait_for(task, timeout=120)
        except asyncio.TimeoutError:
            # Handle timeout, e.g., cancel the task, return a partial response, or raise an exception
            task.cancel()
            raise TimeoutError("RAG chain invocation timed out")
    

        #output = await chain_with_history.invoke({"input": request.query}, config={"configurable": {"session_id": request.session_id}})
        #print("RAG chain invocation completed. Output type:", type(output))

        # If output is a coroutine, await it again
        if inspect.iscoroutine(output):
            output =  output

        #print("after output", output)
        return RAGResponse(answer=output["answer"])
    except Exception as e:
        print(f"Error during RAG chain invocation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
