# --------------------------------------------------
# Dashboard analytics endpoint
# --------------------------------------------------

@router.get("/api/dashboard")
async def dashboard():

    session = Session()

    # ---------------------------------------------
    # Nutrition data
    # ---------------------------------------------

    nutrition = session.query(NutritionLog)\
        .order_by(NutritionLog.date.asc())\
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
    # Sleep aggregation
    # ---------------------------------------------

    sleep_rows = session.query(SleepLog)\
        .order_by(SleepLog.date.asc())\
        .limit(90)\
        .all()

    sleep_hours = []

    sleep_map = {s.date.isoformat(): s.hours for s in sleep_rows}

    for d in dates:

        sleep_hours.append(sleep_map.get(d, 0))

    # ---------------------------------------------
    # Energy balance
    # ---------------------------------------------

    tdee_estimate = 2500  # temporary until dynamic

    energy_balance = []

    for c in calories:

        energy_balance.append(c - tdee_estimate)

    return {

        "dates": dates,
        "calories": calories,
        "weight": weight,
        "steps": steps,
        "sleep": sleep_hours,
        "energy_balance": energy_balance

    }