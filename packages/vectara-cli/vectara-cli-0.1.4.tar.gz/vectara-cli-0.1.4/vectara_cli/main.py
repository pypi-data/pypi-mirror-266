# ./vectara_cli/main.py

from .core import VectaraClient , ConfigManager
from .advanced.noncommercial.nerdspan import Span
from .advanced.noncommercial.rebel import Rebel
import json
import sys
import os

def main():
    if command == "set-api-keys":
        if len(args) != 3:
            print("Usage: vectara-cli set-api-keys customer_id api_key")
            return
        customer_id = args[1]
        api_key = args[2]
        ConfigManager.set_api_keys(customer_id, api_key)
        print("API keys set successfully.")
        return
    try:
        customer_id, api_key = ConfigManager.get_api_keys()
    except ValueError as e:
        print(e)
        return

    vectara_client = VectaraClient(customer_id, api_key)

    if command == "index-document":
        if len(args) < 6:
            print("Usage: vectara-cli index-document corpus_id document_id title metadata_json section_text")
            return
        corpus_id = args[1]
        document_id = args[2]
        title = args[3]
        metadata = json.loads(args[4])
        section_text = args[5]
        response, success = vectara_client.index_document(corpus_id, document_id, title, metadata, section_text)
        if success:
            print("Document indexed successfully.")
        else:
            print("Document indexing failed.", response)
    elif command == "query":
        if len(args) < 4:
            print("Usage: vectara-cli query query_text num_results corpus_id")
            return
        query_text = args[1]
        num_results = int(args[2])
        corpus_id = args[3]
        response = vectara_client.query(query_text, num_results, corpus_id)
        print(response)
    elif command == "create-corpus":
        if len(args) < 3:
            print("Usage: vectara-cli create-corpus corpus_id name")
            return
        corpus_id = args[1]
        name = args[2]
        response = vectara_client.create_corpus(corpus_id, name, "Description", 1234567890, True, False, False, False, False, "default", 10000, [], [])
        print(response)
    elif command == "delete-corpus":
        if len(args) < 2:
            print("Usage: vectara-cli delete-corpus corpus_id")
            return
        corpus_id = args[1]
        response, success = vectara_client.delete_corpus(corpus_id)
        if success:
            print("Corpus deleted successfully.")
        else:
            print("Failed to delete corpus:", response)
    elif command == "upload-document":
        if len(args) < 4:
            print("Usage: vectara-cli upload-document corpus_id file_path document_id")
            return
        corpus_id = args[1]
        file_path = args[2]
        document_id = args[3]  # Optional, pass None if not provided
        metadata = {}  # Extend to accept metadata as an argument if needed
        try:
            response, status = vectara_client.upload_document(corpus_id, file_path, document_id, metadata)
            print("Upload successful:", response)
        except Exception as e:
            print("Upload failed:", str(e))
    elif command == "span-text":
        if len(args) < 5:
            print("Usage: vectara-cli process-text text model_name model_type")
            return
        text = args[1]
        model_name = args[2]
        model_type = args[3]
        span = Span(text, customer_id, api_key)
        span.load_model(model_name, model_type)
        output_str, key_value_pairs = span.analyze_text(model_name)
        print(output_str)
        print(key_value_pairs)
    elif command == "nerdspan-upsert-folder":
        if len(args) < 5:
            print("Usage: vectara-cli process-and-upload folder_path model_name model_type")
            return
        folder_path = args[1]
        model_name = args[2]
        model_type = args[3]
        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return
        span = Span("", customer_id, api_key)  
        corpus_id_1, corpus_id_2 = span.process_and_upload(folder_path, model_name, model_type)
        print(f"Documents processed and uploaded. Raw uploads in Corpus ID: {corpus_id_1}, Processed uploads in Corpus ID: {corpus_id_2}")
    elif command == "rebel-upsert-folder":
        if len(args) < 4:
            print("Usage: vectara-cli advanced-upsert-folder folder_path corpus_id_1 corpus_id_2")
            return
        folder_path = args[1]
        corpus_id_1 = args[2]
        corpus_id_2 = args[3]
        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return
        rebel = Rebel()
        rebel.advanced_upsert_folder(vectara_client, corpus_id_1, corpus_id_2, folder_path)
        print(f"Advanced processing and upsert completed for folder: {folder_path}")
    elif command == "upload-enriched-text":
        if len(args) < 6:
            print("Usage: vectara-cli upload-enriched-text corpus_id document_id model_name text")
            return
        corpus_id = args[1]
        document_id = args[2]
        model_name = args[3]
        text = " ".join(args[4:])
        enterprise_span = EnterpriseSpan(model_name)
        predictions = enterprise_span.predict(text)
        enterprise_span.upload_enriched_text(corpus_id, document_id, text, predictions)
        print("Enriched text uploaded successfully.")
    elif command == "span-enhance-folder":
        if len(args) < 5:
            print("Usage: vectara-cli span-enhance-folder corpus_id_1 corpus_id_2 model_name folder_path")
            return
        corpus_id_1 = args[1]
        corpus_id_2 = args[2]
        model_name = args[3]
        folder_path = args[4]
        if not os.path.isdir(folder_path):
            print(f"The specified folder path does not exist: {folder_path}")
            return
        enterprise_span = EnterpriseSpan(model_name)
        enterprise_span.span_enhance(corpus_id_1, corpus_id_2, folder_path)
        print(f"Documents in {folder_path} enhanced and uploaded to corpora: {corpus_id_1} (plain), {corpus_id_2} (enhanced)")
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
