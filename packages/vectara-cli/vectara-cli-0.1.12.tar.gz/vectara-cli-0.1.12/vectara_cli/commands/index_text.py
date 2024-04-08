# ./commands/index_text.py
from vectara_cli.helptexts.help_text import print_index_text_usage


def main(args, vectara_client):
    if len(args) < 5:
        print_index_text_usage()
        return
    corpus_id, document_id, text, context, metadata_json = args[:5]
    custom_dims = []  # This could be extended to support custom dimensions passed as arguments.
    try:
        response = vectara_client.index_text(
            corpus_id=corpus_id,
            document_id=document_id,
            text=text,
            context=context,
            metadata_json=metadata_json,
            custom_dims=custom_dims
        )
        print("Indexing response:", response)
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("This script is intended to be used as a module and should not be executed directly.")