import os
import json, logging
from crude_oil_scrapper import scrape
from crude_oil_json_data_cleaning import clean_data
from crude_oil_transform_json import transform_data
from crude_oil_convert_output_from_json_to_jil_format import (
    convert_output_from_json_to_jil_format,
)
from crude_oil_read_write import save_data_to_file
from crude_oil_upload_to_s3 import upload_to_s3

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)

url = os.environ.get("CRUDE_OIL_URL")
bucket_name = os.environ.get("BUCKET_NAME")
source = os.environ.get("CRUDE_OIL_SOURCE")

def scrape_crude_oil_data():
    os.makedirs("/tmp/crude_oil_temp",exist_ok=True)

    # Running scrapper.py for extracting data and html script
    try:
        logging.info("Starting the data scraping process.")
        logging.info(url)
        data_and_html = scrape(
            url, 3, 5
        )
        logging.info("Website scrapping and HTML rendering completed successfully")

        raw_scrapped_data = data_and_html[0]
        html_script = data_and_html[1]

        save_data_to_file(html_script, "/tmp/crude_oil_temp/crude_oil.html")
        logging.info("Data successfully saved to crude_oil.html")

    except Exception as e:
        logging.error(f"Failed during scraping or saving: {e}")
        return

    # Running json_data_cleaning.py for cleaning the raw extracted data
    try:
        logging.info("Starting JSON data cleaning.")

        cleaned_data = clean_data(json.loads(raw_scrapped_data))
        logging.info("JSON data cleaning completed successfully.")

    except Exception as e:
        logging.error(f"Failed during data cleaning: {e}")
        return

    # Running transform_json.py for transforming into the required json format
    try:
        logging.info("Starting JSON data transformation.")

        transformed_data = transform_data(json.loads(cleaned_data))
        logging.info("JSON data transformation completed successfully.")

    except Exception as e:
        logging.error(f"Failed during data transformation: {e}")
        return

    # Running convert_output_from_json_to_jil_format.py for converting the json file into julia file
    try:
        logging.info("Starting Julia file generation.")

        transformed_json_data = json.loads(transformed_data)
        jl_data = convert_output_from_json_to_jil_format(transformed_json_data)
        logging.info("Julia file generation completed successfully.")

        save_data_to_file(jl_data, "/tmp/crude_oil_temp/crude_oil.jl")
        logging.info("Data successfully saved to crude_oil.jl")

    except Exception as e:
        logging.error(f"Failed during Julia file generation or saving: {e}")
        return

    # Running upload_to_s3.py for julia file
    try:
        logging.info("Starting upload of crude_oil.jl to S3 bucket.")

        # Extract the extraction_date from the transformed JSON
        extraction_date = transformed_json_data[0]["extractionDate"]

        upload_to_s3(bucket_name, source, extraction_date, "bronze", "crude_oil.jl")
        logging.info("Upload of crude_oil.jl completed successfully.")

    except Exception as e:
        logging.error(f"Failed during upload of crude_oil.jl: {e}")
        return

    # Running upload_to_s3.py for html file
    try:
        logging.info("Starting upload of crude_oil.html to S3 bucket.")

        upload_to_s3(bucket_name, source, extraction_date, "raw", "crude_oil.html")
        logging.info("Upload of crude_oil.html completed successfully.")

    except Exception as e:
        logging.error(f"Failed during upload of crude_oil.html: {e}")
        return

    logging.info("All processes completed successfully.")
