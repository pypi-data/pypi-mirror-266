# ./commands/create_corpus_advanced.py

# create_corpus.py

# from vectara_cli.utils import get_vectara_client
import json
import sys
from vectara_cli.data.corpus_data import CorpusData
from vectara_cli.data.defaults import CorpusDefaults
from vectara_cli.helptexts.help_text import print_create_corpus_advanced_help

def parse_json_arg(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")

def parse_args(args):
    if len(args) < 2:
        print_create_corpus_advanced_help()
        sys.exit(1)

    name = args[0]
    description = args[1]
    options = CorpusDefaults.get_defaults()

    for arg in args[2:]:
        if arg.startswith('--custom_dimensions='):
            options["customDimensions"] = parse_json_arg(arg.split('=', 1)[1])
        elif arg.startswith('--filter_attributes='):
            options["filterAttributes"] = parse_json_arg(arg.split('=', 1)[1])
        elif arg.startswith('--encoder_id='):
            options["encoderId"] = int(arg.split('=', 1)[1])
        elif arg.startswith('--metadata_max_bytes='):
            options["metadataMaxBytes"] = int(arg.split('=', 1)[1])
        elif arg.startswith('--swap_qenc='):
            options["swapQenc"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--swap_ienc='):
            options["swapIenc"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--textless='):
            options["textless"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--encrypted='):
            options["encrypted"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']
        elif arg.startswith('--public='):
            options["public"] = arg.split('=', 1)[1].lower() in ['true', '1', 't', 'y', 'yes']

    return name, description, options

def main(args, vectara_client):
    if len(args) < 2:
        print_create_corpus_advanced_help()
        return

    name, description, options = parse_args(args)

    corpus_data = CorpusData(corpus_id=None, name=name, description=description, **options)


    try:
        response = vectara_client.create_corpus(corpus_data.to_dict())
        print(json.dumps(response, indent=4))
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main(sys.argv)