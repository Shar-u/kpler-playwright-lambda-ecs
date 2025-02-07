from natural_gas_get_publication_date import get_publication_date
from natural_gas_get_file import get_file
from natural_gas_convert_output_from_json_to_jil_format import (
    convert_output_from_json_to_jil_format,
)
from natural_gas_convert_to_json import convert_to_json
from natural_gas_upload_to_s3 import upload_to_s3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
import os, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)

natural_gas_url = os.environ.get("NATURAL_GAS_URL")
bucket_name = os.environ.get("BUCKET_NAME")
natural_gas_source = os.environ.get("NATURAL_GAS_SOURCE")

extraction_date = datetime.today().strftime("%Y-%m-%d")


def scrape_natural_gas_data():
    """
    Main function to orchestrate the data extraction, transformation, and loading process.

    Args:
        url (str): The URL to scrape data from.
        bucket_name (str): The name of the S3 bucket for storing data.
        source (str): The source identifier for organizing data in the bucket.
        extraction_date (str): The date of data extraction in 'YYYY-MM-DD' format.

    Returns:
        None

    Raises:
        Exception: If any step in the process fails.
    """
    logging.info("Starting the data pipeline execution.")
    logging.info(natural_gas_url)

    try:
        os.makedirs("tmp/natural_gas",exist_ok=True)
        response, dl_link, last_path_segment = get_file(natural_gas_url)
        publication_date = get_publication_date(response)
        output_json = convert_to_json(
            last_path_segment, publication_date, dl_link, extraction_date
        )
        convert_output_from_json_to_jil_format(last_path_segment, output_json)

        raw_file = last_path_segment
        bronze_file = f"{raw_file}.jl"
        upload_to_s3(raw_file, bucket_name, natural_gas_source, extraction_date, "raw")
        upload_to_s3(
            bronze_file, bucket_name, natural_gas_source, extraction_date, "bronze"
        )
        logging.info("Data pipeline executed successfully.")
    except Exception as e:
        logging.error(f"Error in data pipeline: {e}")
        raise


# if __name__ == '__main__':
#     url = os.environ.get('URL')
#     bucket_name = os.environ.get('BUCKET_NAME')
#     source = os.environ.get('SOURCE')
#     extraction_date = datetime.today().strftime('%Y-%m-%d')
#     main(url, bucket_name, source, extraction_date)
