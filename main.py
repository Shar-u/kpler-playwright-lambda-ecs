from manifesto_main import scrape_maritime_export_data
from natural_gas_main import scrape_natural_gas_data
from crude_oil_main import scrape_crude_oil_data
# from electricity_and_gas import scrape_electricity_gas_data
# from electric_power_main import scrape_electric_power_data
from plan_operation_system_main import scrape_operation_system_data
from datetime import datetime
import logging, os


# Configure logging with filename included
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    force=True,
)

file_name = os.environ.get("FILE_NAME")


def lambda_handler(event, context):
    if file_name == "natural_gas":
        # Scrapping data for Natural Gas
        logging.info(
            "################################## NATURAL GAS SCRAPPING START ########################################"
        )
        scrape_natural_gas_data()  # --working
        logging.info(
            "################################## NATURAL GAS SCRAPPING END ########################################"
        )

    elif file_name == "crude_oil":
        # Scrapping data for Crude Oil
        logging.info(
            "################################## CRUDE OIL SCRAPPING START ########################################"
        )
        scrape_crude_oil_data()  # --working
        logging.info(
            "################################## CRUDE OIL SCRAPPING END ########################################"
        )

    # elif file_name == "electricity_&_gas":
    #     # Scrapping data for Electricity and Gas
    #     logging.info(
    #         "################################## ELECTRICITY & GAS SCRAPPING START ########################################"
    #     )
    #     scrape_electricity_gas_data()  # --working
    #     logging.info(
    #         "################################## ELECTRICTY & GAS SCRAPPING END ########################################"
    #     )

    # elif file_name == "electric_power":
    #     # Scraping data for Electric Power
    #     logging.info(
    #         "################################## ELECTRIC POWER SCRAPPING START ########################################"
    #     )
    #     scrape_electric_power_data()  # --working
    #     logging.info(
    #         "################################## ELECTRIC POWER SCRAPPING END ########################################"
    #     )

    elif file_name == "maritime_manifesto":
        # Scrapping data for Maritime Export
        logging.info(
            "################################## MARITIME MANIFESTO SCRAPPING START ########################################"
        )
        scrape_maritime_export_data()
        logging.info(
            "################################## MARITIME MANIFESTO SCRAPPING END ########################################"
        )

    elif file_name == "operation_system":
        # Scrapping data for operation system
        logging.info(
            "################################## OPERATION SYSTEM SCRAPPING START ########################################"
        )
        scrape_operation_system_data()  # -- working
        logging.info(
            "################################## OPERATION SYSTEM  SCRAPPING END ########################################"
        )

    return {
        "statusCode": 200,
        "body": event
    }
