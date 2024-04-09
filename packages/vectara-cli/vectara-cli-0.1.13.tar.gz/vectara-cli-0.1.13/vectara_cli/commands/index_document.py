# ./commands/index_document.py

import json
from vectara_cli.core import VectaraClient
from vectara_cli.helptexts.help_text import print_index_document_help

def main(args, vectara_client):
    if len(args) < 4:
        print_index_document_help()
        return
    corpus_id = int(args[0])
    document_id = args[1]
    title = args[2]
    metadata_json = args[3]
    section_text = args[4]
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding metadata_json: {e}")
        return
    response, success = vectara_client.index_document(
        corpus_id, document_id, title, metadata, section_text
    )

    if success:
        print("Document indexed successfully.")
    else:
        print(f"Document indexing failed: {response}")

if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
