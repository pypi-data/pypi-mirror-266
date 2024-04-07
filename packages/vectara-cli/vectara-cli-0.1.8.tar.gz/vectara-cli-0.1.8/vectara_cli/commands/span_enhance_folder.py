# ./commands/span_enhance_folder.py

import os
from vectara_cli.config_manager import ConfigManager
from vectara_cli.advanced.commercial.enterprise import EnterpriseSpan


def main(args, vectara_client):
    if len(args) < 5:
        print(
            "Usage: vectara-cli span-enhance-folder corpus_id_1 corpus_id_2 model_name folder_path"
        )
        return

    corpus_id_1 = args[1]
    corpus_id_2 = args[2]
    model_name = args[3]
    folder_path = args[4]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return

        enterprise_span = EnterpriseSpan(model_name, customer_id, api_key)
        enterprise_span.span_enhance(corpus_id_1, corpus_id_2, folder_path)
        print(
            f"Documents in {folder_path} enhanced and uploaded to corpora: {corpus_id_1} (plain), {corpus_id_2} (enhanced)"
        )
    except Exception as e:
        print("An error occurred during the enhancement process:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
