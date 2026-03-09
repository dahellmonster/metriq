import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from .base import BaseImporter


class AppleHealthImporter(BaseImporter):

    def detect(self, data: str) -> bool:
        return "HKQuantityTypeIdentifierDietaryEnergyConsumed" in data

    def parse(self, file_path):

        daily = defaultdict(lambda: {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "steps": 0,
            "weight": None
        })

        for event, elem in ET.iterparse(file_path):

            if elem.tag != "Record":
                continue

            type_name = elem.attrib.get("type")
            value = float(elem.attrib.get("value", 0))
            date = elem.attrib.get("startDate")

            date = datetime.fromisoformat(date).date()

            if type_name == "HKQuantityTypeIdentifierDietaryEnergyConsumed":
                daily[date]["calories"] += value

            elif type_name == "HKQuantityTypeIdentifierDietaryProtein":
                daily[date]["protein"] += value

            elif type_name == "HKQuantityTypeIdentifierDietaryCarbohydrates":
                daily[date]["carbs"] += value

            elif type_name == "HKQuantityTypeIdentifierDietaryFatTotal":
                daily[date]["fat"] += value

            elif type_name == "HKQuantityTypeIdentifierStepCount":
                daily[date]["steps"] += value

            elif type_name == "HKQuantityTypeIdentifierBodyMass":
                daily[date]["weight"] = value

            elem.clear()

        return daily