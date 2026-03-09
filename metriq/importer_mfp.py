import myfitnesspal
import time
from datetime import date, timedelta
from metriq.database import Session
from metriq.models import NutritionLog

def import_recent_days(username, password, days=3):

    for attempt in range(3):
        try:
            client = myfitnesspal.Client(username, password)
            break
        except Exception:
            time.sleep(5)

    session = Session()

    for i in range(days):
        d = date.today() - timedelta(days=i)
        day = client.get_date(d)
        totals = day.totals

        entry = NutritionLog(
            date=d,
            calories=totals.get("calories",0),
            protein=totals.get("protein",0),
            carbs=totals.get("carbohydrates",0),
            fat=totals.get("fat",0),
            source="myfitnesspal"
        )

        session.merge(entry)

    session.commit()
