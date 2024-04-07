from .filter_attribute import FilterAttribute
from .custom_dimension import CustomDimension

class CorpusData:
    def __init__(self, corpus_id, name, description, dtProvision, enabled, swapQenc, swapIenc, textless, encrypted, encoderId, metadataMaxBytes, customDimensions, filterAttributes):
        self.corpus_id = corpus_id
        self.name = name
        self.description = description
        self.dtProvision = dtProvision
        self.enabled = enabled
        self.swapQenc = swapQenc
        self.swapIenc = swapIenc
        self.textless = textless
        self.encrypted = encrypted
        self.encoderId = encoderId
        self.metadataMaxBytes = metadataMaxBytes
        self.customDimensions = [CustomDimension(**dim) for dim in customDimensions]
        self.filterAttributes = [FilterAttribute(**attr) for attr in filterAttributes]

    def to_dict(self):
        return {
            "id": self.corpus_id,
            "name": self.name,
            "description": self.description,
            "dtProvision": self.dtProvision,
            "enabled": self.enabled,
            "swapQenc": self.swapQenc,
            "swapIenc": self.swapIenc,
            "textless": self.textless,
            "encrypted": self.encrypted,
            "encoderId": self.encoderId,
            "metadataMaxBytes": self.metadataMaxBytes,
            "customDimensions": [dim.to_dict() for dim in self.customDimensions],
            "filterAttributes": [attr.to_dict() for attr in self.filterAttributes],
        }
