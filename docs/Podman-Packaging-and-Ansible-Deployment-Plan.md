# Podman packaging and Ansible deployment plan

Goal: package the full TL Manager stack as containers and deploy it with Ansible
on a RHEL-family host (Rocky/Alma/RHEL 9). Podman is the runtime; Ansible is
the deployment mechanism.

## How many containers should we have?

Minimum for a self-contained lab stack is **three containers** in a single pod:

1. **tlm-db**: MySQL 8 (data store)
2. **tlm-cas**: Apereo CAS (SSO)
3. **tlm-app**: Tomcat 9 + TL Manager WAR

Optional add-ons:

- **Reverse proxy / TLS** (nginx or apache) if we want one HTTPS endpoint and
  TLS termination. This makes it **four containers**.
- **External services**: If DB or CAS is provided by external infrastructure,
  reduce to **one container** (tlm-app) or **two** (tlm-app + tlm-cas).

This plan targets the 3-container baseline and keeps the proxy optional.

## Container breakdown

| Container | Image source | Role | Ports | Volumes |
|-----------|--------------|------|-------|---------|
| tlm-db | mysql:8 (upstream) | Database | 3306 (internal only) | db data, init scripts |
| tlm-cas | Custom image from CAS overlay (or known CAS image) | SSO | 8080/8443 (internal or proxied) | cas config |
| tlm-app | Custom image: Tomcat 9 + OpenJDK 8 + TL Manager WAR | Web app | 8080 (exposed or proxied) | app config, logs |
| tlm-proxy (optional) | nginx/apache image | TLS termination | 443 (public) | proxy config, certs |

Notes:

- Use a **Podman pod** so containers share a localhost network namespace.
- Only expose the web entrypoint (tomcat or proxy) on the host.
- Keep DB port internal unless needed for debugging.

## Packaging plan (images)

1. **tlm-app image**
   - Base: tomcat:9 + OpenJDK 8 (build your own if no official image exists)
   - Copy TL Manager WAR into webapps/
   - Provide config via environment variables or mounted config files

2. **tlm-cas image**
   - Build from CAS overlay (preferred) to control config
   - Mount minimal application.yml for in-memory users and service registry

3. **tlm-db image**
   - Use upstream mysql:8
   - Mount init SQL to create db/user and any schema if required

## Ansible deployment plan

Use Ansible to build/pull images and run containers. Avoid ad-hoc shell scripts
and ensure idempotency.

**Recommended Ansible structure**

- roles/
  - base_host: install podman, firewalld, dependencies
  - podman_network: create pod and volumes
  - podman_images: build tlm-app and tlm-cas images, pull mysql
  - podman_runtime: run containers with restart policy
  - podman_systemd: generate or manage systemd units (or quadlet)
  - smoke_test: curl TL Manager and CAS endpoints

**Key Ansible modules**

- containers.podman.podman_image
- containers.podman.podman_container
- containers.podman.podman_volume
- containers.podman.podman_pod

**Variables to externalize**

- db_user, db_password, db_name
- cas_server_url, cas_service_url
- tlm_public_url
- podman_image_tags

## Deployment order

1. Provision host and install podman.
2. Create pod, volumes, and config directories.
3. Build/pull images (tlm-app, tlm-cas, mysql).
4. Start tlm-db and wait for readiness.
5. Start tlm-cas.
6. Start tlm-app.
7. Register systemd units for restart on boot.
8. Run smoke tests.

## Decision summary

- **Container count:** 3 required, 4 with optional proxy/TLS.
- **Packaging:** custom images for tlm-app and tlm-cas; upstream mysql image.
- **Deployment:** Ansible using Podman modules with idempotent tasks.
