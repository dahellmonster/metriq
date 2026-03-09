from fastapi import FastAPI
from metriq.analytics import analytics_summary

app = FastAPI(title="Metriq Health Analytics API")

@app.get("/analytics")
def analytics():
    return analytics_summary()
