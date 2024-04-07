# query.py

from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 4:
        print("Usage: vectara-cli query query_text num_results corpus_id")
        return
    query_text = args[1]
    num_results = int(args[2])
    corpus_id = args[3]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        response = vectara_client.query(query_text, num_results, corpus_id)
        print(response)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
