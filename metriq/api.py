from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from datetime import date
from metriq.importer_registry import detect_importer
from metriq.database import Session
from metriq.models import NutritionLog

app = FastAPI()

templates = Jinja2Templates(directory="metriq/templates")

@app.get("/health")
async def health():
    return {"status": "ok"}
    
@app.get("/analytics")
async def analytics():

    session = Session()

    rows = session.query(NutritionLog).order_by(NutritionLog.date.desc()).limit(30).all()

    data = []

    for r in rows:
        data.append({
            "date": r.date,
            "calories": r.calories,
            "protein": r.protein,
            "carbs": r.carbs,
            "fat": r.fat
        })

    return {
        "days": len(data),
        "data": data
    }

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


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