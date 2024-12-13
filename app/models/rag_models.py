from pydantic import BaseModel
from typing import List, Dict, Optional

class RAGRequest(BaseModel):
    session_id: str
    query: str

class ContextDocument(BaseModel):
    metadata: Optional[Dict[str, str]]  # Metadata is optional and contains key-value pairs
    page_content: Optional[str]  # Page content is optional


class RAGResponse(BaseModel):
    humanRequest: str
    aiResponse: str
    context: List[ContextDocument]  # List of context documents
