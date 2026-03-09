from fastapi import APIRouter
from metriq.database import Session
from metriq.models import NutritionLog, BiometricsLog

router = APIRouter()

@router.get("/summary")
async def summary():

    session = Session()

    nutrition = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .first()

    if not nutrition:
        return {"status": "no data"}

    weight = session.query(BiometricsLog)\
        .order_by(BiometricsLog.date.desc())\
        .first()

    return {
        "date": str(nutrition.date),
        "calories": nutrition.calories,
        "protein": nutrition.protein,
        "carbs": nutrition.carbs,
        "fat": nutrition.fat,
        "weight": weight.weight if weight else None
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

        weight = session.query(BiometricsLog)\
            .filter(BiometricsLog.date == r.date)\
            .first()

        data.append({
            "date": str(r.date),
            "calories": r.calories,
            "protein": r.protein,
            "carbs": r.carbs,
            "fat": r.fat,
            "weight": weight.weight if weight else None
        })

    return {"days": len(data), "data": data}
    
@router.get("/tdee")
async def tdee():

    session = Session()

    nutrition_rows = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(30)\
        .all()

    weight_rows = session.query(BiometricsLog)\
        .order_by(BiometricsLog.date.desc())\
        .limit(30)\
        .all()

    if len(nutrition_rows) < 14 or len(weight_rows) < 2:
        return {"error": "not enough data"}

    calories = [r.calories for r in nutrition_rows if r.calories]
    weights = [r.weight for r in weight_rows if r.weight]

    avg_intake = sum(calories) / len(calories)

    weight_change = weights[0] - weights[-1]

    kcal_change = weight_change * 7700

    tdee = avg_intake - (kcal_change / len(nutrition_rows))

    return {
        "average_intake": round(avg_intake, 1),
        "estimated_tdee": round(tdee, 1),
        "weight_change": round(weight_change, 2)
    }