import os
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from database import init_db, persist_mission, query_all_missions

app = FastAPI(title="AeroSORA Regulatory Triage Server", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

class MissionPayload(BaseModel):
    pilot_id: str = Field(..., example="PILOT-UK-904")
    uas_callsign: str = Field(..., example="DJI-M300-RTK")
    mission_label: str = Field(..., example="Structural Pylon Inspection")
    raw_flight_brief: str = Field(..., min_length=10)

@app.get("/api/v1/health")
def system_health():
    return {
        "status": "ONLINE",
        "regulatory_framework": "UK CAA CAP 722 / JARUS SORA v2.5",
        "database": "SQLite Connected"
    }