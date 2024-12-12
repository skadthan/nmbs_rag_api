from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from app.utilities import getiamuserid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserChatHistoryRequest(BaseModel):
    user_session_id: str

class ChatSessionHistory:
    """
    A class to manage chat session history using DynamoDB.
    """

    def __init__(self, table_name: str):
        """
        Initialize the ChatSessionHistory with a DynamoDB table name.
        :param table_name: The name of the DynamoDB table.
        """
        self.table_name = table_name

    async def get_session_history(self, user_session_id: str):
        """
        Retrieve chat messages for a given session ID.
        :param user_session_id: The session ID of the user.
        :return: List of messages from the chat history.
        """
        history = DynamoDBChatMessageHistory(
            table_name=self.table_name,
            session_id=user_session_id,
        )
        messages=history.messages
        #print("\n DynamoDBChatMessageHistory: ", messages)
        return messages