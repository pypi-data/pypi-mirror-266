# ./commands/upload_document.py

from vectara_cli.utils.config_manager import ConfigManager
from vectara_cli.helptexts.help_text import print_upload_document_help

def main(args, vectara_client):
    if len(args) < 3:
        print_upload_document_help()
        return

    corpus_id = args[0]
    file_path = args[1]
    document_id = args[2] if len(args) > 3 else None
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
    main(sys.argv)
