from datetime import datetime, timedelta
import json, logging
import numpy as np
import pandas as pd

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def convert_to_json(last_path_segment, publication_date, dl_link, extraction_date):
    """
    Converts data from an Excel file into a structured JSON format.

    Args:
        last_path_segment (str): Path to the Excel file.
        publication_date (str): The publication date in 'YYYY-MM-DD' format.
        dl_link (str): The download link for the source file.

    Returns:
        list: A list of dictionaries representing the structured JSON data.

    Raises:
        ValueError: If the data extraction fails or the file cannot be processed.
    """
    logging.info(f"Processing file: {last_path_segment}")

    try:
        # Load the Excel file
        df = pd.read_excel(rf"{last_path_segment}", skiprows=9, header=[0, 1])
        df.set_index(df.columns[0], inplace=True)
        logging.info("Excel file loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading Excel file: {e}")
        raise ValueError("Failed to load the Excel file")

    # Define the specific combinations to extract
    extraction_combos = [
        ("Energy Sector", "Power", "RLNG"),
        ("Energy Sector", "Power", "Domestic"),
        ("Energy Sector", "CGD", "RLNG"),
        ("Energy Sector", "CGD", "Domestic"),
        ("Energy Sector", "Refinery", "RLNG"),
        ("Energy Sector", "Refinery", "Domestic"),
        ("Energy Sector", "I/C for P/L System", "RLNG"),
        ("Energy Sector", "I/C for P/L System", "Domestic"),
        ("Energy Sector", "Agriculture(Tea Plantation)", "RLNG"),
        ("Energy Sector", "Agriculture(Tea Plantation)", "Domestic"),
        ("Energy Sector", "Industrial", "RLNG"),
        ("Energy Sector", "Industrial", "Domestic"),
        ("Energy Sector", "Manufacturing", "RLNG"),
        ("Energy Sector", "Manufacturing", "Domestic"),
        ("Energy Sector", "Other/Misc", "RLNG"),
        ("Energy Sector", "Other/Misc", "Domestic"),
        ("Non Energy Sectors", "Fertilizer", "RLNG"),
        ("Non Energy Sectors", "Fertilizer", "Domestic"),
        ("Non Energy Sectors", "Petrochemical", "RLNG"),
        ("Non Energy Sectors", "Petrochemical", "Domestic"),
        ("Non Energy Sectors", "LPG Shrinkage", "RLNG"),
        ("Non Energy Sectors", "LPG Shrinkage", "Domestic"),
        ("Non Energy Sectors", "Sponge Iron/Steel", "RLNG"),
        ("Non Energy Sectors", "Sponge Iron/Steel", "Domestic"),
    ]

    energy_values = []

    # Loop through all unique dates in the first row of the MultiIndex
    for date in df.columns.levels[0]:
        if isinstance(date, datetime):
            for sector, subsector, fuel_type in extraction_combos:
                try:
                    value = df.loc[subsector, (date, fuel_type)]
                    energy_values.append(
                        {
                            "date": date,
                            "sector": sector,
                            "subsector": subsector,
                            "fuel_type": fuel_type,
                            "value": value,
                        }
                    )
                except KeyError as e:
                    logging.warning(
                        f"Missing data for {sector}, {subsector}, {fuel_type} on {date}: {e}"
                    )

    # Grouping the results by date
    grouped_by_date = {}

    for value in energy_values:
        date = value["date"]
        if date not in grouped_by_date:
            grouped_by_date[date] = []

        grouped_by_date[date].append(
            {
                "type": "measured",
                "facets": [value["sector"], value["subsector"], value["fuel_type"]],
                "value": None if np.isnan(value["value"]) else round(value["value"]),
                "unit": "Mt",
            }
        )

    output = []

    for date, values_list in grouped_by_date.items():
        next_month_start = (date + timedelta(days=32)).replace(day=1)
        date_interval = (
            f"{date.strftime('%Y-%m-%d')}/{next_month_start.strftime('%Y-%m-%d')}"
        )

        ## <Changed the ordering of the 'sourceUri' key> <Aadhya> <17/01/2025> START ##
        output.append(
            {
                "dateInterval": date_interval,
                "country": "IND",
                "sourceName": "ppac.gov.in/natural-gas",
                "sourceUri": dl_link,
                "publicationDate": publication_date,
                "extractionDate": extraction_date,
                "values": values_list,
            }
        )

        ## <Changed the ordering of the 'sourceUri' key> <Aadhya> <17/01/2025> END ##

    # Save the output as JSON
    try:
        with open(f"tmp/natural_gas/{last_path_segment}.json", "w") as f:
            json.dump(output, f, indent=4)
        logging.info(f"JSON file saved successfully as '{last_path_segment}.json'")
    except IOError as e:
        logging.error(f"Error saving JSON file: {e}")
        raise ValueError("Failed to save the JSON file")

    return output
