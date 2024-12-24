import boto3
dynamodb = boto3.resource("dynamodb")
client = boto3.client('sts')

try:
    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName="UserChatSessionHistoryTable",
        KeySchema=[{"AttributeName": "SessionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "SessionId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    # Wait until the table exists.
    table.meta.client.get_waiter("table_exists").wait(TableName="UserChatSessionHistoryTable")

    # Print out some data about the table.
    print(table.item_count)
    print("UserSessionTable created successfully!")
except Exception as e:
    print(e)