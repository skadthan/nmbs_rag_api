from passlib.context import CryptContext
from app import config
import boto3
from fastapi import HTTPException
from fastapi.responses import JSONResponse


# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')

# Use Passlib to hash and verify passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fetch_user_password(user_id: str):
    try:
        # Fetch user item from the Users table
        response = users_table.get_item(Key={"UserId": user_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="User not found in the database.")

        # Extract and return the password
        user_item = response["Item"]
        return user_item.get("password")
    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e  # Propagate the exception
    except Exception as e:
        print(f"Unexpected Exception: Error fetching password for UserId {user_id} - {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred while fetching password.")



def verify_user(username: str, password: str) -> bool:
    """
    Verifies if the provided username and password are correct.
    """
    try:
        # Fetch hashed password for the given username
        hashed_password = fetch_user_password(username)

        # Verify the provided password against the hashed password
        #print("Fetched hashed_password:", hashed_password)
        if not pwd_context.verify(password, hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password.")

        return True

    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise e  # Reraise HTTPException to propagate it

    except Exception as e:
        print(f"Unexpected Exception: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error occurred during user verification.")
