from fastapi import APIRouter, UploadFile, File
from metriq.database import Session
from metriq.models import NutritionLog
from metriq.importers.apple_health_xml import AppleHealthImporter

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    path = f"/tmp/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    importer = AppleHealthImporter()

    parsed = importer.parse(path)

    session = Session()

    for day, values in parsed.items():

        entry = NutritionLog(
            date=day,
            calories=values.get("calories",0),
            protein=values.get("protein",0),
            carbs=values.get("carbs",0),
            fat=values.get("fat",0),
            steps=values.get("steps",0),
            weight=values.get("weight"),
            source="apple_health"
        )

        session.merge(entry)

    session.commit()

    return {"status":"imported","days":len(parsed)}