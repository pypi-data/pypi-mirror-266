# ./vectara-cli/core.py

import requests
import json
import os
import logging
from .corpus_data import CorpusData
from .defaults import CorpusDefaults

class VectaraClient:
    def __init__(self, customer_id, api_key):
        self.base_url = "https://api.vectara.io"
        self.customer_id = str(customer_id)
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "customer-id": str(customer_id),
            "x-api-key": api_key,
        }

    def index_text(
        self,
        corpus_id,
        document_id,
        text,
        context="",
        metadata_json="{}",
        custom_dims=None,
        timeout=30
    ):
        if custom_dims is None:
            custom_dims = []
        try:
            metadata_json_obj = json.loads(metadata_json)  # Ensure metadata_json is a valid JSON string
        except json.JSONDecodeError:
            raise ValueError("metadata_json must be a valid JSON string.")
        
        corpus_id = str(corpus_id)
        url = f"{self.base_url}/v1/core/index"
        payload = {
            "customerId": self.customer_id,
            "corpusId": corpus_id,
            "document": {
                "documentId": document_id,
                "metadataJson": json.dumps(metadata_json_obj),
                "parts": [
                    {
                        "text": text,
                        "context": context,
                        "metadataJson": json.dumps(metadata_json_obj),
                        "customDims": custom_dims,
                    }
                ],
                "defaultPartContext": context,
                "customDims": custom_dims,
            },
        }
        try:
            response = requests.post(f"{self.base_url}/v1/core/index", headers=self.headers, json=payload, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise

    def query(self, query_text, num_results=10, corpus_id=None):
        url = f"{self.base_url}/v1/query"
        data_dict = {
            "query": [
                {
                    "query": query_text,
                    "num_results": num_results,
                    "corpus_key": [
                        {
                            "customer_id": self.headers["customer-id"],
                            "corpus_id": corpus_id,
                        }
                    ],
                }
            ]
        }

        response = requests.post(url, headers=self.headers, data=json.dumps(data_dict))
        if response.status_code != 200:
            print(f"Query failed with status code: {response.status_code}")
            return None

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            print("Failed to parse JSON response from query.")
            return None

        return self._parse_query_response(response_data)

    def _parse_query_response(self, response_data):
        if "responseSet" in response_data:
            for response_set in response_data["responseSet"]:
                if "response" in response_set:
                    # Extracting and returning the first response for simplicity. Adjust as needed.
                    responses = response_set["response"]
                    return [
                        self._extract_response_info(response) for response in responses
                    ]
        else:
            print("No response set found in the data")
        return []

    @staticmethod
    def _extract_response_info(response):
        return {
            "text": response.get("text", ""),
            "score": response.get("score", 0),
            "metadata": response.get("metadata", []),
            "documentIndex": response.get("documentIndex"),
            "corpusKey": response.get("corpusKey", {}),
        }

    def _get_index_request_json(
        self, corpus_id, document_id, title, metadata, section_text
    ):
        """Constructs the JSON payload for a document to be indexed."""
        document = {
            "document_id": document_id,
            "title": title,
            "metadata_json": json.dumps(metadata),
            "section": [
                {"text": section_text},
            ],
        }

        request = {
            "customer_id": self.customer_id,
            "corpus_id": corpus_id,
            "document": document,
        }

        return json.dumps(request)

    def create_corpus(self, corpus_data: CorpusData):
        url = f"{self.base_url}/v1/create-corpus"
        payload = corpus_data 

        response = requests.post(url, headers=self.headers, data=json.dumps({"corpus": payload}))
        return self._parse_response(response)

    def _parse_response(self, response):
        if response.status_code == 200:
            try:
                response_data = response.json()
                return {"success": True, "data": response_data}
            except ValueError:
                return {"success": False, "error": "Invalid JSON in response"}
        else:
            try:
                error_data = response.json()
                return {"success": False, "error": error_data}
            except ValueError:
                return {"success": False, "error": f"HTTP Error {response.status_code}: {response.text}"}

    def _get_index_request_json(
        self, corpus_id, document_id, title, metadata, section_text
    ):
        # Construct the document payload
        document = {
            "document_id": document_id,
            "title": title,
            "metadata_json": metadata,  # Pass the dictionary directly if the API expects an object
            "section": [
                {"text": section_text},
            ],
        }

        # Construct the full request payload
        request = {
            "customer_id": self.customer_id,
            "corpus_id": corpus_id,
            "document": document,
        }

        # Convert the request payload to JSON and log it
        json_payload = json.dumps(request)
        print("Constructed JSON payload:", json_payload)  # Log the payload for debugging

        return json_payload


    def index_document(self, corpus_id, document_id, title, metadata, section_text):
        """
        Indexes a document to the specified corpus using the Vectara platform.

        Args:
            corpus_id (int): ID of the corpus to which data needs to be indexed.
            document_id (str): Unique identifier for the document.
            title (str): Title of the document.
            metadata (dict): A dictionary containing metadata about the document.
            section_text (str): The main content/text of the document.

        Returns:
            A tuple containing the response and a boolean indicating success or failure.
        """
        idx_address = f"{self.base_url}/v1/index"
        metadata_json = json.dumps(metadata)  # Convert metadata to a JSON string

        payload = {
            "customerId": self.customer_id,
            "corpusId": corpus_id,
            "document": {
                "documentId": document_id,
                "title": title,
                "metadataJson": metadata_json, 
                "sections": [{
                    "text": section_text
                }]
            }
        }

        try:
            response = requests.post(idx_address, headers=self.headers, json=payload) 
            response.raise_for_status()  

            message = response.json()
            if "status" in message and message["status"]["code"] in ("OK", "ALREADY_EXISTS"):
                logging.info("Document indexed successfully or already exists.")
                return message, True
            else:
                logging.error("Indexing failed with status: %s", message.get("status", {}))
                return message.get("status", {}), False
        except requests.exceptions.HTTPError as e:
            logging.error("HTTP error occurred: %s", e)
            return {"code": "HTTP_ERROR", "message": str(e)}, False
        except requests.exceptions.RequestException as e:
            logging.error("Error during requests to Vectara API: %s", e)
            return {"code": "REQUEST_EXCEPTION", "message": str(e)}, False
        except ValueError as e:
            logging.error("Invalid response received from Vectara API: %s", e)
            return {"code": "INVALID_RESPONSE", "message": "The response from Vectara API could not be decoded."}, False


    def index_documents_from_folder(
        self, corpus_id, folder_path, return_extracted_document=False
    ):
        """Indexes all documents in a specified folder.

        Args:
            corpus_id: The ID of the corpus to which the documents will be indexed.
            folder_path: The path to the folder containing the documents.

        Returns:
            A list of tuples, each containing the document ID and a boolean indicating success or failure.
        """
        results = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            document_id = os.path.splitext(file_name)[0]

            try:
                response, status = self.upload_document(
                    corpus_id,
                    file_path,
                    document_id=document_id,
                    return_extracted_document=return_extracted_document,
                )
                extracted_text = (
                    response.get("extractedText", "")
                    if return_extracted_document
                    else None
                )
                results.append((document_id, status == "Success", extracted_text))
                if status != "Success":
                    logging.error(f"Failed to index document {document_id}: {response}")
                else:
                    logging.info(f"Successfully indexed document {document_id}")
            except Exception as e:
                logging.error(f"Error uploading or indexing file {file_name}: {e}")
                results.append((document_id, False, None))

        return results

    def delete_corpus(self, corpus_id):
        """Deletes a specified corpus.

        Args:
            corpus_id: The ID of the corpus to be deleted.

        Returns:
            A tuple containing the response JSON and a boolean indicating success or failure.
        """
        url = f"{self.base_url}/v1/delete-corpus"
        payload = json.dumps({"corpusId": corpus_id})

        try:
            response = requests.post(url, headers=self.headers, data=payload)
            response_json = response.json()

            # Check if the response has a 'status' field and handle accordingly
            if "status" in response_json:
                vectara_status_code = response_json["status"].get("code", "UNKNOWN")
                if vectara_status_code == "OK":
                    logging.info("Corpus deleted successfully.")
                    return response_json, True
                else:
                    logging.error(
                        "Failed to delete corpus with Vectara status code %s, detail: %s",
                        vectara_status_code,
                        response_json["status"].get("statusDetail", "No detail"),
                    )
                    return response_json, False
            else:
                logging.error("Unexpected response format: %s", response.text)
                return response_json, False
        except requests.exceptions.RequestException as e:
            logging.error("Request failed: %s", e)
            return {"error": str(e)}, False

    def upload_document(
        self,
        corpus_id,
        file_path,
        document_id=None,
        metadata=None,
        return_extracted_document=False,
    ):
        """
        Uploads and indexes a document into a corpus.

        Args:
            corpus_id: The ID of the corpus into which the document should be indexed.
            file_path: The path to the file to be uploaded.
            document_id: Optional. The Document ID to assign to the file.
            metadata: Optional. A dictionary containing user-defined metadata to attach to the document.
            return_extracted_document: Optional. If set to true, the server returns the extracted document.

        Returns:
            A tuple containing the server's response as a JSON object and a status message.
        """
        url = f"{self.base_url}/v1/upload?c={self.customer_id}&o={corpus_id}"
        if return_extracted_document:
            url += "&d=true"

        files = {"file": open(file_path, "rb")}
        if metadata is not None:
            files["doc_metadata"] = (None, json.dumps(metadata), "application/json")

        response = requests.post(
            url,
            headers={
                key: val for key, val in self.headers.items() if key != "Content-Type"
            },
            files=files,
        )

        if response.status_code == 200:
            return response.json(), "Success"
        else:
            try:
                error_response = response.json()
                error_message = error_response.get("message", "Unknown error")
            except json.JSONDecodeError:
                error_message = "Failed to parse error response."

            raise Exception(
                f"Failed to upload document: HTTP {response.status_code} - {error_message}"
            )


# # Example usage
# CUSTOMER_ID = "your_customer_id"
# API_KEY = "your_api_key"
# CORPUS_ID = "your_corpus_id"
# FILE_PATH = "/path/to/your/document.pdf"
# DOCUMENT_ID = "unique_document_id"  # Optional
# METADATA = {"author": "Author Name", "title": "Document Title"}  # Optional

# vectara_client = VectaraClient(CUSTOMER_ID, API_KEY)
# try:
#     response = vectara_client.upload_document(CORPUS_ID, FILE_PATH, DOCUMENT_ID, METADATA)
#     print("Upload successful:", response)
# except Exception as e:
#     print("Upload failed:", str(e))

# # Example usage:
# CUSTOMER_ID = "your_customer_id"
# API_KEY = "your_api_key"
# CORPUS_ID = 1  # Example corpus ID, replace with actual corpus ID to delete

# vectara_client = VectaraClient(CUSTOMER_ID, API_KEY)
# response, success = vectara_client.delete_corpus(CORPUS_ID)

# if success:
#     print("Corpus deleted successfully.")
# else:
#     print("Failed to delete corpus:", response)
# # Example usage:
# CUSTOMER_ID = "your_customer_id"
# API_KEY = "your_api_key"
# CORPUS_ID = "your_corpus_id"

# vectara_client = VectaraClient(CUSTOMER_ID, API_KEY)

# # Indexing a document
# metadata = {
#     "book-name": "Another example title",
#     "collection": "Mathematics",
#     "author": "Example Author",
# }
# section_text = "The answer to the ultimate question of life, the universe, and everything is 42."
# document_id = "doc-id-2"
# title = "Another Example Title"

# response, success = vectara_client.index_document(CORPUS_ID, document_id, title, metadata, section_text)
# if success:
#     print("Document indexed successfully.")
# else:
#     print("Document indexing failed.", response)

# # Example usage:
# CUSTOMER_ID = "your_customer_id"
# API_KEY = "your_api_key"

# vectara_client = VectaraClient(CUSTOMER_ID, API_KEY)

# # Creating a corpus
# create_corpus_response = vectara_client.create_corpus(
#     corpus_id=123456789,
#     name="Example Corpus",
#     description="This is an example corpus.",
#     dtProvision=1234567890,
#     enabled=True,
#     swapQenc=False,
#     swapIenc=False,
#     textless=False,
#     encrypted=False,
#     encoderId="default",
#     metadataMaxBytes=10000,
#     customDimensions=[
#         {"name": "dimension1", "description": "First custom dimension", "servingDefault": 1.0, "indexingDefault": 1.0}
#     ],
#     filterAttributes=[
#         {"name": "filter1", "description": "First filter attribute", "indexed": True, "type": "FILTER_ATTRIBUTE_TYPE__UNDEFINED", "level": "FILTER_ATTRIBUTE_LEVEL__UNDEFINED"}
#     ]
# )
# print(create_corpus_response)
# # Example usage:
# CUSTOMER_ID = "your_customer_id"
# API_KEY = "your_api_key"
# CORPUS_ID = "your_corpus_id"

# vectara_client = VectaraClient(CUSTOMER_ID, API_KEY)

# # Indexing a document
# index_response = vectara_client.index_document(
#     corpus_id=CORPUS_ID,
#     document_id="unique_document_id",
#     text="This is the document text.",
#     context="Document context",
#     metadata_json='{"author": "John Doe"}'
# )
# print(index_response)

# # Querying
# query_response = vectara_client.query(
#     query_text="What is the meaning of life?",
#     num_results=10,
#     corpus_id=CORPUS_ID
# )
# print(query_response)
