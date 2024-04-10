# ./data/query_request

class ContextConfig:
    def __init__(self, chars_before, chars_after, sentences_before, sentences_after, start_tag, end_tag):
        self.chars_before = chars_before
        self.chars_after = chars_after
        self.sentences_before = sentences_before
        self.sentences_after = sentences_after
        self.start_tag = start_tag
        self.end_tag = end_tag

    def to_dict(self):
        return {
            "charsBefore": self.chars_before,
            "charsAfter": self.chars_after,
            "sentencesBefore": self.sentences_before,
            "sentencesAfter": self.sentences_after,
            "startTag": self.start_tag,
            "endTag": self.end_tag,
        }

class SummaryConfig:
    def __init__(self, summarizer_prompt_name, max_summarized_results, response_lang):
        self.summarizer_prompt_name = summarizer_prompt_name
        self.max_summarized_results = max_summarized_results
        self.response_lang = response_lang

    def to_dict(self):
        return {
            "summarizerPromptName": self.summarizer_prompt_name,
            "maxSummarizedResults": self.max_summarized_results,
            "responseLang": self.response_lang,
        }

# query_request.py

class CorpusKey:
    def __init__(self, customer_id, corpus_id, semantics='DEFAULT'):
        self.customer_id = customer_id
        self.corpus_id = corpus_id
        self.semantics = semantics

    def to_dict(self):
        return {
            "customerId": self.customer_id,
            "corpusId": self.corpus_id,
            "semantics": self.semantics,
        }

class Dimension:
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
        }

class LexicalInterpolationConfig:
    def __init__(self, lambda_val, dimensions):
        self.lambda_val = lambda_val
        self.dimensions = dimensions

    def to_dict(self):
        return {
            "lambda": self.lambda_val,
            "dim": [dimension.to_dict() for dimension in self.dimensions],
        }

class ModelParams:
    def __init__(self, max_tokens, temperature, frequency_penalty, presence_penalty):
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def to_dict(self):
        return {
            "maxTokens": self.max_tokens,
            "temperature": self.temperature,
            "frequencyPenalty": self.frequency_penalty,
            "presencePenalty": self.presence_penalty,
        }

class ChatConfig:
    def __init__(self, store, conversation_id, factual_consistency_score):
        self.store = store
        self.conversation_id = conversation_id
        self.factual_consistency_score = factual_consistency_score

    def to_dict(self):
        return {
            "store": self.store,
            "conversationId": self.conversation_id,
            "factualConsistencyScore": self.factual_consistency_score,
        }

class QueryRequest:
    def __init__(self, query, start, num_results, context_config, corpus_keys, metadata_filter=None, lexical_interpolation_config=None, summary_config=None, debug=False, chat_config=None):
        self.query = query
        self.start = start
        self.num_results = num_results
        self.context_config = context_config
        self.corpus_keys = corpus_keys
        self.metadata_filter = metadata_filter
        self.lexical_interpolation_config = lexical_interpolation_config
        self.summary_config = summary_config
        self.debug = debug
        self.chat_config = chat_config

    def to_dict(self):
        request_dict = {
            "query": self.query,
            "start": self.start,
            "numResults": self.num_results,
            "contextConfig": self.context_config.to_dict(),
            "corpusKey": [corpus_key.to_dict() for corpus_key in self.corpus_keys],
            "debug": self.debug,
        }
        if self.metadata_filter is not None:
            request_dict["metadataFilter"] = self.metadata_filter
        if self.lexical_interpolation_config is not None:
            request_dict["lexicalInterpolationConfig"] = self.lexical_interpolation_config.to_dict()
        if self.summary_config is not None:
            request_dict["summary"] = [self.summary_config.to_dict()]
        if self.chat_config is not None:
            request_dict["chat"] = self.chat_config.to_dict()
        return request_dict