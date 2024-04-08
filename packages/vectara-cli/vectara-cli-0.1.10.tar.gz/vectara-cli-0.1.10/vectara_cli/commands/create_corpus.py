# create_corpus.py

# from vectara_cli.utils import get_vectara_client
from vectara_cli.corpus_data import CorpusData
from vectara_cli.defaults import CorpusDefaults

def print_help():
    help_text = """
Usage: vectara create-corpus <corpus_id> <name> <description> [options]

Arguments:
    <corpus_id>    The unique identifier for the corpus. Must be an integer.
    <name>         The name of the corpus. This should be a unique name that describes the corpus.
    <description>  A brief description of what the corpus is about.

Options:
    --custom_dimensions JSON_STRING  Optional. A JSON string representing custom dimensions for the corpus. 
                                     Custom dimensions allow you to add additional metadata that can be used for 
                                     filtering and querying. Example: '{"dimension1": "value1", "dimension2": "value2"}'
    --filter_attributes JSON_STRING  Optional. A JSON string representing attributes used for filtering documents 
                                     within the corpus. Example: '{"attribute1": "value1", "attribute2": "value2"}'
    --public BOOLEAN                 Optional. A boolean flag indicating whether the corpus should be public 
                                     (true) or private (false). Default is false.

Examples of usage:
    Create a basic corpus:
        vectara create-corpus 123 "My Corpus" "A corpus containing documents on topic XYZ"

    Create a corpus with custom dimensions and filter attributes:
        vectara create-corpus 456 "Research Papers" "Corpus for academic research papers" --custom_dimensions '{"subject": "Computer Science", "year": "2024"}' --filter_attributes '{"author": "John Doe"}'

    Create a public corpus:
        vectara create-corpus 789 "Public Data" "A corpus of public datasets" --public true

Note:
    - Ensure that the JSON strings for --custom_dimensions and --filter_attributes are properly formatted. Incorrect JSON format will result in an error.
    - The --public option is a simple flag. If you want the corpus to be public, include '--public true' in your command. The default behavior is to create a private corpus if the flag is not specified.
"""
    print(help_text)

def parse_json_arg(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def main(args, vectara_client):
    if len(args) < 4:
        print_help()
        return

    corpus_id = int(args[1])
    name = args[2]
    description = args[3]

    defaults = CorpusDefaults.get_defaults()

    custom_dimensions_json = next((arg.split('=')[1] for arg in args if arg.startswith('--custom_dimensions=')), None)
    filter_attributes_json = next((arg.split('=')[1] for arg in args if arg.startswith('--filter_attributes=')), None)

    if custom_dimensions_json:
        custom_dimensions_list = parse_json_arg(custom_dimensions_json)
        defaults['customDimensions'] = [CustomDimension(**dim).to_dict() for dim in custom_dimensions_list]

    if filter_attributes_json:
        filter_attributes_list = parse_json_arg(filter_attributes_json)
        defaults['filterAttributes'] = [FilterAttribute(**attr).to_dict() for attr in filter_attributes_list]

    # Assuming get_vectara_client() is a function that initializes and returns a VectaraClient instance
    # vectara_client = vectara_client

    corpus_data = {
        "id": corpus_id,
        "name": name,
        "description": description,
        **defaults
    }#.to_dict()

    try:
        response = vectara_client.create_corpus(corpus_data)
        print(response)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    import sys
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