import pandas as pd
import json, boto3, os, logging
from datetime import datetime, timedelta
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)


# Define column mapping for known facets
column_mapping = {
    "Entradas al Sistema ": "Inputs",
    "Plantas de Regasificación": "Regasification Plants",
    "BARCELONA": "BARCELONA",
    "CARTAGENA": "CARTAGENA",
    "HUELVA": "HUELVA",
    "BBG": "BBG",
    "SAGUNTO": "SAGUNTO",
    "REGANOSA": "REGANOSA",
    "MUSEL": "MUSEL",
    "Conexiones Internacionales": "Cross border pipes",
    "VIP PIRINEOS": "VIP PIRINEOS",
    "VIP IBÉRICO": "VIP IBÉRICO",
    "TARIFA": "TARIFA",
    "ALMERÍA": "ALMERIA",
    "Total\nProducción Nacional ": "Production",
    "Salidas": "Output",
    "Total \nRed de Transporte": "Network",
    "Cisternas": "Storage",
    "Existencias Útiles en Almacenamiento único": "Single Storage",
}


# Function to format date to 'YYYY-MM-DD'
def format_date(date):
    try:
        if isinstance(date, str):
            if date.strip().lower() == "total" or not date.strip():
                return None
            return datetime.strptime(date.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
        elif isinstance(date, datetime):
            return date.strftime("%Y-%m-%d")
    except ValueError:
        return None


# Function to clean up the facets
def clean_facets(facets):
    cleaned_facets = [
        facet.strip().replace("\n", " ")
        for facet in facets
        if facet and "Unnamed:" not in facet
    ]
    return cleaned_facets


# Function to extract metadata
def extract_metadata(filename, date_folder):
    metadata_file = os.path.join(date_folder, "excel_files_with_dates.xlsx")
    metadata_df = pd.read_excel(metadata_file)

    matched_row = metadata_df[metadata_df["Filename"] == filename]

    if not matched_row.empty:
        source_uri = matched_row.iloc[0]["Excel URL"]
        publication_date = matched_row.iloc[0]["Publication Date"]
    else:
        source_uri = ""
        publication_date = ""

    return source_uri, publication_date


# Function to parse Excel and convert to Julia
def parse_excel_to_julia(input_file, sheet1_name, sheet2_name, date_folder):
    try:
        # Generate output file name based on input file name
        output_julia_file = os.path.splitext(input_file)[0] + ".jl"

        # Load and process sheet 1
        df_1 = pd.read_excel(
            input_file, sheet_name=sheet1_name, header=[0, 1, 2], skiprows=5
        )
        if df_1.empty:
            logging.error(f"Error: The sheet {sheet1_name} is empty.")
            return

        df_1.dropna(how="all", inplace=True)
        df_1.dropna(axis=1, how="all", inplace=True)

        # Remove "Unnamed" columns
        df_1.columns = [
            tuple(col if "Unnamed" not in col else "" for col in cols)
            for cols in df_1.columns
        ]
        df_1.columns = [
            col for col in df_1.columns if any(col)  # Keep columns with non-empty names
        ]

        # Validate and clean date column for sheet 1
        potential_date_column = df_1.iloc[:, 0]
        valid_date_mask = pd.to_datetime(potential_date_column, errors="coerce").notna()
        df_1 = df_1[valid_date_mask]
        date_column_1 = pd.to_datetime(df_1.iloc[:, 0], errors="coerce")
        df_1 = df_1.iloc[:, 1:]

        # Ensure required columns are included
        valid_columns = [
            col
            for col in df_1.columns
            if col[0] in column_mapping and col[1] in column_mapping
        ]
        if not valid_columns:
            logging.error("No valid columns matched the column_mapping in sheet 1.")
            return

        df_1 = df_1[valid_columns]

        # Load and process sheet 2
        df_2 = pd.read_excel(input_file, sheet_name=sheet2_name, skiprows=5)
        if df_2.empty:
            logging.error(f"Error: The sheet {sheet2_name} is empty.")
            return

        df_2.dropna(how="all", inplace=True)
        df_2.dropna(axis=1, how="all", inplace=True)

        # Remove "Unnamed" from columns in sheet 2
        df_2.columns = [col if "Unnamed" not in col else "" for col in df_2.columns]

        # Validate and clean date column for sheet 2
        potential_date_column_2 = df_2.iloc[:, 0]
        valid_date_mask_2 = pd.to_datetime(
            potential_date_column_2, errors="coerce"
        ).notna()
        df_2 = df_2[valid_date_mask_2]
        date_column_2 = pd.to_datetime(df_2.iloc[:, 0], errors="coerce")
        df_2.set_index(date_column_2, inplace=True)

        # Extract column from sheet 2
        if "Existencias Útiles en Almacenamiento único" not in df_2.columns:
            logging.error(
                "Error: 'Existencias Útiles en Almacenamiento único' column not found in sheet 2."
            )
            return

        existencias_column = df_2["Existencias Útiles en Almacenamiento único"]

        # Align second sheet data with the first sheet
        df_1.index = date_column_1
        combined_df = df_1.copy()
        combined_df["Existencias Útiles en Almacenamiento único"] = (
            existencias_column.reindex(combined_df.index)
        )

        # Extract metadata
        source_uri, publication_date = extract_metadata(
            input_file.split("/")[-1], date_folder
        )

        # Write date-wise output to Julia file
        with open(output_julia_file, "w", encoding="utf-8") as f:
            for date, row in combined_df.iterrows():
                output = {
                    "dateInterval": f"{date.strftime('%Y-%m-%d')}/{(date + timedelta(days=1)).strftime('%Y-%m-%d')}",
                    "country": "ESP",
                    "sourceName": "enagas.eses/plan-operacion-sistema",
                    "sourceUri": source_uri,
                    "publicationDate": datetime.strptime(
                        publication_date, "%d/%m/%Y"
                    ).strftime("%Y-%m-%d"),
                    "extractionDate": datetime.now().strftime("%Y-%m-%d"),
                    "values": [],
                }

                for col, value in row.items():
                    if pd.isna(value):
                        continue

                    if col == "Existencias Útiles en Almacenamiento único":
                        facets = ["Single Storage"]
                    else:
                        # Exclude empty column names and replace missing levels
                        facets = [
                            column_mapping.get(level, "Unknown")
                            for level in col
                            if level
                        ]

                    value_entry = {
                        "type": "measured",
                        "facets": facets,
                        "value": round(value, 1),
                        "unit": (
                            "GWh"
                            if col == "Existencias Útiles en Almacenamiento único"
                            else "GWh/day"
                        ),
                    }
                    output["values"].append(value_entry)

                # Write each JSON object as a single line
                f.write(json.dumps(output, ensure_ascii=False) + "\n")

        logging.info(f"Julia file created successfully: {output_julia_file}")

    except Exception as e:
        logging.error(f"Error: {str(e)}")


# Function to upload data to S3_bucket


def upload_files_to_s3(excel_file_path, julia_file_path):
    """
    Uploads an Excel file and a Julia file to an S3 bucket with dynamic S3 keys
    based on the content of the Julia file.

    :param excel_file_path: Local path to the Excel file.
    :param julia_file_path: Local path to the Julia (.jl) file.
    """
    try:
        # Step 1: Parse the Julia file to extract sourceName and extractionDate
        with open(julia_file_path, "r", encoding="utf-8") as f:
            julia_lines = f.readlines()

        # Initialize variables for sourceName and extractionDate
        source_name = None
        extraction_date = None

        # Parse each JSON object in the .jl file
        for line in julia_lines:
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            try:
                julia_json = json.loads(line)

                # Extract sourceName and extractionDate (assumes they're the same for all lines)
                if not source_name:
                    source_name = julia_json.get("sourceName")
                if not extraction_date:
                    extraction_date = julia_json.get("extractionDate")

            except json.JSONDecodeError as e:
                logging.error(f"Skipping invalid JSON line: {line} - {e}")

        if not source_name or not extraction_date:
            raise ValueError(
                "Missing required keys 'sourceName' or 'extractionDate' in Julia file."
            )

        # Step 2: Construct the dynamic S3 keys
        excel_file_name = os.path.basename(excel_file_path)  # Extract file name
        julia_file_name = os.path.basename(julia_file_path)  # Extract file name

        s3_excel_key = f"{source_name}/{extraction_date}/raw/{excel_file_name}"
        s3_julia_key = f"{source_name}/{extraction_date}/bronze/{julia_file_name}"

        # Step 3: Upload the files to S3
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "kpler-data-scraping"

        # Upload Excel file
        s3_client.upload_file(excel_file_path, bucket_name, s3_excel_key)
        logging.info(
            f"Successfully uploaded Excel file to s3://{bucket_name}/{s3_excel_key}"
        )

        # Upload Julia file
        s3_client.upload_file(julia_file_path, bucket_name, s3_julia_key)
        logging.info(
            f"Successfully uploaded Julia file to s3://{bucket_name}/{s3_julia_key}"
        )

    except FileNotFoundError as e:
        logging.error(f"Error: File not found - {e}")
    except NoCredentialsError:
        logging.error("Error: AWS credentials not available.")
    except PartialCredentialsError:
        logging.error("Error: Incomplete AWS credentials configuration.")
    except ValueError as e:
        logging.error(f"Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
