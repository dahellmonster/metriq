from metriq.importers.mfp_csv import MfpCsvImporter
from metriq.importers.apple_health_xml import AppleHealthImporter

IMPORTERS = {
    "mfp": MfpCsvImporter(),
    "apple_health": AppleHealthImporter()
}

def get_importer(source: str):
    if source not in IMPORTERS:
        raise ValueError(f"Unsupported source: {source}")
    return IMPORTERS[source]
