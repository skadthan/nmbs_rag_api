from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import boto3
from uuid import uuid4
from passlib.context import CryptContext
from typing import List
from app.models.user_role_models import UserRegistration, RoleApproval

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
users_table = dynamodb.Table('Users')
roles_table = dynamodb.Table('Roles')
role_requests_table = dynamodb.Table('RoleRequests')

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(user: UserRegistration):
    try:
        # Check if user already exists
        response = users_table.get_item(Key={"UserId": user.email})
        if "Item" in response:
            raise HTTPException(status_code=400, detail="User already exists")

        # Hash password
        hashed_password = hash_password(user.password)

        # Create user entry
        #user_id = str(uuid4())
        users_table.put_item(
            Item={
                "UserId": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "date_of_birth": user.date_of_birth,
                "password": hashed_password,
                "roles": []  # Initially empty roles
            }
        )

        # Create role request entry
        request_id = str(uuid4())
        role_requests_table.put_item(
            Item={
                "RequestId": request_id,
                "UserId": user.email,
                "requested_roles": user.requested_roles,
                "status": "pending"
            }
        )
        return {"error_code": 200, "message": "User registered successfully. Role request pending approval.", "request_id": request_id}
    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        print("Exception: User Registration create_user ",str(e))
        # General error message
        error_message = {
                "status_code": 500,
                "error_message": str(e)
            }
        
        # Return a JSON response with the custom error message
        return JSONResponse(status_code=200, message=error_message)

def approve_roles(approval: RoleApproval):
    try:
        # Fetch role request
        response = role_requests_table.get_item(Key={"RequestId": approval.request_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Role request not found")

        role_request = response["Item"]
        
        if approval.status == "approved":
            # Update user roles
            user_id = role_request["UserId"]
            user_response = users_table.get_item(Key={"UserId": user_id})
            if "Item" not in user_response:
                raise HTTPException(status_code=404, detail="User not found")

            user = user_response["Item"]
            updated_roles = list(set(user.get("roles", []) + role_request["requested_roles"]))

            users_table.update_item(
                Key={"UserId": user_id},
                UpdateExpression="SET #roles = :roles",
                ExpressionAttributeNames={"#roles": "roles"},  # Escape reserved keyword
                ExpressionAttributeValues={":roles": updated_roles}
            )

        # Update role request status
        role_requests_table.update_item(
            Key={"RequestId": approval.request_id},
            UpdateExpression="SET #status = :status",  # Escape reserved keyword
            ExpressionAttributeNames={"#status": "status"},  # Alias for reserved keyword
            ExpressionAttributeValues={":status": approval.status}
        )
        return {"error_code": 200, "message": "Role request updated successfully."}
    except Exception as e:
        #raise HTTPException(status_code=500, detail=str(e))
        print("Exception: User Registration approve_roles - ",str(e))
        # General error message
        error_message = {
                "status_code": 500,
                "error_message": str(e)
            }
        
        # Return a JSON response with the custom error message
        return JSONResponse(status_code=200, message=error_message)