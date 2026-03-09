class BaseImporter:
    def detect(self, data: str) -> bool:
        """Return True if this importer can parse the data"""
        raise NotImplementedError

    def parse(self, data: str):
        raise NotImplementedError
