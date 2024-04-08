# /utils.py
from vectara_cli.config_manager import ConfigManager
def get_vectara_client():
    customer_id, api_key = ConfigManager.get_api_keys()
    from vectara_cli.core import VectaraClient  
    return VectaraClient(customer_id=customer_id, api_key=api_key)

def set_api_keys(customer_id, api_key):
    ConfigManager.set_api_keys(customer_id, api_key)
    print("API keys set successfully.")