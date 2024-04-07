#./defaults.py

class CorpusDefaults:
    DT_PROVISION = 1234567890
    ENABLED = True
    SWAP_QENC = False
    SWAP_IENC = False
    TEXTLESS = False
    ENCRYPTED = True
    ENCODER_ID = "default"
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
