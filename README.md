# NWKRTC Leave Assistant

A mobile-friendly dashboard and cloud-worker prototype for preparing an NWKRTC leave application workflow.

## Current status: safe simulation prototype

This version **does not log in to the live NWKRTC portal and does not submit leave applications**. It implements the mobile UI, a small API, request history, and the date rule described for the portal. Live integration must only be added after confirming that automated access is permitted and testing the workflow safely.

## Features

- Mobile-friendly dashboard
- India-time date calculation (Asia/Kolkata)
- One-day Casual Leave (CL) validation
- Validates the user-described rule: eligible date is exactly 9 calendar days ahead
- SQLite request history
- Simulation-only request creation with clear status
- Tests for month boundaries and invalid dates

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

## Important behavior

- The app uses the current date in India to calculate the eligible date.
- A request is accepted only when the chosen date is exactly nine calendar days ahead and the leave type is CL.
- The request is stored as SIMULATED; this is not proof of an application in the NWKRTC system.
- No retry or auto-submit behavior exists. The app never touches the live portal.

## AWS deployment (next milestone)

Deploy behind HTTPS and restrict access before exposing it publicly. Use a private security group, a reverse proxy with TLS, and a service manager. Configure a durable database and CloudWatch logging before production use. Do not expose an unauthenticated leave-control panel to the public internet.

## Live portal integration is intentionally out of scope

Before adding it:
1. Confirm the portal/organization permits browser automation.
2. Verify the single-session behavior and expected session expiry.
3. Do not store passwords, cookies, or employee details in GitHub.
4. Require explicit review before any real leave submission.
5. Treat timeouts after clicking Apply as UNKNOWN and verify portal status before any retry to avoid duplicate requests.

Never commit credentials or session cookies. Keep .env local and use AWS Secrets Manager/SSM Parameter Store if an authorized integration is later approved.
