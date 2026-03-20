# --------------------------------------------------
# Sleep Scoring Engine
# --------------------------------------------------

from datetime import datetime, timedelta
from statistics import stdev

from metriq.database import Session
from metriq.models import HealthRecord


def get_sleep_data(session, days=7):
    """
    Fetch sleep duration + time in bed for last N days
    """

    cutoff = datetime.utcnow() - timedelta(days=days)

    records = session.query(HealthRecord)\
        .filter(HealthRecord.type.in_(["sleep", "in_bed"]))\
        .filter(HealthRecord.start_date >= cutoff)\
        .all()

    daily = {}

    for r in records:

        day = r.start_date.date()

        if day not in daily:
            daily[day] = {"sleep": 0, "in_bed": 0}

        if r.type == "sleep":
            daily[day]["sleep"] += float(r.value)

        if r.type == "in_bed":
            daily[day]["in_bed"] += float(r.value)

    return daily


# --------------------------------------------------
# Scoring Functions
# --------------------------------------------------

def duration_score(seconds):

    hours = seconds / 3600

    if hours >= 8:
        return 100
    elif hours >= 7:
        return 90
    elif hours >= 6:
        return 75
    elif hours >= 5:
        return 60
    else:
        return 40


def efficiency_score(sleep, in_bed):

    if in_bed == 0:
        return 0

    eff = sleep / in_bed

    if eff >= 0.95:
        return 100
    elif eff >= 0.90:
        return 90
    elif eff >= 0.85:
        return 80
    else:
        return 60


def consistency_score(durations):

    if len(durations) < 3:
        return 80  # neutral

    try:
        variation = stdev(durations)

        if variation < 1800:  # <30 min variance
            return 100
        elif variation < 3600:
            return 85
        elif variation < 5400:
            return 70
        else:
            return 50

    except:
        return 80


# --------------------------------------------------
# Main calculation
# --------------------------------------------------

def calculate_sleep_score():

    session = Session()

    daily = get_sleep_data(session)

    if not daily:
        return {"error": "no sleep data"}

    # get latest day
    latest_day = max(daily.keys())

    latest = daily[latest_day]

    sleep = latest["sleep"]
    in_bed = latest["in_bed"]

    # scores
    d_score = duration_score(sleep)
    e_score = efficiency_score(sleep, in_bed)

    durations = [v["sleep"] for v in daily.values()]
    c_score = consistency_score(durations)

    # weighted score
    final_score = (
        d_score * 0.5 +
        e_score * 0.3 +
        c_score * 0.2
    )

    return {
        "date": latest_day,
        "sleep_hours": round(sleep / 3600, 2),
        "efficiency": round(sleep / in_bed, 2) if in_bed else 0,
        "duration_score": d_score,
        "efficiency_score": e_score,
        "consistency_score": c_score,
        "sleep_score": round(final_score, 1)
    }