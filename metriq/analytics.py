import pandas as pd
from metriq.database import Session
from metriq.models import NutritionLog, ActivityLog, BiometricsLog

def analytics_summary():

    session = Session()

    food = session.query(NutritionLog).all()
    activity = session.query(ActivityLog).all()
    weight = session.query(BiometricsLog).all()

    df_food = pd.DataFrame([f.__dict__ for f in food])
    df_activity = pd.DataFrame([a.__dict__ for a in activity])
    df_weight = pd.DataFrame([w.__dict__ for w in weight])

    if df_food.empty:
        return {"status": "no_data"}

    avg_food = df_food["calories"].tail(7).mean()

    avg_activity = 0
    if not df_activity.empty:
        avg_activity = df_activity["calories"].tail(7).mean()

    net_calories = avg_food - avg_activity

    weight_trend = None
    if not df_weight.empty:
        df_weight = df_weight.sort_values("date")
        weight_trend = df_weight["weight"].rolling(7).mean().iloc[-1]

    fat_loss_week = (net_calories * 7) / 7700

    return {
        "avg_food_calories_7d": round(avg_food,1),
        "avg_activity_calories_7d": round(avg_activity,1),
        "net_calories": round(net_calories,1),
        "estimated_fat_loss_week_kg": round(fat_loss_week,2),
        "weight_trend": weight_trend
    }
