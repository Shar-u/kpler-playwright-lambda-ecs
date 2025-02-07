import requests, logging
from bs4 import BeautifulSoup

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def get_file(url):
    """
    Downloads a file from a given webpage containing a link.

    Args:
        url (str): The URL of the webpage containing the download link.

    Returns:
        bytes: The content of the downloaded file.

    Raises:
        ValueError: If the download link is not found or the file fails to download.
    """
    logging.info(f"Fetching the webpage: {url}")

    # Send a GET request to the provided URL
    try:
        res = requests.get(url)
        res.raise_for_status()  # Raise an error for bad responses
    except requests.RequestException as e:
        logging.error(f"Failed to fetch the webpage: {e}")
        raise

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(res.text, "html.parser")

    # Find the link by the specified class attribute
    link = soup.find("a", class_="fz18 fw400 my-4 mb-auto")
    if not link or "href" not in link.attrs:
        logging.error("Download link not found on the webpage.")
        raise ValueError("Download link not found")

    # Extract the download link
    dl_link = link["href"]
    logging.info(f"Download link found: {dl_link}")

    # Extract the last segment of the URL as the filename
    last_path_segment = dl_link.split("/")[-1]

    # Send a GET request to download the file
    try:
        response = requests.get(dl_link)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to download the file: {e}")
        raise

    # Save the file locally
    try:
        with open(f"tmp/natural_gas/{last_path_segment}", "wb") as file:
            file.write(response.content)
        logging.info(f"File downloaded successfully as '{last_path_segment}'")
    except IOError as e:
        logging.error(f"Failed to save the file: {e}")
        raise

    # Return the response if successful
    return response, dl_link, last_path_segment
