# --------------------------------------------------
# Mi Fitness Importer
# --------------------------------------------------

import os
import requests
from datetime import datetime

from metriq.database import Session
from metriq.models import HealthRecord
from metriq.importers.xiaomi_auth import login


BASE_URL = "https://de.hlth.io.mi.com/app/v1"



def get_headers():

    token = get_token()

    return {
        "apptoken": token["apptoken"],
        "userid": token["userid"],
        "Content-Type": "application/json"
    }

def fetch_sport_records(watermark=""):

    url = f"{BASE_URL}/data/get_sport_records_by_watermark"

    payload = {
        "watermark": watermark
    }

    r = requests.post(url, json=payload, headers=get_headers())

    r.raise_for_status()

    return r.json()


def normalize_sport(records):

    normalized = []

    for r in records:

        ts = datetime.fromtimestamp(r["start_time"])

        normalized.append({
            "type": "steps",
            "value": str(r.get("steps", 0)),
            "timestamp": ts
        })

        normalized.append({
            "type": "distance",
            "value": str(r.get("distance", 0)),
            "timestamp": ts
        })

        normalized.append({
            "type": "calories",
            "value": str(r.get("calories", 0)),
            "timestamp": ts
        })

    return normalized


def save_records(records):

    session = Session()

    for r in records:

        rec = HealthRecord(
            type=r["type"],
            value=r["value"],
            start_date=r["timestamp"],
            end_date=r["timestamp"]
        )

        session.add(rec)

    session.commit()


def sync():

    data = fetch_sport_records()

    records = data["data"]["records"]

    normalized = normalize_sport(records)

    save_records(normalized)

    return len(normalized)