import uvicorn
from fastapi import FastAPI

from metriq.api.health import router as health_router
from metriq.api.upload import router as upload_router
from metriq.api.analytics import router as analytics_router

app = FastAPI()

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(analytics_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)