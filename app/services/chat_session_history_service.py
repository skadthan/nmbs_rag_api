from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from app.utilities import getiamuserid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import boto3
from botocore.config import Config

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
        self.dynamodb = boto3.resource('dynamodb', config=Config(region_name='us-east-1'))  # Initialize the DynamoDB resource
        self.table = self.dynamodb.Table(self.table_name)  # Reference the DynamoDB table

    async def get_session_history(self, user_session_id: str):
        """
        Retrieve chat messages for a given session ID.
        :param user_session_id: The session ID of the user.
        :return: List of messages from the chat history.
        """
        #history = DynamoDBChatMessageHistory(table_name=self.table_name,session_id=user_session_id,)
        #messages=history.messages
        """
        Fetch all messages for the current session from DynamoDB.
        """
        try:
            # Fetch the chat history from DynamoDB
            #print(f"Fetching from table: {self.table_name}, session ID: {user_session_id}")
            response = self.table.get_item(Key={'SessionId': user_session_id})
            #print("DynamoDB Response:", response)
            messages = response.get('Item', {}).get('History', [])
            #print("Chat History Messages:", messages)
            return messages
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            raise