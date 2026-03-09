from metriq.importers.mfp_csv import MfpCsvImporter
from metriq.importers.apple_health_xml import AppleHealthImporter

IMPORTERS = [
    MfpCsvImporter(),
    AppleHealthImporter()
]

def detect_importer(data: str):

    for importer in IMPORTERS:
        if importer.detect(data):
            return importer

    raise ValueError("No compatible importer found")
