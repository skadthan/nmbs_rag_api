import os
from dotenv import load_dotenv

load_dotenv()  # This will load environment variables from a `.env` file

# AWS Configuration
AWS_PROFILE = profile_name = os.getenv("AWS_PROFILE", "ai-project") 
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_ENDPOINT = os.getenv("BEDROCK_ENDPOINT", "https://bedrock-runtime.us-east-1.amazonaws.com")
BEDROCK_ASSUME_ROLE_ARN ="arn:aws:iam::account-id:role/nmbs-ecs-role"
# Elasticsearch Local Configuration
#ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://localhost:9200")
# Elasticsearch Docker Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://host.docker.internal:9200")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "password")
SSL_ASSERT_FINGERPRINT = os.getenv("SSL_ASSERT_FINGERPRINT","48:DA:5E:B4:A2:E7:59:29:DF:FC:5A:9A:B6:72:50:E4:D1:58:1F:0B:6E:2B:EE:1B:CE:23:A2:79:B9:46:DD:5D")


# Amazon OpenSearch Serverless Configuration
AOSS_ENDPOINT = os.getenv("AOSS_ENDPOINT", "https://d5pfykmqchz1gw7wzshe.us-east-1.aoss.amazonaws.com")
AOSS_VECTORSTORE_NAME = os.getenv("AOSS_VECTORSTORE_NAME", "ashu-open-search-vector-db")
AOSS_VECTORSTORE_INDEX = os.getenv("AOSS_VECTORSTORE_INDEX", "ashu-open-search-vector-db-index")



# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "ashu-data")
S3_FILE_PREFIX = os.getenv("S3_FILE_PREFIX", "/nimbus/")

# Data Directory
S3_LOCAL_DATA_FOLDER= os.path.join(os.path.dirname(os.path.abspath(__name__)), "data")

# Default Vector Store
DEFAULT_INDEX_NAME = os.getenv("DEFAULT_INDEX_NAME", "nmbs-capabilities-index") #cms-marketing-guidance-vector-db, ashu-elastic-search-vector-db, nimbus-capabilities-vector-db

# Bedrock LLMs
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL_ID", "amazon.titan-tg1-large")

# General App Configurations
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))  # Default chunk size for text splitting
OVERLAP = int(os.getenv("OVERLAP", 50))  # Default overlap size for text chunks

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "app.log")

USER_CREDENTIALS = {
    "admin": os.getenv("ADMIN_PASSWORD", "Ananya#2021"),
    "skadthan": os.getenv("USER_PASSWORD", "Ashu#123"),
}

#CORS Configuration
CORS_ORGIN_URL ="https://apps.adeptaugmentit.com"