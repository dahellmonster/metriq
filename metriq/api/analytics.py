from fastapi import APIRouter
from metriq.database import Session
from metriq.models import NutritionLog

router = APIRouter()

@router.get("/summary")
async def summary():

    session = Session()

    row = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .first()

    if not row:
        return {"status": "no data"}

    return {
        "date": str(row.date),
        "calories": row.calories,
        "protein": row.protein,
        "carbs": row.carbs,
        "fat": row.fat,
        "steps": row.steps,
        "weight": row.weight
    }


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
            "date": str(r.date),
            "calories": r.calories,
            "protein": r.protein,
            "carbs": r.carbs,
            "fat": r.fat,
            "steps": r.steps,
            "weight": r.weight
        })

    return {"days": len(data), "data": data}
    
@router.get("/tdee")
async def tdee():

    session = Session()

    rows = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(30)\
        .all()

    if len(rows) < 14:
        return {"error": "not enough data"}

    calories = [r.calories for r in rows if r.calories]
    weights = [r.weight for r in rows if r.weight]

    if len(weights) < 2:
        return {"error": "not enough weight data"}

    avg_intake = sum(calories) / len(calories)

    weight_change = weights[0] - weights[-1]

    kcal_change = weight_change * 7700

    tdee = avg_intake - (kcal_change / len(rows))

    return {
        "average_intake": round(avg_intake, 1),
        "estimated_tdee": round(tdee, 1),
        "weight_change": round(weight_change, 2)
    }