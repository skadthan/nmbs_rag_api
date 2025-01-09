from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
import boto3
from uuid import uuid4
from passlib.context import CryptContext
from typing import List
from app.models.user_role_models import UserRegistration, RoleApproval, User
import logging
from botocore.config import Config

# Enable debug logging
#logging.basicConfig(level=logging.DEBUG)
#boto3.set_stream_logger('', logging.DEBUG)

dynamodb = boto3.resource('dynamodb', config=Config(region_name='us-east-1'))
ai_app_config_table = dynamodb.Table('AIApplicationConfig')


def get_ai_app_config(application_id: str):
    try:
        # Fetch user information from Users table
        response = ai_app_config_table.get_item(Key={"ApplicationId": application_id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="AI Application not found")
        
        ai_app_config = response["Item"]
    

        # Build a structured response
        ai_app_profile = {
            "ApplicationId": ai_app_config.get("ApplicationId"),
            "ApplicationName": ai_app_config.get("ApplicationName"),
            "ModelId": ai_app_config.get("ModelId"),
            "ModelName": ai_app_config.get("ModelName"),
            "ModelParams": ai_app_config.get("ModelParams"),
            "SystemPrompt": ai_app_config.get("SystemPrompt"),
            "QAPrompt": ai_app_config.get("QAPrompt"),
        }

        #print("AI Application Configuration Profile Retrieved: ", ai_app_profile)
        return ai_app_profile

    except HTTPException as http_exc:
        # Explicitly re-raise HTTP exceptions
        print("HTTP Exception: ", str(http_exc))
        raise http_exc
    except Exception as e:
        # Handle unexpected exceptions
        print("Exception: Error fetching AI Application Configuration profile - ", str(e))
        error_message = {
            "status_code": 500,
            "error_message": f"An internal error occurred: {str(e)}"
        }
        return JSONResponse(status_code=500, content=error_message)


def get_ai_apps():
    try:
        # Fetch all items from the AIApplicationConfig table
        response = ai_app_config_table.scan()

        if 'Items' not in response or not response['Items']:
            raise HTTPException(status_code=404, detail="AI Application config table is empty")

        # Build a structured response
        ai_apps = []
        for item in response['Items']:
            ai_apps.append({
                "ApplicationId": item.get("ApplicationId"),
                "ApplicationName": item.get("ApplicationName")
            })

        print("AI Applications Retrieved: ", ai_apps)
        return ai_apps

    except HTTPException as http_exc:
        # Explicitly re-raise HTTP exceptions
        print("HTTP Exception: ", str(http_exc))
        raise http_exc
    except Exception as e:
        # Handle unexpected exceptions
        print("Exception: Error fetching AI Application Configuration table - ", str(e))
        error_message = {
            "status_code": 500,
            "error_message": f"An internal error occurred: {str(e)}"
        }
        return JSONResponse(status_code=500, content=error_message)
