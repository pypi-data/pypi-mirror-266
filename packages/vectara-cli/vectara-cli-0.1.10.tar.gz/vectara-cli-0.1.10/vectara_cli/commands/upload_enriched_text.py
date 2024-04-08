# ./commands/upload_enriched_text.py

from vectara_cli.config_manager import ConfigManager
from vectara_cli.advanced.commercial.enterprise import EnterpriseSpan


def main(args, vectara_client):
    if len(args) < 6:
        print(
            "Usage: vectara-cli upload-enriched-text corpus_id document_id model_name text"
        )
        return

    corpus_id = args[1]
    document_id = args[2]
    model_name = args[3]
    text = " ".join(args[4:])

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        enterprise_span = EnterpriseSpan(model_name, customer_id, api_key)
        predictions = enterprise_span.predict(text)
        enterprise_span.upload_enriched_text(corpus_id, document_id, text, predictions)
        print("Enriched text uploaded successfully.")
    except Exception as e:
        print("Failed to upload enriched text:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
