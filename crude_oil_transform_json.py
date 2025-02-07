"""
transform_json.py

This script transforms cleaned data from `cleaned_scrapped_data.json` into a structured JSON format

Functions:
- transform_data: Converts the cleaned data into a JSON format with structured fields like 
  dateInterval, country, sourceName, and measured values.

Usage:
Place the cleaned JSON file (`cleaned_scrapped_data.json`) in the same directory and run this script 
to generate the transformed JSON data.

Dependencies:
- logging_config
"""

import os
import json, logging
import calendar
from datetime import datetime, timedelta

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)

source_uri = os.environ.get("CRUDE_OIL_URL")
source_name = os.environ.get("CRUDE_OIL_SOURCE")

def transform_data(input_json):
    logging.info("Transforming data")

    country = "CHN"

    # Current date
    extraction_date = datetime.today().strftime("%Y-%m-%d")

    transformed_data = []
    current_period_data = None
    accumulated_data = None

    for row in input_json:

        # Skipping Growth Rate and Accumulated Growth Rate data
        if (
            "Growth Rate" in row["Indicators"]
            or "Accumulated Growth Rate" in row["Indicators"]
        ):
            continue

        if "Current Period" in row["Indicators"]:
            current_period_data = row
        elif "Accumulated" in row["Indicators"]:
            accumulated_data = row

    for month in current_period_data:
        if month == "Indicators":
            continue

        current_period_value = current_period_data.get(month, "")
        accumulated_value = accumulated_data.get(month, "") if accumulated_data else ""

        # Setting up dateInterval
        try:
            month_obj = datetime.strptime(month, "%b %Y")
            start_date = month_obj.replace(day=1).strftime("%Y-%m-%d")
            end_date = (
                (month_obj.replace(day=1) + timedelta(days=32))
                .replace(day=1)
                .strftime("%Y-%m-%d")
            )
            date_interval = f"{start_date}/{end_date}"

            _, last_day = calendar.monthrange(month_obj.year, month_obj.month)
            publication_date = month_obj.replace(day=last_day).strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(f"Invalid month format: {month}")
            continue

        # publication_date = '2024-11-30'

        values = []

        # If current_period_value is empty, append null
        if current_period_value == "":
            values.append(
                {
                    "type": "measured",
                    "facets": ["Output of Crude oil, Current Period"],
                    "value": None,
                    "unit": "10kt",
                }
            )

        else:
            values.append(
                {
                    "type": "measured",
                    "facets": ["Output of Crude oil, Current Period"],
                    "value": float(current_period_value),
                    "unit": "10kt",
                }
            )

        # If accumulated_value is empty, append null
        if accumulated_value == "":
            values.append(
                {
                    "type": "measured",
                    "facets": ["Output of Crude oil, Accumulated"],
                    "value": None,
                    "unit": "10kt",
                }
            )

        else:
            values.append(
                {
                    "type": "measured",
                    "facets": ["Output of Crude oil, Accumulated"],
                    "value": float(accumulated_value),
                    "unit": "10kt",
                }
            )

        transformed_data.append(
            {
                "dateInterval": date_interval,
                "country": country,
                "sourceName": source_name,
                "sourceUri": source_uri,
                "publicationDate": publication_date,
                "extractionDate": extraction_date,
                "values": values,
            }
        )

    return json.dumps(transformed_data, indent=4)
