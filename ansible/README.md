# Ansible

Place here:

- **Base server:** playbook for hostname, firewall, OpenJDK 8, Tomcat user (see deployment plan §10 Prompt 1).
- **Tomcat + MySQL:** tasks for Tomcat 9, MySQL 8, DB and user creation, MySQL connector (see plan §10 Prompt 2).
- **CAS:** optional role or playbook for minimal Apereo CAS (see plan §10 Prompt 4).
- **TL Manager config:** template for `context.xml` or app properties (see plan §10 Prompt 5).
- **Podman stack:** playbook/role that creates pod, volumes, images, and runs
  tlm-app, tlm-db, and tlm-cas containers (see Podman plan doc).

Use variables for DB password, CAS URL, and TL Manager URL; keep secrets in vault or `.env` (not committed).
