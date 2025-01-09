import boto3
from datetime import datetime
from botocore.config import Config

dynamodb = boto3.resource("dynamodb",config=Config(region_name='us-east-1'))
table_name = "UserSessionTable"
table = dynamodb.Table(table_name)

def insert_user_session(user_id, session_id):
    timestamp = datetime.utcnow().isoformat()
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
        table.put_item(Item=item)
        print(f"Session {session_id} for user {user_id} inserted successfully.")
    except Exception as e:
        print(f"Error inserting session: {e}")

# Example Usage
insert_user_session("skadthan", "session-3")
