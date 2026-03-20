# --------------------------------------------------
# Metriq Application Entry Point
# --------------------------------------------------

import uvicorn

from fastapi import FastAPI

# --------------------------------------------------
# Database
# --------------------------------------------------

from metriq.database import engine
from metriq.models import Base

# IMPORTANT:
# Import models so SQLAlchemy registers them
import metriq.models

# --------------------------------------------------
# Routers
# --------------------------------------------------

from metriq.api.health import router as health_router
from metriq.api.upload import router as upload_router
from metriq.api.analytics import router as analytics_router
from metriq.api.health_sync import router as health_sync_router
from metriq.api.profile import router as profile_router
from metriq.api.dashboard import router as dashboard_router
from metriq.api.mifitness import router as mifitness_router
from metriq.api.sleep import router as sleep_router

# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI()

# --------------------------------------------------
# Database initialization
# --------------------------------------------------

@app.on_event("startup")
def startup():

    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Router registration
# --------------------------------------------------

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analytics_router)
app.include_router(health_sync_router)
app.include_router(profile_router)
app.include_router(dashboard_router)
app.include_router(mifitness_router)
app.include_router(sleep_router)

# --------------------------------------------------
# Uvicorn entrypoint
# --------------------------------------------------

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )