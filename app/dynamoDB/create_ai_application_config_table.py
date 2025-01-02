import boto3
from decimal import Decimal
from dynamoDB.create_sequence import generate_sequence_number

def create_ai_application_config_table():
    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='AIApplicationConfig',
        KeySchema=[
            {
                'AttributeName': 'ApplicationId',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ApplicationId',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    print("Creating AIApplicationConfig table...")
    table.wait_until_exists()
    print("Table created successfully!")
    return table


def insert_ai_application_config_data():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('AIApplicationConfig')

    applications = [
        {
            "ApplicationId": str(generate_sequence_number()),
            "ApplicationName": "Nimbus Capability Statement AI Helper",
            "ModelName": "anthropic.claude-3-sonnet",
            "ModelParams": {
                "temperature": Decimal("0.0"),
                "top_p": Decimal("0.5"),
                "max_tokens_to_sample": Decimal("2000")
            },
            "SystemPrompt":  "You are assisting in generating a comprehensive capabilities statement based on user queries and contextual information."
    "Given the chat history and the latest user query, rewrite the query to be a self-contained question,"
    "including any missing information required to answer it effectively. Ensure the question is framed professionally"
    "and aligns with the goal of constructing a detailed capabilities statement."
    "Do NOT answer the question—only reformulate it. If no reformulation is needed, return the query as is.",
            "QAPrompt": """You are an AI assistant tasked with providing detailed and relevant responses for generating a capabilities statement. \
Using the retrieved documents and context, answer the user query as accurately and professionally as possible. \
If the retrieved context does not contain sufficient information to answer the query, state: \
"I do not have enough context to provide an answer."\

Guidelines:\
1. Provide answers that are factual and directly relevant to constructing a capabilities statement.\
2. Use concise, professional language tailored to the capabilities domain.\
3. Reference retrieved context explicitly when possible, such as contracts, proposals, or assessments.\

{context}"""
        },
        {
            "ApplicationId": str(generate_sequence_number()),
            "ApplicationName": "Nimbus Contract Language Enhancer",
            "ModelName": "anthropic.claude-3-sonnet",
            "ModelParams": {
                "temperature": Decimal("0.2"),
                "top_p": Decimal("0.9"),
                "max_tokens_to_sample": Decimal("1500")
            },
            "SystemPrompt":  "You are assisting in generating a comprehensive capabilities statement based on user queries and contextual information."
    "Given the chat history and the latest user query, rewrite the query to be a self-contained question,"
    "including any missing information required to answer it effectively. Ensure the question is framed professionally"
    "and aligns with the goal of constructing a detailed capabilities statement."
    "Do NOT answer the question—only reformulate it. If no reformulation is needed, return the query as is.",
            "QAPrompt": """You are an AI assistant tasked with providing detailed and relevant responses for generating a capabilities statement. \
Using the retrieved documents and context, answer the user query as accurately and professionally as possible. \
If the retrieved context does not contain sufficient information to answer the query, state: \
"I do not have enough context to provide an answer."\

Guidelines:\
1. Provide answers that are factual and directly relevant to constructing a capabilities statement.\
2. Use concise, professional language tailored to the capabilities domain.\
3. Reference retrieved context explicitly when possible, such as contracts, proposals, or assessments.\

{context}"""
        }
    ]

    for app in applications:
        table.put_item(Item=app)

    print("Inserted application configurations successfully!")

if __name__ == "__main__":
    # Call the function
    #create_ai_application_config_table()

    # Call the function
    insert_ai_application_config_data()