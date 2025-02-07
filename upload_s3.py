import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s"
)

import boto3
import os

s3_client = boto3.client('s3', region_name='us-east-1')

### <replaced manifesto_upload with upload>  Vismaya  17/01/2025 START ####  
def upload(file_path,bucket_name,s3_path):
    """
    Uploads a local file to an S3 bucket.
    :param file_path: Local file path to upload.
    :param s3_path: The file path to save in S3.
    :param bucket_name: The S3 bucket name.
    """
    try:
        s3_client.upload_file(file_path, bucket_name, s3_path)
        logging.info(f"File uploaded to {s3_path} in S3.")
    except Exception as e:
        logging.error(f"Failed to upload file to S3: {str(e)}")
### <replaced manifesto_upload with upload>  Vismaya  17/01/2025 END ####  

def upload_electric_power_scrapped_ouput_to_bucket(file_path, bucket_name, object_key):
    """Uploads files to S3 bucket"""
    try:
        if not os.path.isfile(file_path):
            logging.error(f"Error: The file '{file_path}' does not exist.")
            raise ValueError(f'File not found: {file_path}')
        s3_client.upload_file(file_path, bucket_name, object_key)
        logging.info(f"File uploaded successfully to {bucket_name}/{object_key}")
    except Exception as e:
        logging.error(f"Unexpected error during file upload: {e}")


