# Ansible — TL Manager deployment

Automates **Phase 1** (base server), **Phase 2** (Tomcat 9 + MySQL 8), and **Phase 4** (TL Manager WAR + config) from the [deployment plan](../docs/EU-Trusted-List-Manager-Deployment-Plan.md).

## Requirements

- **Control node:** Ansible 2.14+
- **Target:** RHEL 9 (or Rocky Linux 9 / AlmaLinux 9)
- **Collections:** `community.mysql`, `ansible.posix`

Install collections:

```bash
cd ansible && ansible-galaxy collection install -r requirements.yml
```

## Layout

- **roles/**
  - **base_server** — hostname, firewalld, packages (Java 8, git, curl, …), `tomcat` user
  - **tomcat** — Apache Tomcat 9.0.x from tarball, systemd service, MySQL connector JAR
  - **mysql** — MySQL 8 server, database `tlmanager`, user `tlmanager`
  - **tlmanager** — deploy WAR (expanded), `context.xml` (JDBC), `proxy.properties`, patch `application.properties` (JDBC, proxy.*, signer/keystore, hibernate), **create signer keystore** (directory + keytool JKS + ownership), MySQL connector in `WEB-INF/lib`; verifies context startup from catalina.out. See [../docs/TL-Manager-Non-EU-Deployment.md](../docs/TL-Manager-Non-EU-Deployment.md).
- **playbooks/**
  - **site.yml** — full run (base → mysql+tomcat → tlmanager)
  - **01-base.yml**, **02-runtime.yml**, **03-tlmanager.yml** — run phases separately
- **inventory.example** — copy to `inventory` and set host, user
- **group_vars/tlmanager/deployment-passwords.yml** — DB usernames and plain-English passwords for PoC; loaded automatically for `[tlmanager]` hosts so you can run without `-e`
- **.env.example** (repo root) — same passwords in KEY=VALUE form for reference; Ansible does not read `.env`

## Quick start

1. **Package:** Put `TL-NEU-6.0.ZIP` in the repo **`packages/`** directory (or a `.war` file there).

2. **Inventory:** Copy and edit:
   ```bash
   cp ansible/inventory.example ansible/inventory
   # Edit ansible/inventory: set your VM hostname/IP and ansible_user (no passwords needed)
   ```

3. **Credentials (PoC / automatic deployment):** DB usernames and passwords are in **`ansible/group_vars/tlmanager/deployment-passwords.yml`** (e.g. user `tlmanager`, password `TrustedListManagerDatabasePassword`). Loaded automatically — no `-e` needed. To change user or password, edit that file. See **`.env.example`** in repo root for the same values in KEY=VALUE form. For production, use vault or `-e` and do not commit real secrets.

4. **Run** (from repo root or from `ansible/`):
   ```bash
   ansible-galaxy collection install -r ansible/requirements.yml
   cd ansible && ansible-playbook -i inventory playbooks/site.yml
   ```
   Or run phase by phase (no password args; they come from group_vars):
   ```bash
   cd ansible
   ansible-playbook -i inventory playbooks/01-base.yml
   ansible-playbook -i inventory playbooks/02-runtime.yml
   ansible-playbook -i inventory playbooks/03-tlmanager.yml
   ```
   To fix “Access denied” for user `tlmanager`: re-run so MySQL and the app get the same password from group_vars:
   ```bash
   ansible-playbook -i inventory playbooks/02-runtime.yml   # updates MySQL user password
   ansible-playbook -i inventory playbooks/03-tlmanager.yml # updates app and restarts Tomcat
   ```

5. **After run:** Tomcat listens on port **8080**. Open `http://<your-vm>:8080/` (or the context you set).  
   **CAS** is not installed by these playbooks; add Phase 3 (CAS) manually or a separate role, then set `tlmanager_cas_server_url` and `tlmanager_cas_service_url`.

## Variables (main)

| Variable | Role | Default | Description |
|----------|------|---------|-------------|
| `base_hostname` | base_server | `tl-manager-lab.internal` | Hostname to set |
| `mysql_tlmanager_user` | mysql | `tlmanager` (in deployment-passwords.yml) | MySQL user for DB `tlmanager` |
| `tlmanager_db_user` | tlmanager | same | JDBC username (must match MySQL user) |
| `mysql_tlmanager_password` | mysql | from `group_vars/tlmanager/deployment-passwords.yml` | Password for DB user |
| `tlmanager_db_password` | tlmanager | same file | Same value (JDBC in context.xml and application.properties) |
| `tlmanager_war_path` | tlmanager | (auto from packages/) | Path to WAR on controller; else uses `packages/*.war` or extracts from `packages/TL-NEU-6.0.ZIP` |
| `tlmanager_webapp_context` | tlmanager | `ROOT` | Context path: `ROOT` → `/`, or `tlmanager` → `/tlmanager` |

For PoC, passwords live in `group_vars/tlmanager/deployment-passwords.yml` (plain English). For production, use vault or `-e` and do not commit that file with real secrets.

## Troubleshooting

**`curl localhost:8080` → Connection refused**

- Role **tomcat** leaves the service **stopped** (so the WAR can be deployed first). Role **tlmanager** starts Tomcat at the end. If you ran only `02-runtime.yml` or Tomcat was restarted/rebooted and failed to start, the service may be down.
- On the target VM:
  ```bash
  sudo systemctl status tomcat
  sudo systemctl start tomcat
  ```
- If it fails to start, check logs (often JDBC/context.xml or missing DB):
  ```bash
  sudo journalctl -u tomcat -n 80 --no-pager
  sudo tail -100 /opt/tomcat/logs/catalina.out
  ```
- Then check that port 8080 is listening: `sudo ss -tlnp | grep 8080`.

**`JDBC Driver class not found` / `Unable to load class []`**

- The app reads `jdbc.driverClassName`, `jdbc.url`, etc. from `WEB-INF/classes/application.properties` (empty in the WAR). The role patches these with `replace` and adds `setenv.sh` for JVM `-D`. Re-run the playbook so the patch is applied; the playbook then checks catalina.out and fails if the context still reports startup failure.

**`Access denied for user 'tlmanager'@'localhost' (using password: YES)`**

- The app connects to MySQL with `jdbc.username` / `jdbc.password` from `application.properties`. Those are set from `tlmanager_db_user` / `tlmanager_db_password` when you run the playbook. The MySQL user `tlmanager` is created by the **mysql** role with `mysql_tlmanager_password`. Both must match. Re-run the playbook with the same password you used when creating the DB: `-e mysql_tlmanager_password=YOUR_PASS -e tlmanager_db_password=YOUR_PASS`. Or set the MySQL user password to match what you pass: `sudo mysql -e "ALTER USER 'tlmanager'@'localhost' IDENTIFIED BY 'YourPass'; FLUSH PRIVILEGES;"`, then restart Tomcat.

**`proxy.properties` cannot be opened** / **Could not resolve placeholder 'proxy.http.enabled'**

- The TL Manager app (ProxyConfiguration) requires proxy settings. The role deploys `proxy.properties` in `WEB-INF/classes/` and **also patches `application.properties`** with `proxy.http.enabled=false` and `proxy.https.enabled=false` so Spring resolves these placeholders even when loading order differs. Re-run the tlmanager playbook so the app is redeployed with both files:
  `ansible-playbook -i inventory playbooks/03-tlmanager.yml`
  (Passwords from `group_vars/tlmanager/deployment-passwords.yml` if needed.)

**HTTP 500 – keyStore NullPointerException / Servlet [dispatcher] threw exception**

- The app’s `SignersService` needs a **signer keystore** (path + password). If missing, the `keyStore` bean in `BusinessConfig` throws `NullPointerException` and the dispatcher servlet fails to start.
- The **tlmanager** role can create a **minimal JKS keystore** for lab use and set `signer.keystore.path` / `signer.keystore.password` (and `keystore.path` / `keystore.password`) in `application.properties`. Run the playbook again so these are applied:
  `ansible-playbook -i inventory playbooks/03-tlmanager.yml`
- Defaults: keystore path `/opt/tomcat/conf/tlmanager-signer.jks`, password `changeit`. Override with `tlmanager_signer_keystore_path`, `tlmanager_signer_keystore_password` in inventory or group_vars. For real signing (e.g. QSCD), replace this keystore with your production one and set the same properties.

**HTTP 404 – Not Found on `/login`**

- The app redirects to the CAS login page; if CAS is not deployed, you get 404 on `/login`. See [TL-Manager-Non-EU-Deployment.md](../docs/TL-Manager-Non-EU-Deployment.md) section "HTTP 404 – Not Found on /login (CAS not deployed)": deploy Apereo CAS (or EC CAS WAR) and set `tlmanager_cas_server_url` and `tlmanager_cas_service_url` to match (e.g. when using an SSH tunnel, use the tunnel host/port in both URLs). Re-run the playbook after changing these vars.

## Optional

- **base_install_podman** (default: false) — set to `true` in inventory or vars to install Podman on the host.
- **CAS:** After deploying a minimal Apereo CAS (Phase 3), set `tlmanager_cas_server_url` and `tlmanager_cas_service_url`; the current `context.xml` only configures JDBC; CAS is often configured in the app’s own properties.
