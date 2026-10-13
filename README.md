# NWKRTC Leave Assistant

A mobile-friendly dashboard and cloud-worker prototype for preparing an NWKRTC leave application workflow.

## Current status: simulation-only prototype

The app does **not** log in to the live NWKRTC portal or submit leave applications. It includes the dashboard, a FastAPI backend, SQLite request history, date validation, and a scheduled mock workflow.

## Features

- Responsive dashboard for phone and desktop
- India-time date calculation (Asia/Kolkata)
- One-day Casual Leave (CL) validation
- Checks the user-described rule: eligible date is exactly 9 calendar days ahead
- SQLite request history
- Simulation-only job creation
- Mock workflow for preflight and the 6:00 AM sequence
- Unit tests and GitHub Actions test workflow

## Run locally

Python 3.11+ is recommended.

    python -m venv .venv
    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    uvicorn backend.app:app --reload

Open http://127.0.0.1:8000. API health: http://127.0.0.1:8000/api/health

Run tests:

    pytest -q

## Run the scheduler simulation

In a separate terminal:

    python -m backend.scheduler

The process logs a simulated preflight at 05:57 and a mock workflow at 06:00, using Asia/Kolkata time. It runs continuously until stopped with Ctrl+C. It does not open a browser, use credentials, or contact NWKRTC. Do not treat SIMULATED as a real application.

## API endpoints

- GET /api/health — health and current safety mode
- GET /api/rules — current India date and eligible date
- POST /api/jobs — create a validated simulation record
- GET /api/jobs — list recent records
- GET /api/jobs/{id} — inspect one record

## AWS deployment: not performed yet

Before any internet-accessible deployment, add authentication, HTTPS, network restrictions, logging, backups, and a safe stop mechanism. Do not expose an unauthenticated leave-control panel to the public internet.

## Live portal integration is intentionally disabled

Before implementing live browser automation:
1. Confirm the portal owner/organization permits it.
2. Verify the single-session behavior and session expiry.
3. Never commit credentials, cookies, employee identifiers, or .env files.
4. Require explicit review before any real leave submission.
5. Treat timeouts after clicking Apply as UNKNOWN and verify portal status before any retry to avoid duplicate requests.
6. Do not bypass CAPTCHA, access controls, or session restrictions.

Keep secrets local during development; if an authorized integration is approved, use AWS Secrets Manager or Systems Manager Parameter Store.
