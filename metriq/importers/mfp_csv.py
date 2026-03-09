import csv
from .base import BaseImporter

class MfpCsvImporter(BaseImporter):

    def parse(self, text):

        if isinstance(text, str):
            text = text.splitlines()

        reader = csv.DictReader(text)

        calories = 0
        protein = 0
        carbs = 0
        fat = 0

        for row in reader:
            calories += float(row.get("Calories", 0) or 0)
            protein += float(row.get("Protein", 0) or 0)
            carbs += float(row.get("Carbohydrates", 0) or 0)
            fat += float(row.get("Fat", 0) or 0)

        return {
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fat": fat
        }
