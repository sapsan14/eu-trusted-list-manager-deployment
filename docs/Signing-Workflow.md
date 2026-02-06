# Signing workflow (NexU)

TL Manager uses **NexU** for local signing with smart cards/USB tokens/HSM (PKCS#11).

**Download NexU:** [https://github.com/nowina-solutions/nexu](https://github.com/nowina-solutions/nexu)

## Where NexU must run

NexU must run on the **same machine as the browser** used to sign in TL Manager.
If you run the UI from the RHEL9 VM console, install NexU on that VM.
If you access the UI from your workstation, install NexU on the workstation instead.

## Minimal setup — Windows

1) Download the latest NexU release (installer or ZIP) from the releases page.  
2) Install and start NexU (it runs locally in the system tray).  
3) Install the vendor driver/middleware for your token (PKCS#11).  
4) Verify the token is visible to the OS and NexU is running.  
5) In TL Manager, open a draft and click **Sign**.

## Minimal setup — Linux

1) Download the latest NexU release (ZIP) from the releases page.  
2) Run NexU (Java required; start script provided in the release).  
3) Install the vendor PKCS#11 module for your token/HSM.  
4) Verify the token is visible (e.g., with vendor tools).  
5) In TL Manager, open a draft and click **Sign**.

## Example step (UI)

When NexU is not running, TL Manager shows the following message:

![NexU required message](../assets/c__Users_anton.sokolov_AppData_Roaming_Cursor_User_workspaceStorage_c046dcfb97636f2e59014e96a0defae2_images_image-028edccc-779f-4786-808e-ffd27c3d38a2.png)

If you prefer not to use NexU, export the TL XML, sign it with an external tool, and import it back into TL Manager.

## Emulator option (SoftHSM2)

If the physical USB token is not yet available, you can test with **SoftHSM2**:

1) Install SoftHSM2 and OpenSC (PKCS#11 tools).  
2) Create a test token and key pair.  
3) Start NexU and ensure it can access the PKCS#11 module.  
4) Sign from TL Manager via NexU and document the result.

The Ansible playbook `ansible/playbooks/06-signing-tools.yml` automates package installation and optional SoftHSM token creation.
