from datetime import date, timedelta

from fastapi.testclient import TestClient

import backend.app as app_module


def test_health_endpoint_is_simulation_only():
    with TestClient(app_module.app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["mode"] == "simulation"
    assert payload["portal_access"] == "disabled"


def test_rules_endpoint_returns_nine_day_eligible_date():
    with TestClient(app_module.app) as client:
        response = client.get("/api/rules")

    assert response.status_code == 200
    payload = response.json()
    assert date.fromisoformat(payload["eligible_date"]) == (
        date.fromisoformat(payload["today"]) + timedelta(days=9)
    )
    assert payload["days_ahead"] == 9


def test_create_job_records_simulation_not_real_submission(monkeypatch):
    monkeypatch.setattr(app_module, "create_job", lambda leave_date, leave_type: 123)
    with TestClient(app_module.app) as client:
        rules = client.get("/api/rules").json()
        response = client.post(
            "/api/jobs",
            json={"leave_date": rules["eligible_date"], "leave_type": "CL"},
        )

    assert response.status_code == 201
    assert response.json()["id"] == 123
    assert response.json()["status"] == "SIMULATED"
    assert "Nothing was submitted" in response.json()["message"]


def test_create_job_rejects_wrong_leave_type():
    with TestClient(app_module.app) as client:
        rules = client.get("/api/rules").json()
        response = client.post(
            "/api/jobs",
            json={"leave_date": rules["eligible_date"], "leave_type": "EL"},
        )

    assert response.status_code == 422


def test_create_job_rejects_wrong_date():
    with TestClient(app_module.app) as client:
        rules = client.get("/api/rules").json()
        wrong_date = (
            date.fromisoformat(rules["today"]) + timedelta(days=8)
        ).isoformat()
        response = client.post(
            "/api/jobs",
            json={"leave_date": wrong_date, "leave_type": "CL"},
        )

    assert response.status_code == 422


def test_missing_job_returns_404(monkeypatch):
    monkeypatch.setattr(app_module, "get_job", lambda job_id: None)
    with TestClient(app_module.app) as client:
        response = client.get("/api/jobs/999999")

    assert response.status_code == 404


def test_dashboard_api_requires_configured_credentials(monkeypatch):
    monkeypatch.setattr(app_module, "ADMIN_USERNAME", "admin")
    monkeypatch.setattr(app_module, "ADMIN_PASSWORD", "test-password")
    with TestClient(app_module.app) as client:
        denied = client.get("/api/rules")
        accepted = client.get("/api/rules", auth=("admin", "test-password"))

    assert denied.status_code == 401
    assert accepted.status_code == 200


def test_production_fails_closed_when_auth_is_not_configured(monkeypatch):
    monkeypatch.setattr(app_module, "APP_ENV", "production")
    monkeypatch.setattr(app_module, "ADMIN_USERNAME", "")
    monkeypatch.setattr(app_module, "ADMIN_PASSWORD", "")
    with TestClient(app_module.app) as client:
        response = client.get("/api/rules")

    assert response.status_code == 503


def test_cross_origin_state_change_is_rejected():
    with TestClient(app_module.app) as client:
        response = client.post(
            "/api/jobs",
            headers={"Origin": "https://attacker.example"},
            json={"leave_date": "2099-01-01", "leave_type": "CL"},
        )

    assert response.status_code == 403
