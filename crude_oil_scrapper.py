"""
scrapper.py

This script scrapes crude oil data and html script from the National Bureau of Statistics of China 
(https://data.stats.gov.cn/english/easyquery.htm?cn=A01) using Playwright.

Features:
- Automates browser interactions to navigate and extract data.
- Implements retries for handling navigation failures.
- Returns extracted data as json and html script.
- Logs events and errors for monitoring.

Usage:
Run the script to perform the scraping operation.

Dependencies:
- Playwright
- logging_config
"""

import json, logging
import time
from playwright.sync_api import sync_playwright

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def scrape(url, retries, delay):
    logging.info("Starting scraping process")
    with sync_playwright() as p:
        logging.info("Launching browser")
        try:
            browser = p.chromium.launch(
                args=[
                    "--disable-web-security",
                    "--disable-features=IsolateOrigins,site-per-process",
                    "--no-sandbox",
                ]
            )
        except Exception as e:
            logging.error(f"Failed to launch browser: {e}")
            raise

        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        timeout = 30000
        # Navigating to the website with retries
        for attempt in range(retries):
            try:
                logging.info(f"Attempt {attempt + 1}: Navigating to URL")
                logging.info(url)
                page.goto(url, wait_until="networkidle", timeout=timeout)
                break
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    timeout = 50000
                else:
                    logging.error("All retry attempts failed")
                    raise

        time.sleep(5)

        # HTML Rendering
        logging.info("Rendering HTML content")
        try:
            html_content = page.content()
            logging.info("HTML content Rendered successfully")
        except Exception as e:
            logging.error(f"Failed during rendering: {e}")
            raise

        # Navigating inside the website to get the crude oil data
        logging.info("Interacting with the page to extract data")
        try:
            page.click('text="Energy"')
            page.wait_for_selector('text="Output of Energy Products"')

            page.click('text="Output of Energy Products"')
            page.wait_for_selector('text="Crude oil"')

            page.click('text="Crude oil"')
            time.sleep(10)

            page.click('text="LATEST13"')
            page.fill(".dtText", "1970-")
            page.click('text="Submit"')

            page.wait_for_selector(
                'span[code="198301"]', timeout=60000
            )  ### For the entire data to load | Sahil | 21-01-2025

            time.sleep(10)
        except Exception as e:
            logging.error(f"Failed during interaction: {e}")
            raise

        # Extracting the data from the webpage
        logging.info("Extracting table data")
        try:
            table = page.locator("div.table_container_main")
            headers = [
                header.inner_text().strip()
                for header in table.locator("thead th").all()
            ]

            rows = []
            for row in table.locator("tbody tr").all():
                cells = [cell.inner_text().strip() for cell in row.locator("td").all()]
                row_data = dict(zip(headers, cells))
                rows.append(row_data)

            json_data = json.dumps(rows, indent=4)

        except Exception as e:
            logging.error(f"Failed to extract or save table data: {e}")
            raise

        context.close()
        browser.close()
        logging.info("Browser closed")

        return json_data, html_content
