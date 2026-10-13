# NWKRTC Leave Assistant

A mobile-friendly dashboard and cloud-worker prototype for preparing an NWKRTC leave application workflow.

## Safety-first development status

This repository starts in **simulation mode**. It does not log into the live NWKRTC portal or submit leave applications. Live integration should only be enabled after you have confirmed that automated access is permitted and tested selectors safely.

## Planned stack

- FastAPI backend
- Playwright browser automation (mock portal only initially)
- Mobile-friendly HTML/CSS/JavaScript frontend
- SQLite job/status store
- AWS EC2 deployment guide

## Initial workflow

1. Open the dashboard from a phone.
2. Configure a one-day Casual Leave (CL) request.
3. Validate the portal's 9-calendar-day eligibility rule.
4. Queue a simulated job for 6:00 AM India time.
5. Review status; uncertain submissions must never be automatically retried.

Never commit portal credentials, cookies, employee identifiers, or `.env` files.
