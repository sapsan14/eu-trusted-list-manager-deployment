# Daily Report: TL Manager (non‑EU) — Progress and Next Steps

**Project:** EU Trusted List Manager (non‑EU v6)  
**Date:** 05 Feb 2026  
**Owner:** Anton Sokolov  
**Stakeholder:** Bart / ZetesConfidens Trust Services

## 1) Completed
- ✅ TL Manager v6.0 package received and stored in `packages/`.
- ✅ Lab VM on RHEL 9 provisioned and reachable via SSH.
- ✅ Base stack installed: OpenJDK 8, Tomcat 9, MySQL 8.
- ✅ Database and user `tlmanager` created.
- ✅ TL Manager (WAR) deployed to Tomcat with `application.properties` and `context.xml`.
- ✅ Signer keystore created automatically and wired into configuration.
- ✅ CAS deployed with minimal configuration for one service.
- ✅ TL Manager UI is reachable; CAS login works.
- ✅ Deployment documentation updated.
- ✅ TL_COUNTRIES seeded (ISO 3166‑1 + EU); country list populated.
- ✅ Draft storage paths fixed for Linux; custom-config directories created.
- ✅ Create empty draft works in UI.
- ✅ Import test TL XML works (`test/BE.xml`).

## 2) Key Results
- Working end‑to‑end configuration on RHEL 9 achieved.
- Stack viability confirmed (JDK8/Tomcat9/MySQL8) including CAS integration.
- Baseline prepared for production‑readiness assessment.

## 3) Remaining Steps (Checklist)
### Functional validation
- [x] Create/import a test Trusted List (XML).
- [ ] Edit and save changes via the UI.
- [ ] Verify operator audit/logging (if available).
- [ ] Record any limitations or errors found.

### Signing (optional)
- ✅ Order 6 QSCD tokens (via Riho).
- [ ] Install token drivers on workstation.
- [ ] Run signing/validation test and document results.

### Production readiness
- [ ] Fill in the production‑readiness assessment table (plan §11).
- [ ] Document backups, monitoring, security updates, and runbook.
- [ ] Record risks (JDK 8 EOL, dependencies, CAS hardening).
- [ ] Provide a recommendation for Bart.

## 4) Risks and Notes
- 🔴 JDK 8 is EOL; requires a dedicated security assessment.
- 🔴 CAS needs further hardening for production (TLS, IdP, policies).
- 🔴 If incompatibilities appear, compare against Debian 12 stack in a container.

## 5) Recommendations
- Complete functional validation and document findings.
- 🟡 Prepare a short “Production Readiness Assessment” (1–2 pages).
- 🟡 Consider a Podman-based variant for reproducibility and potential production use.

---
**Status:** Lab deployment is working; validation and production‑readiness assessment remain.
