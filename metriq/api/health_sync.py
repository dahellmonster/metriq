from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import os

from metriq.database import Session
from metriq.models import HealthRecord

router = APIRouter()


def get_api_key():
    """
    Read API key from environment dynamically so changes
    to .env (via profile page) take effect immediately.
    """
    return os.getenv("METRIQ_API_KEY")


def parse_datetime(value):
    """
    Safely parse ISO timestamps.
    """
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None


@router.post("/health_sync")
async def health_sync(request: Request):

    # -------- AUTHENTICATION --------

    api_key = get_api_key()

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API key not configured"
        )

    header_key = request.headers.get("X-METRIQ-API-KEY")

    if header_key != api_key:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    # -------- PAYLOAD --------

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    # Accept single object or list
    if not isinstance(payload, list):
        payload = [payload]

    session = Session()

    inserted = 0

    # -------- PROCESS RECORDS --------

    for item in payload:

        metric = item.get("metric")
        value = item.get("value")
        unit = item.get("unit")
        source = item.get("source", "healthkit")

        start_date = parse_datetime(item.get("start_date"))
        end_date = parse_datetime(item.get("end_date"))

        # Basic validation
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

        session.add(record)

        inserted += 1

    session.commit()

    return {
        "status": "ok",
        "records_inserted": inserted
    }