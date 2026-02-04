# Notes

## Linux version choice for Trusted List Manager

**Official (EC):** The plan states the **official EC stack** as **Debian 12** with OpenJDK 1.8, Tomcat 9.0.102, MySQL 8.0.41 — i.e. the vendor’s documented platform is Debian 12.

**Our plan:** The target OS is an **RHEL derivative** (Rocky Linux 9 / AlmaLinux 9 / RHEL 9) as the corporate standard (Bart’s preference).

**How we determine the choice:**

1. **Source of truth** — The **EC Service Manual (PDF)** linked in §2.1. That document should state which OS the application was tested/supported on (likely Debian 12). That is the “initial requirements” from the vendor. *From our plan (§5), the cited official EC stack is: Debian 12, OpenJDK 1.8, Tomcat 9.0.102, MySQL 8.0.41 — the full manual (PDF) must be checked on EC site for any other requirements.*
2. **What actually matters for the app** — Not the distro per se but the **stack**: Java 8, Tomcat 9, MySQL 8. Those are standard and available on RHEL 9.
3. **Risk in the plan (§7):** “TL Manager not compatible with RHEL/MySQL 8 / Tomcat 9.0.x” — mitigation is already there: if issues appear, test on **Debian 12 in a container** (Podman) first to see if it’s OS-specific.

**Recommendation:**

- **Primary choice:** Use **corporate RHEL (or Rocky 9 / Alma 9)** — aligns with Bart and the plan; same stack versions are available; single platform for automation and support.
- **Verify “initial requirements”:** When you have the package, open the **EC Service Manual** and check the supported/tested platform section; if it says “Debian only”, treat that as the officially recommended environment, but not a hard blocker as long as Java/Tomcat/MySQL versions match.
- **If something breaks on RHEL:** Per the plan, run the same stack on **Debian 12 in Podman** and compare; if it works there and not on RHEL, document it as an RHEL compatibility issue and either fix config/env on RHEL or accept Debian in a container as the supported setup.

**Bottom line:** We decide the Linux version from (1) what the EC Service Manual says (official requirements) and (2) corporate standard (RHEL). **Choice: start with an RHEL derivative; if compatibility issues appear, validate on Debian 12 in a container and document the outcome in the production-readiness assessment.**
