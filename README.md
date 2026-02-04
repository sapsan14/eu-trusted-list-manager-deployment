# EU Trusted List Manager — Deployment

Lab deployment and evaluation of the **European Commission’s Trusted List Manager** (non-EU v6) on Red Hat–family Linux (VM or Podman). Goal: get a working setup and assess production-readiness for non-EU Trusted List Operators.

**Owner:** Anton Sokolov · **Stakeholder:** Bart / ZetesConfidens Trust Services

---

## What’s in this repo

| Path | Description |
|------|-------------|
| [docs/EU-Trusted-List-Manager-Deployment-Plan.md](docs/EU-Trusted-List-Manager-Deployment-Plan.md) | **Main plan:** scope, resource ordering, time estimates, risks, checklists, LLM prompts. |
| `scripts/` | Automation helpers (smoke tests, env checks). |
| `ansible/` | (Optional) Ansible playbooks for VM setup, Tomcat, MySQL, CAS. |

---

## Quick start

1. **Read the plan:** [docs/EU-Trusted-List-Manager-Deployment-Plan.md](docs/EU-Trusted-List-Manager-Deployment-Plan.md) — single source of truth for scope (Bart’s briefing), resource ordering (VM, Nexus account), and step-by-step checklists.
2. **Order resources** (in parallel): VM (Rocky/Alma/RHEL 9), Nexus/DBB account for TL Manager package (see plan §4).
3. **Run phases 1–7** from the plan; use §10 LLM prompts to generate Ansible/shell snippets if needed.
4. **Fill production-readiness** table (§11) and share with Bart.

---

## Stack (target)

- **OS:** Rocky Linux 9 / AlmaLinux 9 / RHEL 9  
- **Runtime:** OpenJDK 8, Apache Tomcat 9, MySQL 8  
- **Auth:** Apereo CAS (minimal config)  
- **Deploy:** Single VM or Podman containers  

---

## References

- [TL Manager non-EU v6](https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0)  
- [eIDAS Dashboard](https://eidas.ec.europa.eu/efda/home) (EU replacement)  
- [Apereo CAS](https://github.com/apereo/cas)  

---

*This project is for internal evaluation only. The Trusted List Manager is decommissioned for EU use but remains in use for non-EU countries.*
