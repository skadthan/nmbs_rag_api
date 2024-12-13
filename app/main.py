from fastapi import FastAPI
from app.routers import chat, embeddings, chat_session_history,iam_info,chat_runnable_with_history, auth

app = FastAPI(root_path="/nmbs/api")
app.include_router(auth.router,prefix="/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/chat", tags=["Chatbot"])
app.include_router(chat_runnable_with_history.router,prefix="/chat", tags=["ContextualChatBot"])
app.include_router(embeddings.router, prefix="/embeddings", tags=["Embeddings"])
app.include_router(chat_session_history.router,prefix="/session",tags=["GetChatHistory"])
app.include_router(iam_info.router, prefix="/iam",tags=["GetIAMInfo"])



@app.get("/")
async def root():
    return {"message": "Welcome to the RAG API Service!"}
