# config_manager.py
from dotenv import load_dotenv, set_key
import os

ENV_FILE_PATH = '.env'
class ConfigManager:
    @staticmethod
    def set_api_keys(customer_id, api_key):
        """
        Sets the customer ID and API key in the .env file.
        """
        # Ensure that the .env file is loaded.
        load_dotenv(ENV_FILE_PATH)
        
        set_key(ENV_FILE_PATH, 'VECTARA_CUSTOMER_ID', customer_id)
        set_key(ENV_FILE_PATH, 'VECTARA_API_KEY', api_key)

    @staticmethod
    def get_api_keys():
        """
        Retrieves the customer ID and API key from the .env file.
        """
        # Ensure that the .env file is loaded.
        load_dotenv(ENV_FILE_PATH)
        
        # Retrieve the values.
        customer_id = os.getenv('VECTARA_CUSTOMER_ID')
        api_key = os.getenv('VECTARA_API_KEY')
        
        if customer_id is None or api_key is None:
            raise ValueError(
                "API keys are not set in the .env file. Please set them using the appropriate method."
            )
        return customer_id, api_key