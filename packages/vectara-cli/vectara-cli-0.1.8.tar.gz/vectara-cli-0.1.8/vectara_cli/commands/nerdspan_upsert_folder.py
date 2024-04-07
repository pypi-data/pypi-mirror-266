# ./commands/nerdspan_upsert_folder.py

import os
from vectara_cli.advanced.noncommercial.nerdspan import Span
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 5:
        print("Usage: vectara-cli process-and-upload folder_path model_name model_type")
        return

    folder_path = args[1]
    model_name = args[2]
    model_type = args[3]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return

        span = Span("", customer_id, api_key)
        corpus_id_1, corpus_id_2 = span.process_and_upload(
            folder_path, model_name, model_type
        )
        print(
            f"Documents processed and uploaded. Raw uploads in Corpus ID: {corpus_id_1}, Processed uploads in Corpus ID: {corpus_id_2}"
        )
    except Exception as e:
        print("An error occurred during processing:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
