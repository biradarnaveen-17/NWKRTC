"""Optional daily scheduler for a simulation-only workflow.

Run with: python -m backend.scheduler
This process only logs a simulated preflight at 05:57 and mock run at 06:00
Asia/Kolkata time. It does not open a browser or contact NWKRTC.
"""
import logging
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from backend.leave_rules import eligible_leave_date
from backend.workflow import run_mock_workflow

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("nwkrtc.scheduler")
TZ = ZoneInfo("Asia/Kolkata")


def run_preflight(now: datetime | None = None) -> dict[str, str]:
    current = now.astimezone(TZ) if now else datetime.now(TZ)
    target = eligible_leave_date(current.date())
    result = {
        "mode": "simulation",
        "stage": "preflight",
        "current_time": current.isoformat(),
        "eligible_date": target.isoformat(),
        "message": "Preflight complete; live portal access is disabled.",
    }
    logger.info("PRE-FLIGHT %s", result)
    return result


def run_scheduled_mock(now: datetime | None = None) -> dict:
    current = now.astimezone(TZ) if now else datetime.now(TZ)
    target = eligible_leave_date(current.date())
    result = run_mock_workflow(current.date(), target).as_dict()
    result["mode"] = "simulation"
    result["run_time"] = current.isoformat()
    logger.info("MOCK WORKFLOW %s", result)
    return result


def next_run(hour: int, minute: int, now: datetime | None = None) -> datetime:
    current = now.astimezone(TZ) if now else datetime.now(TZ)
    candidate = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= current:
        candidate += timedelta(days=1)
    return candidate


def main() -> None:
    import time

    logger.warning(
        "Simulation scheduler started. It never logs in to or submits leave on the live portal."
    )
    while True:
        current = datetime.now(TZ)
        preflight_at = next_run(5, 57, current)
        submit_at = next_run(6, 0, current)
        # If preflight and run fall on different dates because startup is after 05:57,
        # the next preflight is tomorrow and the next run is tomorrow too.
        if preflight_at.date() != submit_at.date():
            preflight_at = submit_at - timedelta(minutes=3)
        while datetime.now(TZ) < preflight_at:
            time.sleep(min(5, max(1, (preflight_at - datetime.now(TZ)).total_seconds())))
        run_preflight()
        while datetime.now(TZ) < submit_at:
            time.sleep(min(2, max(1, (submit_at - datetime.now(TZ)).total_seconds())))
        run_scheduled_mock()
        # Prevent a tight loop and move to the next day's schedule.
        time.sleep(2)


if __name__ == "__main__":
    main()
