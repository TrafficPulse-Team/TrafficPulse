from fastapi import FastAPI
from backend.routes.api import router
from database.database import init_db

app=FastAPI(title="TrafficPulse AI API",version="0.1.0",
            description="Local-first API for traffic video analysis.")
app.include_router(router)

@app.on_event("startup")
def startup():
    init_db()
