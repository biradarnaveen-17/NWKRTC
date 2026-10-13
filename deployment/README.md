# Deployment notes

The repository includes a Dockerfile and local-only Docker Compose configuration. This is a deployment starting point, not an AWS deployment that has already been performed.

## Test the container locally

    docker compose up --build -d
    docker compose ps
    docker compose logs -f web

Open http://127.0.0.1:8000 and confirm the health endpoint reports simulation mode:

    curl http://127.0.0.1:8000/api/health

Stop it with:

    docker compose down

Request data persists in the named Docker volume. To remove the volume as well, use `docker compose down -v` only if you intentionally want to delete the local test history.

## Before any AWS deployment

- Use an EC2 instance in a supported region and restrict inbound access.
- The Compose file binds port 8000 to loopback only. Do not change it to a public bind until HTTPS and authentication are in place.
- Put HTTPS and authentication in front of the dashboard.
- Store secrets in AWS Secrets Manager or Systems Manager Parameter Store; never in Git.
- Configure backups, logs, updates, and a way to stop the worker.
- Confirm that the portal owner permits automated access before implementing live browser automation.

## First smoke test

1. Create an isolated test environment.
2. Run the container.
3. Confirm /api/health reports simulation mode and portal access disabled.
4. Prepare a test request and confirm its status is SIMULATED.
5. Run `pytest -q` and confirm the workflow checks pass.

## Live automation safeguards required before implementation

The live portal workflow is not included. Any approved future integration must respect the portal's single-session behavior, use secure secrets, avoid repeated submission after uncertain timeouts, and verify the final portal status before reporting success.
