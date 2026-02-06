# TL Manager (non-EU) v6 — Deployment and automation

This document describes how **TL Manager non-EU v6** is deployed in this project and what is done **automatically** by Ansible. It complements the PDF guides in `docs/` and the [Deployment Plan](EU-Trusted-List-Manager-Deployment-Plan.md).

Related guides:
- `docs/VM-Deployment-Guide.md` — step-by-step VM install
- `docs/Production-Adjustments.md` — production hardening checklist
- `docs/DSS-and-Signing.md` — DSS relationship and signing summary

---

## Reference documentation (PDF)

| Document | Location | Description |
|----------|----------|-------------|
| **Service Offering Description** | `docs/TL-Manager(ServiceOfferingDescription) (v0.03).pdf` | Purpose, users, roles, access process (EC TLSO). |
| **Installation, Migration & Utilisation guide** | `docs/TLManager Non-EU - V6.0 - Installation, Migration & Utilisation guide 1.pdf` | Installation, migration and usage for non-EU v6.0. |

Official EC page: [TL manager non-EU v6.0](https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0).

---

## Why the official Installation guide doesn't mention the keyStore error

The **CEF eSignature TLManager Non-EU V6 – Installation/Migration and Utilization guide** (e.g. §2.4–2.5) describes:

- Copying the folder **tlmanager-non-eu-config** into the Tomcat installation folder.
- Copying from the release **lib** into Tomcat's **lib**: `application-tlmanager-non-eu-custom.properties`, `proxy.properties`, `logback.xml`, and the MySQL driver.
- Updating **application-tlmanager-non-eu-custom.properties** with CAS URLs, JDBC URL, username and password.

The guide **does not mention** the **signer keystore** or the **keyStore** bean. If you deploy only as described there (no keystore configuration), the application can fail at startup with HTTP 500 and:

`Factory method 'keyStore' threw exception; nested exception is java.lang.NullPointerException` in `BusinessConfig`.

So the error is **not documented** in the official guide; it is a **documentation gap**. The application's `SignersService` (and the `keyStore` bean in `BusinessConfig`) requires a configured keystore path and password. Without them, the bean throws an NPE.

**What this project does:** The Ansible role follows the official layout (Tomcat **lib**, **tlmanager-non-eu-config**) and in addition:

1. Deploys **application-tlmanager-non-eu-custom.properties** into Tomcat **lib** with JDBC, CAS placeholders, **and all signer/keystore properties** (path, password, type, and alternate names the app may use).
2. Ensures the **keystore file** exists (creates a minimal JKS for lab if missing), sets ownership, and patches the WAR's **application.properties** and **setenv.sh** so that the keyStore bean receives the same values even if the app reads from the WAR first.

So we both align with the official deployment structure and fill the missing keystore configuration that the guide omits.

---

## What Ansible does automatically (no manual steps)

Running `ansible-playbook -i inventory playbooks/site.yml` (or `03-tlmanager.yml` for TL Manager only, or `04-cas.yml` for CAS only) performs the following **without manual intervention**:

### Phase 3 — CAS (optional, before or with TL Manager)

- Resolves **CAS WAR** from `packages/cas-server-webapp-4.0.0.war` or extracts it from `packages/TL-NEU-6.0.ZIP` on the controller.
- Copies the WAR to Tomcat `webapps/` as `cas-server-webapp-4.0.0.war` (context path `/cas-server-webapp-4.0.0`).
- Notifies Tomcat to restart so the CAS application is loaded.

Variables: `cas_webapp_context` (default `cas-server-webapp-4.0.0`), optional `cas_war_path` to point to the WAR file on the controller.

### Phase 4 — Application deployment (TL Manager)

- Creates **Tomcat lib** and **tlmanager-non-eu-config** directories (as in the official guide §2.4) and deploys **application-tlmanager-non-eu-custom.properties** into Tomcat **lib** (JDBC, CAS placeholders, and **signer keystore** settings — the latter not mentioned in the guide).
- Resolves the WAR from `packages/` (e.g. `tl-manager-non-eu.war` or from `TL-NEU-6.0.ZIP`).
- Deploys the exploded WAR to Tomcat `webapps/tl-manager-non-eu/`.
- Patches the WAR's `application.properties`: JDBC driver, URL, username, password; Hibernate `hbm2ddl.auto=update`.
- Patches **Linux custom-config paths** (`tsl.folder`, `logs.folder`, `dss.constraint`) and creates the corresponding directories so draft storage works on Linux.
- Copies `tsl-constraint.xml` from the WAR into `/opt/tomcat/custom-config/tsl-constraint.xml` (used by DSS validation).
- Seeds `TL_COUNTRIES` with **ISO 3166‑1 + EU** so the “Select a Country” list is populated and draft import works.
- Deploys `proxy.properties` and patches `application.properties` with all proxy settings (enabled, host, port, user, password, exclude) so the UI starts without proxy.
- Ensures MySQL Connector/J is present: looks for JAR in `/usr/share/java` or Tomcat lib; if missing, installs via dnf or downloads from Maven Central; copies it to `WEB-INF/lib`.
- Sets ownership of the webapp to the `tomcat` user.
- Starts Tomcat and waits for port 8080.

### Signer keystore (required for UI — keyStore bean)

The application's **SignersService** depends on a **signer keystore**. If it is missing, the `keyStore` bean in `BusinessConfig` throws `NullPointerException` and the dispatcher servlet fails (HTTP 500). The role makes this work automatically:

1. **Create directory**  
   Ensures the directory for the keystore exists (e.g. `/opt/tomcat/conf`).

2. **Create minimal JKS keystore**  
   If the keystore file does not exist and `tlmanager_signer_keystore_create` is true (default), runs:
   - `keytool -genkeypair -keystore /opt/tomcat/conf/tlmanager-signer.jks -storepass changeit -keypass changeit -alias tlmanager -dname "CN=TL Manager Lab, O=Lab, C=EU" -validity 3650 -keyalg RSA -keysize 2048`

3. **Set ownership and permissions**  
   Sets the keystore file owner/group to `tomcat` and mode `0600` so Tomcat can read it.

4. **Patch application.properties and setenv.sh**  
   Writes into `application.properties` (and JVM `-D` in `setenv.sh`) so the `keyStore` bean gets path, type and password:
   - `signer.keystore.path`, `signer.keystore.password`; `keystore.path`, `keystore.password`
   - `keystore.filename`, `keystore.type`, `keystore.file` (overrides WAR default)
   - `keyStoreFilename`, `keyStoreType`, `keyStorePassword` (camelCase) and `key-store-filename`, `key-store-type`, `key-store-password` (relaxed binding)

So you do **not** need to run keytool or edit properties by hand for a lab run. For production signing, replace the keystore with your real one (e.g. QSCD export or production JKS) and set `tlmanager_signer_keystore_path` and `tlmanager_signer_keystore_password` (and optionally set `tlmanager_signer_keystore_create: false`).

---

## Post‑deploy prerequisites for Drafts (created/imported TLs)

Two application behaviors must be configured explicitly on Linux after the initial deploy. This repo handles both automatically now, but they are **required** for a functioning UI.

### 1) Country list (TL_COUNTRIES) must be seeded

Symptoms when missing:
- “Select a Country” is empty.
- Importing a TL fails with: **“Scheme Territory … empty or not found in properties.”**

**What this repo does:** seeds the table with **ISO 3166‑1 + EU**.

### 2) Draft storage path must use Linux separators

The WAR ships with Windows‑style defaults:
```
tsl.folder = ${catalina.base}\\custom-config\\tsl
logs.folder = ${catalina.base}\\custom-config\\logs
dss.constraint = ${catalina.base}\\custom-config\\tsl-constraint.xml
```

Symptoms when not fixed:
- “Create an empty draft” or “Import from local file” fails with **Bad Request**.
- Logs show a path like:
  `.../custom-config\tsl/BE/...` and “No such file or directory”.

**What this repo does:** sets Linux paths and creates them:
- `/opt/tomcat/custom-config/tsl`
- `/opt/tomcat/custom-config/logs`
- `/opt/tomcat/custom-config/tsl-constraint.xml` (copied from the WAR)

---

## Functional test steps (lab / acceptance)

Use these steps after initial deploy to verify that the system is operational:

1) **Login**
   - Open TL Manager and authenticate via CAS.

2) **Draft creation**
   - Go to **My Drafts**.
   - Confirm “Select a Country” has entries.
   - Select a country (e.g., **BE**) and click **Create an empty draft**.
   - Verify the draft appears in the list.

3) **Import a TL XML**
   - Click **Import from a local file** and upload `test/BE.xml`.
   - Verify a draft is created and appears in the list.

4) **Open and edit**
   - Open the draft and make a small change (e.g., a label or Scheme Operator Name).
   - Save and confirm no errors.

5) **Check logs**
   - Confirm no errors in `catalina.out` related to draft storage or DSS validation.

---

## Signing workflow (NexU)

NexU steps and UI example are documented in `docs/Signing-Workflow.md`.
NexU is required for in-browser signing and runs on the operator Windows workstation; download links are listed there.

If you prefer not to use NexU, export the TL XML, sign it with an external tool, and import it back into TL Manager.

---

## Production requirements (must do)

**Keys and signing**
- Replace the lab JKS with a **production signing key** (QSCD/HSM or approved keystore).
- Set:
  - `tlmanager_signer_keystore_path`
  - `tlmanager_signer_keystore_password`
  - `tlmanager_signer_keystore_create: false`

**Storage and paths**
- Ensure `/opt/tomcat/custom-config/` is on persistent storage.
- Set strict file permissions for keystore and logs.
- Back up **TSL drafts** and **logs** as part of the runbook.

**Security and compliance**
- Move passwords to **vault** (do not keep in `group_vars`).
- Harden CAS (TLS, IdP, policies) and align certificate hostname.
- Perform security review of **JDK 8** (EOL) and dependencies.

**Operational**
- Monitor Tomcat, MySQL, disk usage, and log rotation.
- Define recovery steps for DB + `custom-config`.

---

## Variables (defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `tlmanager_webapp_context` | `tl-manager-non-eu` | Context path (URL: `/tl-manager-non-eu/`). |
| `tlmanager_signer_keystore_path` | `/opt/tomcat/conf/tlmanager-signer.jks` | Path to signer JKS. |
| `tlmanager_signer_keystore_password` | `changeit` | Keystore (and key) password. |
| `tlmanager_signer_keystore_create` | `true` | Create minimal JKS if missing. |
| `tlmanager_custom_config_dir` | `/opt/tomcat/custom-config` | Base dir for custom-config. |
| `tlmanager_tsl_folder` | `/opt/tomcat/custom-config/tsl` | Draft storage path. |
| `tlmanager_logs_folder` | `/opt/tomcat/custom-config/logs` | TL Manager logs path. |
| `tlmanager_dss_constraint_path` | `/opt/tomcat/custom-config/tsl-constraint.xml` | DSS constraint file path. |
| `tlmanager_seed_countries` | `true` | Seed `TL_COUNTRIES` with ISO 3166‑1 + EU. |
| `tlmanager_seed_countries_sql_path` | `/tmp/tl_countries_iso3166.sql` | Seed SQL location on host. |
| `cas_webapp_context` | `cas-server-webapp-4.0.0` | CAS context path (URL: `/cas-server-webapp-4.0.0/`). |
| `cas_war_path` | (none) | Path to CAS WAR on controller; if unset, role uses `packages/cas-server-webapp-4.0.0.war` or extracts from `packages/TL-NEU-6.0.ZIP`. |
| `tomcat_https_enabled` | `false` | Enable HTTPS connector and generate a JKS keystore. |
| `tomcat_https_port` | `8443` | HTTPS port for Tomcat. |
| `tomcat_https_keystore_path` | `/opt/tomcat/conf/tomcat.jks` | Keystore path used by HTTPS connector. |
| `tomcat_https_keystore_password` | `changeit` | Keystore password for HTTPS connector. |
| `tlmanager_cas_truststore_path` | `/opt/tomcat/conf/cas-truststore.jks` | Truststore for CAS HTTPS certificate. |
| `tlmanager_cas_truststore_password` | `changeit` | Truststore password for CAS HTTPS certificate. |
| `tlmanager_cas_truststore_alias` | `cas-tomcat` | Alias for CAS cert in truststore. |

Credentials for DB and app are taken from `ansible/group_vars/tlmanager/deployment-passwords.yml` (see [Ansible README](../ansible/README.md)).

---

## Operational guides

Operational steps and troubleshooting are maintained in focused guides:

- `docs/VM-Deployment-Guide.md` — install steps, access URLs, bootstrap user, SSH tunnel, common fixes
- `docs/Production-Adjustments.md` — production hardening checklist
- `docs/DSS-and-Signing.md` — DSS relationship and signing summary

---

## See also

- `docs/EU-Trusted-List-Manager-Deployment-Plan.md` — plan, status, and checklists
- `ansible/README.md` — playbooks and variables
- `docs/README.md` — documentation index (all guides and PDFs)
