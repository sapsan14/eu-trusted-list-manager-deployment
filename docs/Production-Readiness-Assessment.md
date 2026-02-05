# Production Readiness Assessment — Trusted List Manager (non-EU v6)

This document is the production-readiness assessment template for the TL Manager
stack. It replaces the earlier "Production-Adjustments" draft and should be
used as the single assessment artifact.

## 1) Summary

- **Date:** YYYY-MM-DD
- **Reviewer:** Name
- **Environment:** lab / pre-prod / prod
- **Recommendation:** Go / No-Go / Go with conditions
- **Key risks:** List top 3

## 2) Architecture snapshot

Baseline container stack:

- **tlm-app:** Tomcat 9 + OpenJDK 8 + TL Manager WAR
- **tlm-db:** MySQL 8
- **tlm-cas:** Apereo CAS
- **Optional:** Reverse proxy / TLS termination

## 3) Readiness checklist

| Area | Current state | Gap / risk | Required adjustment |
|------|---------------|------------|---------------------|
| Deployment reproducibility | | | Ansible roles + variables |
| Dependency lifecycle | | | Java 8 EOL plan |
| Authentication / CAS | | | Integrate real IdP |
| TLS / certificates | | | Enforce HTTPS everywhere |
| Secrets management | | | Vault or Ansible vault |
| Backup and restore | | | DB + config backup |
| Monitoring / logging | | | Central logs + health checks |
| Security updates | | | Patch cadence / CVE owner |
| Network segmentation | | | Internal-only DB/CAS |
| Audit / traceability | | | Ensure audit logs retained |
| Documentation / handover | | | Runbook + on-call notes |
| EC decommissioning risk | | | Monitor EC roadmap |

## 4) Required adjustments (action list)

Fill in concrete changes needed to move from lab to production-like:

1. **[P1]** Example: add reverse proxy with TLS and HSTS.
2. **[P1]** Example: move CAS to corporate IdP or LDAP.
3. **[P2]** Example: add nightly DB backup to internal storage.

## 5) References

- Main plan: `docs/EU-Trusted-List-Manager-Deployment-Plan.md` (§11)
- Podman packaging plan: `docs/Podman-Packaging-and-Ansible-Deployment-Plan.md`
