from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from metriq.api.health_sync import router as health_sync_router
from metriq.api.profile import router as profile_router

from datetime import date
from metriq.importer_registry import detect_importer
from metriq.database import Session
from metriq.models import NutritionLog

app = FastAPI()
app.include_router(health_sync_router)
app.include_router(profile_router)

templates = Jinja2Templates(directory="metriq/templates")

@app.get("/health")
async def health():
    return {"status": "ok"}
    
@app.get("/analytics")
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

    return {"days": len(data), "data": data}

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})
    
@app.get("/tdee")
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

@app.get("/summary")
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
    
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    path = f"/tmp/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    # Detect importer based on file type
    if file.filename.endswith(".xml"):
        from metriq.importers.apple_health_xml import AppleHealthImporter
        importer = AppleHealthImporter()

    elif file.filename.endswith(".csv"):
        from metriq.importers.mfp_csv import MfpCsvImporter
        importer = MfpCsvImporter()

    else:
        raise Exception("Unsupported file type")

    parsed = importer.parse(path)

    session = Session()

    for day, values in parsed.items():

        entry = NutritionLog(
            date=day,
            calories=values["calories"],
            protein=values["protein"],
            carbs=values["carbs"],
            fat=values["fat"],
            source="import"
        )

        session.merge(entry)

    session.commit()

    return {"status": "imported", "days": len(parsed)}