# ./commands/create_corpus_advanced.py

# create_corpus.py

# from vectara_cli.utils import get_vectara_client
import json
import sys
from vectara_cli.corpus_data import CorpusData
from vectara_cli.defaults import CorpusDefaults
from vectara_cli.helptexts.help_text import print_create_corpus_advanced_help

def parse_json_arg(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def parse_args(args):
    if len(args) < 2:
        print_help()
        sys.exit(1)

    name = args[0]
    description = args[1]
    options = CorpusDefaults.get_defaults()

    for arg in args[2:]:
        if arg.startswith('--custom_dimensions='):
            options["customDimensions"] = parse_json_arg(arg.split('=', 1)[1])
        elif arg.startswith('--filter_attributes='):
            options["filterAttributes"] = parse_json_arg(arg.split('=', 1)[1])
        elif arg.startswith('--encoder_id='):
            options["encoderId"] = int(arg.split('=', 1)[1])
        elif arg.startswith('--metadata_max_bytes='):
            options["metadataMaxBytes"] = int(arg.split('=', 1)[1])
        elif arg.startswith('--swap_qenc='):
            options["swapQenc"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--swap_ienc='):
            options["swapIenc"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--textless='):
            options["textless"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--encrypted='):
            options["encrypted"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']

    return name, description, options

def main(args, vectara_client):
    if len(args) < 3:
        print_create_corpus_advanced_help()
        return

    name, description, options = parse_args(args[1:])

    corpus_data = CorpusData(corpus_id=17, name=name, description=description, **options)


    try:
        response = vectara_client.create_corpus(corpus_data.to_dict())
        print(json.dumps(response, indent=4))
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv)
# def parse_custom_dimensions(dimensions_str):
#     """Parse custom dimensions from a JSON string."""
#     if dimensions_str:
#         try:
#             return json.loads(dimensions_str)
#         except json.JSONDecodeError:
#             raise ValueError("Invalid JSON format for custom dimensions.")
#     return []
    # parser = argparse.ArgumentParser(description="Create a new corpus in Vectara platform.")
    # parser.add_argument("--corpus_id", type=int, help="Corpus ID", required=True)
    # parser.add_argument("--name", type=str, help="Name of the corpus", required=True)
    # parser.add_argument("--description", type=str, default="A Vectara Corpus", help="Description of the corpus")
    
    # parsed_args = parser.parse_args(args)
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