from app.utilities.llm_client import get_bedrock_embedding_model
from app.utilities.esclient import get_es_connection
from app.utilities.s3.download_file import download_file
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_elasticsearch import ElasticsearchStore
from app.config import DEFAULT_INDEX_NAME
import chardet
from docx import Document
from langchain_community.document_loaders import Docx2txtLoader

def process_file(bucket_name: str, file_name: str):
    local_file = download_file(bucket_name, file_name)
    embedding_model = get_bedrock_embedding_model()
    es_client = get_es_connection()
    
    try:
        with open(local_file, "r",encoding='UTF-8') as file:
            #print("DEFAULT_INDEX_NAME: ", DEFAULT_INDEX_NAME)
            ES_INDEX_NAME=DEFAULT_INDEX_NAME
            loader = Docx2txtLoader(local_file)
            document= loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200,)
            split_data = text_splitter.split_documents(document)
            #print("split_data: ",split_data)
           
        es_vector_store = ElasticsearchStore(es_connection=es_client,index_name=ES_INDEX_NAME,embedding=embedding_model)
        docsearch = es_vector_store.from_documents(documents=split_data,embedding=embedding_model,index_name=ES_INDEX_NAME,es_connection=es_client)
        return docsearch
    except Exception as e:
        print(f"Error reading .docx file: {e}")
        return None