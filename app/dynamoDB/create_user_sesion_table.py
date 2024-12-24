import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")

try:
    table = dynamodb.create_table(
        TableName="UserSessionTable",
        KeySchema=[
            {"AttributeName": "UserId", "KeyType": "HASH"},
            {"AttributeName": "SessionId", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "UserId", "AttributeType": "S"},
            {"AttributeName": "SessionId", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    table.meta.client.get_waiter("table_exists").wait(TableName="UserSessionTable")
    print("UserSessionTable created successfully!")
except Exception as e:
    print(f"Error creating table: {e}")
