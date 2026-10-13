from datetime import date, datetime
from zoneinfo import ZoneInfo

from backend.scheduler import next_run, run_preflight, run_scheduled_mock
from backend.workflow import run_mock_workflow


def test_mock_workflow_has_simulated_steps_only():
    result = run_mock_workflow(date(2026, 10, 14), date(2026, 10, 23))
    assert result.status == "SIMULATED"
    assert "simulation_complete" in result.steps
    assert "no nwkrtc website was opened" in result.message.lower()


def test_mock_workflow_rejects_invalid_date():
    result = run_mock_workflow(date(2026, 10, 14), date(2026, 10, 22))
    assert result.status == "REJECTED"
    assert result.steps[-1] == "validation_failed"


def test_preflight_is_explicitly_simulation_mode():
    now = datetime(2026, 10, 14, 5, 57, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = run_preflight(now)
    assert result["mode"] == "simulation"
    assert result["eligible_date"] == "2026-10-23"


def test_scheduled_mock_does_not_claim_submission():
    now = datetime(2026, 10, 14, 6, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    result = run_scheduled_mock(now)
    assert result["status"] == "SIMULATED"
    assert result["mode"] == "simulation"
    assert "No NWKRTC website" in result["message"]


def test_next_run_rolls_over_to_tomorrow():
    now = datetime(2026, 10, 14, 6, 1, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert next_run(6, 0, now).date() == date(2026, 10, 15)
