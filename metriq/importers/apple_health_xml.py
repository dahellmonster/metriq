import xml.etree.ElementTree as ET
from .base import BaseImporter

class AppleHealthImporter(BaseImporter):

    def parse(self, xml):

        root = ET.fromstring(xml)

        calories = 0
        protein = 0
        carbs = 0
        fat = 0

        for record in root.findall("Record"):

            type_name = record.attrib.get("type")
            value = float(record.attrib.get("value", 0))

            if type_name == "HKQuantityTypeIdentifierDietaryEnergyConsumed":
                calories += value

            if type_name == "HKQuantityTypeIdentifierDietaryProtein":
                protein += value

            if type_name == "HKQuantityTypeIdentifierDietaryCarbohydrates":
                carbs += value

            if type_name == "HKQuantityTypeIdentifierDietaryFatTotal":
                fat += value

        return {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
