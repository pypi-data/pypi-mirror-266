# vectara_cli/main.py

import sys
from vectara_cli.commands import set_api_keys, index_document, query, create_corpus, delete_corpus
from vectara_cli.config_manager import ConfigManager
from vectara_cli.core import VectaraClient

def get_vectara_client():
    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        return VectaraClient(customer_id, api_key)
    except ValueError as e:
        print(e)
        sys.exit(1)

def print_help():
    help_text = """
    Usage: vectara-cli <command> [arguments]

    Commands:
    set-api-keys <customer_id> <api_key> - Set the API keys for Vectara client.
    index-document <args> - Index a document in the Vectara platform.
    query <args> - Query the Vectara platform.
    create-corpus <args> - Create a new corpus in the Vectara platform.
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

def main():
    args = sys.argv[1:]
    if not args or args[0] in ('help', '--help', '-h'):
        print_help()
        return

    command = args[0]

    '''TODO create help function for all commands and what they do'''

    if command == "set-api-keys":
        set_api_keys.main(args)
    else:
        vectara_client = get_vectara_client()

        if command == "index-document":
            index_document.main(args, vectara_client)
        elif command == "query":
            query.main(args, vectara_client)
        elif command == "create-corpus":
            create_corpus.main(args, vectara_client)
        elif command == "delete-corpus":
            delete_corpus.main(args, vectara_client)
        elif command == "span-text":
            delete_corpus.main(args, vectara_client)
        elif command == "span-enchance-folder":
            delete_corpus.main(args, vectara_client)
        elif command == "upload-document":
            delete_corpus.main(args, vectara_client)
        elif command == "upload-enriched-text":
            delete_corpus.main(args, vectara_client)
        elif command == "nerdspan-upsert-folder":
            delete_corpus.main(args, vectara_client)
        elif command == "rebel-upsert-folder":
            delete_corpus.main(args, vectara_client)
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
