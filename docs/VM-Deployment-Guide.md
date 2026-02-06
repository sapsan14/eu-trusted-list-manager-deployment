# TL Manager (non-EU) v6 — VM deployment guide

This guide is a VM-focused runbook for the **Ansible-based** deployment.

Related guides:
- [TL Manager Non‑EU Deployment and Automation](TL-Manager-Non-EU-Deployment.md) — what Ansible automates and variable defaults
- [Production Adjustments](Production-Adjustments.md) — production hardening checklist
- [DSS and Signing](DSS-and-Signing.md) — DSS relationship and signing summary

## Prerequisites

- RHEL 9 (or Rocky/Alma 9) VM with SSH access.
- Package: `packages/TL-NEU-6.0.ZIP` (or a TL Manager WAR) in repo root.
- Ansible 2.14+ on the control machine.

## Inventory (minimal)

`ansible/inventory`:
```
[tlmanager]
tl-manager-lab.internal ansible_connection=ssh ansible_user=anton

[tlmanager:vars]
base_hostname=tl-manager-lab.internal

# Enable HTTPS for CAS SSO
tomcat_https_enabled=true
# CAS URLs must match the HTTPS certificate hostname
tlmanager_cas_server_url=https://tl-manager-lab.internal:8443/cas-server-webapp-4.0.0
tlmanager_cas_service_url=https://tl-manager-lab.internal:8443/tl-manager-non-eu

# Bootstrap user (optional)
tlmanager_bootstrap_user_ecas_id=test
tlmanager_bootstrap_user_name=Test
tlmanager_bootstrap_role_code=SUP
```

## First install (VM)

From `ansible/`:
```
ansible-galaxy collection install -r requirements.yml
ansible-playbook -i inventory playbooks/site.yml
```

Or phase-by-phase:
```
ansible-playbook -i inventory playbooks/01-base.yml
ansible-playbook -i inventory playbooks/02-runtime.yml
ansible-playbook -i inventory playbooks/04-cas.yml
ansible-playbook -i inventory playbooks/03-tlmanager.yml
ansible-playbook -i inventory playbooks/05-bootstrap-user.yml
```

## Access URLs

- HTTP: `http://<host>:8080/tl-manager-non-eu/`
- HTTPS: `https://<host>:8443/tl-manager-non-eu/`

CAS login (default EC CAS WAR): `test` / `password`.

## SSH tunnel (local access)

```
ssh -L 8443:localhost:8443 anton@tl-manager-lab.internal
```
Add a local hostname so the certificate matches:
```
127.0.0.1 tl-manager-lab.internal
```
Then open:
```
https://tl-manager-lab.internal:8443/tl-manager-non-eu/
```

## Common issues

- **CAS redirects to HTTP:** set HTTPS URLs in inventory and re-run `03-tlmanager.yml`.
- **PKIX errors:** run `03-tlmanager.yml` (truststore is generated automatically).
- **Unauthorized after login:** run `05-bootstrap-user.yml` and/or map the CAS user to a role.

## See also

- [TL Manager Non‑EU Deployment and Automation](TL-Manager-Non-EU-Deployment.md) — full automation details and variables
- [Production Adjustments](Production-Adjustments.md) — production hardening checklist
- [DSS and Signing](DSS-and-Signing.md) — DSS relationship and signing summary
