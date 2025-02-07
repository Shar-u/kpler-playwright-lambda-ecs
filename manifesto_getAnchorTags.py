from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from selenium.common import exceptions
from uniqueList import UniqueList
import logging
from tempfile import mkdtemp

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


# changes sharul
from dotenv import load_dotenv
import os

load_dotenv()
EXECUTABLE_PATH = os.environ.get('EXECUTABLE_PATH')


def get_anchor_tags(driver,url,start_date,end_date,used_links,check_for_next_link)->list:
    try:
        final_anchor_list = UniqueList()
        # Open the website
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        try:

            alert = driver.switch_to.alert
            # logging.info("Alert text:", alert.text)
            alert.accept()
        except Exception as e:
            logging.error(e)

        # Locate the start date input field and enter the date
        start_date_field = driver.find_element(By.NAME, "fech_llega_ini")  # Replace with the actual ID or selector
        start_date_field.clear()
        start_date_field.send_keys(start_date)

        # Locate the end date input field and enter the date
        end_date_field = driver.find_element(By.NAME, "fech_llega_fin")  # Replace with the actual ID or selector
        end_date_field.clear()
        end_date_field.send_keys(end_date)

        # Optional: Submit the form or click a button
        submit_button = driver.find_element(By.XPATH, '//input[@value="Consultar"]') 
        submit_button.click()

        # Wait for the next page or response to load
        time.sleep(5)
        table_data = []
        anchor_tags_first_page =[]
        anchor_tags = []
        page1_links = []
        page2_links = []
        final_links = []

        WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//table[.//b[text()='RESULTADO DE CONSULTA']]"))
            )
        table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table

        # Extract table rows
        # rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
        anchor_tags_first_page = driver.find_elements(By.XPATH, "//table[@class='beta']//a")
        
        logging.info('anchor tags from first page')
        logging.info(f'used_links in get anchor tag ---> {used_links}')
        if not check_for_next_link:
            for anchor in anchor_tags_first_page:
                if anchor.text.strip() in used_links:
                    continue
                logging.info(f'returning anchor tag ---> {anchor.text.strip()}')
                return anchor    
        else:
            logging.info('########checking for next button########')
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Siguiente')]")
                if next_button.is_enabled():
                    next_button.click()
                    # Wait for the next page to load
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(table)  # Wait for the current table to be replaced
                    )
                    table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table

                    # rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
                    anchor_tags = driver.find_elements(By.XPATH, "//table[@class='beta']//a")

                    logging.info('anchor tags from next page')
                    for anchor in anchor_tags:
                        if anchor.text.strip() in used_links:
                            continue
                        logging.info(f'returning anchor tag ---> {anchor.text.strip()}')
                        return anchor    
                    
            except Exception:
                logging.error(f'Error in get_anchor_tags function {e}')
                raise e

    except Exception as e:
        logging.error(f'Error in get_anchor_tags function {e}')
        raise e


def save_anchor_tags(url,start_date,end_date)->list:
    try:
        # # Initialize the WebDriver (e.g., Chrome)
        # service = Service(executable_path=EXECUTABLE_PATH)
        # options = webdriver.ChromeOptions()
        # # adding option for headless mode , sharul, 17-1-2025
        # # start
        # options.add_argument("--headless")  # Enable headless mode
        # options.add_argument("--disable-gpu")  # Disable GPU acceleration
        # options.add_argument("--no-sandbox")  # Required for running on Linux servers
        # options.add_argument("--disable-dev-shm-usage")  # Prevent crashes
        # # end
        # driver = webdriver.Chrome(service=service, options=options)

        # changed start
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
        # end changes

        final_anchor_list = UniqueList()
        # Open the website
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        try:
            alert = driver.switch_to.alert
            # logging.info("Alert text:", alert.text)
            alert.accept()
        except Exception as e:
            logging.error(e)

        # Locate the start date input field and enter the date
        start_date_field = driver.find_element(By.NAME, "fech_llega_ini")  # Replace with the actual ID or selector
        start_date_field.clear()
        start_date_field.send_keys(start_date)

        # Locate the end date input field and enter the date
        end_date_field = driver.find_element(By.NAME, "fech_llega_fin")  # Replace with the actual ID or selector
        end_date_field.clear()
        end_date_field.send_keys(end_date)

        # Optional: Submit the form or click a button
        submit_button = driver.find_element(By.XPATH, '//input[@value="Consultar"]') 
        submit_button.click()

        # Wait for the next page or response to load
        time.sleep(5)
        table_data = []
        anchor_tags_first_page =[]
        anchor_tags = []
        page1_links = []
        page2_links = []
        final_links = []
        find_prv_button = False
        while True:
            WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//table[.//b[text()='RESULTADO DE CONSULTA']]"))
                )
            table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table

            # Extract table rows
            rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
            anchor_tags_first_page = driver.find_elements(By.XPATH, "//table[@class='beta']//a")
            
            logging.info('anchor tags from first page')
            for anchor in anchor_tags_first_page:
                # logging.info(anchor.text.strip())
                page1_links.append(anchor.text.strip())
                # logging.info("Alert text:", alert.text)

            # Loop through rows and extract cell data
            for row in rows:  # Skip the header row
                cells = row.find_elements(By.XPATH, ".//td")
                if cells:
                    table_data.append({
                        "Manifiesto": cells[0].text,
                        "Fecha de Zarpe": cells[1].text,
                        "Nombre de la Nave": cells[2].text,
                    })

            logging.info('########checking for next button########')
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Siguiente')]")
                if next_button.is_enabled():
                    find_prv_button = True
                    next_button.click()
                    # Wait for the next page to load
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(table)  # Wait for the current table to be replaced
                    )
                    table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table

                    rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
                    anchor_tags = driver.find_elements(By.XPATH, "//table[@class='beta']//a")

                    logging.info('anchor tags from next page')
                    for anchor in anchor_tags:
                        page2_links.append(anchor.text.strip())
                    
                    # Loop through rows and extract cell data
                    for row in rows:  
                        cells = row.find_elements(By.XPATH, ".//td")
                        if cells:
                            table_data.append({
                                "Manifiesto": cells[0].text,
                                "Fecha de Zarpe": cells[1].text,
                                "Nombre de la Nave": cells[2].text,
                            })


                else:
                    logging.info('Breaking while loop as next button is not found')
                    break  # Exit the loop if the Next button is not enabled

            
            except Exception:
                find_prv_button = False
                logging.error('Siguiente button not found')
                break  # Exit the loop if no Next button is found

        logging.info('While Loop Completed..!!!')
        logging.info(f'going back to privious page ::: {find_prv_button}')
        if find_prv_button:
            privious_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Anterior')]")
            if privious_button.is_enabled():
                privious_button.click()
                time.sleep(5)
        logging.info(table_data)
 
        final_anchor_link_list = [x for x in page1_links] + [x for x in page2_links]
        final_links.append(page1_links)
        final_links.append(page2_links)

        logging.info(f'final_links  ---> {final_links}')
        if len(final_links) >= 1:
            logging.info('saving scrapped data into a file############')
            file_name = "/tmp/manifesto_temp/anchor_link.json" #changed path
            with open(file_name, "w") as json_file:
                json.dump(final_links, json_file)
            logging.info(f'saved scrapped data into a {file_name}############')
        else:
            logging.info(f'No data found for  final_anchor_link_list ############')

        driver.quit() #changes sharul
        return final_links ,final_anchor_link_list

    except Exception as e:
        logging.error(f'Error in get_anchor_tags function {e}')
        raise e
    
