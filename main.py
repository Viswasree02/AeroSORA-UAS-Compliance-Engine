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
    from ai_parser import extract_mission_telemetry
    from logic_layer import evaluate_airworthiness_risk

    @app.post("/api/v1/triage")
    def run_triage(payload: MissionPayload):
        telemetry = extract_mission_telemetry(payload.raw_flight_brief)
        evaluation = evaluate_airworthiness_risk(telemetry)

        persist_mission(
            pilot_id=payload.pilot_id,
            callsign=payload.uas_callsign,
            label=payload.mission_label,
            mtow=telemetry["mtow_kg"],
            alt=telemetry["planned_altitude_m"],
            crowd=1 if telemetry["over_uninvolved_people"] else 0,
            score=evaluation["risk_index"],
            category=evaluation["operational_category"],
            decision=evaluation["flight_decision"],
            directives_json=json.dumps(evaluation["directives"])
        )

        return {
            "status": "PROCESSED",
            "telemetry": telemetry,
            "evaluation": evaluation
        }