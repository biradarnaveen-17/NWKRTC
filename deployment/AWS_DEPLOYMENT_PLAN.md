# AWS deployment plan (not deployed)

This document describes a safe future deployment target for the NWKRTC Leave Assistant. It is an implementation plan, not evidence that AWS resources exist.

## Current scope

The application is a simulation-only FastAPI service with a static dashboard and SQLite metadata store. It does not authenticate to or submit requests to the NWKRTC portal.

## Suggested architecture for a small prototype

- **EC2** runs the containerized FastAPI service.
- **Security group** permits inbound HTTPS only through a reverse proxy/load balancer; do not expose port 8000 directly to the public internet.
- **HTTPS** is terminated at an Application Load Balancer or a correctly configured reverse proxy with a valid certificate.
- **Authentication** is required before the dashboard and job APIs can be accessed. Use a managed identity provider or a well-reviewed authentication layer; do not invent a homemade password scheme.
- **Secrets Manager / Parameter Store** holds any future authorized portal credentials. Never put secrets in GitHub, images, committed environment files, browser storage, or logs.
- **CloudWatch** collects application logs and health signals. Redact credentials, cookies, employee identifiers, and session tokens.
- **Persistent data**: SQLite is suitable for a single-instance prototype only. For a multi-instance or production service, move metadata to a managed database such as RDS and plan backups/retention.
- **Least privilege IAM**: use an EC2 instance role with only the permissions required to read named secrets and write logs.

## Safe rollout order

1. Run the test suite in GitHub Actions and fix every failure.
2. Build and run the container locally; verify /api/health, /api/rules, and validation errors.
3. Configure the prototype's `NWKRTC_ADMIN_USERNAME` and `NWKRTC_ADMIN_PASSWORD` through a secret store; verify production fails closed if missing. The app checks same-origin on browser state-changing requests. Before public exposure, still add HTTPS, rate limiting, monitoring, and preferably a managed identity provider; HTTP Basic alone is not a complete production identity solution.
4. Create AWS resources manually or through reviewed infrastructure-as-code, with budget alerts and a clear teardown plan.
5. Deploy the simulation version first and verify HTTPS, access restrictions, persistent storage, logs, restart behavior, and backup/restore.
6. Keep live portal integration disabled until the portal owner confirms automation is permitted and the single-session behavior is understood.
7. If an authorized live integration is later built, require an explicit approval step for any actual submission, and treat a timeout after Apply as an unknown outcome that must be verified before retrying.

## Cost and safety controls

- Set an AWS Budget alert before creating billable resources.
- Use tags for project and environment.
- Restrict SSH to a known administrator IP or use Systems Manager Session Manager.
- Never make SQLite files or admin endpoints publicly downloadable.
- Configure a kill switch so the scheduled worker can be disabled quickly.
- Do not bypass CAPTCHA, authentication, or portal access/session controls.

## Current status

No AWS resources have been provisioned and no public URL exists for this prototype. The current Docker Compose port is bound to 127.0.0.1 for local use.
