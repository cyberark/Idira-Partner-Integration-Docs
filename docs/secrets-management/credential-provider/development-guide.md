# Idira Credential Provider (CP) — Development Guide

**Workflow:** Secrets Management  
**Integration:** Credential Provider (CP)  
**Type:** Development Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.2  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Credential Provider (CP) — agent-based secret retrieval from the Idira Vault.
WORKFLOW: Secrets Management
USE CASE: Credential Provider — an application retrieves a secret from the Idira Vault through a CP
  agent installed on the application's own machine.
INTEGRATION PATTERN: LOCAL SDK / CLI CALL. Not HTTP. See the warning below.
AUTH METHOD: Application authentication, configured server-side (Section 11) — no token, no login call
AUTH HEADER FORMAT: NOT APPLICABLE — there are no HTTP requests in this kit.
BASE URL: NOT APPLICABLE — there is no endpoint.
TELEMETRY: it=CP — but NOT sent as a header. See the telemetry warning below.
  ../../telemetry-reference.md carries the transform and the it registry.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THERE IS NO REST API IN THIS KIT. This is stated twice in the guide (Sections 1 and 12) because it
is the thing an agent most reliably gets wrong. Retrieval is a call to the Application Password SDK
(C, Java, .NET) or the `clipasswordsdk` / `CLIPasswordSDK64.exe` CLI, executed on the same machine as
the CP agent. There is no endpoint, no base URL, no `Authorization` header, no token endpoint and no
OAuth flow. An integration that generates an HTTP client here has misread the kit — that is
../central-credential-provider/, the agentless REST sibling.

TELEMETRY IS SUBMISSION METADATA HERE, NOT A HEADER. Because there is no HTTP request, there is
nothing to attach `x-cybr-telemetry` to. Check 3.7 still grades the four field values (`in`, `it`,
`iv`, `vn`, with `vv` optional) — they are supplied in the wrapper or configuration metadata handed
over at certification time (Section 13). Do not generate header-setting code for this kit, and do not
report the requirement as inapplicable: the values are required, the header is not.

THE CLIENT MUST RUN ON THE SAME MACHINE AS THE AGENT (Section 12). That is the whole shape of the
kit. It rules out containerised and serverless callers, and it is why the decision guide routes
those to CCP or Secrets Manager instead.

CROSS-KIT TRAP ON AUDITING — THIS KIT GRADES THE INVERSE OF THE EPM KITS: check 3.2 requires the CP
audit trail and logging to be DISABLED for production use, enabled only for troubleshooting.
../../epm/ticketing-jit/ requires `Audit: true` on every policy and never disabled, including in
production. Both are correct in their own kit. Do not carry either setting across.

THE QUERY CONTRACT — WHERE GENERATED CODE FAILS:
- Query syntax is semicolon-delimited Vault account properties: `Property1=Value;Property2=Value`
  over `Safe`, `UserName`, `Address`, `Object` and any other account property (Section 8). `Folder`
  applies only to PAM Self-Hosted. Always include `Safe` and `Object` or `UserName`: without Safe or
  Object, CP searches as if the query were a regular expression, even when an exact query was sent.
- The query MUST return EXACTLY ONE account. Multiple matches is an error, not a list.
- Never hardcode an account or `Object` name. The customer must be able to supply a free-text query
  from configuration (check 3.3) — that is the prerequisite for dual accounts.
- Dual accounts use `VirtualUsername` so the currently active account is always returned
  (check 3.4, Section 9).

ROTATION IS EXPECTED, NOT AN ERROR (checks 2.3 and 3.6, Section 10). Wait 5 seconds, retrieve again,
retry the operation — or request `PasswordChangeInProcess` in the output, which is `False` unless
rotation is running. `FailRequestOnPasswordChange=true` makes the request fail during a change;
`false` returns the value and lets you check `PasswordChangeInProcess` yourself.
An integration that fails on the first stale-secret error fails this check.

DO NOT PACKAGE THE IDIRA SDKs (check 3.5, Section 12). Reference them from the default installation
location. Vendoring or bundling them into the partner's own distributable fails certification.

EXACT VALUES AND NAMES, ALL GRADED:
- Application ID format is `<Partner Name>-<Product Name>` (check 4.1) — e.g. `Acme-SecurityScanner`.
- Partner safe name is `PARTNER-<PARTNER>`; the provider user created at install is
  `Prov_<Your Hostname>` and needs Retrieve Accounts, List Accounts and View Safe Members on the
  safe, AND the application (App ID) itself must be a Safe member with Retrieve Accounts (Section 7).
  A retrieval that fails with both in place is an App ID or authentication fault, not a missing
  object.
- After ANY authentication-mechanism change, restart the CP service (check 4.3) — the
  "Idira Application Password Provider" service on Windows, `service aimprv restart` on Linux.
- Terminology: `CP`, never `AIM` (check 5.1). `AIM` is the retired name — note that the Windows
  distribution file is still named `AAM-Windows64` and the Linux RPM `CARKaim-*`, so the old names
  survive in filenames. Do not use them in documentation or UI text.
- CP supports four application authentication methods: Allowed Machines, OS User, Path and Hash
  (Section 11). Certificate methods are CCP-ONLY and NOT available for agent-based CP. Checks 2.4 and
  4.2 grade Allowed Machines and OS User; Path and Hash are recommended in addition. Do not carry
  CCP's certificate methods across.

THE LINUX PROVISIONING PASSWORD IS ONE-TIME AND CONSUMED (Section 6, step 3). After
`appprovideruser.cred` exists the agent authenticates from that file. Do not hardcode it, commit it,
or reuse it as an application password.

SIBLING KITS — four Secrets Management kits, easily confused:
- ../central-credential-provider/: the agentless REST path. it=CCP. It REQUIRES CP installed first,
  so this guide's installation steps are its prerequisite too.
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
> Use this guide if your application runs on a managed machine and can have the CP agent installed alongside it.

---

## 1. Overview

The Credential Provider (CP) is an agent-based solution. The CP agent is installed on the same machine as your application. Your application makes local SDK or CLI calls to the CP agent, which retrieves secrets from the Idira Vault (Privileged Access Manager SaaS or Self-Hosted) on its behalf.

**CP has no REST API.** All secret retrieval is done through the Application Password SDK (C, Java, .NET, CLI).

**Integration pattern:**  
App → CP agent (local) → Idira Vault → secret returned to app

---

## 2. When to Use CP

- Your application runs on a persistent, non-containerized machine (Windows or Linux)
- Installing an agent alongside the application is acceptable
- You need SDK-based integration (C, Java, .NET, or CLI)
- Agent-based authentication provides stronger identity binding than REST in your customer's environment

For agentless REST-based retrieval, use the [Central Credential Provider (CCP)](../central-credential-provider/development-guide.md) instead.

---

## 3. Prerequisites

- An Idira partner account with access to the Idira shared ISP environment (`https://c3.cyberark.cloud`)
- Your Application ID — format: `<Partner Name>-<Product Name>` (provided by Idira Technical Alliances on onboarding)
- Your partner safe name: `PARTNER-<PARTNER>` (provided on onboarding)
- The `BizDevTch-CPCCP-Distribution.zip` distribution file — download from Idira Marketplace, search "For C3 Partners"
- A server (Windows or Linux) to install the CP agent on

---

## 4. Application ID

The Application ID identifies your application to the Idira Vault. Use the format:

```
<Partner Name>-<Product Name>
```

Example: `Acme-SecurityScanner`

The Application ID is provisioned by Idira Technical Alliances during onboarding. To manage authentication mechanisms (OS User, machine address, certificate) for your Application ID, use the **CP-CCP Application Management** tile in the Applications tab of the shared ISP User Portal.

After any change to authentication mechanisms, restart the CP service on your server.

---

## 5. Windows Installation

1. Log in as administrator on the CP server.
2. From `DISTRIBUTION`, extract the file beginning with `AAM-Windows64`. This is the CP installation folder.
3. Run the silent installer:
   ```
   setup /s /f1"DISTRIBUTION\Silent-Install\windows\silent.iss"
   ```
   This installs binaries, config files, and the "Idira Application Password Provider" service. The server will restart.
4. After restart, log back in as administrator.
5. Create the credential file from `C:\Program Files\CyberArk\ApplicationPasswordProvider\Vault\`:
   ```
   CreateCredFile AppProviderUser.cred Password /Username <username> /Password <password> /Hostname /EntropyFile
   ```
   `<username>` and `<password>` are provided with the distribution.
6. Update `Vault.ini` to point to the C3 proxy server (use the Proxy folder from the distribution).
7. Start the "Idira Application Password Provider" service.
8. Test from `C:\Program Files\CyberArk\ApplicationPasswordSdk\`:
   ```
   CLIPasswordSDK64.exe GetPassword /p AppDescs.AppID=<PARTNER_AppID> /p Query="Safe=<PARTNER-SAFE>;Folder=Root;Object=account2retrieve" /o Password
   ```
   A successful response prints the password for the test account. Check `C:\Program Files\CyberArk\ApplicationPasswordProvider\Logs` for errors.

---

## 6. Linux Installation

1. Ensure `/var/tmp/aimparms` contains:
   ```ini
   [Main]
   AcceptCyberArkEULA=yes
   CreateVaultEnvironment=no
   ```
2. Install the RPM:
   ```bash
   rpm -ivh CARKaim-13.00.02.4.x86_64.rpm
   ```
3. Create the partner credential file from `/etc/opt/CARKaim/vault/`:
   ```bash
   ./CreateCredFile appprovideruser.cred Password \
     -Username PROV_PROVIDER_<PARTNER> -Password <provisioning-password> -Hostname -EntropyFile
   ```
   `<provisioning-password>` is the one-time provisioning password your Idira Technical Alliances contact gives you at onboarding. It is consumed when the credential file is created — the CP agent authenticates from `appprovideruser.cred` afterwards, not from the password. Do not hard-code it, commit it, or reuse it as an application password.
4. Update `/etc/opt/CARKaim/vault/vault.ini` with the C3 vault and proxy details (use the Proxy folder's `vault.ini`). Test connectivity:
   ```bash
   nc -vz vault-c3.privilegecloud.cyberark.cloud 1858
   ```
5. Restart the service and verify startup:
   ```bash
   service aimprv restart
   cat /var/opt/CARKaim/logs/APPConsole.log
   ```
6. Test retrieval from `/opt/CARKaim/sdk/`:
   ```bash
   ./clipasswordsdk GetPassword \
     -p AppDescs.AppID=<PARTNER>_appID \
     -p Query="Safe=PARTNER-<PARTNER>;Folder=Root;Object=account2retrieve" \
     -o Password
   ```
   Expected output: the value stored on the `account2retrieve` object in your partner safe — a demo value seeded at onboarding. A successful retrieval prints that value and nothing else; an empty result or a non-zero exit is a permissions or App ID fault, not a missing object.

---

## 7. Verify Safe Permissions

When CP is installed, a provider user called `Prov_<Your Hostname>` is created in the Vault. This user must have the correct permissions on the safe containing the secrets.

In Idira Privileged Access Manager SaaS (or PVWA), go to **Policies → Access Control (Safes)**, select your safe, and under the **Members** tab add `Prov_<hostname>` with:
- Retrieve Accounts
- List Accounts
- View Safe Members

Then add the **application** (your Application ID) as a Safe member with:

- Retrieve Accounts

Both memberships are required. If the Safe uses object-level access, both the provider user and the application need access to the account. See [Provisioning privileged application accounts](https://docs.cyberark.com/credential-providers/latest/en/content/ccp/provisioning-privileged-application-accounts.htm).

---

## 8. Retrieving Secrets in Production

**Query format:**
```
Property1=Value;Property2=Value;...PropertyN=Value
```
Where `Property` is a Vault account property such as `Safe`, `UserName`, `Address`, or `Object`. `Folder` is supported only on PAM Self-Hosted — do not set it for Privilege Cloud customers.

- **The query must return exactly one account.** More than one match is an error (unless one of them is already in the CP cache for the same query).
- **Always include `Safe` and `Object` or `UserName`.** Without `Safe` or `Object`, CP searches as if a regular-expression query had been sent, even if you sent an exact one.
- **`QueryFormat`** selects `Exact` (default) or `Regexp` matching.
- **`RequiredProps`** names the account properties to return (`-p RequiredProps=Address,UserName`, or `*`); **`Reason`** records why the password was retrieved in the CP audit log.

See [CLI Application Password SDK syntax](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/cli-application-password-sdk-egssyntax.htm).

**Recommendation:** Allow the customer to enter a free-text query string in your integration's configuration. This supports dual accounts without requiring code changes and is required for certification.

**Windows:**
```
C:\Program Files (x86)\CyberArk\ApplicationPasswordSdk\CLIPasswordSDK.exe GetPassword ^
  /p AppDescs.AppID="PartnerName-ApplicationName" ^
  /p Query="Safe=test;UserName=my-user" ^
  /o Password,PassProps.Address,PassProps.UserName
```

**Linux:**
```bash
/opt/CARKaim/sdk/clipasswordsdk GetPassword \
  -p AppDescs.AppID="PartnerName-ApplicationName" \
  -p Query="Safe=test;UserName=my-user" \
  -o Password,PassProps.Address,PassProps.UserName
```

---

## 9. Dual Accounts

Dual accounts eliminate downtime during secret rotation. Two identical accounts with the same permissions are maintained — one active, one inactive. Rotation happens on the inactive account; they swap after rotation completes.

Use `VirtualUsername` in the query to always retrieve the active account:
```
Safe=Test;Address=components;VirtualUsername=virtual
```

Your integration must support free-text queries to enable this. Do not hard-code account names.

---

## 10. Secret Rotation Handling

If a secret changes between retrieval and use:
1. Wait 5 seconds.
2. Retrieve the secret again.
3. Retry the operation.

You can also request the `PasswordChangeInProcess` property in the output — it is `False` unless rotation is in progress. Pair it with `FailRequestOnPasswordChange`:

- `-p FailRequestOnPasswordChange=true` — the request fails while a change is under way; retry after the wait above.
- `-p FailRequestOnPasswordChange=false` — the request returns the current value; check `PasswordChangeInProcess` and, if `True`, poll until it returns `False`.

---

## 11. Authentication Methods

CP supports the following application authentication methods for production environments. Configure via the CP-CCP Application Management tile in the ISP User Portal:

- **OS User:** CP validates the requesting OS user matches the user specified for the Application ID
- **Allowed Machines:** Restrict access to specific IPs, DNS names, hostnames, or CIDR subnets
- **Path:** CP validates the full path of the calling application
- **Hash:** CP validates a hash of the calling application's executable, so a replaced binary cannot retrieve the secret — see [Generate the application hash value](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/generating-application-hash-value.htm)
- **Certificate:** CCP only — not available for agent-based CP

Idira recommends configuring every method the application can satisfy; for an application on the same machine as CP, always configure OS User and Allowed Machines. See [Application authentication methods](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/application-authentication-methods-general.htm).

Restart the CP service after any authentication mechanism change.

---

## 12. Important CP Constraints

- Client applications **must run on the same machine** as the CP agent
- CP has **no REST API** — only SDK calls (C, Java, .NET, CLI)
- Do not package Idira SDKs with your software — reference them from the default installation location
- Audit trail and logging is for troubleshooting only — disable for production use

---

## 13. Telemetry

CP has **no REST API** (see §12) — retrieval goes through the SDK, so there is no HTTP request to carry the `x-cybr-telemetry` header that REST-based Idira integrations send. The four required fields still apply to CP. Submit them as part of the wrapper or configuration metadata you provide at certification time, using the keys below.

> If your product also has a REST-based component that calls Idira directly, that component does send `x-cybr-telemetry` as a real HTTP header — see the [CCP guide](../central-credential-provider/development-guide.md).

| Field | Key | Required | Example |
|:------|:-----------|:---------|:--------|
| IntegrationName | `in` | Yes | `in=Acme SecurityScanner` |
| IntegrationType | `it` | Yes | `it=CP` |
| IntegrationVersion | `iv` | Yes | `iv=1.0` |
| VendorName | `vn` | Yes | `vn=Acme` |
| VendorVersion | `vv` | No | `vv=4.2` |

---

## 14. Resources

- [CP Documentation | Idira Docs](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/lp_cp.htm)
- [CP-CCP Distribution: Idira Marketplace](https://marketplace.idira.com) — search "For C3 Partners"
- [Idira Shared ISP Environment](https://c3.cyberark.cloud)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-08 | **[Fixed]** Windows paths use the installed folder name `CyberArk` (`C:\Program Files\CyberArk\ApplicationPasswordProvider\…`, `C:\Program Files (x86)\CyberArk\ApplicationPasswordSdk\…`) — the folder is not renamed, and the previous paths did not exist. The Linux SDK path is lower-case `/opt/CARKaim/sdk/`. The application itself must be a Safe member with Retrieve Accounts, in addition to the provider user. **[Added]** Path and Hash authentication; `Folder` is PAM Self-Hosted only; `QueryFormat`, `RequiredProps`, `Reason`; the regular-expression fallback when `Safe` or `Object` is omitted; `FailRequestOnPasswordChange`. Scripts using the previous Windows paths must be updated | Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the fact the guide already states twice and an agent still misses — there is no REST API in this kit, so no endpoint, no base URL, no `Authorization` header and no token flow exist — and with the consequence for telemetry: check 3.7 grades the four field values, but they are submitted as wrapper/configuration metadata rather than sent as `x-cybr-telemetry`, so header-setting code here is wrong while reporting the requirement as inapplicable is also wrong. It also records the cross-kit auditing trap (CP audit logging **disabled** for production, the inverse of the EPM Ticketing/JIT kit's mandatory `Audit: true`), that certificate authentication is CCP-only and not available for agent-based CP, the same-machine constraint, the no-SDK-packaging rule, and that the Linux provisioning password is one-time and consumed by `appprovideruser.cred`. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
