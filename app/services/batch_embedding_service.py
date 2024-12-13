from langchain.document_loaders import CSVLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.vectorstores import FAISS
from pathlib import Path

#from langchain.embeddings import BedrockEmbeddings #Warning message, this is updated to the the following import.
from langchain_aws import BedrockEmbeddings
from langchain_community.document_loaders import Docx2txtLoader
from langchain.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pptx import Presentation
from openpyxl import load_workbook
from langchain.schema import Document
from app.utilities.llm_client import get_bedrock_embedding_model
from app.utilities.esclient import get_es_connection
from app.utilities.s3.download_file import sync_s3_bucket_to_local
import os
from app import config
from langchain_elasticsearch import ElasticsearchStore
from app.config import DEFAULT_INDEX_NAME
from pathlib import Path

def load_docx(file):
    loader = Docx2txtLoader(file)
    documents= loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200,)
    split_data = text_splitter.split_documents(documents)
    print(f"Number of documents={len(documents)}")
    return split_data

def load_pdf(file):
    loader = PyPDFDirectoryLoader(file)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200,)
    split_data = text_splitter.split_documents(documents)
    print(f"Number of documents={len(documents)}")
    return split_data

def load_csv(file):
    loader = CSVLoader(file) # --- > 219 docs with 400 chars, each row consists in a question column and an answer column
    documents = loader.load() #
    print(f"Number of documents={len(documents)}")
    split_data = CharacterTextSplitter(chunk_size=2000, chunk_overlap=400, separator=",").split_documents(documents)
    return split_data

def load_xlsx(file):
    workbook = load_workbook(file)
    full_text = ""
    documents = []
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        for row in sheet.iter_rows(values_only=True):
            row_text = " ".join([str(cell) if cell is not None else "" for cell in row])
            full_text += row_text + "\n"
    
    documents.append(Document(page_content=full_text, metadata={"source": str(file)}))
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200,)
    split_data = text_splitter.split_documents(documents)
    print(f"Processed {len(split_data)} document chunks.")
    return split_data

def load_pptx(file):
    presentation = Presentation(file)
    full_text = ""
    documents = []
    
    for slide in presentation.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                full_text += shape.text + "\n"
    
    documents.append(Document(page_content=full_text, metadata={"source": str(file)}))
    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=200,)
    split_data = text_splitter.split_documents(documents)
    print(f"Processed {len(docs)} document chunks.")
    return split_data
    

def process_s3_bucket(bucket_name: str, vector_index: str):
    es_vector_store=None
    folder_path = config.S3_LOCAL_DATA_FOLDER
    s3_prefix=""
    #sync_s3_bucket_to_local(bucket_name,folder_path,s3_prefix)

    if not vector_index:
        ES_INDEX_NAME=DEFAULT_INDEX_NAME
    else:
        ES_INDEX_NAME=vector_index
    
    embedding_model = get_bedrock_embedding_model()
    es_client = get_es_connection()
    folder_path = Path(folder_path)

    for file_path in folder_path.iterdir():
        try:
            if file_path.is_file():
                #print(f"Processing file: {file_path}")
                file_extension = os.path.splitext(file_path)[1].lower()
                # Check the type based on extension
                
                if file_extension == '.docx':
                    file_type = 'Word Document'
                    docs=load_docx(file_path)
                elif file_extension == '.ppt' or file_extension == '.pptx':
                    file_type = 'PowerPoint Presentation'
                    docs=load_pptx(file_path)
                elif file_extension == '.xlsx':
                    file_type = 'Excel Spreadsheet'
                    docs=load_xlsx(file_path)
                elif file_extension == '.pdf':
                    file_type = 'PDF Document'
                    loader = PyPDFDirectoryLoader(file_path)
                    docs=load_pdf(file_path)
                elif file_extension == '.csv':
                    file_type = 'CSV File'
                    docs=load_csv(file_path)
                else:
                    file_type = 'Unknown Type'

                print(f"{file_path}: {file_type}")

                # Update or create the ElasticSearch vectorstore
                if es_vector_store is None:
                    es_vector_store = ElasticsearchStore(es_connection=es_client,index_name=ES_INDEX_NAME,embedding=embedding_model)
                    docsearch = es_vector_store.from_documents(documents=docs,embedding=embedding_model,index_name=ES_INDEX_NAME,es_connection=es_client)
                else:
                    es_vector_store.add_documents(documents=docs)     

        except Exception as e:
            print(f"Error processing {file_path}: {e}")