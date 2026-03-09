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

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    path = f"/tmp/{file.filename}"

    with open(path, "wb") as f:
        f.write(await file.read())

    importer = detect_importer(path)
    data = importer.parse(path)

    session = Session()

    for day, values in data.items():

        entry = NutritionLog(
            date=day,
            calories=values["calories"],
            protein=values["protein"],
            carbs=values["carbs"],
            fat=values["fat"],
            source="apple_health"
        )

        session.merge(entry)

    session.commit()

    return {"status": "imported", "days": len(data)}
