# DSS and Trusted List signing

This note answers: **“Is EU Trust List Manager using DSS? And can you sign with TL Manager?”**

## ✅ 1. Does the EU Trust List Manager use DSS?
Yes. The official TL Manager release notes show updates tied to DSS, e.g. **“Update to DSS 5.0”**, which indicates TL Manager integrates DSS components.  
Source: EC TLSO Community – Trusted List Manager release notes.  
[https://ec.europa.eu/digital-building-blocks/sites/display/TLSO/Trusted+List+Manager](https://ec.europa.eu/digital-building-blocks/sites/display/TLSO/Trusted+List+Manager?src=contextnavpagetreemode)

## ✅ 2. Can DSS sign Trusted Lists (TSL)?
Yes. DSS provides a **Trusted List signature REST API** that explicitly **“Signs the XML Trusted List with the provided signatureValue.”**  
Source: DSS REST API (Trusted List signature service).  
[https://ec.europa.eu/digital-building-blocks/DSS/webapp-demo/apidocs/eu/europa/esig/dss/ws/signature/rest/client/RestTrustedListSignatureService.html](https://ec.europa.eu/digital-building-blocks/DSS/webapp-demo/apidocs/eu/europa/esig/dss/ws/signature/rest/client/RestTrustedListSignatureService.html)

## ✅ 3. Can TL Manager sign TSLs?
Technically **yes**, but **only when you supply your own signing key** and configure the signer.  
TL Manager relies on DSS signing operations (see above), which require a **signature value** to be provided by your own key/token.

## ❗ Important note about signing keys
DSS is the signing engine and does **not** provide keys. You must supply and manage the signing material (QSCD or approved keys).  
The official DSS source repository is:  
[https://github.com/esig/dss](https://github.com/esig/dss)

## 🔍 Summary

| Question | Answer |
|---|---|
| Does EU TL Manager use DSS? | Yes — TL Manager releases include DSS updates (e.g. “Update to DSS 5.0”). |
| Can DSS sign TSL files? | Yes — DSS provides a Trusted List signing REST API. |
| Can TL Manager sign TSLs? | Yes, if you configure a signing key/token. |
| Does DSS provide keys? | No — you must supply and manage keys. |
