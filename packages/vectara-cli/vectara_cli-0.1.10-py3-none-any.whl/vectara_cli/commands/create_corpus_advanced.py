# ./commands/create_corpus_advanced.py

# create_corpus.py

# from vectara_cli.utils import get_vectara_client
import json
import sys
from vectara_cli.corpus_data import CorpusData
from vectara_cli.defaults import CorpusDefaults

def print_help():
    help_text = """
Usage: vectara create-corpus-advanced <name> <description> [options]

Arguments:
    <name>         The name of the corpus. This should be a unique name that describes the corpus.
    <description>  A brief description of what the corpus is about.

Options:
    --custom_dimensions JSON_STRING  Optional. A JSON string representing custom dimensions for the corpus.
    --filter_attributes JSON_STRING  Optional. A JSON string representing attributes used for filtering documents within the corpus.
    --public BOOLEAN                 Optional. A boolean flag indicating whether the corpus should be public (true) or private (false). Default is false.
    --encoder_id INT                 Optional. Encoder ID, default is 1.
    --metadata_max_bytes INT         Optional. Maximum metadata bytes, default is 10000.
    --swap_qenc BOOLEAN              Optional. Swap query encoder, default is False.
    --swap_ienc BOOLEAN              Optional. Swap index encoder, default is False.
    --textless BOOLEAN               Optional. If the corpus is textless, default is False.
    --encrypted BOOLEAN              Optional. If the corpus is encrypted, default is True.

Examples of usage:
    vectara create-corpus-advanced "My Corpus" "A corpus containing documents on topic XYZ"
    vectara create-corpus-advanced "Research Papers" "Corpus for academic research papers" --custom_dimensions '{"dimension1": "value1", "dimension2": "value2"}' --filter_attributes '{"author": "John Doe"}'
    vectara create-corpus-advanced "Public Data" "A corpus of public datasets" --public true
"""
    print(help_text)

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
        print_help()
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