from fastapi import APIRouter, UploadFile, File, HTTPException
from tempfile import NamedTemporaryFile

from metriq.importers.apple_health_json import import_file as import_json

router = APIRouter()


@router.post("/import")
async def import_health(file: UploadFile = File(...)):

    filename = file.filename.lower()

    if not (filename.endswith(".json") or filename.endswith(".xml")):
        raise HTTPException(status_code=400, detail="Only JSON or XML supported")

    with NamedTemporaryFile(delete=False) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    # JSON for now
    if filename.endswith(".json"):
        result = import_json(tmp_path)

    else:
        # placeholder for XML importer
        raise HTTPException(status_code=400, detail="XML importer not implemented yet")

    return result