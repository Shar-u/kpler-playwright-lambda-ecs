
import json
import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)



def generate_jl_file(file_path):
    """
    Generates a Julia (.jl) file from a JSON file.
    This function reads a JSON file from the specified file path, converts its content to a JSON string,
    and writes the string to a new file named "consultarManifiesto.jl". If the input file is empty,
    it loggings a message indicating that the file is empty.
    Args:
        file_path (str): The path to the JSON file to be read.
    Raises:
        json.JSONDecodeError: If the file contains invalid JSON data.
        FileNotFoundError: If the specified file does not exist.
        IOError: If there is an error reading from or writing to the file.
    """
    try:
        with open(file_path, 'r') as file:
            # Check if the file is empty
            if file.read().strip():  # .strip() removes any whitespace/newline characters
                file.seek(0)  # Reset the file pointer to the beginning
                data = json.load(file)  # Load the JSON data
                # logging("Data loaded successfully:", data)
                
                # chnaged path to /tmp/manifesto_temp
                with open("/tmp/manifesto_temp/consultarManifiesto.jl", "w") as f:
                    for record in data:
                        julia_data = f"{json.dumps(record)}\n"
                        f.write(julia_data)
            else:
                logging("File is empty")
    except FileNotFoundError:
        logging(f"Error: The file {file_path} does not exist.")
    except json.JSONDecodeError:
        logging(f"Error: The file {file_path} contains invalid JSON.")
    except IOError as e:
        logging(f"Error: An I/O error occurred: {e}")