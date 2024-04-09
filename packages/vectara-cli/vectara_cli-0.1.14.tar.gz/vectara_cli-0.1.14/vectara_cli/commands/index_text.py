# ./commands/index_text.py
from vectara_cli.helptexts.help_text import print_index_text_usage
from vectara_cli.data.custom_dimension import TextCustomDimensions
from vectara_cli.data.metadata_handler import MetaDataJson, MetaDataDefault
# from vectara_cli.defaults import DefaultTextCustomDimensions
import json

def parse_custom_dimensions(args):
    """
    Parses custom dimensions from command line arguments.
    Expected format for each custom dimension is 'name=value'.
    Returns a list of TextCustomDimensions instances.
    """
    custom_dims = []
    for arg in args:
        if '=' in arg:
            name, value_str = arg.split('=', 1)
            try:
                value = float(value_str)
                custom_dims.append(TextCustomDimensions(name, value))
            except ValueError:
                raise ValueError(f"Invalid value for custom dimension '{name}': must be a float.")
    return custom_dims

def main(args, vectara_client):
    if len(args) < 5:
        print_index_text_usage()
        return
    corpus_id, document_id, text, context, metadata_json = args[:5]
    metadata_json = args[4] if len(args) > 4 else json.dumps(MetaDataDefault.get_default())
    additional_args = args[5:] if len(args) > 5 else []

    custom_dims = parse_custom_dimensions(additional_args)
    custom_dims_dicts = [dim.to_dict() for dim in custom_dims]
    metadata_dict = MetaDataJson.from_string(metadata_json)
       
    try:
        response = vectara_client.index_text(
            corpus_id=corpus_id,
            document_id=document_id,
            text=text,
            context=context,
            metadata_json=json.dumps(metadata_dict),
            custom_dims=custom_dims_dicts
        )
        print("Indexing response:", response)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("This script is intended to be used as a module and should not be executed directly.")

# def main(args, vectara_client):
#     if len(args) < 5:
#         print_index_text_usage()
#         return
#     corpus_id, document_id, text, context, metadata_json = args[:5]
#     custom_dims = [] 
#     custom_dims = [dim.to_dict() for dim in DefaultCustomDimensions.get_default_dimensions()]
# # ## :      Extend this to accept custom dimensions from command line arguments 
#     try:
#         response = vectara_client.index_text(
#             corpus_id=corpus_id,
#             document_id=document_id,
#             text=text,
#             context=context,
#             metadata_json=metadata_json,
#             custom_dims=custom_dims
#         )
#         print("Indexing response:", response)
#     except ValueError as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     print("This script is intended to be used as a module and should not be executed directly.")