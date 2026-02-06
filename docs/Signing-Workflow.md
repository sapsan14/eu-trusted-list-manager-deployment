# Signing workflow (NexU)

TL Manager uses **NexU** for local signing with smart cards/USB tokens (PKCS#11).
NexU is **required** for in-browser signing from TL Manager.

**Download NexU:**

- Main download page: [https://lab.nowina.solutions/nexu-demo/download-nexu](https://lab.nowina.solutions/nexu-demo/download-nexu)
- Windows bundle 1.22: [https://code.europa.eu/qualifications-courses-and-credentials/european-digital-credentials/-/blob/master/nexu-bundle-1.22.zip](https://code.europa.eu/qualifications-courses-and-credentials/european-digital-credentials/-/blob/master/nexu-bundle-1.22.zip)

The 1.22 bundle is Windows-only; for non-Windows environments, use external signing.

## Where NexU must run

NexU must run on the **same machine as the browser** used to sign in TL Manager.
In our setup, this is the operator **Windows workstation**, not the server VM.

## Minimal setup — Windows

1) Download NexU from the links above (ZIP or installer).  
2) Install and start NexU (it runs locally in the system tray).  
3) Install the vendor driver/middleware for your token (PKCS#11).  
4) Verify the token is visible to the OS and NexU is running.  
5) In TL Manager, open a draft and click **Sign**.

## Example step (UI)

When NexU is not running, TL Manager shows the following message:

![NexU required message](../assets/c__Users_anton.sokolov_AppData_Roaming_Cursor_User_workspaceStorage_c046dcfb97636f2e59014e96a0defae2_images_image-028edccc-779f-4786-808e-ffd27c3d38a2.png)

If you prefer not to use NexU, export the TL XML, sign it with an external tool, and import it back into TL Manager.
