# Idira Central Credential Provider (CCP) — Development Guide

**Workflow:** Secrets Management  
**Integration:** Central Credential Provider (CCP)  
**Type:** Development Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.1  
**Last Updated:** 2026-09-30

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Central Credential Provider (CCP) — agentless secret retrieval from the Idira Vault.
WORKFLOW: Secrets Management
USE CASE: Central Credential Provider — an application retrieves a secret from the Idira Vault over
  the network, with no agent on the application's own machine.
INTEGRATION PATTERN: REST. A single GET against an IIS-hosted web service the customer deploys on
  their own network. There is no SDK and no SaaS endpoint.
AUTH METHOD: Application authentication, configured server-side — NOT a token flow (see Section 7)
AUTH HEADER FORMAT: NONE. There is no Authorization header and no bearer token anywhere in this kit.
BASE URL: https://<CCP-SERVER>/AIMWebService/api/Accounts   (customer-hosted; no fixed hostname)
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs.
  it=CCP — see ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THERE IS NO TOKEN ENDPOINT AND NO OAUTH IN THIS KIT. Do not generate a client-credentials flow, a
`platformtoken` call, or an `Authorization:` header here — none of them exist. CCP authenticates the
CALLING APPLICATION, not a user, by three server-side mechanisms (Section 7): OS User, Allowed
Machines, and Certificate Serial Number. The partner's code contributes exactly one thing to that:
presenting a client certificate (mTLS — `requests.get(..., cert=Certificate)`, Section 6). Everything
else is configured by the customer in the CP-CCP Application Management tile. Checks 4.2 and 4.3
grade that all three are configured and tested.

CCP IS NOT STANDALONE — IT REQUIRES CP. The CP agent holds the Vault connection; CCP is a REST web
service layered on top of it (Section 1). An integration plan that installs only CCP does not work.
../credential-provider/development-guide.md carries the CP installation steps.

CROSS-KIT TRAP ON AUDITING — THIS KIT GRADES THE INVERSE OF THE EPM KITS: check 3.2 requires the
CP/CCP audit trail and logging to be DISABLED for production use, enabled only for troubleshooting.
../../epm/ticketing-jit/ requires `Audit: true` on every policy and never disabled, including in
production. Both are correct in their own kit. Do not carry either setting across in either
direction.

THE QUERY CONTRACT — WHERE GENERATED CODE FAILS:
- The query MUST return EXACTLY ONE account (Section 5). Multiple matches is an error, not a list.
- Never hardcode an `Object` name. The customer must be able to supply a free-text `Query` from
  configuration (check 3.3). This is not a convenience — it is the prerequisite for dual accounts.
- Dual accounts use `VirtualUsername` in the query so the currently active account is always the one
  returned (check 3.4, Section 8). Example: `Safe=Test;Address=components;VirtualUsername=virtual`.
- The password comes back in the response's `Content` field. It is not the whole body.

ROTATION IS EXPECTED, NOT AN ERROR (checks 2.3 and 3.5, Section 9). Customers rotate on a schedule,
so an authentication failure using a just-retrieved secret is normal. The graded behaviour is:
wait 5 seconds, re-retrieve the secret, retry the operation once, and only then surface a clear
error — or poll the `PasswordChangeInProcess` property and wait while it is `True`. An integration
that fails fast on the first auth error fails this check.

EXACT VALUES AND NAMES, ALL GRADED:
- Application ID format is `<Partner Name>-<Product Name>` (check 4.1), issued by Idira Technical Alliances.
- Partner safe name is `PARTNER-<PARTNER>`, issued at onboarding.
- After ANY change to the authentication mechanisms, `iisreset` (check 4.4). This is an IIS reset,
  not a Windows service restart and not an application-pool recycle.
- Terminology: `CCP`, never `AAM` (check 5.1). `AAM` is the retired name.

PLATFORM: the CCP server is a dedicated WINDOWS server running IIS, installed via `msiexec` and
`APPCMD` (Section 4). The calling application can be in any language on any OS that can make an
HTTPS call with a client certificate.

SIBLING KITS — four Secrets Management kits, easily confused:
- ../credential-provider/: the agent-based SDK path, same Vault. it=CP. CCP's own prerequisite.
- ../secrets-manager-saas/: SaaS/cloud-native retrieval. it=SecretsManager
- ../secrets-manager-self-hosted/: the self-hosted counterpart. it=SecretsManagerSH
- Start at ../decision-guide.md if the choice is not already settled; check 2.1 grades that it was.
NOTE ON DIRECTION: these four kits RETRIEVE secrets from Idira. ../../discovery/secrets/ does the
opposite — it reports secrets that exist elsewhere into an inventory, and never transmits a secret
value at all. Do not conflate them.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — which Secrets Management dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **Not sure this is the right guide?** See the [Decision Guide](../decision-guide.md) first.  
> Use this guide if your application cannot or should not run an agent locally — CCP retrieves secrets via a REST call to a centrally-deployed IIS service.

---

## 1. Overview

The Central Credential Provider (CCP) is an agentless secrets retrieval solution. Unlike CP, CCP does not require an agent on the same machine as the application. Instead, CCP runs as an IIS-hosted REST web service on a dedicated CCP server. Any application on the network can call the CCP REST endpoint to retrieve a secret.

**CCP requires CP to already be installed.** The CP agent provides the connection to the Idira Vault; CCP extends CP with a REST web service layer.

**Integration pattern:**  
App → CCP REST endpoint (network) → CCP server → CP agent → Idira Vault → secret returned to app

---

## 2. When to Use CCP

- Your application cannot or should not have a local agent installed
- Your application is written in any language that can make HTTP calls
- You need machine-to-machine REST-based secret retrieval
- The application may run on multiple machines but you want a single retrieval point

For agent-based SDK retrieval, use the [Credential Provider (CP)](../credential-provider/development-guide.md) instead. If your tool is SaaS or cloud-native, use [Secrets Manager SaaS](../secrets-manager-saas/development-guide.md).

---

## 3. Prerequisites

- CP installed and connected to the Idira Vault — see [CP Development Guide](../credential-provider/development-guide.md) for installation steps
- A dedicated Windows server for CCP with IIS installed
- Your Application ID — format: `<Partner Name>-<Product Name>` (provided by Idira Technical Alliances)
- Your partner safe name: `PARTNER-<PARTNER>` (provided on onboarding)
- The `BizDevTch-CPCCP-Distribution.zip` distribution file — download from Idira Marketplace, search "For C3 Partners"

---

## 4. CCP Installation

1. Log in as administrator on the CCP server.
2. From `DISTRIBUTION`, extract the folder beginning with "Central Credential Provider". This is `INSTALLATION-FOLDER`.
3. From `INSTALLATION-FOLDER\Central Credential Provider WebService`, run the silent installer:
   ```
   "c:\Windows\System32\msiexec.exe" /i AIMWebService.msi /qn
   ```
4. Configure the IIS Application Pool:
   ```
   "c:\Windows\System32\inetsrv\APPCMD" add apppool /name:AIMWebServiceAppPool
   "c:\Windows\System32\inetsrv\APPCMD" set app "Default Web Site/AIMWebService" /applicationPool:AIMWebServiceAppPool
   ```
5. Set the Application ID in `C:\inetpub\wwwroot\AIMWebService\web.config` — update the key `AppID` to the CCP AppID provided by Idira Technical Alliances.
6. Restart IIS:
   ```
   iisreset
   ```
7. Test the endpoint from a browser (replace `APPID` and `SAFENAME`):
   ```
   https://IISSERVER/AIMWebservice/api/Accounts?AppID=APPID&Safe=SAFENAME&Object=account2retrieve
   ```
   A successful response is a JSON object where the `Content` field contains the password.

---

## 5. Retrieve a Secret via REST

```bash
curl -X GET \
  "https://<CCP-SERVER>/AIMWebService/api/Accounts?AppID=<APP_ID>&Safe=<SAFE>&Object=<OBJECT_NAME>" \
  --cert client.pem
```

**Query parameters:**

| Parameter | Required | Description |
|:----------|:---------|:------------|
| `AppID` | Yes | Your Application ID |
| `Safe` | Yes | Safe name containing the account |
| `Object` | Conditional | Account object name — use with Safe to target a specific account |
| `UserName` | Conditional | Username property of the account |
| `Address` | Conditional | Address property of the account |
| `Query` | Optional | Free-text query string combining multiple properties |

The query must return exactly one account. If multiple accounts match, CCP returns an error.

**Recommendation:** Allow the customer to provide a free-text query in your integration's configuration. This is required for dual accounts support.

---

## 6. Certificate Authentication Example

```python
import requests
import json
import sys

Certificate = '.\client.pem'
BASEURL = 'https://{}/AIMWebService/api/Accounts?AppID={}&Query={}'

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("usage: {} Address ApplicationID Query".format(sys.argv[0]))
        quit()
    address, appid, query = sys.argv[1], sys.argv[2], sys.argv[3]
    URL = BASEURL.format(address, appid, query)
    response = requests.get(URL, verify=Certificate, cert=Certificate)
    print(json.dumps(json.loads(response.text), indent=2))
```

---

## 7. Application Authentication

CCP validates the calling application using one or more of these mechanisms. Configure via the **CP-CCP Application Management** tile in the Applications tab of the shared ISP User Portal:

| Method | Description |
|:-------|:------------|
| **OS User** | CCP validates the requesting OS user against the user specified for the Application ID in the Vault |
| **Allowed Machines** | Restrict to specific IPs, DNS names, hostnames, or CIDR IPv4 subnets |
| **Certificate Serial Number** | Application sends the correct client certificate; CCP validates Serial Number, SAN, Subject, and Issuer |

Use all three in production where possible. After any change to authentication mechanisms, restart IIS.

---

## 8. Dual Accounts

CCP supports dual accounts to eliminate downtime during secret rotation. Use `VirtualUsername` in the query to always retrieve the currently active account:

```
Safe=Test;Address=components;VirtualUsername=virtual
```

Your integration must support free-text queries to enable this. Do not hard-code account object names.

---

## 9. Secret Rotation Handling

Because customers rotate secrets on a schedule:

1. If a secret operation fails with an authentication error, wait 5 seconds and re-retrieve the secret.
2. Retry the operation once.
3. If it fails again, surface a clear error to the user.

You can also check the `PasswordChangeInProcess` property in the CCP response — if `True`, wait and retry.

---

## 10. Telemetry Header

Include the `x-cybr-telemetry` HTTP header on all CCP REST requests, Base64 URL-encoded:

| Field | Header Key | Required | Example |
|:------|:-----------|:---------|:--------|
| IntegrationName | `in` | Yes | `in=Acme DataPipeline` |
| IntegrationType | `it` | Yes | `it=CCP` |
| IntegrationVersion | `iv` | Yes | `iv=1.0` |
| VendorName | `vn` | Yes | `vn=Acme` |
| VendorVersion | `vv` | No | `vv=3.1` |

---

## 11. Resources

- [CCP Documentation | Idira Docs](https://docs.cyberark.com/credential-providers/latest/en/content/ccp/lp_eucentralcredentialprovider.htm)
- [CP-CCP Distribution: Idira Marketplace](https://marketplace.idira.com) — search "For C3 Partners"
- [Idira Shared ISP Environment](https://c3.cyberark.cloud)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the two facts a generated integration gets wrong here: there is no token endpoint, no OAuth flow and no `Authorization` header in this kit at all — authentication is of the calling *application*, configured server-side, with the partner's code contributing only a client certificate — and CCP is not standalone, it requires CP already installed to hold the Vault connection. It also records the cross-kit auditing trap (check 3.2 requires CP/CCP audit logging **disabled** for production, the inverse of the EPM Ticketing/JIT kit's mandatory `Audit: true`), the query contract (exactly one account, no hardcoded `Object`, `VirtualUsername` for dual accounts, password in `Content`), and that a rotation-time auth failure is expected behaviour to retry rather than an error to surface. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
