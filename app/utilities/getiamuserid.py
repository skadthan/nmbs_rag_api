import boto3
from botocore.config import Config
from app import config

# Initialize the IAM client
iam_client = boto3.client('iam', config=Config(region_name=config.AWS_REGION))
client = boto3.client('sts',config=Config(region_name=config.AWS_REGION))


def get_iam_user_id():
    """
    Fetches the IAM user ID.
    Replace this logic with your method for retrieving the current IAM user ID.
    :return: A unique IAM user ID string.
    """
    # Get the caller identity
    identity = client.get_caller_identity()
    
    # Extract and return the User ID
    user_id = identity['UserId']
    return user_id


def get_iam_user_full_name():
    """
    Fetches the full name of the current IAM user.
    :return: The full name of the IAM user (if exists) or the User ARN as fallback.
    """
    # Get the caller identity
    identity = client.get_caller_identity()
    
    # Extract the User ARN from the identity
    user_arn = identity['Arn']
    
    # Check if the ARN corresponds to an IAM user
    if 'user/' in user_arn:
        # Extract the user name from the ARN
        user_name = user_arn.split('/')[-1]
        
        # Get IAM user details
        response = iam_client.get_user(UserName=user_name)
        user = response['User']
        
        # Full name can be in Tags or User Metadata (if set)
        full_name = None
        if 'Tags' in user:
            for tag in user['Tags']:
                if tag['Key'].lower() in ('full_name', 'name'):
                    full_name = tag['Value']
        
        # Return full name if found, otherwise the user name
        return full_name or user_name
    
    return "Unknown User"

# Get the full name of the IAM user
user_full_name = get_iam_user_full_name()
#print(user_full_name)

# Get UserId for sessionId
user_id = get_iam_user_id()
#print(user_id)
