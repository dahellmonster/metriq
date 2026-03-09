# Example code snippet to add into your existing api.py

from fastapi import UploadFile, File
from datetime import date
from metriq.importer_registry import get_importer
from metriq.database import Session
from metriq.models import NutritionLog


@app.post("/import/{source}")
async def import_data(source: str, file: UploadFile = File(...)):

    importer = get_importer(source)

    contents = await file.read()

    parsed = importer.parse(contents.decode())

    session = Session()

    entry = NutritionLog(
        date=date.today(),
        calories=parsed.get("calories", 0),
        protein=parsed.get("protein", 0),
        carbs=parsed.get("carbs", 0),
        fat=parsed.get("fat", 0),
        source=source
    )

    session.merge(entry)
    session.commit()

    return {"status": "imported"}
