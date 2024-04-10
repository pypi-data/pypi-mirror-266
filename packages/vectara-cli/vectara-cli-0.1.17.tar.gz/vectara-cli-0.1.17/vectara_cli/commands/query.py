# query.py

from vectara_cli.core import VectaraClient
from vectara_cli.utils.config_manager import ConfigManager
from vectara_cli.data.query_response import QueryResponse

def main(args, vectara_client):
    if len(args) < 3:
        print("Usage: vectara-cli query query_text num_results corpus_id")
        return
    query_text = args[0]
    num_results = int(args[1])
    corpus_id = args[2]

    try:
        # customer_id, api_key = ConfigManager.get_api_keys()
        response = vectara_client.query(query_text, num_results, corpus_id)
        parsed_response = QueryResponse.parse_response(response)
        for item in parsed_response:
            print(item)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    import sys

    main(sys.argv)
