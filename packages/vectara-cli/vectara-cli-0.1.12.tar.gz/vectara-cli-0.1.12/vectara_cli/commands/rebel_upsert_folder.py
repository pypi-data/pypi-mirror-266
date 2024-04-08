# ./commands/rebel_upsert_folder.py

import os
from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager
from vectara_cli.advanced.noncommercial.rebel import Rebel


def main(args, vectara_client):
    if len(args) < 4:
        print(
            "Usage: vectara-cli advanced-upsert-folder folder_path corpus_id_1 corpus_id_2"
        )
        print(
            "Usage: vectara-cli advanced-upsert-folder folder_path corpus_id_1 corpus_id_2"
        )
        return

    folder_path = args[1]
    corpus_id_1 = args[2]
    corpus_id_2 = args[3]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()

        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return

        rebel = Rebel()
        rebel.advanced_upsert_folder(
            vectara_client, corpus_id_1, corpus_id_2, folder_path
        )
        rebel.advanced_upsert_folder(
            vectara_client, corpus_id_1, corpus_id_2, folder_path
        )
        print(f"Advanced processing and upsert completed for folder: {folder_path}")
    except Exception as e:
        print("An error occurred during the upsert process:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
