# Trusted List Manager (EU OSS) — Deployment Plan

**Owner:** Anton Sokolov  
**Stakeholder:** Bart / ZetesConfidens Trust Services  
**Single source of truth:** Bart’s briefing (see §1)  
**Status:** Draft — detailed plan with time estimates, risks, resource ordering and automation  
**Target:** RHEL 9 (company standard); VM or Podman

> **Note on naming:** This plan covers the **Trusted List Manager** (web app for browsing, editing, monitoring Trusted Lists), not a “generator”. The EU also provides a separate **Trusted List Signing Tool** (local signing); that is secondary in scope.

---

# Table of Contents

- [1. Source of truth — Scope and task (Bart)](#1-source-of-truth--scope-and-task-bart)
- [2. Tools in scope](#2-tools-in-scope)
- [3. Prerequisites and blockers](#3-prerequisites-and-blockers)
- [4. Resource ordering and procurement](#4-resource-ordering-and-procurement)
- [5. Environment and stack](#5-environment-and-stack)
- [6. Detailed plan with time estimates](#6-detailed-plan-with-time-estimates)
- [7. Risks and mitigations](#7-risks-and-mitigations)
- [8. Concrete steps (checklist)](#8-concrete-steps-checklist)
- [9. Automation where possible](#9-automation-where-possible)
- [10. LLM-readable prompts](#10-llm-readable-prompts)
- [11. Production-readiness evaluation](#11-production-readiness-evaluation)
- [12. Forward-looking: post-PoC and scaling](#12-forward-looking-post-poc-and-scaling)
- [13. References](#13-references)

---

# 1. Source of truth — Scope and task (Bart)

**SCOPE:**  
Experimentation with the European Commission’s open-source tool for editing, signing, and validating trusted lists. The Commission has published two tools: **Trusted List Manager** and **Trusted List Signing Tool**. The **Manager** is the most important and is the **priority**.  
The goal is to test how complex it is to **deploy, host, and support/maintain** this tool as a service for **non-EU countries**.

**TASK:**  
- Try to **install it and get it to a working setup**.  
- Either as a **VM** or a **Podman** container.  
- Best with **RHEL 9** (company standard).  
- **Evaluate how complex it is to make it production ready.**

---

# 2. Tools in scope

## 2.1 Trusted List Manager (non-EU, priority)

- **What:** Web application for browsing, editing, and monitoring Trusted Lists. Provided by the EC to Trusted List Operators.  
- **Status:** In October 2025 it was announced that the Trusted List Manager is being **decommissioned** for EU use; it is no longer hosted or maintained. The replacement is the **eIDAS Dashboard** (https://eidas.ec.europa.eu/efda/home). **For non-EU countries it remains in use**; recently **v6** was released.  
- **Service manual (PDF):** EC link below; **local copy:** `docs/TL-Manager(ServiceOfferingDescription) (v0.03).pdf`  
  https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/42358785/Trusted+List+Manager?preview=/42358785/52598139/TL-Manager(ServiceOfferingDescription)%20(v0.03).pdf  
  *(This SOD describes purpose, users, roles, access process; it does not specify OS or runtime stack — see §5 for stack from deployment package/other EC docs.)*  
- **Source and deployment package (non-EU v6.x):**  
  - **Internal ZIP on hand:** v6.4 (from Aldo).  
  - Public page: https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0  
- **Nexus (login may be required for downloads; TL Manager ZIP already available internally):**  
  - Browse: `https://ec.europa.eu/digital-building-blocks/artifact/#browse/browse:esignaturetlm:eu%2Feuropa%2Fec%2Fcef%2Fesignature%2FTL-NEU%2F6.0`  
  - ZIP: `.../TL-NEU-6.0.ZIP` (if needed)

**Signing options:**  
- **NexU** (Nowina) — local signature device: https://lab.nowina.solutions/nexu-demo/download-nexu (use with eIDAS USB tokens from QSCD.eu; e.g. Gemalto SafeNet eToken 5110 CC (940); good for hardware interop test; may not produce a TL that validates unless CA certs are added to the TL Manager trust store).  
- **Trusted List Signing Tool** (local) — sign TLs locally, then upload/download (un)signed XML via the Manager:  
  https://ec.europa.eu/digital-building-blocks/artifact/#browse/browse:esignaturetlm:eu%2Feuropa%2Fec%2Fcef%2Fesignature%2FTLSigning%2F2.1  

## 2.2 Trusted List Signing Tool (secondary)

- **What:** Small local digital signing software; creates **XAdES** signatures compliant with **ETSI TS 119 612 v2.1.1 to v2.4.1**; detects trusted list version and signs accordingly.  
- **Page:** https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/924976410/Trusted+List+Signing+Tool  
- **Version:** v2.1 (04/2025), compliant with TL v6 specification.  
- **Download:** Repository managed by Nexus/DBB for the EC; **requires an account** (still pending; **only needed for the TL Signing Tool**).  
- **Source and build instructions:**  
  https://ec.europa.eu/digital-building-blocks/artifact/#browse/browse:esignaturetlm:eu%2Feuropa%2Fec%2Fcef%2Fesignature%2FTLSigning  

---

# 3. Prerequisites and blockers

| Item | Status | Action |
|------|--------|--------|
| **TL Manager ZIP (non-EU v6.4)** | Available | Received from Aldo; store securely and checksum. |
| **Nexus / DBB account (TL Signing Tool only)** | Blocker only if Signing Tool is required | Request access via EC Digital Building Blocks or TLSO contact. |
| **RHEL 9 VM or host** | Available | VM already provisioned (Aldo). See §4 for fallback request. |
| **Podman (optional)** | Preferred for reproducibility | Install Podman on RHEL 9 if containerized. |
| **Network** | Lab/internal | Ensure host can reach EC URLs for docs; no public exposure of the app until approved. |

---

# 4. Resource ordering and procurement

Order these **in parallel** where possible to avoid idle time. Lead times are typical; adjust to your organisation.

| Resource | Spec / details | Who to request | Lead time (estimate) | Checklist |
|----------|----------------|----------------|------------------------|-----------|
| **VM (lab)** | 2 vCPU, 4 GB RAM, 20 GB disk; **RHEL 9**; internal/lab network (VM already available from Aldo) | IT / infra team or cloud portal | 0–10 days | [ ] Request form submitted (if needed); [ ] OS template chosen; [ ] Hostname reserved (e.g. `tl-manager-lab.internal`); [ ] SSH key or VPN access confirmed |
| **Nexus / DBB account (TL Signing Tool only)** | Access to EC Digital Building Blocks artifact repository (TL Signing Tool) | EC TLSO or DBB contact; or internal (if ZetesConfidens has a shared account) | 1–4 weeks | [ ] Contact identified; [ ] Request sent; [ ] Credentials received and stored in vault |
| **Internal DNS (optional)** | A record for `tl-manager-lab.internal` (and e.g. `cas-lab.internal` if CAS on same host) | Network / DNS team | 1–3 days | [ ] Hostname(s) requested; [ ] Record created |
| **SSL certificate (later)** | For production-like HTTPS (internal CA or public); not required for initial lab | PKI / security team | 1–2 weeks when needed | [ ] Deferred until after PoC |
| **Backup storage (later)** | Quota for DB + config backups if moving to production-like | IT / backup team | 1–2 weeks when needed | [ ] Deferred until after PoC |
| **eIDAS USB tokens (QSCD.eu, CC-certified)** | 6 units; e.g. Gemalto SafeNet eToken 5110 CC (940) | **Riho** / procurement | 1–3 weeks | [ ] Order placed; [ ] Delivery confirmed; [ ] Tokens inventoried |

**Concrete VM request text (copy-paste friendly):**

- **Purpose:** Lab deployment of EU Trusted List Manager (non-EU v6) for evaluation.  
- **OS:** RHEL 9.  
- **Sizing:** 2 vCPU, 4 GB RAM, 20 GB disk.  
- **Network:** Internal/lab only; outbound HTTPS for EC documentation.  
- **Access:** SSH (key-based); no public inbound except SSH if required.  
- **Hostname:** `tl-manager-lab.internal` (or as per company naming).

---

# 5. Environment and stack

**Official stack (from EC — Debian 12):**  
- OpenJDK **1.8**  
- Apache Tomcat **9.0.102**  
- MySQL **8.0.41**  
- Linux (Debian 12)

**Target for this plan (RHEL 9):**  
- **OS:** RHEL 9  
- **Java:** OpenJDK 8 (match application requirement; use `java-1.8.0-openjdk` on RHEL)  
- **App server:** Apache Tomcat 9.0.x (align with 9.0.102 if possible)  
- **Database:** MySQL 8.0.x (or MariaDB 10.6+ if compatible per manual)  
- **Auth:** CAS (Apereo CAS) — SSO for operator login  
- **Deployment:** Single VM **or** Podman containers (Tomcat + MySQL + optional CAS container)

**CAS (Central Authentication Service):**  
- Apereo CAS: https://github.com/apereo/cas  
- Supports CAS, SAML2, OIDC, OAuth2, MFA, LDAP, etc.; deploy as separate service or container; TL Manager will be configured to use CAS as identity provider.

---

# 6. Detailed plan with time estimates

Estimates assume one person; **Phase 0** can run in parallel with VM request.

| Phase | Description | Est. time (days) | Est. hours | Notes |
|-------|-------------|------------------|------------|--------|
| **0** | Confirm TL Manager ZIP (v6.4) on hand; request Nexus/DBB only if TL Signing Tool needed | 0.5 d | 1–2 h active | ZIP already available from Aldo; account only for Signing Tool. |
| **1** | Provision base VM; OS hardening; SSH; firewall; base packages | 0.5 d | 2–4 h | Can be automated (Ansible/IaC). VM lead time separate. |
| **2** | Install OpenJDK 8, Tomcat 9, MySQL 8 (or MariaDB) on host or containers | 0.5–1 d | 4–6 h | Package manager + config or Podman Compose. |
| **3** | Deploy and configure CAS (minimal config for TL Manager) | 1–2 d | 6–12 h | CAS is feature-rich; minimal setup for one service. |
| **4** | Deploy TL Manager WAR; configure DB, CAS URL, app props | 1 d | 4–6 h | Follow EC service manual. |
| **5** | Smoke test: login via CAS, open UI, create/edit test TL | 0.5 d | 2–4 h | Validates end-to-end. |
| **6** | Optional: NexU + eIDAS USB token signing interop test | 0.5 d | 2–4 h | Hardware interop only. |
| **7** | Document steps; production-readiness evaluation (§11) | 0.5 d | 2–4 h | Written report + checklist. |
| **Total (hands-on)** | | **~5–8 d** | **~24–44 h** | Excluding VM lead time (already available) and any Nexus lead time if TL Signing Tool is required. |

**Calendar view:** With VM and TL Manager ZIP already available, plan for **~1–2 weeks** to a working lab. If the TL Signing Tool is required, add Nexus lead time (1–4 weeks).

---

# 7. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Nexus/DBB account for TL Signing Tool never granted or delayed | Medium | Low–Medium | Proceed with TL Manager; request early if Signing Tool is needed; document fallback. |
| TL Manager not compatible with RHEL/MySQL 8 / Tomcat 9.0.x | Low–Medium | High | Stick to documented versions; test on Debian 12 in a container first if issues arise. |
| CAS setup more complex than expected | Medium | Medium | Allocate 2 days for CAS; use minimal overlay or prebuilt CAS Docker image; consider “static user list” only for lab. |
| OpenJDK 8 EOL / security | High (fact) | Medium long-term | For PoC acceptable; for production document upgrade path (e.g. TL Manager on newer Java if EC releases) or isolation. |
| EC discontinues non-EU TL Manager | Low (short term) | High | Monitor EC announcements; non-EU still supported; plan migration to eIDAS Dashboard or other if EC policy changes. |
| VM or network not ready on time | Low–Medium | Schedule slip | VM already available; validate network access early; use local Podman on laptop as fallback. |
| No TLS in lab | Low | Low | Acceptable for internal lab; document TLS as production requirement. |
| Database or config loss | Low | Medium | Document backup procedure in runbook; implement once moving to production-like. |

---

# 8. Concrete steps (checklist)

## Phase 0 — Unblock package access

- [ ] Confirm TL Manager ZIP (v6.4) received from Aldo; store in a secure project location and verify it contains WAR and/or deployment instructions.
- [ ] Record where the package is stored and checksum (e.g. SHA-256) for reproducibility.
- [ ] If the TL Signing Tool is in scope: request Nexus / Digital Building Blocks account.
- [ ] Once account is granted, download the TL Signing Tool package and record checksum.

## Phase 1 — Base VM / host

- [ ] **Confirm VM** (see §4): RHEL 9; use Aldo’s VM or order 2 vCPU, 4 GB RAM, 20 GB disk if needed.
- [ ] Set hostname (e.g. `tl-manager-lab.internal`).
- [ ] Configure firewall: allow SSH (22), HTTP/HTTPS (80/443) for Tomcat if needed; block everything else from outside.
- [ ] Install base packages: `podman` (if using containers), `git`, `curl`, `wget`, `vim`.
- [ ] Create a dedicated service user for running Tomcat (if not using containers).
- [ ] Harden OS: disable unnecessary services; ensure `sshd` is key-only if possible.

# Phase 2 — Runtime stack (choose A or B)

**Option A — Host install (no containers)**

- [ ] Install OpenJDK 8: `dnf install java-1.8.0-openjdk java-1.8.0-openjdk-devel`.
- [ ] Download Apache Tomcat 9.0.102 (or latest 9.0.x) from Apache mirror; unpack to `/opt/tomcat` (or company path).
- [ ] Create `tomcat` user; set `CATALINA_HOME`; fix permissions.
- [ ] Install MySQL 8.0: `dnf install mysql-server` (or enable MySQL repo and install); start and enable `mysqld`.
- [ ] Create database and user for TL Manager (e.g. `tlmanager` / password); grant privileges.
- [ ] Configure Tomcat `server.xml` (connector port 8080 or 8443); optionally add MySQL connector JAR to Tomcat lib.

**Option B — Podman**

- [ ] Write a `Dockerfile` or use image for Tomcat 9 + OpenJDK 8; image for MySQL 8.
- [ ] Create `podman-compose.yml` or shell script: start MySQL container, Tomcat container; mount WAR deployment dir or copy WAR into image.
- [ ] Create MySQL database and user inside MySQL container (init script or manual run).
- [ ] Expose Tomcat port (e.g. 8080) on host.

## Phase 3 — CAS

- [ ] Deploy Apereo CAS (e.g. overlay from https://github.com/apereo/cas) as a separate WAR or use a minimal CAS Docker image.
- [ ] Configure CAS to allow one service (TL Manager callback URL); minimal auth (e.g. static user list or LDAP if available).
- [ ] Note CAS login URL and service URL for TL Manager configuration.
- [ ] Test CAS login in browser.

## Phase 4 — TL Manager application

- [ ] Copy TL Manager WAR into Tomcat `webapps/` (e.g. `webapps/ROOT.war` or `webapps/tlmanager.war`).
- [ ] Create application configuration (per EC manual): JDBC URL, DB user, CAS login URL, CAS service URL, any trust store paths.
- [ ] Restart Tomcat; check logs for startup errors.
- [ ] Open TL Manager URL in browser; complete first-time setup if required by the app.

## Phase 5 — Validation

- [ ] Log in to TL Manager via CAS (operator flow).
- [ ] Create or import a minimal test trusted list (XML); edit and save.
- [ ] Confirm audit/logging of operator actions if the app provides it.
- [ ] Document URL, default roles, and any limitations found.

## Phase 6 — Optional signing

- [ ] Install NexU (or TL Signing Tool if available) on a workstation; use CC-certified eIDAS USB tokens (QSCD.eu, e.g. Gemalto SafeNet eToken 5110 CC (940)).
- [ ] In TL Manager, test “sign with local device” or “upload signed XML” flow; document result (e.g. “signed but not validated” without CA in trust store).

## Phase 7 — Documentation and evaluation

- [ ] Write internal doc: architecture, ports, DB credentials storage, backup of DB and config.
- [ ] Fill production-readiness evaluation (§11); share with Bart.

---

# 9. Automation where possible

| Task | Automation approach |
|------|----------------------|
| VM provisioning | Ansible playbook or Terraform: create VM, hostname, firewall, base packages, `podman`. |
| OpenJDK + Tomcat + MySQL on host | Ansible: install packages, unpack Tomcat, create DB and user, deploy config files. |
| Podman stack | `podman-compose` or shell: start MySQL, Tomcat; init DB from SQL file. |
| CAS deployment | Ansible or container: deploy CAS WAR, drop minimal `application.properties` (or YAML). |
| TL Manager config | Ansible template or script: write `context.xml` / app properties from variables (DB URL, CAS URL). |
| Smoke test | Script: `curl` CAS login page, then TL Manager URL; optional Selenium/Playwright for UI login (LLM can generate script from prompt). |

**Deliverable idea:** One Ansible playbook (or Podman Compose + one init script) that: installs OpenJDK 8, Tomcat 9, MySQL 8, deploys WAR and config, and optionally starts a minimal CAS — so that only “obtain WAR and set variables” remains manual.

---

# 10. LLM-readable prompts

Use these as-is for an LLM or assistant to generate scripts, configs, or commands. Assume RHEL 9 unless stated.

**Prompt 1 — Base server**  
“Generate an Ansible playbook for RHEL 9 that: sets hostname to tl-manager-lab; installs podman, git, curl, wget, java-1.8.0-openjdk, and firewalld; opens SSH (22) and HTTP (80) and HTTPS (443); creates a user ‘tomcat’ with no login shell. Use only dnf and standard modules.”

**Prompt 2 — Tomcat and MySQL on host**  
“Generate Ansible tasks for RHEL 9: install Apache Tomcat 9.0.102 from tarball into /opt/tomcat, run as user tomcat, listen on 8080; install MySQL 8 server, create database ‘tlmanager’ and user ‘tlmanager’ with a password from variable; add MySQL connector JAR to Tomcat lib. Output tasks only, no playbook wrapper.”

**Prompt 3 — Podman stack**  
“Write a podman-compose.yml or shell script that: runs MySQL 8 container with a named volume and env MYSQL_DATABASE=tlmanager, MYSQL_USER and MYSQL_PASSWORD; runs a Tomcat 9 container with OpenJDK 8, mounting a host directory for webapps so we can drop a WAR. Expose Tomcat on host 8080. Include a short README with start/stop commands.”

**Prompt 4 — CAS minimal**  
“I need minimal Apereo CAS 6.x configuration for one service: the service ID is ‘https://tl-manager-lab.internal/.*’ and the CAS server URL is https://cas-lab.internal/cas. Provide application.yml (or properties) snippets for in-memory service registry and one static user (e.g. admin/admin) for testing. No LDAP, no MFA.”

**Prompt 5 — TL Manager config**  
“The Trusted List Manager (EU EC, non-EU v6) runs on Tomcat and needs: MySQL JDBC URL jdbc:mysql://localhost:3306/tlmanager, username tlmanager, password from env; CAS login URL https://cas-lab.internal/cas/login; CAS service URL https://tl-manager-lab.internal/. Where would these typically go in a Tomcat-deployed Java app (context.xml, JNDI, or application properties)? Give a concrete example for Tomcat 9.”

**Prompt 6 — Smoke test**  
“Write a bash script that: (1) curls -s -o /dev/null -w '%{http_code}' http://localhost:8080/ and expects 200 or 302; (2) curls the CAS login page and checks for 200; (3) prints PASS or FAIL. Use only curl and standard shell. No authentication in script.”

---

# 11. Production-readiness evaluation

After the working setup is in place, fill this table and add a short narrative for Bart.

| Criterion | Low / Medium / High effort | Notes |
|-----------|----------------------------|--------|
| Deployment reproducibility | | Ansible / Podman / manual? |
| Dependency lifecycle | | OpenJDK 8 EOL; Tomcat 9; MySQL 8 maintenance. |
| CAS hardening | | Real IdP, TLS, MFA? |
| Backup and restore | | DB + config + WAR. |
| Desktop study: Azure/AWS for production readiness | | Would managed backups/HA reduce effort? |
| Monitoring and logging | | App logs, access logs, audit trail. |
| Security updates | | Who tracks CVEs for Tomcat/MySQL/Java? |
| Documentation and handover | | Runbook, credentials store. |
| EC decommissioning risk (EU) | | Non-EU still supported; track EC announcements. |

**Deliverable:** One-page “Production readiness assessment” with the table above and 3–5 concrete steps to move from “lab” to “production-like” (or recommendation not to productionize).

---

# 12. Forward-looking: post-PoC and scaling

- **If PoC succeeds:** Plan a “production-like” environment: dedicated VM(s), TLS, real IdP (e.g. company LDAP/OIDC), backup, monitoring, and runbook. Consider separate CAS instance and DB backup retention.
- **Compliance:** For non-EU TL operators, document how this deployment aligns with any national or contractual requirements (e.g. eIDAS alignment, audit logs).
- **High availability:** Current plan is single VM; HA would require Tomcat cluster, MySQL replication or managed DB, and CAS HA — document as future option if demand grows.
- **EC roadmap:** Monitor eIDAS Dashboard and EC communications; if non-EU migration path is announced, plan migration from TL Manager to the new tool.
- **TL Signing Tool:** Once Nexus access is available, add build/deploy of TL Signing Tool (or document “sign on workstation + upload” as supported workflow).

---

# 13. References

- **Bart’s briefing** — Single source of truth (this document §1).  
- **TL Manager (non-EU v6):**  
  https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0  
- **TL Manager service manual (PDF):**  
  https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/42358785/Trusted+List+Manager?preview=/42358785/52598139/TL-Manager(ServiceOfferingDescription)%20(v0.03).pdf  
- **eIDAS Dashboard (EU replacement):** https://eidas.ec.europa.eu/efda/home  
- **NexU (Nowina):** https://lab.nowina.solutions/nexu-demo/download-nexu  
- **QSCD.eu (eIDAS USB tokens, CC-certified):** https://qscd.eu/  
- **Trusted List Signing Tool:**  
  https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/924976410/Trusted+List+Signing+Tool  
- **Apereo CAS:** https://github.com/apereo/cas  

---

**Document version:** Draft v4 — updated per Bart (RHEL 9, package availability, signing-tool account, hardware tokens, cloud eval criterion).  
**Comments welcome.**
