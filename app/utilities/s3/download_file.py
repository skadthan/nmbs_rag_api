import boto3
import os
from botocore.config import Config

# Specify the AWS profile name
#os.environ["AWS_DEFAULT_REGION"] = boto3.Session().region_name 
#session = boto3.Session(profile_name='default')

# Initialize awsauth, open search parameters, boto clients and llm model 
#s3 = session.client('s3')
s3 = boto3.resource('s3', config=Config(region_name='us-east-1'))

def download_file(bucket_name,  file_name):
    #print('Debug:4, bucket_name & : file_name ', file_name)
    local_path_s3_file = f"/tmp/{file_name.split('/')[-1]}"
    s3.download_file(bucket_name, file_name, local_path_s3_file)
    #print('Downloaded S3 file to local_path: ', local_path_s3_file)
    return local_path_s3_file

def sync_s3_bucket_to_local(s3_bucket_name, local_directory, s3_prefix=""):
    """
    Sync files from an S3 bucket to a local directory.

    :param s3_bucket_name: Name of the S3 bucket.
    :param local_directory: Local directory to save the files.
    :param s3_prefix: Prefix of the files in S3 (optional).
    :param region_name: AWS region where the S3 bucket is located (default: us-east-1).
    """
    
    # List objects in the S3 bucket
    paginator = s3.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=s3_bucket_name, Prefix=s3_prefix)

    for page in response_iterator:
        if "Contents" not in page:
            print(f"No files found in bucket {s3_bucket_name} with prefix '{s3_prefix}'")
            return
        
        for obj in page["Contents"]:
            s3_key = obj["Key"]
            file_name = os.path.relpath(s3_key, s3_prefix) if s3_prefix else s3_key
            local_file_path = os.path.join(local_directory, file_name)
            print("S3 bucket sync.. local_file_path:",local_file_path)

            # Create directories if needed
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            # Download the file
            print(f"Downloading {s3_key} to {local_file_path}")
            s3.download_file(s3_bucket_name, s3_key, local_file_path)