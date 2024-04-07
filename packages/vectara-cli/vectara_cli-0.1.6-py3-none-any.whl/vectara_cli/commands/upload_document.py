# ./commands/upload_document.py

from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager


def main(args):
    if len(args) < 4:
        print("Usage: vectara-cli upload-document corpus_id file_path [document_id]")
        return

    corpus_id = args[1]
    file_path = args[2]
    document_id = args[3] if len(args) > 3 else None
    metadata = {}  # Extend this to accept metadata as an argument if needed

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        vectara_client = VectaraClient(customer_id, api_key)
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
