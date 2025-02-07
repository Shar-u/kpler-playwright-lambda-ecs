"""
Uploads a file to an S3 bucket with a specified path structure.

Args:
- bucket_name (str): Target S3 bucket name.
- source (str): Source directory for categorization.
- extraction_date (str): Date to include in the S3 path.
- category (str): Subfolder/category for the file in the S3 bucket.
- last_path_segment (str): Name of the file to upload.
"""

import boto3, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def upload_to_s3(bucket_name, source, extraction_date, category, last_path_segment):

    logging.info("Initializing S3 client.")

    s3_client = boto3.client("s3")
    file_path = f"/tmp/crude_oil_temp/{last_path_segment}"
    object_key = f"{source}/{extraction_date}/{category}/{last_path_segment}"

    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        logging.info(f"File uploaded successfully to {bucket_name}/{object_key}")
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        raise
