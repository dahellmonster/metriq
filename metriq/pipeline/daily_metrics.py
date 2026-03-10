from collections import defaultdict

from metriq.database import Session
from metriq.models import HealthRecord, SleepLog


def run_daily_pipeline():

    session = Session()

    sleep_records = session.query(HealthRecord)\
        .filter(HealthRecord.type == "HKCategoryTypeIdentifierSleepAnalysis")\
        .all()

    daily_sleep = defaultdict(float)

    for r in sleep_records:

        if r.start_date and r.end_date:

            hours = (r.end_date - r.start_date).total_seconds() / 3600

            date = r.start_date.date()

            daily_sleep[date] += hours

    for date, hours in daily_sleep.items():

        entry = SleepLog(
            date=date,
            duration_hours=hours,
            source="apple_health"
        )

        session.merge(entry)

    session.commit()