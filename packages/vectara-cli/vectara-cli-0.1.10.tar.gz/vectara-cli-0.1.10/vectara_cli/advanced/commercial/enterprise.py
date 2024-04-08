# ./advanced/commercial/enterpise.py

import logging
from typing import List, Any, Dict
from vectara_cli.core import VectaraClient
import span_marker
from span_marker import SpanMarkerModel
import random
import string


class EnterpriseSpan:
    """
    EnterpriseSpan class for handling advanced text processing and analysis in enterprise applications.
    This class wraps around the SpanMarkerModel for keyphrase extraction and adds enterprise-level features
    such as detailed logging, error handling, and customization options, including an easy way to specify models.
    """

    MODEL_MAP = {
        "keyphrase": "tomaarsen/span-marker-bert-base-uncased-keyphrase-inspec",
        "science": "tomaarsen/span-marker-bert-base-ncbi-disease",
    }

    def __init__(self, model_name: str):
        """
        Initializes the EnterpriseSpan model with a given model name.

        Parameters:
            model_name (str): User-friendly name or identifier for the pretrained model.
        """
        self.model_name = model_name
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_path = self._get_model_path()
        self.model = self._load_model()
        self.vectara_client = VectaraClient()

    def _get_model_path(self) -> str:
        """
        Translates the user-friendly model name to its specific identifier.

        Returns:
            str: The model identifier.
        """
        if self.model_name in self.MODEL_MAP:
            return self.MODEL_MAP[self.model_name]
        else:
            self.logger.warning(
                f"Model name {self.model_name} not recognized. Attempting to use it as a direct path or identifier."
            )
            return self.model_name

    def _load_model(self) -> SpanMarkerModel:
        """
        Loads the SpanMarkerModel from the specified path.

        Returns:
            SpanMarkerModel: The loaded model.
        """
        try:
            model = SpanMarkerModel.from_pretrained(self.model_path)
            self.logger.info(f"Model loaded successfully from {self.model_path}")
            return model
        except Exception as e:
            self.logger.error(f"Failed to load model from {self.model_path}: {e}")
            raise

    def predict(self, text: str) -> List[Dict[str, Any]]:
        """
        Runs inference on the given text and returns the extracted entities.

        Parameters:
            text (str): The input text for which to predict entities.

        Returns:
            List[Dict[str, Any]]: A list of entities with their respective information.
        """
        try:
            entities = self.model.predict(text)
            self.logger.info(f"Prediction successful for input text: {text[:30]}...")
            return entities
        except Exception as e:
            self.logger.error(
                f"Prediction failed for input text: {text[:30]}... Error: {e}"
            )
            raise

    def format_predictions(self, predictions: List[Dict[str, Any]]) -> str:
        """
        Formats the predictions into a structured string that can be easily read and used.

        Parameters:
            predictions (List[Dict[str, Any]]): The list of entities predicted by the model.

        Returns:
            str: A formatted string of predictions.
        """
        formatted = ""
        for pred in predictions:
            formatted += (
                f"{pred['entity_group']}: {pred['word']} (Score: {pred['score']:.2f})\n"
            )
        return formatted.strip()

    def format_predictions(self, predictions: List[Dict[str, Any]]) -> str:
        formatted = ""
        for pred in predictions:
            formatted += (
                f"{pred['entity_group']}: {pred['word']} (Score: {pred['score']:.2f})\n"
            )
        return formatted.strip()

    def generate_metadata(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        metadata = {}
        for pred in predictions:
            key = pred["entity_group"]
            if key not in metadata:
                metadata[key] = []
            metadata[key].append(pred["word"])
        return metadata

    def text_chunk(self, text, chunk_size=512):
        """
        Breaks down text into smaller chunks of a specified size.

        Parameters:
            text (str): The text to be chunked.
            chunk_size (int): The maximum size of each text chunk.

        Returns:
            List[str]: A list of text chunks.
        """
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def upload_enriched_text(self, corpus_id, document_id, text, predictions):
        metadata = self.generate_metadata(predictions)
        enriched_text = self.format_predictions(predictions) + "\n\n" + text
        try:
            response, success = self.vectara_client.index_document(
                corpus_id, document_id, "Enriched Text", metadata, enriched_text
            )
            if success:
                self.logger.info("Enriched document uploaded successfully.")
            else:
                self.logger.error("Failed to upload enriched document.")
        except Exception as e:
            self.logger.error(f"An error occurred while uploading the document: {e}")

    def span_enhance(self, corpus_id_1, corpus_id_2, folder_path):
        """
        Enhances documents using the SpanMarkerModel and uploads them to Vectara.

        Args:
            corpus_id_1 (int): ID for the first corpus (plain text).
            corpus_id_2 (int): ID for the second corpus (enhanced text).
            folder_path (str): Path to the folder containing documents.
        """
        # Create two new corpora
        corpus_id_1 = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        corpus_id_2 = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        self.vectara_client.create_corpus(
            corpus_id=corpus_id_1,
            name=f"{corpus_id_1}_Plain",
            description="Plain Document Index",
        )
        self.vectara_client.create_corpus(
            corpus_id=corpus_id_2,
            name=f"{corpus_id_2}_Enhanced",
            description="Enhanced Document Index",
        )

        results = self.vectara_client.index_documents_from_folder(
            corpus_id_1, folder_path, return_extracted_document=True
        )

        for document_id, success, extracted_text in results:
            if not success or not extracted_text:
                continue
            text_chunks = self.text_chunk(extracted_text)

            for chunk in text_chunks:
                predictions = self.predict(chunk)
                self.upload_enriched_text(corpus_id_2, document_id, chunk, predictions)


# # Example usage
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#     enterprise_model = EnterpriseSpan("keyphrase")
#     text = "Example text for processing."
#     try:
#         entities = enterprise_model.predict(text)
#         formatted_predictions = enterprise_model.format_predictions(entities)
#         print("Predictions:\n", formatted_predictions)
#         # Prepend formatted predictions to the original text
#         complete_text = f"Extracted Information:\n{formatted_predictions}\n\nOriginal Text:\n{text}"
#         print("\nComplete Text:\n", complete_text)
#     except Exception as e:
#         print(f"An error occurred: {e}")