# --------------------------------------------------
# Metriq Analytics API
# --------------------------------------------------

from fastapi import APIRouter

from metriq.database import Session
from metriq.models import NutritionLog, SleepLog

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
# Dashboard data endpoint
# --------------------------------------------------

@router.get("/api/dashboard")
async def dashboard():

    session = Session()

    # ---------------------------------------------
    # Nutrition data
    # ---------------------------------------------

    nutrition = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(90)\
        .all()

    dates = []
    calories = []
    weight = []
    steps = []

    for r in nutrition:

        dates.append(r.date.isoformat())
        calories.append(r.calories or 0)
        weight.append(r.weight or 0)
        steps.append(r.steps or 0)

    # ---------------------------------------------
    # Sleep data
    # ---------------------------------------------

    sleep_rows = session.query(SleepLog)\
        .order_by(SleepLog.date.desc())\
        .limit(90)\
        .all()

    sleep_map = {}

    for s in sleep_rows:

        sleep_map[s.date.isoformat()] = s.hours

    sleep = []

    for d in dates:

        sleep.append(sleep_map.get(d, 0))

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
        "energy_balance": energy_balance

    }