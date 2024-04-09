# vectara-cli\advanced\non-commercial\rebel.py

import torch
import torch.nn as nn 
from torch.nn import CrossEntropyLoss, BCEWithLogitsLoss
from transformers import DebertaV2Config, DebertaV2PreTrainedModel, DebertaV2Model
from transformers.models.deberta_v2.modeling_deberta_v2 import (
    ContextPooler,
    StableDropout,
)
from transformers.file_utils import ModelOutput
from transformers import pipeline
from dataclasses import dataclass
from typing import Optional, Tuple
from vectara_cli.core import VectaraClient


@dataclass
class TXNLIClassifierOutput(ModelOutput):
    loss: Optional[torch.FloatTensor] = None
    logits: torch.FloatTensor = None
    logits_xnli: torch.FloatTensor = None
    hidden_states: Optional[Tuple[torch.FloatTensor]] = None
    attentions: Optional[Tuple[torch.FloatTensor]] = None


class DebertaV2ForTripletClassification(DebertaV2PreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.num_labels = getattr(config, "num_labels", 2)
        self.deberta = DebertaV2Model(config)
        self.pooler = ContextPooler(config)
        self.classifier = nn.Linear(self.pooler.output_dim, self.num_labels)
        drop_out = getattr(config, "cls_dropout", None)
        self.dropout = StableDropout(
            drop_out if drop_out is not None else config.hidden_dropout_prob
        )
        self.classifier_xnli = nn.Linear(self.pooler.output_dim, 3)
        self.post_init()

    def forward(
        self,
        input_ids=None,
        attention_mask=None,
        token_type_ids=None,
        position_ids=None,
        inputs_embeds=None,
        labels=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
    ):
        return_dict = (
            return_dict if return_dict is not None else self.config.use_return_dict
        )
        outputs = self.deberta(
            input_ids,
            token_type_ids=token_type_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            inputs_embeds=inputs_embeds,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )
        encoder_layer = outputs[0]
        pooled_output = self.pooler(encoder_layer)
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        logits_xnli = self.classifier_xnli(pooled_output)
        loss = None
        if labels is not None:
            if labels.dtype != torch.bool:
                loss_fct = CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))
            else:
                loss_fct = BCEWithLogitsLoss()
                loss = loss_fct(logits_xnli.view(-1, 3), labels.view(-1).long())
        if not return_dict:
            output = (logits,) + outputs[2:]
            return ((loss,) + output) if loss is not None else output
        return TXNLIClassifierOutput(
            loss=loss,
            logits=logits,
            logits_xnli=logits_xnli,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )


class Rebel:
    def __init__(self, model_path="microsoft/deberta-v2-xlarge"):
        self.config = DebertaV2Config.from_pretrained(model_path)
        self.model = DebertaV2ForTripletClassification(self.config)
        self.triplet_extractor = pipeline(
            "text2text-generation",
            model="Babelscape/rebel-large",
            tokenizer="Babelscape/rebel-large",
        )

    def extract_triplets(self, text):
        triplets = []
        relation, subject, relation, object_ = "", "", "", ""
        text = text.strip()
        current = "x"
        for token in (
            text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split()
        ):
            if token == "<triplet>":
                current = "t"
                if relation != "":
                    triplets.append(
                        {
                            "head": subject.strip(),
                            "type": relation.strip(),
                            "tail": object_.strip(),
                        }
                    )
                    relation = ""
                subject = ""
            elif token == "<subj>":
                current = "s"
                if relation != "":
                    triplets.append(
                        {
                            "head": subject.strip(),
                            "type": relation.strip(),
                            "tail": object_.strip(),
                        }
                    )
                object_ = ""
            elif token == "<obj>":
                current = "o"
                relation = ""
            else:
                if current == "t":
                    subject += " " + token
                elif current == "s":
                    object_ += " " + token
                elif current == "o":
                    relation += " " + token
        if subject != "" and relation != "" and object_ != "":
            triplets.append(
                {
                    "head": subject.strip(),
                    "type": relation.strip(),
                    "tail": object_.strip(),
                }
            )
        return triplets

    def extract_text(self, text):
        extracted_text = self.triplet_extractor.tokenizer.batch_decode(
            [
                self.triplet_extractor(text, return_tensors=True, return_text=True)[0][
                    "generated_token_ids"
                ]
            ]
        )[
            0
        ]  # return text true so the text chunk is directly useable.
        return extracted_text

    def forward_pass(self, **kwargs):
        # Perform forward pass with the model
        return self.model(**kwargs)

    def chunk_text(self, text, chunk_size=512):
        """
        Splits the text into chunks of a specified size.

        Args:
            text (str): The text to be chunked.
            chunk_size (int): The desired size of each text chunk.

        Returns:
            list: A list of text chunks.
        """
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    def extract_keywords(self, model_output):
        """
        Extracts keywords or metadata from the model's output. Placeholder implementation.

        Args:
            model_output: The output from the model's forward pass.

        Returns:
            dict: A dictionary representing the extracted metadata.
        """
        keywords = []
        for triplet in self.extract_triplets(model_output):
            keywords.append(f"{triplet['head']}:{triplet['type']}:{triplet['tail']}")
        return {"keywords": keywords}

    def advanced_upsert_folder(
        self, vectara_client: VectaraClient, corpus_id_1, corpus_id_2, folder_path
    ):
        """
        Handles the creation of two corpora, indexing documents, and uploading text chunks with metadata.

        Args:
            vectara_client (VectaraClient): An instance of the VectaraClient to interact with the Vectara API.
            corpus_id_1 (int): The ID of the first corpus.
            corpus_id_2 (int): The ID of the second corpus.
            folder_path (str): The path to the folder containing documents to be indexed.
        """
        # Step 1: Create two corpora
        corpus_id_1 = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        corpus_id_2 = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        vectara_client.create_corpus(
            corpus_id=corpus_id_1,
            name="{corpus_id_1}_Plain",
            description="Plain Document Index for ",
        )
        vectara_client.create_corpus(
            corpus_id=corpus_id_2,
            name="{corpus_id_2}_Advanced",
            description="Second corpus",
        )

        # Step 2: Index documents from folder into the first corpus and get plain text
        results = vectara_client.index_documents_from_folder(
            corpus_id_1, folder_path, return_extracted_document=True
        )

        for document_id, success, extracted_text in results:
            if not success or not extracted_text:
                print(
                    f"Skipping document {document_id} due to failure in extraction or indexing."
                )
                continue

            # Step 3: Chunk plain text into sized text chunks (assuming a function to do this)
            text_chunks = self.chunk_text(extracted_text)

            for chunk in text_chunks:
                output = self.forward_pass(text=chunk)
                metadata = self.extract_keywords(output)

                vectara_client.index_document(
                    corpus_id_2,
                    document_id,
                    title="Chunk Title",
                    metadata=metadata,
                    section_text=chunk,
                )

        return corpus_id_1, corpus_id_2


# # Example usage
# advanced = Advanced()
# # For triplet extraction
# triplets = advanced.extract_triplets("Punta Cana is a resort town in the municipality of Higuey, in La Altagracia Province, the eastern most province of the Dominican Republic")
# print(triplets)
# # For classification/forward pass (fill in the actual arguments)
# # output = advanced.forward_pass(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
