# ./commands/span_text.py

from vectara_cli.advanced.noncommercial.nerdspan import Span
from vectara_cli.utils.config_manager import ConfigManager


def main(args, vectara_client):
    
    if len(args) < 3:
        print("Usage: vectara-cli span-text text model_name model_type")
        return
    # _, text, model_name, model_type = args

    text = args[0]
    model_name = args[1]
    model_type = args[2]

    try:
        span = Span(text, vectara_client, model_name, model_type)
        span.load_model(model_name, model_type)  
        output_str, key_value_pairs = span.analyze_text(model_name, model_type)
        print(output_str)
        print(json.dumps(key_value_pairs))
    except Exception as e:
        print("Error processing text:", str(e))


if __name__ == "__main__":
    import sys

    main(sys.argv)
