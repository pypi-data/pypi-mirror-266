#./defaults.py

class CorpusDefaults:
    DT_PROVISION = None
    ENABLED = True
    SWAP_QENC = False
    SWAP_IENC = False
    TEXTLESS = False
    ENCRYPTED = True
    ENCODER_ID = 1
    METADATA_MAX_BYTES = 10000
    CUSTOM_DIMENSIONS = []
    FILTER_ATTRIBUTES = []

    @staticmethod
    def get_defaults():
        return {
            "dtProvision": CorpusDefaults.DT_PROVISION,
            "enabled": CorpusDefaults.ENABLED,
            "swapQenc": CorpusDefaults.SWAP_QENC,
            "swapIenc": CorpusDefaults.SWAP_IENC,
            "textless": CorpusDefaults.TEXTLESS,
            "encrypted": CorpusDefaults.ENCRYPTED,
            "encoderId": CorpusDefaults.ENCODER_ID,
            "metadataMaxBytes": CorpusDefaults.METADATA_MAX_BYTES,
            "customDimensions": CorpusDefaults.CUSTOM_DIMENSIONS,
            "filterAttributes": CorpusDefaults.FILTER_ATTRIBUTES,
        }

class DefaultTextCustomDimensions:
    @staticmethod
    def get_default_dimensions():
        # Example custom dimensions
        return [
            TextCustomDimensions(name="relevance", value=0.9),
            TextCustomDimensions(name="freshness", value=0.8)
        ]