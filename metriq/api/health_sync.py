# --------------------------------------------------
# Health Data Ingestion API
# --------------------------------------------------

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import os

from metriq.database import Session
from metriq.models import HealthRecord

router = APIRouter()

# --------------------------------------------------
# API Key
# --------------------------------------------------

def get_api_key():
    return os.getenv("METRIQ_API_KEY")


# --------------------------------------------------
# Helper: parse timestamps safely
# --------------------------------------------------

def parse_datetime(value):

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


# --------------------------------------------------
# Health data ingestion endpoint
# --------------------------------------------------

@router.post("/health_sync")
async def health_sync(request: Request):

    # --------------------------------------------------
    # Authenticate request
    # --------------------------------------------------

    header_key = request.headers.get("X-METRIQ-API-KEY")

    if header_key != get_api_key():

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    # --------------------------------------------------
    # Parse JSON payload
    # --------------------------------------------------

    payload = await request.json()

    if not isinstance(payload, list):

        payload = [payload]

    session = Session()

    records = []

    # --------------------------------------------------
    # Build record objects
    # --------------------------------------------------

    for item in payload:

        metric = item.get("metric")
        value = item.get("value")
        unit = item.get("unit")
        source = item.get("source", "healthkit")

        start_date = parse_datetime(item.get("start_date"))
        end_date = parse_datetime(item.get("end_date"))

        if not metric or value is None or not start_date:

            continue

        record = HealthRecord(

            type=metric,
            value=str(value),
            unit=unit,
            source=source,
            start_date=start_date,
            end_date=end_date
        )

        records.append(record)

    # --------------------------------------------------
    # Bulk insert (fast ingestion)
    # --------------------------------------------------

    session.bulk_save_objects(records)

    session.commit()

    return {

        "status": "ok",
        "records_inserted": len(records)

    }