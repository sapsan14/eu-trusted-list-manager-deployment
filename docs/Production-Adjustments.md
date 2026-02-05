# TL Manager (non-EU) v6 — Production adjustments

This document lists **what must change** to move from lab/PoC to production.

Related guides:
- `docs/VM-Deployment-Guide.md` — VM install and lab access
- `docs/TL-Manager-Non-EU-Deployment.md` — automation details and variable defaults

## 1) Identity and access

- Replace **AcceptUsersAuthenticationHandler** with real IdP (LDAP/OIDC/SAML).
- Define **CAS services** explicitly (limit to TL Manager URLs).
- Establish **roles** and user provisioning (who gets SUP/MAN/ATH).

## 2) TLS and certificates

- Use **valid PKI certificates** for CAS and TL Manager.
- Enforce **HTTPS only** (disable HTTP or redirect to HTTPS).
- Use hostnames that match certificates (no localhost in prod).

## 3) Secrets management

- Move DB credentials and keystore passwords to **vault**.
- Avoid plaintext secrets in `group_vars` and git history.

## 4) Database and backups

- Ensure DB backups (schema + data) with retention.
- Document restore procedures and RPO/RTO.
- Restrict DB access to localhost or private subnet.

## 5) Signing keys (QSCD)

- Replace lab signer keystore with **production QSCD** or approved keys.
- Document key lifecycle, rotation, and access control.

## 6) Monitoring and logging

- Centralize logs (Tomcat, CAS, audit).
- Add health checks and alerts (service down, login failures).
- Set log retention and size limits.

## 7) Security hardening

- OS hardening (ssh key-only, minimal services, SELinux policy review).
- Firewall rules: only required ports (443/8443, 22 from admin network).
- Regular patching and CVE tracking (Java 8, Tomcat 9, MySQL 8).

## 8) High availability (optional)

- Consider separate CAS and DB nodes.
- Plan HA for Tomcat (or container orchestration).
- Document failover procedures.

## 9) Documentation and runbooks

- Maintain an operator runbook (deploy, backup, restore, rotate certs).
- Track the current configuration and environment variables.

## Minimum production steps (summary)

1. Enable HTTPS with valid certs and disable HTTP.
2. Configure CAS to use real IdP and restrict services.
3. Move secrets to vault and rotate passwords.
4. Replace signer keystore with production QSCD.
5. Set up backups and monitoring.

## See also

- `docs/VM-Deployment-Guide.md` — VM install and lab access
- `docs/TL-Manager-Non-EU-Deployment.md` — automation details and variable defaults
