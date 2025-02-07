"""
json_data_cleaning.py

This script processes raw scraped data from `raw_scrapped_data.json` by converting date keys 
from concatenated month-year format (e.g., "Oct2012", "June 2020") to a readable format ("Oct 2012", "Jun 2020"). 
This step ensures that all records have the correct format for further processing in `transform_json.py`, 
where only data with properly formatted month-year keys is included.

Functions:
- Converts month-year keys in the data to a readable format.

Usage:
Place the raw data JSON file (`raw_scrapped_data.json`) in the same directory as this script 
and run it to generate a cleaned JSON data.

Dependencies:
- logging_config
"""

import json, logging
import re
from collections import OrderedDict

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)


def clean_data(data):
    logging.info("Converting month-year format")
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    for record in data:

        # For preserving the order of the months and years
        ordered_record = OrderedDict()
        ordered_record["Indicators"] = record["Indicators"]

        for key in record:
            if key != "Indicators":
                if record[key]:

                    # Splitting month and year
                    cleaned_key = re.sub(r"([A-Za-z]+)(\d{4})", r"\1 \2", key)
                    month_name, year = cleaned_key.split()

                    # Extracting first 3 alphabets of month name
                    month_idx = months.index(month_name[:3])

                    # Correct format for month and year
                    new_key = f"{months[month_idx]} {year}"
                    ordered_record[new_key] = record[key]
                else:
                    ordered_record[key] = record[key]

        record.clear()
        record.update(ordered_record)

    return json.dumps(data, indent=4)
