class BaseImporter:
    def parse(self, data):
        raise NotImplementedError("Importer must implement parse()")
