# ./commands/upload_document.py

from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 4:
        print("Usage: vectara-cli upload-document corpus_id file_path [document_id]")
        return

    corpus_id = args[1]
    file_path = args[2]
    document_id = args[3] if len(args) > 3 else None
    metadata = {}

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        response, status = vectara_client.upload_document(
            corpus_id, file_path, document_id, metadata
        )

        if status:
            print("Upload successful:", response)
        else:
            print("Upload failed:", response)
    except Exception as e:
        print("Upload failed:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
