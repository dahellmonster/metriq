# --------------------------------------------------
# Metriq Analytics API
# --------------------------------------------------

from fastapi import APIRouter
from sqlalchemy import func
from datetime import date, timedelta

from metriq.database import Session
from metriq.models import NutritionLog, HealthRecord

router = APIRouter()


# --------------------------------------------------
# Summary endpoint
# --------------------------------------------------

@router.get("/summary")
async def summary():

    session = Session()

    row = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .first()

    if not row:

        return {"status": "no data"}

    return {

        "date": row.date,
        "calories": row.calories,
        "protein": row.protein,
        "carbs": row.carbs,
        "fat": row.fat,
        "steps": row.steps,
        "weight": row.weight

    }


# --------------------------------------------------
# Analytics history
# --------------------------------------------------

@router.get("/analytics")
async def analytics():

    session = Session()

    rows = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(90)\
        .all()

    rows.reverse()

    data = []

    for r in rows:

        data.append({

            "date": r.date,
            "calories": r.calories,
            "protein": r.protein,
            "carbs": r.carbs,
            "fat": r.fat,
            "steps": r.steps,
            "weight": r.weight

        })

    return {

        "days": len(data),
        "data": data

    }


# --------------------------------------------------
# Helper: get metric value per day
# --------------------------------------------------

def metric_per_day(session, metric_type):

    rows = session.query(
        func.date(HealthRecord.start_date),
        func.avg(HealthRecord.value)
    ).filter(
        HealthRecord.type == metric_type
    ).group_by(
        func.date(HealthRecord.start_date)
    ).all()

    data = {}

    for d, v in rows:

        try:
            data[str(d)] = float(v)
        except:
            data[str(d)] = 0

    return data


# --------------------------------------------------
# Helper: steps per day (sum)
# --------------------------------------------------

def steps_per_day(session):

    rows = session.query(
        func.date(HealthRecord.start_date),
        func.sum(HealthRecord.value)
    ).filter(
        HealthRecord.type == "HKQuantityTypeIdentifierStepCount"
    ).group_by(
        func.date(HealthRecord.start_date)
    ).all()

    data = {}

    for d, v in rows:

        try:
            data[str(d)] = float(v)
        except:
            data[str(d)] = 0

    return data


# --------------------------------------------------
# Helper: sleep hours
# --------------------------------------------------

def sleep_per_day(session):

    rows = session.query(
        func.date(HealthRecord.start_date),
        func.sum(
            func.julianday(HealthRecord.end_date) -
            func.julianday(HealthRecord.start_date)
        ) * 24
    ).filter(
        HealthRecord.type == "HKCategoryTypeIdentifierSleepAnalysis"
    ).group_by(
        func.date(HealthRecord.start_date)
    ).all()

    data = {}

    for d, v in rows:

        try:
            data[str(d)] = float(v)
        except:
            data[str(d)] = 0

    return data


# --------------------------------------------------
# Dashboard endpoint
# --------------------------------------------------

@router.get("/api/dashboard")
async def dashboard():

    session = Session()

    today = date.today()

    dates = []

    for i in range(90):

        d = today - timedelta(days=89 - i)

        dates.append(d.isoformat())

    # ---------------------------------------------
    # Metrics
    # ---------------------------------------------

    steps_map = steps_per_day(session)

    sleep_map = sleep_per_day(session)

    weight_map = metric_per_day(
        session,
        "HKQuantityTypeIdentifierBodyMass"
    )

    oxygen_map = metric_per_day(
        session,
        "HKQuantityTypeIdentifierOxygenSaturation"
    )

    # ---------------------------------------------
    # Nutrition
    # ---------------------------------------------

    nutrition_rows = session.query(NutritionLog).all()

    nutrition_map = {}

    for r in nutrition_rows:

        nutrition_map[r.date.isoformat()] = r

    # ---------------------------------------------
    # Build arrays
    # ---------------------------------------------

    calories = []
    weight = []
    steps = []
    sleep = []
    oxygen = []

    for d in dates:

        n = nutrition_map.get(d)

        if n:
            calories.append(n.calories or 0)
            weight.append(n.weight or weight_map.get(d, 0))
            steps.append(n.steps or steps_map.get(d, 0))
        else:
            calories.append(0)
            weight.append(weight_map.get(d, 0))
            steps.append(steps_map.get(d, 0))

        sleep.append(sleep_map.get(d, 0))

        oxygen.append(oxygen_map.get(d, 0))

    # ---------------------------------------------
    # Energy balance
    # ---------------------------------------------

    tdee_estimate = 2500

    energy_balance = []

    for c in calories:

        energy_balance.append(c - tdee_estimate)

    return {

        "dates": dates,
        "calories": calories,
        "weight": weight,
        "steps": steps,
        "sleep": sleep,
        "oxygen": oxygen,
        "energy_balance": energy_balance

    }