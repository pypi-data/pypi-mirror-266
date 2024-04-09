# ./commands/delete_corpus.py

from vectara_cli.core import VectaraClient
from vectara_cli.utils.config_manager import ConfigManager
from vectara_cli.helptexts.help_text import show_delete_corpus_help


def main(args, vectara_client):
    if len(args) < 1:
        show_delete_corpus_help()
        return

    corpus_id = args[0]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        response, success = vectara_client.delete_corpus(corpus_id)

        if success:
            print("Corpus deleted successfully.")
        else:
            print("Failed to delete corpus:", response)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
