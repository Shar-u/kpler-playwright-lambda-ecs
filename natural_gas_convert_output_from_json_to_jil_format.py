import json, logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def convert_output_from_json_to_jil_format(last_path_segment, output_json):
    """
    Converts a list of dictionaries in a JSON object into JSON Lines (.jl) format and saves it to a file.

    Args:
        last_path_segment (str): The base filename for saving the output.
        output_json (list): The JSON data (list of dicts) to be converted and saved.

    Returns:
        None: The result is saved as a .jl file with the same base name as provided.

    Raises:
        IOError: If the file cannot be written successfully.
    """

    logging.info("Converting JSON data to JSON Lines (.jl) format.")

    try:
        with open(f"tmp/natural_gas/{last_path_segment}.jl", "w") as f:
            for record in output_json:
                f.write(json.dumps(record) + "\n")
        logging.info(
            f"JSON Lines (.jl) file saved successfully as '{last_path_segment}.jl'"
        )
    except IOError as e:
        logging.error(f"Error saving JSON Lines (.jl) file: {e}")
        raise
