"""NWKRTC Leave Assistant API. Safe prototype: no live portal login or submission."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import create_job, get_job, init_db, list_jobs
from backend.leave_rules import eligible_leave_date, validate_one_day_cl_request

app = FastAPI(title="NWKRTC Leave Assistant", version="0.1.0")
app.mount("/static", StaticFiles(directory="frontend"), name="static")
INDIA_TZ = ZoneInfo("Asia/Kolkata")

class LeaveRequest(BaseModel):
    leave_date: date
    leave_type: str = Field(default="CL", pattern="^CL$")

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/")
def home() -> FileResponse:
    return FileResponse("frontend/index.html")

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "simulation", "portal_access": "disabled"}

@app.get("/api/rules")
def rules() -> dict[str, str | int]:
    today = datetime.now(INDIA_TZ).date()
    return {
        "today": today.isoformat(),
        "eligible_date": eligible_leave_date(today).isoformat(),
        "days_ahead": 9,
        "mode": "simulation",
    }

@app.post("/api/jobs", status_code=201)
def prepare_leave(request: LeaveRequest) -> dict:
    today = datetime.now(INDIA_TZ).date()
    try:
        validate_one_day_cl_request(today, request.leave_date, request.leave_date, request.leave_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    job_id = create_job(request.leave_date.isoformat(), request.leave_type)
    return {
        "id": job_id,
        "status": "SIMULATED",
        "message": "Request saved for demonstration only. Nothing was submitted to NWKRTC.",
    }

@app.get("/api/jobs")
def jobs() -> dict[str, list[dict]]:
    return {"jobs": list_jobs()}

@app.get("/api/jobs/{job_id}")
def job(job_id: int) -> dict:
    found = get_job(job_id)
    if not found:
        raise HTTPException(status_code=404, detail="Job not found")
    return found
