# config_manager.py

import json
import os

CONFIG_FILE_PATH = 'config.json'

class ConfigManager:
    @staticmethod
    def set_api_keys(customer_id, api_key):
        """Sets the customer ID and API key in a configuration file."""
        with open(CONFIG_FILE_PATH, 'w') as config_file:
            json.dump({'VECTARA_CUSTOMER_ID': customer_id, 'VECTARA_API_KEY': api_key}, config_file)

    @staticmethod
    def get_api_keys():
        """Retrieves the customer ID and API key from a configuration file."""
        if not os.path.exists(CONFIG_FILE_PATH):
            raise ValueError(
                "API keys are not set. Please set them using the 'set-api-keys' command."
            )
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config = json.load(config_file)
        return config['VECTARA_CUSTOMER_ID'], config['VECTARA_API_KEY']
