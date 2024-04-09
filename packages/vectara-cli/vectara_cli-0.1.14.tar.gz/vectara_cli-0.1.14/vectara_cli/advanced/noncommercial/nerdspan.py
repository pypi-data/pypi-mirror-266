# ./vectara-cli/advanced/nerdspan.py

import spacy
import span_marker
from span_marker import SpanMarkerModel
from vectara_cli.core import VectaraClient


class Span:
    def __init__(self, text, customer_id, api_key):
        super().__init__(text)
        self.vectara_client = VectaraClient(customer_id, api_key)
        self.model_mapping = {
            "fewnerdsuperfine": "tomaarsen/span-marker-bert-base-fewnerd-fine-super",
            "multinerd": "tomaarsen/span-marker-mbert-base-multinerd",
            "largeontonote": "tomaarsen/span-marker-roberta-large-ontonotes5",
        }

    def load_model(self, model_name, model_type):
        """
        Load a model given its name and type.
        """
        # Resolve the model name to its full identifier
        full_model_name = self.model_mapping.get(model_name, "")
        if not full_model_name:
            raise ValueError(f"Model name '{model_name}' is not recognized.")
        if model_type == "span_marker":
            self.models[model_name] = SpanMarkerModel.from_pretrained(model_name)
        elif model_type == "spacy":
            nlp = spacy.load("en_core_web_sm", exclude=["ner"])
            nlp.add_pipe("span_marker", config={"model": model_name})
            self.models[model_name] = nlp
        else:
            raise ValueError("Unsupported model type")

    def run_inference(self, model_name):
        """
        Run inference using a specified model.
        """
        if model_name not in self.models:
            raise ValueError("Model not loaded")

        model = self.models[model_name]
        if isinstance(model, SpanMarkerModel):
            return model.predict(self.text)
        elif isinstance(model, spacy.language.Language):
            doc = model(self.text)
            return [(entity.text, entity.label_) for entity in doc.ents]
        else:
            raise ValueError("Unsupported model instance")

    def format_output(self, entities):
        """
        Format the output entities into a string and a list of key-value pairs.
        """
        output_str = f"Entities found in text: {self.text}\n"
        key_value_pairs = []
        for entity in entities:
            if isinstance(entity, tuple):
                # spaCy output
                output_str += f"{entity[0]}: {entity[1]}\n"
                key_value_pairs.append({"span": entity[0], "label": entity[1]})
            else:
                # SpanMarkerModel output
                output_str += (
                    f"{entity['span']}: {entity['label']}, Score: {entity['score']}\n"
                )
                key_value_pairs.append(entity)
        return output_str, key_value_pairs

    def analyze_text(self, model_name):
        """
        Analyze the text with a given model and return formatted outputs.
        """
        entities = self.run_inference(model_name)
        return self.format_output(entities)

    def create_corpus(self, name, description):
        corpus_id = uuid.uuid4().int  # Generates a random corpus ID
        response = self.vectara_client.create_corpus(
            corpus_id=corpus_id,
            name=name,
            description=description,
            dtProvision=int(uuid.uuid1().time),  # Example timestamp
            enabled=True,
            swapQenc=False,
            swapIenc=False,
            textless=False,
            encrypted=False,
            encoderId="default",
            metadataMaxBytes=10000,
            customDimensions=[],
            filterAttributes=[],
        )
        print(f"Corpus creation response: {response}")
        return corpus_id

    def text_chunker(self, text, chunk_size=512):
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def process_and_upload(self, folder_path, model_name, model_type):
        # Create two corpora
        corpus_id_1 = self.create_corpus("Corpus 1", "First corpus for raw uploads")
        corpus_id_2 = self.create_corpus(
            "Corpus 2", "Second corpus for processed uploads"
        )

        # Upload documents from folder to the first corpus
        upload_results = self.vectara_client.index_documents_from_folder(
            corpus_id_1, folder_path, return_extracted_document=True
        )

        for document_id, success, extracted_text in upload_results:
            if not success or extracted_text is None:
                print(
                    f"Skipping document {document_id}, upload failed or no text extracted."
                )
                continue

            # Chunk the text
            chunks = self.text_chunker(extracted_text)

            # Process each chunk and re-upload to the second corpus
            self.load_model(model_name, model_type)
            for chunk in chunks:
                self.text = chunk  # Update the Span text to the current chunk
                _, key_value_pairs = self.analyze_text(model_name)
                # Convert key-value pairs to a metadata JSON string
                metadata_json = json.dumps({"entities": key_value_pairs})
                # Index processed chunk into the second corpus
                self.vectara_client.index_text(
                    corpus_id_2, document_id, chunk, metadata_json=metadata_json
                )

        return corpus_id_1, corpus_id_2


# # Example usage
# if __name__ == "__main__":
#     text = "Amelia Earhart flew her single engine Lockheed Vega 5B across the Atlantic to Paris."
#     span = Span(text)

#     # Load and run SpanMarkerModel
#     span.load_model("tomaarsen/span-marker-mbert-base-multinerd", "span_marker")
#     output_str, key_value_pairs = span.analyze_text("tomaarsen/span-marker-mbert-base-multinerd")
#     print(output_str)
#     print(key_value_pairs)

#     # Load and run spaCy model with span_marker pipeline
#     span.load_model("tomaarsen/span-marker-roberta-large-ontonotes5", "spacy")
#     output_str, key_value_pairs = span.analyze_text("tomaarsen/span-marker-roberta-large-ontonotes5")
#     print(output_str)
#     print(key_value_pairs)
