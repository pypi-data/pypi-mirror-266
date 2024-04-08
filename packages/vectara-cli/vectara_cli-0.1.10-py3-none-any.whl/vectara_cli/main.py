
# ./main.py
import sys
from vectara_cli.commands import (
    nerdspan_upsert_folder,
    index_text,
    index_document,
    query,
    create_corpus,
    create_corpus_advanced,
    delete_corpus,
    span_enhance_folder,
    upload_document,
    upload_enriched_text,
    span_text,
    rebel_upsert_folder,
)
from vectara_cli.config_manager import ConfigManager
from vectara_cli.utils import get_vectara_client, set_api_keys as set_api_keys_main


def print_help():
    help_text = """
    Usage: vectara-cli <command> [arguments]

    Commands:
    set-api-keys <customer_id> <api_key> - Set the API keys for Vectara client.
    index-document <args> - Index a document in the Vectara platform.
    query <args> - Query the Vectara platform.
    create-corpus <args> - Create a new corpus in the Vectara platform.
    create-corpus-advanced <args> - more administrative control when you create a new corpus in the Vectara platform.
    delete-corpus <args> - Delete a corpus from the Vectara platform.
    span-text <args> - Process text using the span model.
    span-enhance-folder <args> - Enhance documents in a folder using the span model.
    upload-document <args> - Upload a document to the Vectara platform.
    upload-enriched-text <args> - Upload enriched text to the Vectara platform.
    nerdspan-upsert-folder <args> - Process and upload documents in a folder using the nerdspan model.
    rebel-upsert-folder <args> - Perform advanced upsert for a folder using the rebel model.

    Use 'vectara-cli help' to display this help message.
    """
    print(help_text)
    
def get_command_mapping():
    command_mapping = {
        "index-document": index_document.main,
        "query": query.main,
        "create-corpus": create_corpus.main,
        "create-corpus-advanced" : create_corpus_advanced.main,
        "delete-corpus": delete_corpus.main,
        "span-text": span_text.main,
        "span-enhance-folder": span_enhance_folder.main,
        "upload-document": upload_document.main,
        "upload-enriched-text": upload_enriched_text.main,
        "nerdspan-upsert-folder": nerdspan_upsert_folder.main,
        "rebel-upsert-folder": rebel_upsert_folder.main,
        "index-text": index_text.main,
    }
    return command_mapping

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("help", "--help", "-h"):
        print_help()
        return

    command = sys.argv[1]
    args = sys.argv[1:]
    
    

    if command == "set-api-keys":
        set_api_keys_main(args)
    else:
        try:
            vectara_client = get_vectara_client()
            command_mapping = get_command_mapping()
            if command in command_mapping:
                command_mapping[command](args, vectara_client)
            else:
                print(f"Unknown command: {command}")
                print_help()
        except ValueError as e:
            print(e)
            sys.exit(1)


if __name__ == "__main__":
    main()