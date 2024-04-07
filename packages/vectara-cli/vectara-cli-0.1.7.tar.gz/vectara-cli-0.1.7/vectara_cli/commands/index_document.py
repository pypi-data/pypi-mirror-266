# index_document.py

import json
from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 6:
        print(
            "Usage: vectara-cli index-document corpus_id document_id title metadata_json section_text"
        )
        return
    corpus_id = args[1]
    document_id = args[2]
    title = args[3]
    metadata = json.loads(args[4])
    section_text = args[5]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        response, success = vectara_client.index_document(
            corpus_id, document_id, title, metadata, section_text
        )
        if success:
            print("Document indexed successfully.")
        else:
            print("Document indexing failed.", response)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
