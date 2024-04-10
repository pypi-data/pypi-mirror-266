# ./data/query_response.py

class QueryResponse:
    def __init__(self, response_item):
        self.text = response_item.get('text', '')
        self.score = response_item.get('score', 0.0)
        self.metadata = {item['name']: item['value'] for item in response_item.get('metadata', [])}
        self.document_index = response_item.get('documentIndex', -1)
        self.corpus_key = response_item.get('corpusKey', {})

    def __str__(self):
        return f"Text: {self.text}\nScore: {self.score}\nMetadata: {self.metadata}\nDocument Index: {self.document_index}\nCorpus Key: {self.corpus_key}\n"

    @staticmethod
    def parse_response(response):
        return [QueryResponse(item) for item in response]
