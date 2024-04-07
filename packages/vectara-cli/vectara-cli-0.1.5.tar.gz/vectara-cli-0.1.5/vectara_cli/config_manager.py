# config_manager.py

import os

class ConfigManager:
    @staticmethod
    def set_api_keys(customer_id, api_key):
        """Sets the customer ID and API key as environment variables."""
        os.environ['VECTARA_CUSTOMER_ID'] = customer_id
        os.environ['VECTARA_API_KEY'] = api_key

    @staticmethod
    def get_api_keys():
        """Retrieves the customer ID and API key from environment variables."""
        customer_id = os.getenv('VECTARA_CUSTOMER_ID')
        api_key = os.getenv('VECTARA_API_KEY')
        if not customer_id or not api_key:
            raise ValueError("API keys are not set. Please set them using the 'set-api-keys' command.")
        return customer_id, api_key
