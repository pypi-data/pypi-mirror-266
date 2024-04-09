# create_corpus.py

from vectara_cli.data.corpus_data import CorpusData
from vectara_cli.data.defaults import CorpusDefaults
from vectara_cli.helptexts.help_text import print_create_corpus_help
import sys

def parse_json_arg(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def main(args, vectara_client):
    if len(args) < 2:
        print_create_corpus_help()
        return

    name = args[0]
    description = args[1]

    defaults = CorpusDefaults.get_defaults()

    custom_dimensions_json = next((arg.split('=')[1] for arg in args if arg.startswith('--custom_dimensions=')), None)
    filter_attributes_json = next((arg.split('=')[1] for arg in args if arg.startswith('--filter_attributes=')), None)

    if custom_dimensions_json:
        custom_dimensions_list = parse_json_arg(custom_dimensions_json)
        defaults['customDimensions'] = [CorpusData.CustomDimension(**dim).to_dict() for dim in custom_dimensions_list]

    if filter_attributes_json:
        filter_attributes_list = parse_json_arg(filter_attributes_json)
        defaults['filterAttributes'] = [CorpusData.FilterAttribute(**attr).to_dict() for attr in filter_attributes_list]

    corpus_data = {
    #   "id": corpus_id,
        "name": name,
        "description": description,
        **defaults
    }#.to_dict()

    try:
        response = vectara_client.create_corpus(corpus_data.to_dict())
        print(f"Corpus created successfully. Response: {response}")
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv)