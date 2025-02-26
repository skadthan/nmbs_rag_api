from app.utilities.llm_client import get_bedrock_embedding_model
from app.utilities import esclient
from app.config import DEFAULT_INDEX_NAME
import app.config as conf
from langchain_elasticsearch import ElasticsearchStore
import boto3, os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from langchain_community.vectorstores import OpenSearchVectorSearch
from app import config
from botocore.config import Config
import logging, json
import datetime

def get_es_vector_store():
    vector_store_name = DEFAULT_INDEX_NAME #'ashu-elastic-search-vector-db'
    esconnection=esclient.get_es_connection()
    bedrockembedding=get_bedrock_embedding_model()
    count_documents=esconnection.count(index=vector_store_name)
    #print("Total Documents in the vector",count_documents["count"])
    es_vector_store = ElasticsearchStore(es_connection=esconnection,index_name=vector_store_name,embedding=bedrockembedding)
    return es_vector_store

def get_aoss_vector_store():
    # Set up logging
    logging.basicConfig(level=config.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    try:
        # Get AWS credentials explicitly
        #session = boto3.Session()
        #credentials = session.get_credentials()
        # In get_aoss_vector_store():
        credentials = get_refreshable_credentials()
        frozen_credentials = credentials.get_frozen_credentials()
        
        logger.debug(f"Using AWS Region: {config.AWS_REGION}")
        logger.debug(f"Vector Store Name: {conf.AOSS_VECTORSTORE_NAME}")
        logger.debug(f"Index Name: {conf.AOSS_VECTORSTORE_INDEX}")

        logger.debug(f"AWS Access Key: {credentials.access_key}")
        logger.debug(f"AWS Secret Key: {credentials.secret_key}")
        logger.debug(f"AWS Session Token: {credentials.token}")

        print("printing frozen credentials")

        logger.debug(f"Frozen AWS Access Key: {frozen_credentials.access_key}")
        logger.debug(f"Frozen AWS Secret Key: {frozen_credentials.secret_key}")
        logger.debug(f"Frozen AWS Session Token: {frozen_credentials.token}")

        # Verify credentials are available
        if not all([credentials.access_key, credentials.secret_key]):
            raise ValueError("AWS credentials not found")

        # Initialize the AOSS client with explicit configuration
        aoss_client = boto3.client(
            'opensearchserverless',
            config=Config(
                region_name=config.AWS_REGION,
                retries={'max_attempts': 3, 'mode': 'standard'}
            )
        )

        # Get collection details
        collection_response = aoss_client.batch_get_collection(
            names=[conf.AOSS_VECTORSTORE_NAME]
        )
        
        if not collection_response.get('collectionDetails'):
            raise ValueError(f"Collection {conf.AOSS_VECTORSTORE_NAME} not found")
        else:
            pass
            #logger.debug(f"Collection Response: {collection_response}")
        
        collection_id = collection_response['collectionDetails'][0]['id']
        aoss_host_name = f"{collection_id}.{config.AWS_REGION}.aoss.amazonaws.com:443"
        #logger.debug(f"OpenSearch Host: {aoss_host_name}")

        # Initialize embedding model
        embedding_model = get_bedrock_embedding_model()

        # Create auth handler with explicit credentials
        auth = AWSV4SignerAuth(
            frozen_credentials,
            config.AWS_REGION,
            'aoss'
        )

        # Initialize vector store with detailed configuration
        aoss_vector_store = OpenSearchVectorSearch(
            index_name=conf.AOSS_VECTORSTORE_INDEX,
            embedding_function=embedding_model,
            opensearch_url=aoss_host_name,
            http_auth=auth,
            timeout=100,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            engine="faiss",
            retry_on_timeout=True,
            max_retries=3,
            # Add explicit headers for debugging
            client_options={
                "request_timeout": 30,
                "headers": {
                    "Content-Type": "application/json"
                }
            }
        )

        # Verify connection with a simple request
        try:
            #aoss_vector_store.client.info()
            response = aoss_vector_store.client.count()
            #logger.info(f"Successfully listed collections: {json.dumps(response, default=str)}")
            logger.info("Successfully connected to OpenSearch")
        except Exception as e:
            #logger.error(f"Failed to connect to OpenSearch: {str(e)}")
            raise {str(e)}

        return aoss_vector_store

    except Exception as e:
        #logger.error(f"Error in get_aoss_vector_store: {str(e)}")
        #raise {str(e)}
        raise Exception(f"OpenSearch connection failed: {str(e)}")
    
def get_refreshable_credentials():
    session = boto3.Session()
    credentials = session.get_credentials()
    
    # Check if credentials will expire soon (within 5 minutes)
    if hasattr(credentials, 'expiration') and credentials.expiration:
        time_until_expiry = (credentials.expiration - datetime.datetime.now(datetime.timezone.utc)).total_seconds()
        if time_until_expiry < 300:  # 5 minutes
            # Force refresh by creating a new session
            session = boto3.Session()
            credentials = session.get_credentials()
            print("Vector_Store: Boto Session Credentials Successfully refreshed")
    
    return credentials