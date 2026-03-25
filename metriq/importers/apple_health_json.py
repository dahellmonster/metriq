import json
from datetime import datetime
from sqlalchemy.orm import Session

from metriq.database import SessionLocal
from metriq.models import HealthSample
from metriq.services.metrics import rebuild_daily_metrics


def load_json(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)


def parse_timestamp(ts: str):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def import_file(file_path: str):
    session = SessionLocal()

    inserted = 0
    skipped = 0

    try:
        raw = load_json(file_path)

        for r in raw:
            try:
                ts = parse_timestamp(r["timestamp"])
                date = datetime.strptime(r["date"], "%Y-%m-%d").date()

                sample = HealthSample(
                    timestamp=ts,
                    date=date,
                    metric=r["metric"],
                    value=r["value"],
                )

                session.merge(sample)
                inserted += 1

            except Exception:
                skipped += 1

        session.commit()

        # rebuild daily metrics AFTER insert
        rebuild_daily_metrics(session)

        return {
            "status": "ok",
            "inserted": inserted,
            "skipped": skipped
        }

    except Exception as e:
        session.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        session.close()