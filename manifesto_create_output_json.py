import json
import os
from datetime import datetime
import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def extract_data_from_json(json_file):
    output_header_data = {}

        
    # Open the JSON file and load its content
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Extract required fields (this depends on the structure of your input JSON files)

    dateInterval = data.get("dateInterval",'N/A')
    country = data.get("country",'N/A')
    sourceName = data.get("sourceName",'N/A')
    sourceUri = data.get("sourceUri",'N/A')
    publicationDate = data.get("publicationDate",'N/A')
    extractionDate = data.get("extractionDate",'N/A')

    
    json_directory = '/tmp/manifesto_temp' #changes sharul -----changed

    output_data_list = []
    for filename in os.listdir(json_directory):
        
        if "_scraped_data.json" in filename:
            # logging(f'fetching scrapped data from -->{filename}')
            json_file_path = os.path.join(json_directory, filename)
            # logging(f'fetching data from -->{json_file_path}')
            values_list = fetch_data_from_json(json_file_path)
            if len(values_list) > 0 :
                for values in values_list:
                    # Construct the output in the required format
                    output_header_data ={
                        "dateInterval": dateInterval,
                        "country": country,
                        "sourceName": sourceName,
                        "sourceUri": sourceUri,
                        "publicationDate": publicationDate,
                        "extractionDate": extractionDate,
                        "value":values
                    }
                    output_data_list.append(output_header_data)

    return output_data_list



def fetch_data_from_json(file_path) ->list:

    data = []
    values_list= []
    try:
        # Open the file
        with open(file_path, 'r') as file:
            # Check if the file is empty
            if file.read().strip():  # .strip() removes any whitespace/newline characters
                file.seek(0)  # Reset the file pointer to the beginning
                data = json.load(file)  # Load the JSON data
                # logging("Data loaded successfully:", data)
                extracted_data ={}

                
                entry = data[0]
                # Extract other values based on keys
                
                common_values = []
                        
                if 'MANIFIESTO' in entry:
                    common_values.append({
                    "type": "descriptive",
                    "facets": ["MANIFIESTO"],
                    "value": entry["MANIFIESTO"]
                    })
                if "MATRICULA DE LA NAVE" in entry:
                    common_values.append({
                    "type": "descriptive",
                    "facets": ["MATRICULA DE LA NAVE"],
                    "value": entry["MATRICULA DE LA NAVE"]
                    })
                if "EMPRESA DE TRANSPORTE" in entry:
                    common_values.append({
                    "type": "descriptive",
                    "facets": ["EMPRESA DE TRANSPORTE"],
                    "value": entry["EMPRESA DE TRANSPORTE"]
                    })
                if "NRO DE DETALLES" in entry:
                    common_values.append({
                    "type": "descriptive",
                    "facets": ["NRO DE DETALLES"],
                    "value": entry["NRO DE DETALLES"],
                    "unit": "count"
                    })
                if "NRO BULTOS" in  entry:
                    common_values.append({
                    "type": "measured",
                    "facets": ["NRO BULTOS"],
                    "value": entry["NRO BULTOS"],
                    "unit": "count"
                    })
                if "NACIONALIDAD" in  entry:
                    common_values.append({
                    "type": "descriptive",
                    "facets": ["NACIONALIDAD"],
                    "value": entry["NACIONALIDAD"]
                    })


                # logging(f'extracted_data -----> {extracted_data}')
                if len(data[1]) > 0:

                    for item in data[1]:
                        values=[]
                        values.extend(common_values)
                        puerto = item['Puerto']
                        pesoManifiesto = item['Peso Manifiesto']
                        bultosManifiesto = item["Bultos Manifiesto"]
                        pesoRecibido = item["Peso Recibido"]
                        bultosRecibidos = item["Bultos Recibidos"]
                        embarcador = item["Embarcador"]
                        values.append({
                        "type": "descriptive",
                        "facets": ["Puerto"],
                        "value": puerto
                        })
                        values.append({
                            "type": "measured",
                            "facets": ["Peso Manifiesto"],
                            "value": float(pesoManifiesto.replace(",", "")),  # Convert weight to float for numeric consistency
                            "unit": "count"
                        })
                        values.append({
                            "type": "measured",
                            "facets": ["Bultos Manifiesto"],
                            "value": float(bultosManifiesto.replace(",", "")),  # Convert weight to float for numeric consistency
                            "unit": "count"
                        })
                        values.append({
                            "type": "measured",
                            "facets": ["Peso Recibido"],
                            "value": float(pesoRecibido.replace(",", "")),  # Convert weight to float for numeric consistency
                            "unit": "count"
                        })
                        values.append({
                            "type": "measured",
                            "facets": ["Bultos Recibidos"],
                            "value": float(bultosRecibidos.replace(",", "")),  # Convert weight to float for numeric consistency
                            "unit": "count"
                        })
                        values.append({
                            "type": "descriptive",
                            "facets": ["Embarcador"],
                            "value": embarcador
                        })

                        values_list.append(values)

    
            else:
                logging("The file is empty.")
        # logging(f'values -----> {values}')
        return values_list
    except json.JSONDecodeError:
        logging("Error decoding JSON. The file may be empty or have invalid JSON.")
    except FileNotFoundError:
        logging(f"The file {file_path} does not exist.")


def create_output_json_file(lastPathSegment) -> str:
    # Example: Specify the directory where your JSON files are stored
    # output_data = []
    header_json_directory = '/tmp/manifesto_temp' #changes sharul -----changed
    for filename in os.listdir(header_json_directory):
        
        if "header_data.json" in filename:
            # logging(f'fetching data from -->{filename}')
            json_file_path = os.path.join(header_json_directory, filename)
            output_data = extract_data_from_json(json_file_path)
            # output_data.append(output_header_data)
    
    # changed path to tmp/manifesto_temp
    if len(output_data) > 0:
        with open(f'/tmp/manifesto_temp/{lastPathSegment}.json', 'w') as output_file:
            json.dump(output_data, output_file, indent=4)
        #changes sharul
        return f'/tmp/manifesto_temp/{lastPathSegment}.json'
    else:    
        logging.info("No data found in the output JSON files.")
        return None