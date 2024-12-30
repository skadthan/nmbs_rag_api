import boto3, uuid

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
roles_table = dynamodb.Table('Roles')

def create_users_table():
    table = dynamodb.create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'UserId',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'UserId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'email',
                'AttributeType': 'S'
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'EmailIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'email',
                        'KeyType': 'HASH'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Creating Users table...")
    table.wait_until_exists()
    print("Users table created successfully.")

def create_roles_table():
    table = dynamodb.create_table(
        TableName='Roles',
        KeySchema=[
            {
                'AttributeName': 'RoleId',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'RoleId',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Creating Roles table...")
    table.wait_until_exists()
    print("Roles table created successfully.")

def create_role_requests_table():
    table = dynamodb.create_table(
        TableName='RoleRequests',
        KeySchema=[
            {
                'AttributeName': 'RequestId',
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'RequestId',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    print("Creating RoleRequests table...")
    table.wait_until_exists()
    print("RoleRequests table created successfully.")


def generate_unique_role_id():
    """Generates a unique random role ID using UUID."""
    return str(uuid.uuid4())

def insert_sample_roles_with_random_id():
    roles = [
        {
            "role_name": "User",
            "application": "Nimbus Capability Statement AI Helper",
            "admin_access": False
        },
        {
            "role_name": "Admin",
            "application": "Nimbus Capability Statement AI Helper",
            "admin_access": True
        },
        {
            "role_name": "User",
            "application": "Nimbus Contract Language Enhancer",
            "admin_access": False
        },
        {
            "role_name": "Admin",
            "application": "Nimbus Contract Language Enhancer",
            "admin_access": True
        }
    ]

    for role in roles:
        role_id = generate_unique_role_id()
        role["RoleId"] = role_id
        roles_table.put_item(Item=role)
        print(f"Inserted role: {role['role_name']} with ID {role_id} for {role['application']}")


if __name__ == "__main__":
    #create_users_table()
    #create_roles_table()
    #create_role_requests_table()
    insert_sample_roles_with_random_id()
