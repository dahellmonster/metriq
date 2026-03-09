from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from metriq.database import Session
from metriq.models import NutritionLog, ActivityLog, BiometricsLog
from metriq.importers.apple_health_xml import AppleHealthImporter


router = APIRouter()

templates = Jinja2Templates(directory="metriq/templates")


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    path = f"/tmp/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    importer = AppleHealthImporter()

    parsed = importer.parse(path)

    session = Session()

    nutrition_count = 0

    for day, values in parsed.items():

        entry = NutritionLog(
            date=day,
            calories=values.get("calories", 0),
            protein=values.get("protein", 0),
            carbs=values.get("carbs", 0),
            fat=values.get("fat", 0),
            source="apple_health"
        )

        session.merge(entry)

        nutrition_count += 1

        if values.get("steps"):

            activity = ActivityLog(
                date=day,
                activity_type="steps",
                category="daily",
                calories=None,
                duration=None,
                source="apple_health"
            )

            session.add(activity)

        if values.get("weight"):

            biometrics = BiometricsLog(
                date=day,
                weight=values["weight"],
                bodyfat=None,
                source="apple_health"
            )

            session.merge(biometrics)

    session.commit()

    return {
        "status": "imported",
        "days_processed": len(parsed),
        "nutrition_records": nutrition_count
    }