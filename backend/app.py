"""NWKRTC Leave Assistant API. Safe prototype: no live portal login or submission."""
import hmac
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import create_job, get_job, init_db, list_jobs
from backend.leave_rules import eligible_leave_date, validate_one_day_cl_request

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
ADMIN_USERNAME = os.getenv("NWKRTC_ADMIN_USERNAME", "")
ADMIN_PASSWORD = os.getenv("NWKRTC_ADMIN_PASSWORD", "")
security = HTTPBasic(auto_error=False)

app = FastAPI(
    title="NWKRTC Leave Assistant",
    version="0.2.0",
    docs_url=None if APP_ENV == "production" else "/docs",
    redoc_url=None if APP_ENV == "production" else "/redoc",
    openapi_url=None if APP_ENV == "production" else "/openapi.json",
)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
INDIA_TZ = ZoneInfo("Asia/Kolkata")


class LeaveRequest(BaseModel):
    leave_date: date
    leave_type: str = Field(default="CL", pattern="^CL$")


def require_dashboard_auth(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> str:
    """Require configured HTTP Basic credentials in production and when enabled."""
    configured = bool(ADMIN_USERNAME and ADMIN_PASSWORD)
    if APP_ENV == "production" and not configured:
        raise HTTPException(status_code=503, detail="Dashboard authentication is not configured.")
    if not configured:
        return "local-development"
    username_ok = credentials is not None and hmac.compare_digest(
        credentials.username.encode("utf-8"), ADMIN_USERNAME.encode("utf-8")
    )
    password_ok = credentials is not None and hmac.compare_digest(
        credentials.password.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8")
    )
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.middleware("http")
async def protect_dashboard_and_check_origin(request: Request, call_next):
    # Keep the minimal health endpoint available to container/platform health checks.
    if request.url.path == "/api/health":
        return await call_next(request)

    # Browser state-changing requests must be same-origin. Requests without Origin
    # (e.g. command-line clients) still require authentication when it is enabled.
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin:
            from urllib.parse import urlsplit

            origin_host = urlsplit(origin).netloc
            if not origin_host or origin_host.lower() != request.headers.get("host", "").lower():
                return JSONResponse(status_code=403, content={"detail": "Cross-origin request blocked."})

    # Auth is checked in route dependencies, including the dashboard and every API
    # endpoint except health. Static assets are non-sensitive and contain no secrets.
    return await call_next(request)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/")
def home(_: str = Depends(require_dashboard_auth)) -> FileResponse:
    return FileResponse("frontend/index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "simulation", "portal_access": "disabled"}


@app.get("/api/rules")
def rules(_: str = Depends(require_dashboard_auth)) -> dict[str, str | int]:
    today = datetime.now(INDIA_TZ).date()
    return {
        "today": today.isoformat(),
        "eligible_date": eligible_leave_date(today).isoformat(),
        "days_ahead": 9,
        "mode": "simulation",
    }


@app.post("/api/jobs", status_code=201)
def prepare_leave(
    request: LeaveRequest,
    _: str = Depends(require_dashboard_auth),
) -> dict:
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
def jobs(_: str = Depends(require_dashboard_auth)) -> dict[str, list[dict]]:
    return {"jobs": list_jobs()}


@app.get("/api/jobs/{job_id}")
def job(job_id: int, _: str = Depends(require_dashboard_auth)) -> dict:
    found = get_job(job_id)
    if not found:
        raise HTTPException(status_code=404, detail="Job not found")
    return found
