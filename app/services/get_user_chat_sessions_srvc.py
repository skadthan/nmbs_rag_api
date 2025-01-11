import boto3
from botocore.config import Config
from app.utilities.session_utils import insert_user_session
from app import config

dynamodb = boto3.resource("dynamodb", config=Config(region_name=config.AWS_REGION))
table_name = "UserSessionTable"
table = dynamodb.Table(table_name)


def create_user_session(user_id, session_id):
    try:
        response = insert_user_session(user_id, session_id)
        print(response)
        return response
    except Exception as e:
        print(f"Error fetching user sessions: {e}")
        return None


def get_user_sessions(user_id):
    try:
        # Perform a query on the UserSessionTable
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("UserId").eq(user_id)
        )
        sessions = response.get("Items", [])
        #print(sessions)
        return sessions
    except Exception as e:
        print(f"Error fetching user sessions: {e}")
        return None
    
# Example Usage
'''
user_id = "skadthan"
sessions = get_user_sessions(user_id)

if sessions:
    print(f"Sessions for user {user_id}:")
    for session in sessions:
        print(session)
else:
    print(f"No sessions found for user {user_id}")
'''