import sys
sys.path.append('/Users/skadthan/Desktop/Nimbus AI Project/code/rag-api/venv/lib/python3.13/site-packages')
from . import bedrockclient
from langchain_aws import BedrockLLM
from langchain_aws import BedrockEmbeddings
import os, boto3
from boto3.dynamodb.conditions import Key
from botocore.config import Config
from app import config
#from langchain_community.llms import Bedrock

#Create bedrock client instance function.

def get_bedrock_client():

    boto3_bedrock = bedrockclient.get_bedrock_client(
        #assumed_role=config.BEDROCK_ASSUME_ROLE_ARN,
        #region=os.environ.get("AWS_DEFAULT_REGION", None)
        region=config.AWS_REGION
    )
    return boto3_bedrock

def get_bedrock_embedding_model():
    boto3_bedrock=get_bedrock_client()
    bedrock_embeddings = BedrockEmbeddings(client=boto3_bedrock)
    return bedrock_embeddings

#Create titan embedding instance function.

def get_titan_embedding_model():
    embedding_model=BedrockEmbeddings(
    credentials_profile_name= 'default',
    model_id='amazon.titan-embed-text-v1')
    return embedding_model

# create the Anthropic Model

def get_bedrock_anthropic_claude_llm():
    boto3_bedrock=get_bedrock_client()
    #llm = Bedrock(model_id="anthropic.claude-v2", client=boto3_bedrock, model_kwargs={"max_tokens_to_sample": 200,"temperature": 0.2,"top_p": 0.9})
    llm = BedrockLLM(model_id="anthropic.claude-v2", client=boto3_bedrock, model_kwargs={"max_tokens_to_sample": 2048,"temperature": 0.2,"top_p": 0.9})
    return llm

def get_application_config(application_id):
    dynamodb = boto3.resource('dynamodb',config=Config(region_name=config.AWS_REGION))
    table = dynamodb.Table('AIApplicationConfig')

    response = table.scan(
        FilterExpression=Key('ApplicationId').eq(application_id)
    )

    if 'Items' not in response or not response['Items']:
        raise ValueError(f"No configuration found for application: {application_id}")

    return response['Items'][0]