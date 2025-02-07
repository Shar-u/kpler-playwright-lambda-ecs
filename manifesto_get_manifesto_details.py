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
from datetime import datetime
import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


def save_link_header_data(record):
    logging.info('saving link header data into a file############')
    file_name = 'link_header_data.json'

    with open(file_name, "w") as json_file:
        json.dump(record, json_file, indent=4)


def task(anchor,driver):
    try:
        
        # WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.ID, "example_id"))
        # ).click()
        logging.info('#############################################')
        logging.info(f'##ANCHOR LINK##---> {anchor}')
        time.sleep(5)
        logging.info(f'##ANCHOR LINK string ##---> {anchor.text.strip()}')
        logging.info('#############################################')
        # Extract the text or href of the anchor tag (optional)
        link_text = anchor.text.strip()
        logging.info(f"Opening link: {link_text}")

        # Open the link by clicking the anchor tag
        anchor.click()
        table_data1 = []
        loop_break = False

        WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(By.XPATH, "//table[.//b[text()='Datos del Manifiesto:']]")
                )#Datos del Manifiesto: 24-3102
        table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table
        rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
        header_table_data = []
        for row in rows:  # Skip the header row
            cells = row.find_elements(By.XPATH, ".//td")
            if cells:
                header_table_data.append({
                    "Puerto": cells[0].text,
                    "Peso Manifiesto": cells[7].text
                })
            
        # Print the extracted data
        for record in header_table_data:
            print(record)
        
        structured_data = [{"header": row_data[0], "value": row_data[1]} for row_data in header_table_data if len(row_data) > 1]
        save_link_header_data(structured_data)

        while True:
            try:
                if loop_break:
                    break
                # Wait for the new page or content to load
                WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//table[.//b[text()='RESULTADO DE CONSULTA']]"))
                    )
                table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table
                rows = table.find_elements(By.XPATH, ".//tr[position()>1]")

                # logging.info(rows)
                # table_data1 = []
                for row in rows:  # Skip the header row
                    cells = row.find_elements(By.XPATH, ".//td")
                    if cells:
                        table_data1.append({
                            "Puerto": cells[0].text,
                            "Peso Manifiesto": cells[7].text
                        })
                
                try:
                    next_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Siguiente')]")
                    if next_button.is_enabled():
                        next_button.click()
                        # Wait for the next page to load
                        WebDriverWait(driver, 10).until(
                            EC.staleness_of(table)  # Wait for the current table to be replaced
                        )
                        table = driver.find_element(By.XPATH, "//table[@class='beta' and @align='center']") # Replace with the actual class or ID of the table

                        # Extract table rows
                        rows = table.find_elements(By.XPATH, ".//tr[position()>1]")
                        

                        # Loop through rows and extract cell data
                        for row in rows: 
                            cells = row.find_elements(By.XPATH, ".//td")
                            if cells:
                                table_data1.append({
                                    "Puerto": cells[0].text,
                                    "Peso Manifiesto": cells[7].text
                                })
                    else:
                        loop_break = True
                        break  # Exit the loop if the Next button is not enabled
                except Exception:
                    logging.error('Exiting the loop as next button is not found')
                    loop_break = True
                    break
            except exceptions.NoSuchElementException as e:
                logging.error(f'Element not Found Exception {e}')
                loop_break = True
                break
        if len(table_data1) >= 1:
            logging.info('saving scrapped data into a file############')
            
            file_name = f'{link_text}_scraped_data.json'
            
            
            with open(file_name, "w") as json_file:
                json.dump(table_data1, json_file)
            logging.info(f'saved scrapped data into a {file_name}############')
        else:
            logging.info(f'No data found for  {link_text}############')

    except exceptions.StaleElementReferenceException as e:
        logging.error(f'staleness of element {anchor} exception {e}')
        pass 
    except Exception as e:
        logging.error(f'Error in task function {e}')
        raise e