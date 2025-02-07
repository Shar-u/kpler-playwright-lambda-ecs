from datetime import datetime
import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def get_publication_date(response):
    """
    Extracts and formats the publication date from an HTTP response's headers.

    Args:
        response: The HTTP response object containing headers.

    Returns:
        str: The formatted publication date as 'YYYY-MM-DD'.

    Raises:
        ValueError: If the 'Last-Modified' header is missing or cannot be parsed.
    """
    logging.info("Extracting publication date from response headers.")

    # Attempt to retrieve the 'Last-Modified' header
    last_modified = response.headers.get("Last-Modified")
    if not last_modified:
        logging.error("'Last-Modified' header is missing.")
        raise ValueError("'Last-Modified' header not found in the response headers.")

    # Parse and format the date
    try:
        date_object = datetime.strptime(last_modified, "%a, %d %b %Y %H:%M:%S GMT")
        formatted_date = date_object.strftime("%Y-%m-%d")
        logging.info(f"Publication date parsed successfully: {formatted_date}")
    except ValueError as e:
        logging.error(f"Error parsing the 'Last-Modified' date: {e}")
        raise

    return formatted_date
