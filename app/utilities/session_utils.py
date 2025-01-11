import uuid
from datetime import datetime
import boto3
from botocore.config import Config
from app import config

dynamodb = boto3.resource("dynamodb",config=Config(region_name=config.AWS_REGION))
user_session_table_name = "UserSessionTable"
user_session_table_name = dynamodb.Table(user_session_table_name)

def generate_unique_session_id():
    # Generate a unique session ID using UUID4
    return str(uuid.uuid4())


def generate_unique_session_id(user_id=None):
    # Generate a UUID
    unique_id = uuid.uuid4()
    
    # Get the current timestamp in ISO format
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    
    # If a user ID is provided, include it in the session ID
    if user_id:
        return f"{user_id}-{timestamp}-{unique_id}"
    else:
        return f"{timestamp}-{unique_id}"


def start_new_session(user_id, session_name):
    session_id = generate_unique_session_id()  # Implement your own function
    add_new_session(user_id, session_id, session_name)
    return session_id

def add_new_session(user_id, session_id, session_name):
    
    table = dynamodb.Table("UserSessionTable")
    
    now = datetime.utcnow().isoformat()
    table.put_item(
        Item={
            "UserId": user_id,
            "SessionId": session_id,
            "SessionName": session_name,
            "CreatedAt": now,
            "LastAccessed": now,
        }
    )

def list_sessions(user_id):
    table = dynamodb.Table("UserSessionTable")
    
    response = table.query(
        KeyConditionExpression="UserId = :user_id",
        ExpressionAttributeValues={":user_id": user_id}
    )
    return response.get("Items", [])


def update_last_accessed(user_id, session_id):
    table = dynamodb.Table("UserSessionTable")
    
    now = datetime.utcnow().isoformat()
    table.update_item(
        Key={"UserId": user_id, "SessionId": session_id},
        UpdateExpression="SET LastAccessed = :now",
        ExpressionAttributeValues={":now": now},
    )

def insert_user_session(user_id, session_id):
    timestamp = datetime.utcnow().isoformat()
    print(timestamp)
    item = {
        "UserId": user_id,
        "SessionId": session_id,
        "createdAt": timestamp,
        "lastAccessedAt": timestamp,
        "isActive": True,
        "metadata": {
            "userAgent": "Mozilla/5.0",
            "ipAddress": "192.168.1.1"
        }
    }
    print(item)
    try:
        user_session_table_name.put_item(Item=item)
        print(f"Session {session_id} for user {user_id} inserted successfully.")
        response = {"error_code": 200, "message": "A new chat session id: " +session_id+" for the user id:  " +user_id+ " is created in DB successfully"}
        return response
    except Exception as e:
        print(f"Error inserting session: {e}")