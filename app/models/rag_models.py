from pydantic import BaseModel

class RAGRequest(BaseModel):
    session_id: str
    query: str

class RAGResponse(BaseModel):
    humanRequest: str
    aiResponse: str
