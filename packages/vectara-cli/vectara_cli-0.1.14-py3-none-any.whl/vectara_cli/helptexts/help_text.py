# ./helptexts/helptext.py

def main_help_text():
    help_text = """
    Usage: vectara-cli <command> [arguments]

    Commands:
    set-api-keys <customer_id> <api_key> - Set the API keys for Vectara client.
    index-document <args> - Index a document in the Vectara platform.
    query <args> - Query the Vectara platform.
    create-corpus <args> - Create a new corpus in the Vectara platform.
    create-corpus-advanced <args> - more administrative control when you create a new corpus in the Vectara platform.
    delete-corpus <args> - Delete a corpus from the Vectara platform.
    span-text <args> - Process text using the span model.
    span-enhance-folder <args> - Enhance documents in a folder using the span model.
    upload-document <args> - Upload a document to the Vectara platform.
    upload-enriched-text <args> - Upload enriched text to the Vectara platform.
    nerdspan-upsert-folder <args> - Process and upload documents in a folder using the nerdspan model.
    rebel-upsert-folder <args> - Perform advanced upsert for a folder using the rebel model.
    create-ui - deploy a special UI for your corpus / data.

    Use 'vectara-cli help' to display this help message.
    """
    print(help_text)
    

def print_index_text_usage():
    """
    Prints detailed usage instructions for the index-text command of vectara-cli.
    """
    usage_text = """
    Usage: vectara-cli index-text <corpus_id> <document_id> <text> <context> <metadata_json> [custom_dims...]

    This command allows you to index a text document into the Vectara platform, with optional custom dimensions for advanced indexing strategies.

    Parameters:
    - corpus_id: The unique identifier for the corpus where the document will be indexed. A corpus represents a collection of documents.
    - document_id: A unique identifier for the document being indexed. This ID helps in identifying the document within the corpus.
    - text: The actual text content of the document that you want to index.
    - context: Additional context or information about the document. This could be a summary, tags, or any other relevant information that helps in categorizing or understanding the document.
    - metadata_json: A JSON string containing metadata about the document. This could include information like the author, publish date, document type, etc. The metadata should be formatted as a valid JSON string.
    - custom_dims (optional): Custom dimensions for the document, specified as key=value pairs. These dimensions allow for fine-grained control over how documents are indexed and retrieved.

    Example:
    vectara-cli index-text 12345 67890 "This is the text of the document." "Summary of the document" '{"author":"John Doe", "publishDate":"2024-01-01"}' relevance=0.9 freshness=0.8

    In the above example, 'relevance' and 'freshness' are custom dimensions provided for the document, with their respective values.

    Note:
    - Ensure that the metadata_json is properly formatted as a JSON string. Incorrect formatting can lead to errors in indexing.
    - Custom dimensions should be provided after the mandatory parameters. Each custom dimension should be in the format 'name=value', where 'value' is a numeric value.

    For more information and advanced usage, refer to the Vectara documentation or use the help command.
    """
    print(usage_text.strip())

def print_create_corpus_advanced_help():
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

def print_create_corpus_help():
    help_text = """
Usage: vectara create-corpus <name> <description> [options]

Arguments:
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
        vectara create-corpus "My Corpus" "A corpus containing documents on topic XYZ"

    Create a corpus with custom dimensions and filter attributes:
        vectara create-corpus "Research Papers" "Corpus for academic research papers" --custom_dimensions '{"subject": "Computer Science", "year": "2024"}' --filter_attributes '{"author": "John Doe"}'

    Create a public corpus:
        vectara create-corpus "Public Data" "A corpus of public datasets" --public true

Note:
    - Ensure that the JSON strings for --custom_dimensions and --filter_attributes are properly formatted. Incorrect JSON format will result in an error.
    - The --public option is a simple flag. If you want the corpus to be public, include '--public true' in your command. The default behavior is to create a private corpus if the flag is not specified.
"""
    print(help_text)

def print_index_document_help():

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


def show_delete_corpus_help():
    """
    Displays help information for the delete_corpus.py script.
    """
    help_text = """
    delete_corpus.py Help
    ======================

    Purpose:
    --------
    This script is designed to delete a corpus from the Vectara platform. 
    A corpus is a collection of documents that you can search and analyze. 
    Deleting a corpus will remove all its documents and associated data.

    Usage:
    ------
    vectara delete-corpus.py <corpus_id>

    Arguments:
    ----------
    - corpus_id: The unique identifier for the corpus you wish to delete. 
                 This is a required argument.

    Example:
    --------
    To delete a corpus with the ID 12345, you would use the following command:

    vectara delete-corpus 12345

    Note:
    -----
    Before using this script, ensure you have configured your Vectara API keys 
    correctly. The script retrieves your customer ID and API key from the 
    configuration to authenticate your request.

    If the corpus is deleted successfully, you will see a confirmation message. 
    If there is an error, an appropriate error message will be displayed instead.

    For more information on managing corpora and other functionalities, 
    please refer to the Vectara documentation or the vectara_cli documentation.
    """

    print(help_text)

def print_upload_document_help():
    """
    Prints the help text for the upload_document.py script.
    """
    help_text = """
Vectara CLI Upload Document Help
--------------------------------
The `upload_document.py` script is used to upload documents to a specified corpus within the Vectara platform.

Usage:
    vectara-cli upload-document <corpus_id> <file_path> [document_id]

Parameters:
    <corpus_id>    The ID of the corpus to which the document will be uploaded. This is a required parameter.
    <file_path>    The path to the document file that you want to upload. This is a required parameter.
    [document_id]  An optional parameter that specifies the document ID. If not provided, Vectara will generate one.

Examples:
    1. Upload a document without specifying a document ID:
       vectara-cli upload-document 12345 /path/to/document.pdf

    2. Upload a document with a specified document ID:
       vectara-cli upload-document 12345 /path/to/document.pdf my-document-id

Note:
- The document ID is optional. If not provided, Vectara generates a unique ID for the document.
- Ensure that the corpus ID and API keys are correctly configured before uploading documents.
- Supported document formats include PDF, DOCX, PPTX, and TXT files.

For more information, visit the Vectara documentation at https://docs.vectara.com.
    """
    print(help_text)

if __name__ == "__main__":
    print("This script is intended to be used as a module and should not be executed directly.")
    