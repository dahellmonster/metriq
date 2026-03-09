from fastapi import UploadFile, File, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date

from metriq.importer_registry import detect_importer
from metriq.database import Session
from metriq.models import NutritionLog

templates = Jinja2Templates(directory="metriq/templates")


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    contents = await file.read()
    text = contents.decode()

    importer = detect_importer(text)
    parsed = importer.parse(text)

    session = Session()

    entry = NutritionLog(
        date=date.today(),
        calories=parsed.get("calories",0),
        protein=parsed.get("protein",0),
        carbs=parsed.get("carbs",0),
        fat=parsed.get("fat",0),
        source="auto"
    )

    session.merge(entry)
    session.commit()

    return {"status":"imported","calories":parsed.get("calories",0)}
