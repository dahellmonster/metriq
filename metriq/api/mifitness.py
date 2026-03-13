# --------------------------------------------------
# Mi Fitness Sync API
# --------------------------------------------------

from fastapi import APIRouter

from metriq.importers.mifitness import sync

router = APIRouter()


@router.get("/sync/mifitness")
def mifitness_sync():

    count = sync()

    return {
        "status": "ok",
        "records_imported": count
    }