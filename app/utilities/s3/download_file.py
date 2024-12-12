import boto3
import os

# Specify the AWS profile name
os.environ["AWS_DEFAULT_REGION"] = boto3.Session().region_name 
session = boto3.Session(profile_name='default')

# Initialize awsauth, open search parameters, boto clients and llm model 
s3 = session.client('s3')

def download_file(bucket_name,  file_name):
    #print('Debug:4, bucket_name & : file_name ', file_name)
    local_path_s3_file = f"/tmp/{file_name.split('/')[-1]}"
    s3.download_file(bucket_name, file_name, local_path_s3_file)
    #print('Downloaded S3 file to local_path: ', local_path_s3_file)
    return local_path_s3_file