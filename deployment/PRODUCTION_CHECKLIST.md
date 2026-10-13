# Production deployment checklist (simulation mode only)

This checklist does not create AWS resources. The app is still simulation-only and does not submit leave to NWKRTC.

## Before launching EC2

- [ ] Confirm organization permission for the intended use.
- [ ] Choose a domain and create DNS A/AAAA records pointing to the EC2 public address.
- [ ] Create an AWS Budget alert before launching billable resources.
- [ ] Create a security group that permits inbound TCP 80 and 443 from the internet. Permit SSH (22) only from a trusted administrator IP, or prefer Systems Manager Session Manager. Never expose port 8000.
- [ ] Use a supported Ubuntu LTS AMI, encrypted EBS storage, IMDSv2, and a minimal instance role. Do not attach broad administrator permissions.
- [ ] Install Docker Engine and the Docker Compose plugin from trusted vendor repositories.

## Configure the server

1. Clone this public repository to the server.
2. Copy `deployment/production.env.example` to a server-only `.env` file in the repository root.
3. Set a real domain and contact email. Generate a long unique password. Restrict the file to the deployment administrator (for example, `chmod 600 .env`).
4. Ensure DNS resolves to the EC2 address and ports 80/443 are reachable before starting Caddy; Caddy obtains and renews the TLS certificate.
5. Start the service from the repository root:

   ```sh
   docker compose --env-file .env -f deployment/compose.production.yml up -d --build
   ```

6. Verify the public site uses HTTPS, the dashboard requests authentication, and the health endpoint reports `portal_access: disabled`.
7. Check logs, restart behavior, SQLite persistence, backups, OS updates, and AWS billing. Keep a documented rollback/stop procedure.

## Important limitations

- HTTP Basic is only a minimal prototype gate. For broader/public use, prefer a managed identity provider, add rate limiting and monitoring, and assess CSRF/session design with a security review.
- The health endpoint is intentionally unauthenticated for container health checks; do not put sensitive information in it.
- The app container is configured read-only and drops Linux capabilities; validate this in CI before relying on it.
- The SQLite named volume is single-instance storage. Define and test encrypted backups before keeping important records.
- Never put credentials, cookies, employee identifiers, or session tokens in GitHub, container images, or logs.
- Live portal automation remains disabled. Do not bypass CAPTCHA, authentication, or session restrictions. An ambiguous timeout after a real submission must be verified before retrying.
- No AWS infrastructure has been created by this repository change.
