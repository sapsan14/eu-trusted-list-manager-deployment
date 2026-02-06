# EU Trusted List Manager — Deployment

Lab deployment and evaluation of the **European Commission’s Trusted List Manager** (non-EU v6) on Red Hat–family Linux (VM or Podman). Goal: get a working setup and assess production-readiness for non-EU Trusted List Operators.

**Owner:** Anton Sokolov · **Stakeholder:** Bart / ZetesConfidens Trust Services

---

## What’s in this repo

| Path | Description |
| --- | --- |
| [docs/EU-Trusted-List-Manager-Deployment-Plan.md](docs/EU-Trusted-List-Manager-Deployment-Plan.md) | **Main plan:** scope, resource ordering, time estimates, risks, checklists, LLM prompts. Includes current status and English source of truth. |
| [docs/EU-Trusted-List-Manager-Deployment-Plan-RU.md](docs/EU-Trusted-List-Manager-Deployment-Plan-RU.md) | Russian translation of the main plan (kept in sync with the English version). |
| [docs/TL-Manager-Non-EU-Deployment.md](docs/TL-Manager-Non-EU-Deployment.md) | What Ansible automates, keyStore gap explained, post‑deploy prerequisites, variables reference. |
| [docs/Signing-Workflow.md](docs/Signing-Workflow.md) | NexU signing steps (Windows) with download links and UI example. |
| [docs/VM-Deployment-Guide.md](docs/VM-Deployment-Guide.md) | VM install guide, access URLs, bootstrap user, SSH tunnel, common fixes. |
| [docs/Production-Adjustments.md](docs/Production-Adjustments.md) | Production hardening checklist and required adjustments. |
| [docs/DSS-and-Signing.md](docs/DSS-and-Signing.md) | DSS relationship and Trusted List signing summary. |
| [docs/README.md](docs/README.md) | Documentation index (all guides and PDFs). |
| `docs/TL-Manager(ServiceOfferingDescription) (v0.03).pdf` | EC **Service Offering Description** (SOD) for TL Manager (purpose, roles, access); **no OS/stack requirements** inside. |
| `ansible/` | Ansible roles and playbooks for **Phase 1** (base server), **Phase 2** (Tomcat + MySQL), **Phase 4** (TL Manager). See `ansible/README.md`. |
| `scripts/` | Automation helpers (e.g. Confluence upload, future smoke tests/env checks). |

---

## Docs map

- Start here: [docs/EU-Trusted-List-Manager-Deployment-Plan.md](docs/EU-Trusted-List-Manager-Deployment-Plan.md)
- VM lab runbook: [docs/VM-Deployment-Guide.md](docs/VM-Deployment-Guide.md)
- Automation details: [docs/TL-Manager-Non-EU-Deployment.md](docs/TL-Manager-Non-EU-Deployment.md)
- Production hardening: [docs/Production-Adjustments.md](docs/Production-Adjustments.md)
- DSS and signing: [docs/DSS-and-Signing.md](docs/DSS-and-Signing.md)
- Full docs index: [docs/README.md](docs/README.md)

---

## Quick start

1. **Read the plan:** [docs/EU-Trusted-List-Manager-Deployment-Plan.md](docs/EU-Trusted-List-Manager-Deployment-Plan.md) — single source of truth for scope (Bart’s briefing), resource ordering, and step-by-step checklists (EN + RU).
2. **Status / inputs:**
   - TL Manager package **TL-NEU-6.0.ZIP** is stored locally in `packages/`.
   - Target OS is **RHEL 9 from the start** (Bart), see plan §5 and §6.4.
   - Nexus/DBB account is **only needed for TL Signing Tool**, not for TL Manager package (see plan §3–§4).
3. **Prepare lab VM (Phase 1):**
   - Install **RHEL 9** on the VM (2 vCPU, 4 GB RAM, 20 GB disk, internal network).
   - Ensure you have SSH access from your control node (your laptop / Ansible host).
4. **Automate with Ansible (Phases 1, 2, 4):**
   - See [`ansible/README.md`](ansible/README.md) for roles and commands.
   - Typical run (from `ansible/`):  
     `ansible-galaxy collection install -r requirements.yml`  
     `ansible-playbook -i inventory playbooks/site.yml -e mysql_tlmanager_password=SECRET -e tlmanager_db_password=SECRET`
5. **Continue manually where needed:**
   - **Phase 3 (CAS)** — minimal Apereo CAS deployment is still manual / separate.
   - **Phase 5–7** — validation, optional signing test, documentation, and production-readiness evaluation (§11).
6. **Post‑deploy prerequisites:** see [docs/TL-Manager-Non-EU-Deployment.md](docs/TL-Manager-Non-EU-Deployment.md) for draft storage paths and country‑seed requirements (now automated).
7. **Operational guides:**
   - [docs/VM-Deployment-Guide.md](docs/VM-Deployment-Guide.md)
   - [docs/Production-Adjustments.md](docs/Production-Adjustments.md)

---

## Stack (target)

- **OS:** **RHEL 9** (or Rocky Linux 9 / AlmaLinux 9 as RHEL-equivalent; Bart: \"RHEL 9 from the start\")  
- **Runtime:** OpenJDK 8, Apache Tomcat 9, MySQL 8  
- **Auth:** Apereo CAS (minimal config)  
- **Deploy:** Single VM or Podman containers  

---

## SSH access to the lab VM (RHEL 9)

**Enable and start sshd:**

```bash
sudo dnf install -y openssh-server
sudo systemctl enable sshd
sudo systemctl start sshd
sudo systemctl status sshd
```

**Open SSH in firewalld:**

```bash
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
sudo firewall-cmd --list-services
```

**(Recommended) Use SSH public key auth:**

On the **controller** (your machine / laptop):

```bash
ssh-keygen -t ed25519 -C \"tl-manager-lab\"   # if you do not have a key yet
cat ~/.ssh/id_ed25519.pub
```

On the **RHEL 9 VM** under the user you will use as `ansible_user`:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo 'PASTE_YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

After that, login is simpler:

```bash
ssh <user>@tl-manager-lab.internal
```

Password login can remain enabled for the first steps, or be disabled later in `/etc/ssh/sshd_config` (`PasswordAuthentication no`) after you confirm key login works.

---

## References

- [TL Manager non-EU v6](https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0)  
- [eIDAS Dashboard](https://eidas.ec.europa.eu/efda/home) (EU replacement)  
- [Apereo CAS](https://github.com/apereo/cas)  

---

*This project is for internal evaluation only. The Trusted List Manager is decommissioned for EU use but remains in use for non-EU countries.*
