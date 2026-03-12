# --------------------------------------------------
# Mi Fitness Cloud Importer
# --------------------------------------------------

import requests
from datetime import datetime

from metriq.database import Session
from metriq.models import HealthRecord


# --------------------------------------------------
# Configuration
# --------------------------------------------------

MI_BASE_URL = "https://api-mifit.huami.com"


# --------------------------------------------------
# Login to Mi Fitness cloud
# --------------------------------------------------

def login(username, password):

    url = f"{MI_BASE_URL}/v1/client/login"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "username": username,
        "password": password
    }

    r = requests.post(url, headers=headers, data=payload)

    r.raise_for_status()

    data = r.json()

    return data.get("token")


# --------------------------------------------------
# Fetch sleep data
# --------------------------------------------------

def fetch_sleep(token):

    url = f"{MI_BASE_URL}/v1/sleep"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(url, headers=headers)

    r.raise_for_status()

    return r.json()


# --------------------------------------------------
# Normalize sleep records
# --------------------------------------------------

def normalize_sleep(records):

    normalized = []

    for r in records:

        date = datetime.fromtimestamp(r["start"])

        normalized.append({
            "metric": "sleep_deep",
            "value": r["deep"],
            "unit": "minutes",
            "timestamp": date
        })

        normalized.append({
            "metric": "sleep_rem",
            "value": r["rem"],
            "unit": "minutes",
            "timestamp": date
        })

        normalized.append({
            "metric": "sleep_light",
            "value": r["light"],
            "unit": "minutes",
            "timestamp": date
        })

    return normalized


# --------------------------------------------------
# Save to database
# --------------------------------------------------

def save_records(records):

    session = Session()

    for r in records:

        rec = HealthRecord(
            type=r["metric"],
            value=str(r["value"]),
            unit=r["unit"],
            source="mifitness",
            start_date=r["timestamp"],
            end_date=r["timestamp"]
        )

        session.add(rec)

    session.commit()


# --------------------------------------------------
# Main sync function
# --------------------------------------------------

def sync(username, password):

    token = login(username, password)

    sleep_data = fetch_sleep(token)

    records = normalize_sleep(sleep_data)

    save_records(records)

    return len(records)