import sys
from vectara_cli.helptexts.help_text import print_upload_folder_help

def main(args, vectara_client):
    """
    Main function for uploading and indexing all documents in a specified folder.
    
    Args:
        args: Command line arguments passed to the upload-folder command.
    """
    if len(args) != 2:
            print_upload_folder_help()
            sys.exit(1)

    corpus_id, folder_path = args

    try:
        corpus_id = int(corpus_id)
    except ValueError:
        print("Error: Corpus ID must be an integer.")
        sys.exit(1)

    results = vectara_client.index_documents_from_folder(corpus_id, folder_path)

    for document_id, success, extracted_text in results:
        if success:
            print(f"Successfully indexed document: {document_id}")
            if extracted_text:
                print(f"Extracted Text: {extracted_text[:200]}...") 
        else:
            print(f"Failed to index document: {document_id}")

if __name__ == "__main__":
    main(sys.argv)