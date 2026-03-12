# --------------------------------------------------
# Mi Fitness Sync API
# --------------------------------------------------

from fastapi import APIRouter
import os

from metriq.importers.mifitness import sync

router = APIRouter()


@router.get("/sync/mifitness")
def mifitness_sync():

    username = os.getenv("MI_USERNAME")
    password = os.getenv("MI_PASSWORD")

    count = sync(username, password)

    return {
        "status": "ok",
        "records_imported": count
    }