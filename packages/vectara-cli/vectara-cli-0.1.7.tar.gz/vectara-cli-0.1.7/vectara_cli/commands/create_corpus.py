# create_corpus.py

from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 3:
        print("Usage: vectara-cli create-corpus corpus_id name")
        return
    corpus_id = args[1]
    name = args[2]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        response = vectara_client.create_corpus(
            corpus_id,
            name,
            "Description",
            1234567890,
            True,
            False,
            False,
            False,
            False,
            "default",
            10000,
            [],
            [],
        )
        print(response)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
