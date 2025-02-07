"""
convert_output_from_json_to_jil_format.py

This script converts JSON-formatted data from `json_formatted_data.json` into Julia's `.jl` format.
The output data contains a Julia-compatible data structure 
for further processing.

Functions:
- convert_output_from_json_to_jil_format: Formats the json content into julia compatible data.

Usage:
Ensure the transformed JSON file (`json_formatted_data.json`) is in the same directory, then run this 
script to generate the julia compatible data.

Dependencies:
- logging_config
"""

import json, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def convert_output_from_json_to_jil_format(input_file):
    try:
        logging.info(f"Converting JSON data into Julia compatible data")
        julia_data = ""
        for obj in input_file:
            json_line = json.dumps(obj)
            julia_data += f"{json_line}\n"

    except Exception as e:
        logging.error(f"Failed to store data for Julia: {e}")

    return julia_data
