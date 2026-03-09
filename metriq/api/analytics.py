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
    
@router.get("/dashboard")
async def dashboard():

    session = Session()

    # latest nutrition
    latest_nutrition = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .first()

    # latest weight
    latest_weight = session.query(BiometricsLog)\
        .order_by(BiometricsLog.date.desc())\
        .first()

    # last 7 days nutrition
    last7 = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(7)\
        .all()

    # last 30 days nutrition
    last30 = session.query(NutritionLog)\
        .order_by(NutritionLog.date.desc())\
        .limit(30)\
        .all()

    avg7 = {
        "calories": sum(r.calories for r in last7 if r.calories) / len(last7) if last7 else None,
        "protein": sum(r.protein for r in last7 if r.protein) / len(last7) if last7 else None,
        "carbs": sum(r.carbs for r in last7 if r.carbs) / len(last7) if last7 else None,
        "fat": sum(r.fat for r in last7 if r.fat) / len(last7) if last7 else None,
    }

    avg30 = {
        "calories": sum(r.calories for r in last30 if r.calories) / len(last30) if last30 else None,
        "protein": sum(r.protein for r in last30 if r.protein) / len(last30) if last30 else None,
        "carbs": sum(r.carbs for r in last30 if r.carbs) / len(last30) if last30 else None,
        "fat": sum(r.fat for r in last30 if r.fat) / len(last30) if last30 else None,
    }

    # weight trend
    weights = session.query(BiometricsLog)\
        .order_by(BiometricsLog.date.desc())\
        .limit(30)\
        .all()

    weight_change = None
    if len(weights) >= 2:
        weight_change = weights[0].weight - weights[-1].weight

    # simple TDEE estimate
    tdee = None
    if latest_nutrition and weight_change is not None and len(last30) > 0:

        avg_intake = sum(r.calories for r in last30 if r.calories) / len(last30)

        kcal_change = weight_change * 7700

        tdee = avg_intake - (kcal_change / len(last30))

    return {

        "latest": {
            "date": str(latest_nutrition.date) if latest_nutrition else None,
            "calories": latest_nutrition.calories if latest_nutrition else None,
            "protein": latest_nutrition.protein if latest_nutrition else None,
            "carbs": latest_nutrition.carbs if latest_nutrition else None,
            "fat": latest_nutrition.fat if latest_nutrition else None,
            "weight": latest_weight.weight if latest_weight else None
        },

        "averages": {
            "7_day": avg7,
            "30_day": avg30
        },

        "weight": {
            "current": latest_weight.weight if latest_weight else None,
            "change_30_days": weight_change
        },

        "tdee_estimate": round(tdee, 1) if tdee else None
    }