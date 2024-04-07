# create_corpus.py

import sys
import argparse
from vectara_cli.core import VectaraClient
from vectara_cli.config_manager import ConfigManager
from vectara_cli.corpus_data import CorpusData
from vectara_cli.defaults import CorpusDefaults

def main(args=None, vectara_client=None):
    parser = argparse.ArgumentParser(description="Create a new corpus in Vectara platform.")
    parser.add_argument("corpus_id", type=int, help="Corpus ID")
    parser.add_argument("name", type=str, help="Name of the corpus")
    parser.add_argument("--description", type=str, default="Description", help="Description of the corpus")

    args = parser.parse_args()

    if args is not None:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    defaults = CorpusDefaults.get_defaults()

    corpus_data = CorpusData(
        corpus_id=args.corpus_id,
        name=args.name,
        description=args.description,
        **defaults
    )

    if vectara_client is None:
        from vectara_cli.config_manager import ConfigManager
        customer_id, api_key = ConfigManager.get_api_keys()
        vectara_client = VectaraClient(customer_id, api_key)

    try:
        response = vectara_client.create_corpus(corpus_data)
        print(response)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()

# def parse_custom_dimensions(dimensions_str):
#     """Parse custom dimensions from a JSON string."""
#     if dimensions_str:
#         try:
#             return json.loads(dimensions_str)
#         except json.JSONDecodeError:
#             raise ValueError("Invalid JSON format for custom dimensions.")
#     return []

# def parse_filter_attributes(attributes_str):
#     """Parse filter attributes from a JSON string."""
#     if attributes_str:
#         try:
#             return json.loads(attributes_str)
#         except json.JSONDecodeError:
#             raise ValueError("Invalid JSON format for filter attributes.")
#     return []

# def str2bool(v):
#     """Convert string to boolean."""
#     return v.lower() in ("yes", "true", "t", "1")