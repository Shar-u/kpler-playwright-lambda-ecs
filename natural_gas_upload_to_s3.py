import boto3, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def upload_to_s3(last_path_segment, bucket_name, source, extraction_date, layer):
    """
    Uploads a file to an S3 bucket at a specified path.

    Args:
        last_path_segment (str): The base filename for the file to upload.
        bucket_name (str): The name of the S3 bucket.
        source (str): The data source name for organizing the file in the bucket.
        extraction_date (str): The extraction date in 'YYYY-MM-DD' format for organizing the file.

    Returns:
        None: The file is uploaded directly to the S3 bucket.

    Raises:
        Exception: If the file upload fails.
    """
    logging.info("Initializing S3 client.")

    s3_client = boto3.client("s3")
    file_path = f"tmp/natural_gas/{last_path_segment}"
    object_key = f"{source}/{extraction_date}/{layer}/{last_path_segment}"

    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        logging.info(f"File uploaded successfully to {bucket_name}/{object_key}")
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        raise
