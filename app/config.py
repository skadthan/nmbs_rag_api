import os
from dotenv import load_dotenv

load_dotenv()  # This will load environment variables from a `.env` file

# AWS Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_ENDPOINT = os.getenv("BEDROCK_ENDPOINT", "https://bedrock-runtime.us-east-1.amazonaws.com")

# Elasticsearch Configuration
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "https://localhost:9200")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD", "Ashu#123")
SSL_ASSERT_FINGERPRINT = os.getenv("SSL_ASSERT_FINGERPRINT","48:DA:5E:B4:A2:E7:59:29:DF:FC:5A:9A:B6:72:50:E4:D1:58:1F:0B:6E:2B:EE:1B:CE:23:A2:79:B9:46:DD:5D")

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "ashu-data")
S3_FILE_PREFIX = os.getenv("S3_FILE_PREFIX", "/nimbus/")

# Default Vector Store
DEFAULT_INDEX_NAME = os.getenv("DEFAULT_INDEX_NAME", "nimbus-capabilities-vector-db") #cms-marketing-guidance-vector-db, ashu-elastic-search-vector-db

# Bedrock LLMs
DEFAULT_MODEL_ID = os.getenv("DEFAULT_MODEL_ID", "amazon.titan-tg1-large")

# General App Configurations
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() in ("true", "1", "yes")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))  # Default chunk size for text splitting
OVERLAP = int(os.getenv("OVERLAP", 50))  # Default overlap size for text chunks

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "app.log")
