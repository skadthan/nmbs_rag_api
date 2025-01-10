from app.utilities.llm_client import get_bedrock_embedding_model
from app.utilities import esclient
from app.config import DEFAULT_INDEX_NAME
import app.config as conf
from langchain_elasticsearch import ElasticsearchStore
import boto3, os
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
from langchain_community.vectorstores import OpenSearchVectorSearch

def get_es_vector_store():
    vector_store_name = DEFAULT_INDEX_NAME #'ashu-elastic-search-vector-db'
    esconnection=esclient.get_es_connection()
    bedrockembedding=get_bedrock_embedding_model()
    count_documents=esconnection.count(index=vector_store_name)
    #print("Total Documents in the vector",count_documents["count"])
    es_vector_store = ElasticsearchStore(es_connection=esconnection,index_name=vector_store_name,embedding=bedrockembedding)
    return es_vector_store

def get_aoss_vector_store():
    vector_store_name = conf.AOSS_VECTORSTORE_NAME
    index_name = conf.AOSS_VECTORSTORE_INDEX
    embdedding_model=get_bedrock_embedding_model()

    aoss_client = boto3.client('opensearchserverless')
    collection = aoss_client.batch_get_collection(names=[vector_store_name])
    aoss_host_name = collection['collectionDetails'][0]['id'] + '.' + os.environ.get("AWS_DEFAULT_REGION", None) + '.aoss.amazonaws.com:443'
    print("SURESH-OpenSource-Host", aoss_host_name)

    service = 'aoss'
    credentials = boto3.Session().get_credentials()
    auth = AWSV4SignerAuth(credentials, os.environ.get("AWS_DEFAULT_REGION", None), service)

    aoss_vector_store = OpenSearchVectorSearch(
    index_name=index_name,
    embedding_function=embdedding_model,
    opensearch_url=aoss_host_name,
    http_auth=auth,
    timeout = 100,
    use_ssl = True,
    verify_certs = True,
    connection_class = RequestsHttpConnection,
    engine="faiss",
    )
    return aoss_vector_store