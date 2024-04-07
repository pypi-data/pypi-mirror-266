# set_api_keys.py

from vectara_cli.config_manager import ConfigManager


def main(args):
    if len(args) != 3:
        print("Usage: vectara-cli set-api-keys customer_id api_key")
        return
    customer_id = args[1]
    api_key = args[2]
    ConfigManager.set_api_keys(customer_id, api_key)
    print("API keys set successfully.")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
