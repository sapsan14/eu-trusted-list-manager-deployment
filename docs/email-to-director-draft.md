# Draft email to Bart (Director) — Trusted List Manager deployment

**Replace `[YOUR_GITHUB_REPO_URL]` with your actual GitHub repository URL before sending.**

---

**Subject:** Trusted List Manager (EU) — Prerequisites before starting the deployment PoC

---

Dear Bart,

I am preparing to start the Trusted List Manager deployment project (lab PoC for non-EU v6, based on your briefing). Before I can begin the hands-on work, I need your support on the following:

**1. Access to the deployment package (blocker)**  
The application is distributed via the European Commission’s Digital Building Blocks (Nexus). Download requires a **Nexus/DBB account**, and it is unclear how to obtain one. Without this we cannot get `TL-NEU-6.0.ZIP` (or equivalent).  
**Request:** Could we either (a) request Nexus/DBB access via the EC TLSO or DBB contact, or (b) obtain the package internally if ZetesConfidens already has a shared account or can receive it from EC?

**2. Lab VM**  
I need a lab VM with: **2 vCPU, 4 GB RAM, 20 GB disk**, running Rocky Linux 9 (or AlmaLinux 9 / RHEL 9) on the internal/lab network. The PoC does not require access from outside (we only need outbound HTTPS to EC docs and internal use).  
**Option:** I can probably use our **Estonian Test VM** if it meets the spec and is available — our firewall blocks all external ports anyway, so that fits. Using it would **speed up the process** (no VM lead time).  
**Otherwise:** Approval to request a new VM from IT/infra (or via our cloud portal), with hostname e.g. `tl-manager-lab.internal` and SSH (key-based) access; lead time typically **3–10 days**.

**3. Internal DNS (optional but useful)**  
An A record for the lab hostname (e.g. `tl-manager-lab.internal`) would simplify configuration and CAS integration. Lead time **1–3 days** if we have a standard process.  
**Request:** If we have a simple way to request internal DNS, I’d like to include it from the start.

**4. Network**  
The host must be able to reach the EC documentation URLs (outbound HTTPS). The app will remain **internal/lab only** until we have approval for any broader access.

---

**Time estimates (from the plan)**  
- **Hands-on work (once unblocked):** about **5–8 working days** (~24–44 hours) for install, CAS, TL Manager, smoke test, optional signing, and documentation.  
- **Calendar:** Including VM lead time (5–10 days) and Nexus/DBB lead time (1–4 weeks), expect **2–5 weeks** from first request to a working lab, assuming the package is received within that window.

**PoC vs production (clarification)**  
The plan and the items above are **only for the PoC**: get a working lab deployment (VM or Podman, Tomcat + MySQL + CAS + TL Manager), validate end-to-end, and deliver a short **production-readiness evaluation** (what it would take to run this properly in production).  
**Production** steps (TLS, real IdP e.g. company LDAP/OIDC, backups, monitoring, runbook, high availability) are **out of scope** for this phase. They are described in the plan (§11–§12) as follow-up once we decide to move from “lab” to “production-like” after a successful PoC.

---

I have documented the full scope, phases, risks, and step-by-step checklist here:

**[Deployment plan on GitHub]([YOUR_GITHUB_REPO_URL])**

*(I do not have access to Zetes GitLab, so I am keeping the plan and scripts in a personal GitHub repository. I can move or mirror the content to company infrastructure once access is available.)*

Once the package access and VM are in place, I can proceed with the PoC and then share the production-readiness assessment as outlined in the plan.

Best regards,  
Anton
