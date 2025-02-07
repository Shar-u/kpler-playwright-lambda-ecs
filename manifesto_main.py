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
from manifesto_getAnchorTags import get_anchor_tags , save_anchor_tags
import os
from manifesto_create_output_json import create_output_json_file
from manifesto_julia_file import generate_jl_file
import boto3 
from dotenv import load_dotenv
from upload_s3 import upload
from tempfile import mkdtemp
load_dotenv()

import logging

# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True
)


EXECUTABLE_PATH = os.environ.get('EXECUTABLE_PATH')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MANIFESTO_URL = os.environ.get('MANIFESTO_URL')

# Define start and end dates
# start_date = "04/12/2024"
# end_date = "05/12/2024"
start_date = "11/01/2025"
end_date = "11/01/2025"

lastPathSegment = MANIFESTO_URL.split('=')[-1]
local_file_path = f'/tmp/manifesto_temp/{lastPathSegment}.jl'  #changed

sourceName = "aduanet.gob.pe"
extractionDate = time.strftime('%Y-%m-%d')
object_key = f'{sourceName}/{extractionDate}/bronze/{lastPathSegment}.jl' 

dateInterval = f"{start_date.replace('/','-')}/{end_date.replace('/','-')}"
country = "PER"
sourceName = "aduanet.gob.pe"
publicationDate = f"{start_date.replace('/','-')}"
extractionDate = time.strftime('%Y-%m-%d')

used_links = UniqueList()
unsed_links = UniqueList()
anchor_tags = UniqueList()

def restructure_data(all_table_data)->str:
    
    """
    Restructures the provided table data into a specific dictionary format.
    Args:
        all_table_data (list): A list of lists containing table data entries.
    Returns:
        str: A JSON string representation of the restructured data dictionary.
    The function processes the input data to extract specific fields and 
    organizes them into a dictionary with a predefined order. The fields 
    extracted are:
        - MANIFIESTO
        - MATRICULA DE LA NAVE
        - EMPRESA DE TRANSPORTE
        - NRO DE DETALLES
        - NRO BULTOS
        - NACIONALIDAD
    The resulting dictionary is then converted to a JSON string and returned.
    """
    try:
        logging.info('restructuring data START #############################')
        data_dict = {}
        logging.info(all_table_data)
        # Process the data to convert it into a dictionary
        data =  all_table_data[0]
        for entry in data:
            # logging(entry)
            if len(entry) == 4:
                data_dict[entry[0].strip(": ")] = entry[1].strip(": ")
                data_dict[entry[2].strip(": ")] = entry[3].strip(": ")
            elif len(entry) == 3:
                data_dict[entry[0].strip(": ")] = entry[1].strip(": ")

        logging.info(f'header data ---> {data_dict}')
        new_order = ["MANIFIESTO","MATRICULA DE LA NAVE", "EMPRESA DE TRANSPORTE",  "NRO DE DETALLES","NRO BULTOS" ,"NACIONALIDAD"]
        ordered_dict = {key: data_dict[key] for key in new_order}
        # logging the resulting dictionary
        json.dumps(ordered_dict, indent=4)
        logging.info(f'restructured header data ---> {ordered_dict}')
        logging.info('restructuring data END #############################')
        return ordered_dict#json.dumps(ordered_dict, indent=4)
    except Exception as e:
        logging.error(f'Error in restructure_data function {e}')
        

def get_header_Table_data(driver)->list:
    ## get header data start
    tables = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//table"))  # Find all tables on the page
    )
    index = 1
    # Initialize a list to store all table data
    all_table_data = []
    if len(tables) > 2:
        for i, table in enumerate(tables):
            if i == index:
                # Check if the table has a <tbody>
                rows = table.find_elements(By.XPATH, ".//tbody/tr")
                if not rows:
                    # If no <tbody>, find rows directly under the table
                    rows = table.find_elements(By.XPATH, ".//tr")

                # Extract data from rows
                table_data = []
                for row in rows:
                    cells = row.find_elements(By.XPATH, ".//td")
                    row_data = []
                    for cell in cells:
                        # Check for nested <b> tags and extract text if present
                        bold_elements = cell.find_elements(By.XPATH, ".//b")
                        if bold_elements:
                            row_data.append(", ".join([bold.text.strip() for bold in bold_elements]))
                        else:
                            row_data.append(cell.text.strip())
                    if any(row_data):  # Avoid adding empty rows
                        if 'Datos del Manifiesto' not in row_data[0]:
                            table_data.append(row_data)

                if table_data:  # If the table has data, add it to all_table_data
                    all_table_data.append(table_data)

            # logging the extracted data from all tables
        logging.info(f'Header Table data {all_table_data}')
    # restructure_data(all_table_data)
    return restructure_data(all_table_data)
    ## get header data end


def task(anchor,driver,used_links):
    try:

        logging.info('#############################################')
        logging.info(f'##ANCHOR LINK##---> {anchor.text.strip()}')
        logging.info('#############################################')
        # Extract the text or href of the anchor tag (optional)
        link_text = anchor.text.strip()
        logging.info(f"Opening link: {link_text}")
        used_links.append(link_text)
        logging.info(f'used_links in task ---> {used_links}')

        # Open the link by clicking the anchor tag
        anchor.click()
        table_data1 = []
        loop_break = False
        all_table_data =[]
        all_table_data.append(get_header_Table_data(driver))
        while True:
            try:
                # if loop_break:
                #     break
                


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
                                        "Peso Manifiesto": cells[7].text,
                                        "Bultos Manifiesto":cells[8].text,
                                        "Peso Recibido":cells[9].text,
                                        "Bultos Recibidos":cells[10].text,
                                        "Embarcador":cells[12].text
                                    })
                
                try:
                    logging.info('checking for next button *************************************************************')
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
                                    "Peso Manifiesto": cells[7].text,
                                    "Bultos Manifiesto":cells[8].text,
                                    "Peso Recibido":cells[9].text,
                                    "Bultos Recibidos":cells[10].text,
                                    "Embarcador":cells[12].text
                                })
                    else:
                        loop_break = True
                        break  # Exit the loop if the Next button is not enabled
                except Exception:
                    logging.info('exception in the loop for next button is not found')
                    break
            except exceptions.NoSuchElementException as e:
                logging.error(f'Element not Found Exception {e}')
                loop_break = True
                break
        all_table_data.append(table_data1)
        if len(all_table_data) >= 1:
            logging.info('saving scrapped data into a file############')
            file_name = f"/tmp/manifesto_temp/{link_text}_scraped_data.json"  #changes sharul -----changed
            with open(file_name, "w") as json_file:
                json.dump(all_table_data, json_file)
            logging.info(f'saved scrapped data into a {file_name}############')
        else:
            logging.info(f'No data found for  {link_text}############')
        
    except exceptions.StaleElementReferenceException as e:
        logging.error(f'staleness of element {anchor} exception {e}')
        pass 
    except Exception as e:
        logging.error(f'Error in task function {e}')
        # raise e


def save_json_header_data(dateInterval,country,sourceName,sourceUri,publicationDate,extractionDate):
    logging.info('saving header data into a file############')
    header_data = {
        "dateInterval": dateInterval,
        "country": country,
        "sourceName": sourceName,
        "sourceUri": sourceUri,
        "publicationDate": publicationDate,
        "extractionDate": extractionDate
    }
    file_name = 'header_data.json'
    json_dir='/tmp/manifesto_temp/' #changed sharul -----changed 
    json_file_path = os.path.join(json_dir, file_name)
    with open(json_file_path, "w") as json_file:
        json.dump(header_data, json_file, indent=4)
    logging.info(f'saved header data into a {file_name}############')

def refresh_page(driver):
    logging("Refreshing the page...")
    driver.refresh()

    # Wait for an element on the refreshed page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "some_element_id"))  # Replace with a real locator
    )

    logging("Page refreshed and element loaded.")


# Initialize an S3 client
s3_client = boto3.client(
    's3'
)




def scrape_maritime_export_data():
    try:
        


        logging.info('############################################################################################################################################################################')
        logging.info('###########################################################################  Scrapping Started   ###########################################################################')
        logging.info('############################################################################################################################################################################')
        logging.info(MANIFESTO_URL)
        os.makedirs('/tmp/manifesto_temp', exist_ok=True)
        save_json_header_data(dateInterval,country,sourceName,MANIFESTO_URL,publicationDate,extractionDate)
        anchor_tag_link , unsed_links = save_anchor_tags(MANIFESTO_URL,start_date,end_date)
        

        
        logging.info(f'unsed_links links length ---> {len(unsed_links)}')
        loop_cnt = 0
        check_for_next_link = False

        for x in anchor_tag_link:
            for y in x:

                try:
                    loop_cnt += 1
                    if loop_cnt > len(x):
                        check_for_next_link = True
                    logging.info(f'loop count ---> {loop_cnt} ### {x}  #### {y}   #### {check_for_next_link}')
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

                    # changes start
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
                    # end
                    anchor_tags = get_anchor_tags(driver,MANIFESTO_URL,start_date,end_date,used_links,check_for_next_link)
                    

                    logging.info(f'used links length ---> {len(used_links)}')
                    logging.info(f'unsed_links links length ---> {len(unsed_links)}')

                    if len(unsed_links) == len(used_links):
                        logging.info('*************************All links are used*********************')
                        driver.quit()
                        break
                    else:
                        task(anchor_tags,driver,used_links)
                        driver.quit()
                        
                except Exception as e:
                    logging.error(f'Error in loop  {e}')
                    # raise e
        logging.info('############################################################################################################################################################################')
        logging.info('#############################################################################  Scrapping Ended #############################################################################')
        logging.info('############################################################################# Generate ouput file #########################################################################################')
        file_name = create_output_json_file(lastPathSegment)
        generate_jl_file(file_name)
        upload(local_file_path, BUCKET_NAME, object_key)
    except Exception as e:
        logging.error(f'Error in main function {e}')
        raise e