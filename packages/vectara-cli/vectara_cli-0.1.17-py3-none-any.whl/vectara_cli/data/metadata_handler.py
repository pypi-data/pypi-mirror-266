# ./metadata_handler.py

import json

class MetaDataJson:
    """
    Handles conversion of metadata from a JSON string to a dictionary.
    """
    @staticmethod
    def from_string(metadata_json):
        try:
            return json.loads(metadata_json)
        except json.JSONDecodeError:
            raise ValueError("metadata_json must be a valid JSON string.")

class MetaDataDefault:
    """
    Provides default metadata when none is provided.
    """
    @staticmethod
    def get_default():
        return {
            "author": "Unknown",
            "publishDate": "Unknown",
            "documentType": "Unknown",
            "createdBy": "Tonic-AI",
            "using": "vectara-cli",
            "website":"https://www.tonic-ai.com"
        }