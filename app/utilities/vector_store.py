from app.utilities.llm_client import get_bedrock_embedding_model
from app.utilities import esclient
from langchain.llms import Bedrock
from app.config import DEFAULT_INDEX_NAME
from langchain_elasticsearch import ElasticsearchStore

def get_es_vector_store():
    vector_store_name = DEFAULT_INDEX_NAME #'ashu-elastic-search-vector-db'
    esconnection=esclient.get_es_connection()
    bedrockembedding=get_bedrock_embedding_model()
    count_documents=esconnection.count(index=vector_store_name)
    print("Total Documents in the vector",count_documents["count"])
    es_vector_store = ElasticsearchStore(es_connection=esconnection,index_name=vector_store_name,embedding=bedrockembedding)
    return es_vector_store