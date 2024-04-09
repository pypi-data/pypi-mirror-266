# ./filter_attribute.py

class FilterAttribute:
    def __init__(self, name, description, indexed, type, level):
        self.name = name
        self.description = description
        self.indexed = indexed
        self.type = type
        self.level = level

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "indexed": self.indexed,
            "type": self.type,
            "level": self.level,
        }
