import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

from metriq.database import Session
from metriq.models import HealthRecord


class AppleHealthImporter:

    def parse(self, file_path):

        session = Session()

        BATCH_SIZE = 5000
        batch = []

        wanted_metrics = {
            "HKQuantityTypeIdentifierDietaryEnergyConsumed": "calories",
            "HKQuantityTypeIdentifierDietaryProtein": "protein",
            "HKQuantityTypeIdentifierDietaryCarbohydrates": "carbs",
            "HKQuantityTypeIdentifierDietaryFatTotal": "fat",
            "HKQuantityTypeIdentifierStepCount": "steps",
            "HKQuantityTypeIdentifierBodyMass": "weight",
        }

        daily = defaultdict(lambda: {
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fat": 0,
            "steps": 0,
            "weight": None
        })

        count = 0

        for event, elem in ET.iterparse(file_path, events=("end",)):

            if elem.tag != "Record":
                elem.clear()
                continue

            type_name = elem.attrib.get("type")
            value_raw = elem.attrib.get("value")

            start_date_raw = elem.attrib.get("startDate")
            end_date_raw = elem.attrib.get("endDate")

            try:
                start_date = datetime.strptime(start_date_raw[:19], "%Y-%m-%d %H:%M:%S")
            except:
                elem.clear()
                continue

            try:
                end_date = datetime.strptime(end_date_raw[:19], "%Y-%m-%d %H:%M:%S") if end_date_raw else None
            except:
                end_date = None

            record = HealthRecord(
                type=type_name,
                value=value_raw,
                start_date=start_date,
                end_date=end_date
            )

            batch.append(record)
            count += 1

            # batch insert raw records
            if len(batch) >= BATCH_SIZE:
                for r in batch:
                    session.merge(r)
                session.commit()
                batch.clear()

            # aggregate metrics for analytics
            if type_name in wanted_metrics:

                try:
                    value = float(value_raw)
                except:
                    elem.clear()
                    continue

                date = start_date.date()
                metric = wanted_metrics[type_name]

                if metric == "weight":
                    daily[date][metric] = value
                else:
                    daily[date][metric] += value

            elem.clear()

        # insert remaining records
        if batch:
            for r in batch:
                session.merge(r)
            session.commit()

        print(f"Imported {count} raw health records")

        return daily