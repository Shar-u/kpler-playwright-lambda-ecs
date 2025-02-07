from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from tempfile import mkdtemp
from selenium.webdriver.support import expected_conditions as EC
import os, requests, logging
from urllib.parse import urljoin, urlparse, urlunparse
import pandas as pd
import datetime
from dotenv import load_dotenv
from plan_operation_system_excel_to_julia import (
    parse_excel_to_julia,
    upload_files_to_s3,
)

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)

load_dotenv()
month_year = os.getenv("month-year")
EXECUTABLE_PATH = os.environ.get("EXECUTABLE_PATH")
plan_operation_system_sheet_name_1 = os.environ.get(
    "PLAN_OPERATION_SYSTEM_SHEET_NAME_1"
)
plan_operation_system_sheet_name_2 = os.environ.get(
    "PLAN_OPERATION_SYSTEM_SHEET_NAME_2"
)
website_url = os.environ.get("PLAN_OPERATION_SYSTEM_WEBSITE_URL")


def clean_url(excel_url):
    """Clean URL by removing query parameters."""
    return urlunparse(urlparse(excel_url)._replace(query=""))


def wait_for_element(driver, by, value, timeout=15):
    """Wait for an element to appear on the page."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def scrape_website(url, date):
    try:
        # Set up the Chrome WebDriver with options
        options = webdriver.ChromeOptions()
        service = webdriver.ChromeService("/opt/chromedriver-linux64/chromedriver")

        options.binary_location = '/opt/chrome-linux64/chrome'
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")
        
        driver = webdriver.Chrome(options=options, service=service)
        # driver = webdriver.Chrome(
        #     service=Service(executable_path="/opt/chromedriver"),
        #     options=options,
        # )
        

        # Load the page
        driver.get(url)

        # Wait for the datepicker input to load
        date_input = wait_for_element(
            driver, By.CLASS_NAME, "operation-plan__datepicker-input"
        )

        # Clear the existing date and input the desired date
        date_input.clear()
        date_input.send_keys(date)

        # Click the submit button
        submit_button = wait_for_element(
            driver, By.CLASS_NAME, "operation-plan__arrow-submit"
        )
        submit_button.click()

        # Wait for the files list to update
        WebDriverWait(driver, 15).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, "operation-plan__link-item"),
                str(
                    datetime.datetime.strptime(date, "%m/%Y").year
                ),  # Ensure it matches the year you are filtering
            )
        )

        # Wait for the updated files to load
        wait_for_element(driver, By.CLASS_NAME, "operation-plan__link-item")
        links = driver.find_elements(
            By.XPATH,
            "//li[@class='operation-plan__link-item']//a[contains(@href, '.xlsx')]",
        )

        # Extract links and publication dates
        files_data = [
            {
                "excel_url": clean_url(
                    urljoin(driver.current_url, link.get_attribute("href"))
                ),
                "publication_date": elem.text.strip(),
            }
            for link, elem in zip(
                links, driver.find_elements(By.CLASS_NAME, "operation-plan__link-date")
            )
        ]
        driver.quit()
        return files_data
    except Exception as e:
        return {"error": str(e)}


def extract_filename(excel_url):
    """Extract the filename from a URL."""
    return (
        os.path.basename(urlparse(excel_url).path)
        .split("?")[0]
        .replace("operationplan.getexcelfile.operationplan.", "")
    )


def download_excel(excel_url, folder):
    """Download an Excel file from the given URL."""
    try:
        os.makedirs(folder, exist_ok=True)
        filename = extract_filename(excel_url)
        file_path = os.path.join(folder, filename)

        response = requests.get(excel_url)
        response.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(response.content)

        logging.info(f"Downloaded: {file_path}")
    except Exception as e:
        logging.error(f"Error downloading {excel_url}: {str(e)}")


def save_to_excel(data, output_file):
    """Save data to an Excel file, appending new entries if necessary."""
    df = pd.DataFrame(data)
    if os.path.exists(output_file):
        df_existing = pd.read_excel(output_file)
        new_data = df[~df["Filename"].isin(df_existing["Filename"])]
        df_combined = pd.concat([df_existing, new_data], ignore_index=True)
        df_combined.to_excel(output_file, index=False)
        logging.info(f"Updated {output_file}")
    else:
        df.to_excel(output_file, index=False)
        logging.info(f"Created {output_file}")


# Main function to run the program
def scrape_operation_system_data():

    date = month_year
    folder = os.path.join("/tmp/operation_system", date.replace("/", "-"))
    os.makedirs(folder, exist_ok=True)
    metadata_file = os.path.join(folder, "excel_files_with_dates.xlsx")

    # Step 1: Scrape the website for files
    logging.info("Starting web scraping...")
    logging.info(website_url)
    files_data = scrape_website(website_url, date)

    if "error" in files_data:
        logging.error(f"Scraping failed: {files_data['error']}")
        return

    excel_files_data = [
        {
            "Filename": extract_filename(file["excel_url"]),
            "Publication Date": file["publication_date"],
            "Excel URL": file["excel_url"],
        }
        for file in files_data
    ]

    # Step 2: Download Excel files
    logging.info("Downloading Excel files...")
    for file in excel_files_data:
        download_excel(file["Excel URL"], folder)

    # Step 3: Save metadata to Excel in the same folder
    save_to_excel(excel_files_data, metadata_file)

    # Step 4: Find the latest file based on publication date
    logging.info("Finding the latest file by publication date...")
    metadata_df = pd.read_excel(metadata_file)
    metadata_df["Publication Date"] = pd.to_datetime(
        metadata_df["Publication Date"], format="%d/%m/%Y"
    )
    latest_file_row = metadata_df.sort_values(
        by="Publication Date", ascending=False
    ).iloc[0]
    latest_file_name = latest_file_row["Filename"]
    latest_file_path = os.path.join(folder, latest_file_name)

    logging.info(f"Latest file identified: {latest_file_name}")

    # Step 5: Convert the latest file to Julia format
    output_julia_file = os.path.splitext(latest_file_path)[0] + ".jl"

    logging.info("Converting latest Excel file to Julia format...")
    parse_excel_to_julia(
        latest_file_path,
        plan_operation_system_sheet_name_1,
        plan_operation_system_sheet_name_2,
        folder,
    )

    # Step 6: Upload the files to S3
    logging.info("Uploading files to S3...")
    upload_files_to_s3(latest_file_path, output_julia_file)

    # # Set up the Chrome WebDriver with options
    # options = Options()
    # options.add_argument("--headless")  # Disable chrome popup window
    # options.add_argument("--disable-gpu")  # Disable GPU acceleration
    # options.add_argument("--no-sandbox")  # For running on Linux servers
    # options.add_argument("--disable-dev-shm-usage")  # To avoid crash
    # driver = webdriver.Chrome(
    #     service=Service(executable_path=EXECUTABLE_PATH),
    #     options=options,
    # )


    # driver = webdriver.Chrome(service=Service(EXECUTABLE_PATH), options=options)

    # # Apply headers using CDP (Chrome DevTools Protocol)
    # headers = {
    #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    #     "accept-encoding": "gzip, deflate, br, zstd",
    #     "accept-language": "en-US,en;q=0.7",
    #     "cache-control": "max-age=0",
    #     "connection": "keep-alive",
    #     "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    #     "sec-ch-ua-mobile": "?0",
    #     "sec-ch-ua-platform": '"Windows"',
    #     "sec-fetch-dest": "document",
    #     "sec-fetch-mode": "navigate",
    #     "sec-fetch-site": "none",
    #     "sec-fetch-user": "?1",
    #     "sec-gpc": "1",
    #     "upgrade-insecure-requests": "1",
    #     "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    # }

    # # Enable CDP to override headers
    # driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})


    # # Load the page
    # driver.get("https://www.google.com")
    # logging.info(driver.title)
    # driver.quit()
