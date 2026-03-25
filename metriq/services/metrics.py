from sqlalchemy.orm import Session
from metriq.models import HealthSample, DailyMetrics


def rebuild_daily_metrics(session: Session):

    days = session.query(HealthSample.date).distinct().all()

    for (day,) in days:

        samples = session.query(HealthSample)\
            .filter(HealthSample.date == day)\
            .all()

        steps = sum(s.value for s in samples if s.metric == "steps")
        active = sum(s.value for s in samples if s.metric == "active_energy")
        basal = sum(s.value for s in samples if s.metric == "basal_energy")
        distance = sum(s.value for s in samples if s.metric == "distance_walking_running")
        flights = sum(s.value for s in samples if s.metric == "flights_climbed")

        hr = [s.value for s in samples if s.metric == "heart_rate"]
        avg_hr = sum(hr) / len(hr) if hr else None

        existing = session.query(DailyMetrics)\
            .filter(DailyMetrics.date == day)\
            .first()

        if not existing:
            existing = DailyMetrics(date=day)
            session.add(existing)

        existing.steps = int(steps)
        existing.active_energy = active
        existing.basal_energy = basal
        existing.distance = distance
        existing.flights_climbed = int(flights)
        existing.avg_heart_rate = avg_hr

    session.commit()