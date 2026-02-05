# TL Manager (non-EU) v6 — Deployment and automation

This document describes how **TL Manager non-EU v6** is deployed in this project and what is done **automatically** by Ansible. It complements the PDF guides in `docs/` and the [Deployment Plan](EU-Trusted-List-Manager-Deployment-Plan.md).

---

## Reference documentation (PDF)

| Document | Location | Description |
|----------|----------|-------------|
| **Service Offering Description** | `docs/TL-Manager(ServiceOfferingDescription) (v0.03).pdf` | Purpose, users, roles, access process (EC TLSO). |
| **Installation, Migration & Utilisation guide** | `docs/TLManager Non-EU - V6.0 - Installation, Migration & Utilisation guide 1.pdf` | Installation, migration and usage for non-EU v6.0. |

Official EC page: [TL manager non-EU v6.0](https://ec.europa.eu/digital-building-blocks/sites/spaces/TLSO/pages/920062707/TL+manager+non-EU+v6.0).

---

## Why the official Installation guide doesn’t mention the keyStore error

The **CEF eSignature TLManager Non-EU V6 – Installation/Migration and Utilization guide** (e.g. §2.4–2.5) describes:

- Copying the folder **tlmanager-non-eu-config** into the Tomcat installation folder.
- Copying from the release **lib** into Tomcat’s **lib**: `application-tlmanager-non-eu-custom.properties`, `proxy.properties`, `logback.xml`, and the MySQL driver.
- Updating **application-tlmanager-non-eu-custom.properties** with CAS URLs, JDBC URL, username and password.

The guide **does not mention** the **signer keystore** or the **keyStore** bean. If you deploy only as described there (no keystore configuration), the application can fail at startup with HTTP 500 and:

`Factory method 'keyStore' threw exception; nested exception is java.lang.NullPointerException` in `BusinessConfig`.

So the error is **not documented** in the official guide; it is a **documentation gap**. The application’s `SignersService` (and the `keyStore` bean in `BusinessConfig`) requires a configured keystore path and password. Without them, the bean throws an NPE.

**What this project does:** The Ansible role follows the official layout (Tomcat **lib**, **tlmanager-non-eu-config**) and in addition:

1. Deploys **application-tlmanager-non-eu-custom.properties** into Tomcat **lib** with JDBC, CAS placeholders, **and all signer/keystore properties** (path, password, type, and alternate names the app may use).
2. Ensures the **keystore file** exists (creates a minimal JKS for lab if missing), sets ownership, and patches the WAR’s **application.properties** and **setenv.sh** so that the keyStore bean receives the same values even if the app reads from the WAR first.

So we both align with the official deployment structure and fill the missing keystore configuration that the guide omits.

---

## What Ansible does automatically (no manual steps)

Running `ansible-playbook -i inventory playbooks/03-tlmanager.yml` (or `site.yml`) performs the following **without manual intervention**:

### Application deployment

- Creates **Tomcat lib** and **tlmanager-non-eu-config** directories (as in the official guide §2.4) and deploys **application-tlmanager-non-eu-custom.properties** into Tomcat **lib** (JDBC, CAS placeholders, and **signer keystore** settings — the latter not mentioned in the guide).
- Resolves the WAR from `packages/` (e.g. `tl-manager-non-eu.war` or from `TL-NEU-6.0.ZIP`).
- Deploys the exploded WAR to Tomcat `webapps/tl-manager-non-eu/`.
- Patches the WAR’s `application.properties`: JDBC driver, URL, username, password; Hibernate `hbm2ddl.auto=update`.
- Deploys `proxy.properties` and patches `application.properties` with all proxy settings (enabled, host, port, user, password, exclude) so the UI starts without proxy.
- Ensures MySQL Connector/J is present: looks for JAR in `/usr/share/java` or Tomcat lib; if missing, installs via dnf or downloads from Maven Central; copies it to `WEB-INF/lib`.
- Sets ownership of the webapp to the `tomcat` user.
- Starts Tomcat and waits for port 8080.

### Signer keystore (required for UI — keyStore bean)

The application’s **SignersService** depends on a **signer keystore**. If it is missing, the `keyStore` bean in `BusinessConfig` throws `NullPointerException` and the dispatcher servlet fails (HTTP 500). The role makes this work automatically:

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

## Variables (defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `tlmanager_webapp_context` | `tl-manager-non-eu` | Context path (URL: `/tl-manager-non-eu/`). |
| `tlmanager_signer_keystore_path` | `/opt/tomcat/conf/tlmanager-signer.jks` | Path to signer JKS. |
| `tlmanager_signer_keystore_password` | `changeit` | Keystore (and key) password. |
| `tlmanager_signer_keystore_create` | `true` | Create minimal JKS if missing. |

Credentials for DB and app are taken from `ansible/group_vars/tlmanager/deployment-passwords.yml` (see [Ansible README](../ansible/README.md)).

---

## After deployment

- **URL:** `http://<host>:8080/tl-manager-non-eu/` (with trailing slash). Via SSH tunnel use `-L 8080:localhost:8080` so redirects work.
- **CAS:** Not installed by these playbooks; configure separately and set CAS URLs in app config if required.
- **Signing:** The auto-created keystore is for lab (UI starts). Use a real keystore or QSCD for actual signing.

---

## Troubleshooting

### HTTP 500 — keyStore NullPointerException (BusinessConfig.java:78)

If the dispatcher servlet fails with `Factory method 'keyStore' threw exception; nested exception is java.lang.NullPointerException`:

1. **Ensure only our keystore values are used**  
   The WAR may contain `keystore.password = dss-password` (with spaces). Re-run the playbook so that the role **replaces** any such line with `keystore.password=changeit`. Then check:
   ```bash
   sudo grep -E 'signer\.keystore|keystore\.(path|password)' /opt/tomcat/webapps/tl-manager-non-eu/WEB-INF/classes/application.properties
   ```
   You should see a single `keystore.password=changeit` (no `keystore.password = dss-password`). Paths should be `/opt/tomcat/conf/tlmanager-signer.jks`.

2. **Enable DEBUG for the config package**  
   To see which property values are injected into the `keyStore` bean, add a logger for the business config package. If the app uses Logback (e.g. `WEB-INF/classes/logback.xml` or `logback-spring.xml`), add inside `<configuration>`:
   ```xml
   <logger name="eu.europa.ec.joinup.tsl.business.config" level="DEBUG"/>
   ```
   Restart Tomcat and reproduce the error; then check `/opt/tomcat/logs/catalina.out` (or the app’s log file) for DEBUG lines from `BusinessConfig` showing the path/password values (or their absence). If there is no `logback.xml`, check for `log4j2.xml` or `application.properties` logging settings and set the same logger to DEBUG there.

3. **Verify keystore file**  
   ```bash
   sudo ls -la /opt/tomcat/conf/tlmanager-signer.jks
   ```
   Must be readable by `tomcat` (owner/group and mode `0600` or `0640`).

4. **If it still fails — capture effective config**  
   Re-run the playbook with **`-v`** so Ansible prints the *Effective keystore/signer lines* it wrote. On the server you can also run:
   ```bash
   grep -E 'keystore|signer\.keystore' /opt/tomcat/webapps/tl-manager-non-eu/WEB-INF/classes/application.properties
   cat /opt/tomcat/bin/setenv.sh
   ```
   Confirm paths point to the real JKS and there is no `keystore.password = dss-password`.

5. **Inspect which property names the app expects**  
   The NPE is in `BusinessConfig` (line 78). To see the **exact** `@Value("${...}")` keys the class uses, extract the WAR and decompile the bean class, e.g.:
   ```bash
   unzip -l tl-manager-non-eu.war | grep BusinessConfig
   unzip -p tl-manager-non-eu.war WEB-INF/classes/eu/europa/ec/joinup/tsl/business/config/BusinessConfig.class > /tmp/BusinessConfig.class
   javap -v /tmp/BusinessConfig.class | grep -A1 "RuntimeVisibleAnnotations"
   ```
   Or use a decompiler (e.g. CFR, Procyon) on that `.class` and search for `keyStore` and `@Value`. Then add the missing property name to the Ansible role (e.g. in `ansible/roles/tlmanager/tasks/main.yml` and `templates/setenv.sh.j2`).

### Playbook fails: "Context failed to start"

When the role detects that the Tomcat context did not start (e.g. "Context [/tl-manager-non-eu] startup failed" in `catalina.out`), it **prints an excerpt of catalina.out around that line** (about 120 lines before and 10 after) so you see the **real exception and stack trace**, not the C3P0 connection-pool DEBUG noise that often fills the end of the log. Use that excerpt to fix the cause (missing bean, JDBC, placeholder, keyStore, etc.). **Adding CAS will not fix this** — the application must start successfully first; CAS is only for login after the app is running.

### SSH tunnel: app path does not respond (root works)

If the tunnel uses a different local port than 8080, the app may redirect to port 8080 and the browser then tries your local 8080 (not the tunnel). Use **`ssh -L 8080:localhost:8080`** and open `http://localhost:8080/tl-manager-non-eu/`.

### HTTP 404 – Not Found on `/login` (CAS not deployed)

**Symptom:** You open the TL Manager URL and get redirected to `/login?service=...`, then 404.

Then Tomcat returns **404 – The requested resource [/login] is not available**.

**Cause:** TL Manager uses **Spring Security with CAS** (Central Authentication Service). Unauthenticated users are sent to the CAS server’s **login page**. That login page is **not** part of TL Manager — it is served by a separate **CAS** webapp (e.g. Apereo CAS). The playbooks **do not deploy CAS** (see [Deployment Plan](EU-Trusted-List-Manager-Deployment-Plan.md) Phase 3). So there is no application at `/login` on your Tomcat → 404.

**What to do:**

1. **Deploy CAS** (recommended for real use)  
   - Deploy Apereo CAS (or the CAS WAR from the EC package, if provided) on the **same** Tomcat or on another host.  
   - Typical context for CAS: e.g. `/cas` or `/cas-server-webapp-4.0.0`, so the login URL is `http://<host>:<port>/cas-server-webapp-4.0.0/login`.  
   - Configure TL Manager so it points to that URL via `casServerUrl` and `casServiceUrl` (see below).

2. **Set CAS URLs to match how you access the app**  
   The app reads `casServerUrl` and `casServiceUrl` from `application-tlmanager-non-eu-custom.properties` (in Tomcat `lib/`). Defaults in the role are:
   - `tlmanager_cas_server_url: "http://localhost:8080/cas-server-webapp-4.0.0"`
   - `tlmanager_cas_service_url: "http://localhost:8080/tl-manager-non-eu"`

   If you use an SSH tunnel, set both URLs to the host and port the browser uses (e.g. `http://localhost:8080/...` when using `-L 8080:localhost:8080`), or use the real hostname (e.g. `http://tl-manager-lab.internal:8080/...`).

   After changing these variables, re-run the playbook so the custom properties file is updated, then restart Tomcat.

3. **Lab without CAS**  
   The application is designed to use CAS; there is no “disable CAS” option in the current Ansible role or in the official guide. To get a working UI without deploying full CAS, you would need to change the app’s security configuration (e.g. form login) inside the WAR or via a profile — that is outside the scope of this deployment.

**Summary:** 404 on `/login` means “CAS login page not found”. Deploy CAS at the URL you set in `casServerUrl`, and set both `casServerUrl` and `casServiceUrl` to the same host/port you use in the browser (including when using an SSH tunnel).

---

## See also

- [EU-Trusted-List-Manager-Deployment-Plan.md](EU-Trusted-List-Manager-Deployment-Plan.md) — full plan, phases, risks, references.
- [ansible/README.md](../ansible/README.md) — how to run playbooks, variables, troubleshooting.
