import json
from vectara_cli.core import VectaraClient

def print_help():
    help_text = """
Usage: vectara index-document corpus_id document_id title metadata_json section_text

Arguments:
- corpus_id: The ID of the corpus where the document will be indexed. (integer)
- document_id: A unique identifier for the document. (string)
- title: The title of the document. (string)
- metadata_json: A JSON string containing metadata for the document. Ensure proper escaping. (string)
- section_text: The main content of the document. (string)

Example:
vectara index-document 123 001 "My Document Title" "{\\"author\\":\\"John Doe\\",\\"year\\":2022}" "This is the main content of the document."

This command indexes a document with the specified title, metadata, and content into the corpus with ID 123.
"""
    print(help_text)

def main(args, vectara_client):
    if len(args) < 6:
        print_help()
        return
    corpus_id = int(args[1])
    document_id = args[2]
    title = args[3]
    metadata_json = args[4]
    section_text = args[5]
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding metadata_json: {e}")
        return
    response, success = vectara_client.index_document(
        corpus_id, document_id, title, metadata, section_text
    )

    if success:
        print("Document indexed successfully.")
    else:
        print(f"Document indexing failed: {response}")

if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
