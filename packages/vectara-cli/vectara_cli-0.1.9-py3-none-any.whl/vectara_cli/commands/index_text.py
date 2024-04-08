# ./commands/index_text.py

from vectara_cli.core import VectaraClient

def main(args, vectara_client: VectaraClient):
    if len(args) < 6:
        print("Usage: vectara-cli index-text corpus_id document_id text context metadata_json")
        return
    corpus_id = args[1]
    document_id = args[2]
    text = args[3]
    context = args[4]
    metadata_json = args[5]
    custom_dims = []  # This example does not cover custom dimensions input, but you can extend it.

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
        print(e)

if __name__ == "__main__":
    print("This script is intended to be used as a module.")