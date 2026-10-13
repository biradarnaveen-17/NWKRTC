# Deployment notes

This is a development prototype. Do not expose it publicly or use it for real leave submissions yet.

## Before any AWS deployment

- Use an EC2 instance in a supported region and restrict inbound access.
- Do not open the app directly to the whole internet.
- Put HTTPS and authentication in front of the dashboard.
- Store secrets in AWS Secrets Manager or Systems Manager Parameter Store; never in Git.
- Configure backups, logs, updates, and a way to stop the worker.
- Confirm that the portal owner permits automated access before implementing live browser automation.

## First smoke test

1. Create an isolated test environment.
2. Install Python 3.11+ and the requirements.
3. Run the app behind a local-only bind first.
4. Confirm /api/health reports simulation mode.
5. Submit only a simulated request and verify the status is SIMULATED.
6. Run pytest -q and confirm the workflow checks pass.

## Live automation safeguards required before implementation

The live portal workflow is not included. Any approved future integration must respect the portal's single-session behavior, use secure secrets, avoid repeated submission after uncertain timeouts, and verify the final portal status before reporting success.
