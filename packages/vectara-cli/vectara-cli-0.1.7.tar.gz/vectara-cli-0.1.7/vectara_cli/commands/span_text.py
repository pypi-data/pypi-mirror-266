# ./commands/span_text.py

from vectara_cli.advanced.noncommercial.nerdspan import Span
from vectara_cli.config_manager import ConfigManager


def main(args, vectara_client):
    if len(args) < 5:
        print("Usage: vectara-cli process-text text model_name model_type")
        return

    text = args[1]
    model_name = args[2]
    model_type = args[3]

    try:
        customer_id, api_key = ConfigManager.get_api_keys()
        span = Span(text, customer_id, api_key)
        span.load_model(model_name, model_type)
        output_str, key_value_pairs = span.analyze_text(model_name)
        print(output_str)
        print(key_value_pairs)
    except Exception as e:
        print("Error processing text:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
