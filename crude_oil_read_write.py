"""
read_write.py

The script provides utility functions for reading JSON data from a file 
and saving content to a file. It also includes logging for better traceability 
of operations.

Functions:
- read_json_from_file(file_path):
    Reads JSON data from a specified file and returns it as a Python dictionary.

- save_data_to_file(content, file_path):
    Saves the given content to a specified file.

Dependencies:
- json: Built-in module for handling JSON data.
- logging_config: Custom logging setup module.

Usage:
1. Call `read_json_from_file(file_path)` with the path of the JSON file 
   to read and return its contents.
2. Use `save_data_to_file(content, file_path)` to save a string or serialized data 
   to a specified file path.
"""

import json, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)


# Function for reading input json file data
def read_json_from_file(file_path):
    try:
        logging.info(f"Reading data from {file_path}")
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Failed to read JSON file: {e}")
        raise


# Function to save data
def save_data_to_file(content, file_path):
    try:
        logging.info(f"Saving data to {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        raise
