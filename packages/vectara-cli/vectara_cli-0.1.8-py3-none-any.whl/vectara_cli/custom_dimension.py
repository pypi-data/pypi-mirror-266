class CustomDimension:
    def __init__(self, name, description, servingDefault, indexingDefault):
        self.name = name
        self.description = description
        self.servingDefault = servingDefault
        self.indexingDefault = indexingDefault

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "servingDefault": self.servingDefault,
            "indexingDefault": self.indexingDefault,
        }
