# Idira Identity Security Platform — Identity Response Actions Development Guide

**Workflow:** Identity Response
**Use Case:** Identity Response Actions — XDR / SIEM / SOAR partner integration
**Idira Product:** Idira Identity Security Platform (Identity, Privileged Access Manager SaaS, Secure Infrastructure Access, Secure Cloud Access, Secrets Manager, Endpoint Privilege Manager)
**Type:** Development Guide
**Version:** 1.7
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-05

> **Not sure this is the right guide?** This is currently the only use case in the Identity Response workflow. A decision guide will be added when the workflow gains a second use case.
> Use this guide if: you are an XDR, SIEM, or SOAR platform (for example, Palo Alto Cortex XSIAM/XSOAR, Google Security Operations, or Splunk) and you want to trigger identity, privileged-session, credential, access-policy, or machine-identity response actions in Idira from a detection or playbook.

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Identity Security Platform — Identity Response Actions is a stateless orchestration pattern. It is NOT a single "Response API". A partner XDR/SIEM/SOAR platform calls the existing REST APIs of several Idira SaaS services to run a precise identity or privilege response action.
WORKFLOW: Identity Response
USE CASE: A partner platform (any XDR, SIEM, or SOAR — Cortex, Google SecOps, Splunk, etc.) triggers deterministic identity response actions in Idira in real time — lock user, force logout, expire password, remove privileged role, list/terminate/suspend privileged sessions, rotate/verify a credential, vault a risky account, disable a Secure Infrastructure Access policy, delete/revoke a machine identity (workload or authenticator) in Secrets Manager, and trigger EPM endpoint containment.
INTEGRATION PATTERN: REST. The partner platform (1) resolves the target entity (user, account, session, workload), then (2) calls the action API on the relevant Idira service. Idira acts as a stateless execution engine in v1: locate target, run action, return status.
SCOPE: SaaS only. This guide targets Idira Privileged Access Manager SaaS, Secure Infrastructure Access, Secrets Manager SaaS (Conjur Cloud), and the Idira Identity Security Platform shared services. PAM Self-Hosted is out of scope. Secure Cloud Access (SCA) has a confirmed Access API family but no endpoint-level detail was obtainable without an authenticated api-docs.cyberark.com session — see Section 7.10.

AUTH — THREE DISTINCT MODELS BY TARGET SERVICE (do not mix them):
- Idira Identity Security Platform Shared Services (Identity workforce APIs, Privileged Access Manager SaaS, Secure Infrastructure Access): OAuth 2.0 client_credentials via ISPSS. Token endpoint: POST https://<tenant>.id.cyberark.cloud/oauth2/platformtoken (form body grant_type=client_credentials&client_id=<login>&client_secret=<secret>). Header on calls: "Authorization: Bearer <access_token>".
- Endpoint Privilege Manager (EPM): OAuth via Identity, but the EPM API header format is "Authorization: basic <token>" (not Bearer). See the EPM SOC Response guide.
- Secrets Manager SaaS (Conjur Cloud): a separate JWT retrieved from that service's own authenticate endpoint, sent as "Authorization: Token token=\"<jwt>\"" (not Bearer, not basic). Do not reuse an ISPSS token here.

BASE HOSTS (SaaS):
- Identity workforce APIs: https://<tenant>.id.cyberark.cloud/<path>
- Privilege Cloud PVWA: https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/<path>
- Secure Infrastructure Access (SIA): https://<subdomain>.dpa.cyberark.cloud/api/<path>
- Secrets Manager SaaS (Conjur Cloud): https://<subdomain>.secretsmgr.cyberark.cloud/api/<path>
- EPM: https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/<path>
- Secure Cloud Access (SCA): API family confirmed ("Access API", Authentication API, Cloud scan API, Integrations API, Web app creation API) at api-docs.cyberark.com/sca-api; endpoint paths not confirmed — that portal requires an authenticated session, unlike every other host above.

TELEMETRY: Required on all Idira API requests — x-cybr-telemetry header, Base64url-encoded key=value pairs. it reflects the partner platform category (SOAR / SIEM / XDR).
SANDBOX: C3 Integrations Platform — https://c3.cyberark.cloud
CONTACT: cybr-bizdevtech@paloaltonetworks.com

VERIFIED API CALLS (method + literal path read from live Idira Docs / OpenAPI spec):
  CONTEXT
  - Get user by name → unique ID: POST https://<tenant>.id.cyberark.cloud/CDirectoryService/GetUserByName  (body: username string; key casing [TBD confirm against tenant Swagger])
  - Get accounts → account id:    GET  /PasswordVault/API/Accounts?search=<term>&safeName=<safe>
  - List active sessions:         GET  /PasswordVault/API/LiveSessions?Search=<user>  (returns SessionGuid, CanTerminate, CanSuspend)
  IDENTITY (WORKFORCE)
  - Lock / disable user:          POST /CDirectoryService/SetUserState  (body: ID string, State "Locked"|"Disabled"|"Expired"|"None")
  - Force logout all sessions:    POST /UserMgmt/SignOutEverywhere  (body: user unique ID; key name [TBD])
  - Expire / force password reset: POST /CDirectoryService/ChangeUser (ForcePasswordChangeNext=true) OR SetUserState State="Expired"
  - Remove privileged role:       POST /SaasManage/RemoveUsersAndGroupsFromRole  (body: Name=roleId, Users=[userId])
  - Enforce MFA step-up:          Policy-based via Auth Profile API / authentication profile assignment — no single "require MFA now for user X" endpoint confirmed [TBD]
  PRIVILEGED SESSION (Privileged Access Manager SaaS)
  - Terminate session:            POST /PasswordVault/API/LiveSessions/<SessionGuid>/Terminate/
  - Suspend / resume session:     POST /PasswordVault/API/LiveSessions/<SessionGuid>/Suspend/  (or /Resume/)  — not supported for SSH/OPM sessions
  SECRETS / CREDENTIAL (Privileged Access Manager SaaS)
  - Rotate credential now (CPM):  POST /PasswordVault/API/Accounts/<AccountID>/Change/  (body: ChangeCredsForGroup boolean — page also shows ChangeEntireGroup; parameters table is authoritative, test against tenant)
  - Verify credential (CPM):      POST /PasswordVault/API/Accounts/<AccountID>/Verify/  (no body)
  - Vault a flagged account:      POST /PasswordVault/API/Accounts  (body: platformId + safeName REQUIRED; name, address, userName, secretType, secret, platformAccountProperties, secretManagement.automaticManagementEnabled)
  ACCESS POLICY (SIA — this is the "Access Control Policies API" family, shared across the Manage space, not an SIA-only API)
  - List policies:                GET    https://<subdomain>.dpa.cyberark.cloud/api/access-policies
  - Disable policy:               PUT    https://<subdomain>.dpa.cyberark.cloud/api/access-policies/<policy_id>  (body: policyId, policyName, status="Disabled")
  - Delete policy:                DELETE https://<subdomain>.dpa.cyberark.cloud/api/access-policies/<policy_id>
  - SSH session termination: NO partner-callable API. Confirmed real feature ("SSH session termination", detect-and-respond/manage/privileged-access docs) but it is ITDR-rule-triggered only (automatic, based on Suspicious Activities Rules) — there is no REST endpoint for a third party to invoke it on demand. Do not document this as an action a partner integration can call.
  MACHINE IDENTITY (Secrets Manager SaaS / Conjur Cloud) — see Section 7.11
  - Delete workload (revoke a machine identity): DELETE https://<subdomain>.secretsmgr.cyberark.cloud/api/workloads/<url-encoded identifier>
  - Delete authenticator (revoke an entire auth method): DELETE https://<subdomain>.secretsmgr.cyberark.cloud/api/authenticators/<type>/<name>
  SECURE CLOUD ACCESS (SCA) — Access API family confirmed to exist; endpoint paths [TBD — requires authenticated api-docs.cyberark.com/sca-api session to confirm]. See Section 7.10.
  ENDPOINT (EPM) — see the EPM SOC Response guide for full detail (Authorization: basic <token>)

KEY CONSTRAINTS:
- SaaS only. All hosts are Idira cloud services; do not use PAM Self-Hosted PVWA paths or the Logon API.
- CPM rotate/verify are standard Central Policy Manager operations — do NOT use "ARS" or "SRS" naming; the docs call them "Change credentials immediately" and "Verify credentials".
- To terminate/suspend a session you use the SessionGuid, not the numeric SessionID.
- Privileged Access Manager SaaS, SIA, and Identity use "Bearer <token>". EPM uses "basic <token>". Secrets Manager SaaS uses "Token token=\"<jwt>\"" from its own authenticate endpoint — three auth models across the actions in this guide, not two.
- SIA policy operations require the DpaAdmin role.
- Identity lock/logout actions require system-administrator or user-management rights.
- Secrets Manager delete-workload/delete-authenticator are destructive, not reversible — deleting is not the same risk profile as Identity's lock/disable (State back to None). Prefer these only when the machine identity itself is confirmed compromised, not as a first response.
- v1 is stateless execution only. Rollback of reversible actions (unlock, resume, re-add role) is the partner playbook's responsibility.

TERMINOLOGY (use these exact names in code and docs):
- CyberArk Identity Security Platform → Idira Identity Security Platform
- CyberArk Privilege Cloud → Idira Privileged Access Manager SaaS
- CyberArk Identity → Idira Identity (Identity Administration)
- CyberArk Secrets Manager → Idira Secrets Manager
- CyberArk EPM → Idira Endpoint Privilege Manager
- DPA / Dynamic Privileged Access → Secure Infrastructure Access (SIA)
- CyberArk Conjur / Conjur Cloud → Idira Secrets Manager SaaS

FILES IN THIS DIRECTORY:
- development-guide.md — this file — full integration guide
- certification-checklist.md — requirements checklist for Idira certification review
-->

---

## 1. Why This Integration Matters

Attackers now log in more often than they break in: CrowdStrike attributed 75% of initial-access attacks in 2023 to malware-free techniques such as stolen credentials and valid-account abuse, rising to 82% of detections by its 2026 report. When the target is an identity, blunt endpoint isolation is not enough. SOC teams need to lock the account, end its live privileged sessions, rotate the credential it exposed, and strip its standing privilege, without waiting on a manual handoff to the identity or PAM team. This integration lets any XDR, SIEM, or SOAR platform trigger those precise identity and privilege response actions in Idira as part of the detection-to-containment flow, so a detection signal becomes a governed, auditable, reversible response.

**Industry drivers:**

- **Identity is the primary attack surface.** 75% of 2023 initial-access attacks were malware-free (stolen credentials, phishing, valid accounts), rising to 82% of detections in the 2026 report. (CrowdStrike Global Threat Report, 2024 and 2026)
- **Credential-based breaches are the slowest and costliest to contain.** Breaches that start with stolen or compromised credentials take approximately 292 days to identify and contain, against a global average breach cost of $4.88M. (IBM Cost of a Data Breach Report, 2024)
- **Attacker speed has outpaced manual response.** Average eCrime breakout time fell to 29 minutes, with a fastest recorded time of 27 seconds, far shorter than a human-driven SOC triage cycle. (CrowdStrike Global Threat Report, 2026)
- **Automation measurably reduces cost and dwell time.** Organizations with extensive security AI and automation saved an average of $2.2M per breach and shortened the breach lifecycle by roughly 100 days. (IBM Cost of a Data Breach Report, 2024)
- **Regulation now requires fast, demonstrable incident response.** EU NIS2 requires early incident notification within 24 hours, DORA mandates rapid ICT-incident response for financial entities (in force January 2025), and the US SEC rule requires material-incident disclosure within 4 business days. Automated identity containment shrinks the window these clocks measure. (NIS2 Directive; DORA Regulation; SEC 2023 cyber disclosure rule)

**Highest-demand verticals:** financial services (DORA, FFIEC), healthcare (HIPAA), and federal and public sector (Executive Order 14028, CISA Zero Trust) see the strongest demand for automated identity response, driven by the regulatory mandates above.

---

## 2. Response Actions at a Glance

This integration exposes the response actions below. Each one is a single call your playbook makes after resolving the target entity (user, account, session, or policy). Pick the actions your use case needs — they are independent, and none of them require the others. The **Reversible** column shows which actions your playbook can undo after an investigation clears.

| # | Response action | What it does | Idira service | Reversible? | Section |
|:--|:---|:---|:---|:--:|:--:|
| **Identity (workforce)** | | | | | |
| 1 | Lock / disable user | Blocks the user from authenticating | Identity | Yes — set state back to `None` | [7.4](#74-identity-workforce-actions) |
| 2 | Force logout | Ends all of the user's active sessions and cookies; forces re-login | Identity | No (user simply signs in again) | [7.4](#74-identity-workforce-actions) |
| 3 | Expire password / force reset | Requires the user to set a new password at next login | Identity | No | [7.4](#74-identity-workforce-actions) |
| 4 | Remove privileged role | Strips standing privilege by removing the user from a role | Identity | Yes — re-add to the role | [7.4](#74-identity-workforce-actions) |
| **Privileged session** | | | | | |
| 5 | Terminate session | Ends a specific live privileged session immediately | Privileged Access Manager SaaS | No | [7.5](#75-terminate-a-privileged-session) |
| 6 | Suspend / resume session | Pauses a live session; can be resumed later (not for SSH/OPM) | Privileged Access Manager SaaS | Yes — resume | [7.6](#76-suspend-or-resume-a-privileged-session) |
| **Credential** | | | | | |
| 7 | Rotate credential now | Triggers the CPM to change an exposed credential immediately | Privileged Access Manager SaaS | N/A (new secret issued) | [7.7](#77-secrets-and-credential-actions) |
| 8 | Verify credential | Confirms a credential is valid / rotation succeeded | Privileged Access Manager SaaS | N/A | [7.7](#77-secrets-and-credential-actions) |
| 9 | Vault a flagged account | Brings an unmanaged risky account under Idira management | Privileged Access Manager SaaS | Yes — remove the account | [7.7](#77-secrets-and-credential-actions) |
| **Access policy** | | | | | |
| 10 | Disable access policy | Revokes standing or just-in-time access by disabling a policy | Secure Infrastructure Access | Yes — set status back to `Enabled` | [7.8](#78-disable-a-secure-infrastructure-access-policy) |
| **Machine identity (Secrets Manager)** | | | | | |
| 11 | Delete workload | Revokes a compromised machine identity's ability to authenticate and retrieve secrets | Secrets Manager SaaS | No — deletion, not suspension | [7.11](#711-machine-identity-actions-secrets-manager-saas--conjur-cloud) |
| 12 | Delete authenticator | Revokes an entire authentication method (all workloads using it) | Secrets Manager SaaS | No — deletion, not suspension | [7.11](#711-machine-identity-actions-secrets-manager-saas--conjur-cloud) |
| **Endpoint** | | | | | |
| 14 | Contain endpoint | Applies a restrictive privilege policy to a suspect endpoint | Endpoint Privilege Manager | Yes — see EPM guide | [7.9](#79-endpoint-containment-epm) |
| **Cloud console access (SCA)** | | | | | |
| 15 | Revoke one session | Ends a specific active SCA session by ID | Secure Cloud Access | Unconfirmed — request/response schema not independently verified | [7.10](#710-secure-cloud-access-sca--session-revocation) |
| 16 | Revoke all sessions for a user | Ends every active SCA session for one user | Secure Cloud Access | Unconfirmed — request/response schema not independently verified | [7.10](#710-secure-cloud-access-sca--session-revocation) |

**Not an action a partner can call:** SIA's "SSH session termination" is a real feature but is triggered automatically by ITDR Suspicious Activities Rules, not by an external REST call — do not build against it as if it were action #5's SIA equivalent.

**Common ways partners combine these:**

- **Single surgical action** — one action during an investigation (for example, terminate one suspicious session).
- **Full containment ("Red Button")** — a high-confidence incident runs a set at once: lock user (1) + force logout (2) + terminate sessions (5) + rotate the exposed credential (7) + remove privileged role (4). For a compromised machine identity, add delete workload (11) or delete authenticator (12) once compromise is confirmed.
- **Severity-routed** — map the alert severity to the action scope: high → full containment, medium → lock + logout, low → notify only.

You do not need to build every action to certify. Document which actions your integration implements in the certification checklist.

---

## 3. What the Customer Sees

When a partner playbook triggers an identity response action, the SOC analyst sees the outcome in the Idira consoles and in the incident timeline: the account moves to a locked or disabled state in Idira Identity, active privileged sessions for that user show as terminated or suspended in the session monitor, an exposed credential shows a fresh rotation timestamp, and any revoked standing access no longer appears in the user's entitlements. Each action returns a per-action status (success, partial success, or failure) so the playbook can branch and the analyst can see exactly which controls were applied.

| What the analyst sees | Source field / API |
|:---|:---|
| Account state (Locked / Disabled) | `State` set via `SetUserState` |
| No active privileged sessions | `LiveSessions` list returns none for the user after `Terminate` |
| Credential last rotated timestamp | `lastModifiedDateTime` / `lastVerifiedDateTime` on the account object |
| Standing access removed | Secure Infrastructure Access policy `status` = `Disabled`, or role membership removed |
| Machine identity revoked | Workload or authenticator no longer appears in Secrets Manager SaaS; subsequent authenticate/retrieve calls from it return `401`/`403` |
| Endpoint contained | EPM risk-group membership (see EPM SOC Response guide) |

---

## 4. Prerequisites

### Idira Environment

| Requirement | Detail |
|:---|:---|
| Idira deployment | Idira Identity Security Platform (Identity), plus one or more of: Idira Privileged Access Manager SaaS, Secure Infrastructure Access (SIA), Idira Secrets Manager SaaS (Conjur Cloud), Idira Endpoint Privilege Manager. **SaaS only** — PAM Self-Hosted is out of scope for this integration. |
| Identity service account | OAuth confidential client with system-administrator or user-management rights (for Identity workforce actions). See Section 5. |
| Privileged Access Manager SaaS permissions | For credential actions: "Initiate CPM password management operations" on the Safe. For vaulting: "Add account" plus "Update password" or "Update password properties" on the Safe. For session actions: session-monitoring termination/suspension rights (confirm on your Privileged Access Manager SaaS tenant). |
| SIA role | `DpaAdmin` role for access-policy revocation. SIA has no partner-callable session-termination API — see Section 7.8. |
| Secrets Manager SaaS permissions | Update permissions on the target workload's policy branch (delete workload); membership in `Authn_Admins` or `Conjur_Cloud_Admins` (delete authenticator). See Section 7.11. |
| SCA | Not usable yet for this integration — Access API confirmed to exist but its endpoint reference is behind an authenticated `api-docs.cyberark.com` session. See Section 7.10 before committing to build against it. |
| EPM setup | If the endpoint action is in scope, complete the EPM SOC Response prerequisites (agents 26.4+, policy packages, static groups) |
| Sandbox | C3 Integrations Platform — request access at `cybr-bizdevtech@paloaltonetworks.com` |

### Partner Environment

| Requirement | Detail |
|:---|:---|
| Platform | Any XDR, SIEM, or SOAR platform with playbook or integration-command capability (for example, Palo Alto Cortex XSIAM/XSOAR, Google Security Operations, Splunk SOAR) |
| Outbound connectivity | Reach `https://<tenant>.id.cyberark.cloud`, the Privileged Access Manager SaaS host, `https://<subdomain>.dpa.cyberark.cloud`, `https://<subdomain>.secretsmgr.cyberark.cloud`, and the EPM host as applicable |
| Alert context | Alert payload must carry the identifier needed to resolve the target: username (for identity actions), account name or address (for credential actions), hostname/IP (for endpoint actions), or workload/authenticator identifier (for machine-identity actions) |
| Credential storage | Secure storage for the Idira service-account credentials — not in playbook or connector code |

### Required context IDs (resolve before acting)

| ID | Why it is needed | How to retrieve it |
|:---|:---|:---|
| User unique ID | Identity state, logout, role, and password actions target the user by unique ID, not username | `POST /CDirectoryService/GetUserByName` (Section 7.1) |
| Account ID | Rotate and verify calls require the internal account ID | `GET /PasswordVault/API/Accounts` (Section 7.2) |
| Session GUID | Terminate and suspend target a session by GUID, not the numeric SessionID | `GET /PasswordVault/API/LiveSessions` (Section 7.3) |
| Policy ID | SIA disable/delete target a policy by ID | `GET /api/access-policies` (Section 7.7) |
| Workload / authenticator identifier | Delete-workload and delete-authenticator target by policy-branch path or `<type>/<name>`, not a numeric ID | Known from the alert context or your Secrets Manager policy inventory — no discovery/search endpoint was confirmed in this pass (Section 7.11) |

---

## 5. Authentication

This integration calls several Idira SaaS services, and they use three authentication models. Use the correct model for each target. Mixing them (for example, sending a `Bearer` token to EPM, or an ISPSS token to Secrets Manager SaaS) returns a `401`.

### 5.1 Idira Identity Security Platform Shared Services (Identity, Privileged Access Manager SaaS, SIA)

These services use an OAuth 2.0 client-credentials flow through Idira Identity (ISPSS).

**One-time setup:**

1. In Identity Administration, go to **Core Services → Users** and create a service user. Set a login name, display name, and password.
2. On that user, enable **Is OAuth confidential client** (and **Is Service User**, **Password never expires**).
3. Assign the service user the role(s) that grant the rights this integration needs: system-administrator or user-management rights for Identity workforce actions, `DpaAdmin` for SIA policy actions, and the required Safe permissions for Privileged Access Manager SaaS actions.

**Request a token:**

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/oauth2/platformtoken" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=<service-account-login>" \
  -d "client_secret=<service-account-secret>"
```

Successful response:

```json
{ "access_token": "<jwt>", "token_type": "Bearer", "expires_in": 900 }
```

Use the token on every subsequent call to Identity, Privileged Access Manager SaaS, and SIA:

```
Authorization: Bearer <access_token>
```

Re-request before expiry. Do not request a new token per call, and never write tokens to disk or logs.

### 5.2 Endpoint Privilege Manager (EPM)

If the endpoint containment action is in scope, EPM uses OAuth through Identity but the API header format is `Authorization: basic <token>` (not `Bearer`). See the [EPM SOC Response guide](../../epm/soc-response/development-guide.md) for the full 8-step setup.

### 5.3 Secrets Manager SaaS (Conjur Cloud)

If the machine-identity actions in Section 7.11 are in scope, Secrets Manager SaaS uses its own authenticate flow — a separate JWT, not the ISPSS Bearer token used for Identity/Privileged Access Manager SaaS/SIA.

Use the returned JWT on every subsequent Secrets Manager SaaS call:

```
Authorization: Token token="<jwt>"
```

**What was not fully confirmed in this pass:** the exact request shape of the authenticate call itself (workload vs. user authentication have different flows in Conjur Cloud). Before building, pull the current authenticate API reference from `docs.cyberark.com/secrets-manager-saas` for whichever principal type your service account uses (workload authenticator vs. user), and confirm token lifetime/refresh behavior — it was not stated in the pages retrieved for this guide.

---

## 6. Telemetry Header (Required)

Every Idira API request must include the `x-cybr-telemetry` header, Base64 URL-encoded, as ampersand-delimited key=value pairs:

```
in=<IntegrationName>&it=<IntegrationType>&iv=<version>&vn=<VendorName>
```

| Field | Key | Required | Example |
|:---|:---|:---:|:---|
| Integration Name | `in` | Yes | `in=<Partner> Identity Response` |
| Integration Type | `it` | Yes | `it=SOAR` (or `SIEM` / `XDR` — reflect the partner platform category) |
| Integration Version | `iv` | Yes | `iv=1.0` |
| Vendor Name | `vn` | Yes | `vn=<Partner>` (for example `Palo Alto Networks`, `Google`, `Splunk`) |
| Vendor Version | `vv` | No | `vv=<platform version>` |

Set `in`, `vn`, and `it` to values that describe your platform. Confirm the final values with your Idira Technical Alliances contact before certification.

---

## 7. Core API Operations

> Each action follows the same two-step shape: resolve the target entity, then run the action. Every method and path below was read from live Idira (CyberArk) documentation or the published OpenAPI spec. Replace `<tenant>`, `<subdomain>`, `<EPM_Server>` with your environment values. All hosts are Idira SaaS services.

### 7.1 Get User by Name (resolve user unique ID)

Identity workforce actions target the user by unique ID, not username. Resolve it first.

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/CDirectoryService/GetUserByName" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"name": "<username@suffix>"}'
```

| Field | Required | Description |
|:---|:---:|:---|
| username | Yes | User name of the cloud user to fetch. Format: `username@suffix` if a suffix is required, else `username`. |

> **Note:** The exact JSON key casing for the username field is `[TBD — confirm against your tenant Swagger at /identity-docs-api]`; the input is the username string. The response is a user detail object; read the unique ID from it and use it in the state, logout, role, and password actions below. Use `POST /CDirectoryService/GetUser` to fetch by ID directly.

### 7.2 Get Accounts (resolve account ID)

Rotate and verify calls require the internal account ID.

```bash
curl -X GET \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/Accounts?search=<term>&searchType=contains&safeName=<safe>&limit=50" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "x-cybr-telemetry: <telemetry>"
```

| Query param | Description |
|:---|:---|
| `search` | Keywords to search (for example, account name or address) |
| `searchType` | `contains` (default) or `startswith` |
| `safeName` | Filter to a specific Safe |
| `limit` | Max 1000, default 50 |

**Response — relevant fields:** `id` (unique account ID — use in rotate/verify), `name`, `userName`, `safeName`, `platformId`, `address`, `secretType`, `secretManagement` (automation status, last modified/reconciled/verified timestamps), `remoteMachinesAccess`, `createdTime`. Requires the "List Accounts" permission on the Safe.

**Get account details by ID** — once you have the account `id` (from the search above, or already known from alert context), resolve full details directly without re-searching:

```bash
curl -X GET \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/Accounts/<id>/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "x-cybr-telemetry: <telemetry>"
```

Requires "List Accounts" permission on the Safe where the account is located. Same response shape as the search endpoint above.

**Flag an account into the Discovery Service inventory (lighter-weight alternative to vaulting)** — use this to register a discovered-but-unmanaged account as flagged/under-review without bringing it under full CPM management. This is a lighter action than "Vault a flagged account" (Section 7.7) — it doesn't create a managed Safe account or start credential rotation, it just adds the account to the discovered-accounts inventory for later triage.

```bash
curl -X PUT \
  "https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
        "type": "<account-type>",
        "subType": "loosely",
        "identifiers": {"<key>": "<value>"},
        "source": "<discovering-service-name>",
        "isPrivileged": true
      }'
```

| Field | Required | Description |
|:---|:---:|:---|
| `type` | Yes | Account type |
| `subType` | Yes | Account subtype — documented valid value is `loosely` |
| `identifiers` | Yes | Key-value pairs that define the account's uniqueness |
| `source` | Yes | Name of the service that discovered the account (your integration) |
| `isPrivileged` | No | Whether the account has elevated privileges |
| `customProperties` | No | Additional account metadata |
| `tags` | No | **Deprecated — do not build against this field.** Tag the account with the dedicated tag-associations call below instead. |

Requires the "Privilege Cloud Discovery Source" role. Returns the created discovered-account object (`id`, `type`, `subType`, `identifiers`, `isPrivileged`, `customProperties`, `tags`, `source`).

> **Updated 2026-09-08:** the inline `tags` field on this call is deprecated. Tag management moved to a dedicated API, and **integrations must migrate before November 2026** — after that the legacy field is removed and any tag sent inline is silently dropped.

**Tagging a discovered account (current approach)** — tag as a second call after the account is created, using key-value pairs rather than bare string labels:

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/<discoveredAccount-id>/tag-associations" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"tags": [{"key": "triage-state", "value": "flagged-by-soc"}]}'
```

Take `<discoveredAccount-id>` from the response of the PUT above — do not cache or hardcode it.

> **This request body is inferred, not confirmed — treat it as the one exception to the copy-exactly rule.** The
> `tags` array shape above follows the release note's "key-value format" description and this API's existing
> conventions; it has not been verified against the Privilege Cloud API reference. The endpoint, the method and
> the path are correct. **Confirm the exact payload and response with your Idira Technical Alliances contact
> before you build against it**, and do not let a code generator treat the key names here as settled. Everything
> else quoted verbatim in this guide is exact — this block is marked because it is not.

### 7.3 List Active Privileged Sessions

Resolve the session GUID to act on a live session.

```bash
curl -X GET \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/LiveSessions?Search=<username>&Limit=25" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "x-cybr-telemetry: <telemetry>"
```

**Response — relevant fields:** each session carries `SessionGuid` (use this to terminate/suspend, not the numeric `SessionID`), plus `SessionID`, `User`, `AccountUsername`, `AccountAddress`, `RemoteMachine`, `Protocol`, `RiskScore`, `IsLive`, `Total`, and the capability flags `CanTerminate`, `CanSuspend`, `CanMonitor`. Filter params include `Search`, `Safe`, `FromTime`, `ToTime`, `Activities`, `Limit`, `Offset`, `Sort`.

> **Best practice:** Check `CanTerminate` / `CanSuspend` before issuing the action. Session actions are not supported on PSM for SSH or OPM sessions.

---

### 7.4 Identity (Workforce) Actions

**Lock or disable a user** — sets the account state. `State` accepts `None`, `Locked`, `Disabled`, or `Expired`.

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/CDirectoryService/SetUserState" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"ID": "<user-unique-id>", "State": "Locked"}'
```

| Field | Required | Description |
|:---|:---:|:---|
| `ID` | Yes | Unique ID of the cloud user to change the state for |
| `State` | Yes | `None`, `Locked`, `Disabled`, or `Expired` |

Requires system-administrator or user-management rights. An equivalent path is `POST /UserMgmt/SetCloudLock` with body `{"lockUser": true}` (the user-ID key on that endpoint is `[TBD — confirm against tenant Swagger]`); `SetUserState` is preferred because its fields are fully documented.

**Force logout of all sessions** — deletes all sessions and cookies for the user; the user must sign in again.

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/UserMgmt/SignOutEverywhere" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"<userIdKey>": "<user-unique-id>"}'
```

The body carries the target user's unique ID. The exact JSON key is `[TBD — confirm against tenant Swagger]`. This endpoint requires system-administrator or user-management rights (or the user acting on themselves). Do not use `POST /Security/Logout` for this: that endpoint only logs out the caller's own token (its body field is `redirectUrl`), not a target user.

**Expire password / require reset** — force the user to set a new password.

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/CDirectoryService/ChangeUser" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"Name": "<username>", "ForcePasswordChangeNext": true}'
```

`ForcePasswordChangeNext` requires the user to change password on next login. Alternatively, `SetUserState` with `State: "Expired"` expires the account.

**Remove a privileged role** — strip standing privilege by removing the user from a role.

```bash
curl -X POST \
  "https://<tenant>.id.cyberark.cloud/SaasManage/RemoveUsersAndGroupsFromRole" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"Name": "<role-unique-id>", "Users": ["<user-unique-id>"]}'
```

| Field | Required | Description |
|:---|:---:|:---|
| `Name` | Yes | Unique ID of the role |
| `Users` | Yes | Array of user unique IDs (or user names) to remove from the role |
| `Roles` | No | Array of role IDs/names to remove |
| `Groups` | No | Array of group IDs/names to remove |

> **Enforce MFA step-up:** MFA enforcement is policy-based rather than a single "require MFA now for user X" call. Apply it by assigning an authentication profile (Auth Profile API) or an authentication policy to the user. Note that `POST /CDirectoryService/ExemptUserFromMfa` is the inverse operation and must never be called as part of a containment response.

---

### 7.5 Terminate a Privileged Session

Ends a live monitored session by GUID.

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/LiveSessions/<SessionGuid>/Terminate/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

No request body. The service account needs session-monitoring termination rights on the Privileged Access Manager SaaS tenant. Confirm the exact session-termination permission on your tenant before go-live.

### 7.6 Suspend or Resume a Privileged Session

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/LiveSessions/<SessionGuid>/Suspend/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Substitute `Resume` for `Suspend` to lift the pause. No request body. Requires session-monitoring suspension rights. Not supported for SSH or OPM sessions.

---

### 7.7 Secrets and Credential Actions

**Rotate a credential now** — triggers the CPM to change the credential without delay.

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/Accounts/<AccountID>/Change/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"ChangeCredsForGroup": false}'
```

| Field | Required | Description |
|:---|:---:|:---|
| `ChangeCredsForGroup` | No | Whether the CPM changes credentials on all accounts in the same group. Default `true`. |

> **Note:** The live docs page shows `ChangeEntireGroup` in the sample JSON but names the field `ChangeCredsForGroup` in the parameters table. The parameters table is authoritative; test against your target tenant. Requires "Initiate CPM password management operations" on the Safe. This is a standard CPM operation. Do not use "ARS" or "SRS" naming.

**Verify a credential** — marks the account for CPM verification to confirm rotation succeeded.

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/Accounts/<AccountID>/Verify/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "x-cybr-telemetry: <telemetry>"
```

No request body. To confirm the result, poll `GET /PasswordVault/API/Accounts/<AccountID>` and read `lastVerifiedDateTime`, `lastModifiedDateTime`, and `lastReconciledDateTime`.

**Vault a flagged account** — add a privileged account that the partner platform flagged as risky but that is not yet managed.

```bash
curl -X POST \
  "https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/API/Accounts" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{
        "platformId": "<PlatformID>",
        "safeName": "<SafeName>",
        "name": "<account-name>",
        "address": "<machine-address>",
        "userName": "<account-username>",
        "secretType": "password",
        "secret": "<secret-value>",
        "secretManagement": {"automaticManagementEnabled": true}
      }'
```

| Field | Required | Description |
|:---|:---:|:---|
| `platformId` | Yes | Platform definition (case-sensitive) |
| `safeName` | Yes | Target Safe |
| `name` | No | Account object name |
| `address` | No | Machine name or address |
| `userName` | No | Account user name |
| `secretType` | No | `password` or `key` |
| `secret` | No | The password or SSH key value |
| `secretManagement.automaticManagementEnabled` | No | Enables CPM auto-management |

Requires "Add account" plus "Update password" or "Update password properties" on the Safe. The response includes the assigned `id`.

---

### 7.8 Disable a Secure Infrastructure Access Policy

Revoke standing or just-in-time access by disabling (or deleting) a Secure Infrastructure Access (SIA) policy.

```bash
# List policies to find the target
curl -X GET \
  "https://<subdomain>.dpa.cyberark.cloud/api/access-policies" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"

# Disable the policy in place
curl -X PUT \
  "https://<subdomain>.dpa.cyberark.cloud/api/access-policies/<policy_id>" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"policyId": "<policy_id>", "policyName": "<name>", "status": "Disabled"}'
```

| Field | Required | Description |
|:---|:---:|:---|
| `policyId` | Yes | Policy UUID |
| `policyName` | Yes | Policy name, 1–200 chars |
| `status` | No | `Irrelevant`, `Enabled`, `Disabled`, `Draft`, or `Expired`. Set `Disabled` to revoke. |

Requires the `DpaAdmin` role. To remove the policy entirely, use `DELETE /api/access-policies/<policy_id>` (no body).

> **Note:** Disabling (or deleting) the policy is the supported revocation path documented here.
>
> **SIA in-progress session termination — confirmed, not partner-callable.** SIA has a real "SSH session termination" capability (`manage/privileged-access` and `detect-and-respond/itdr` doc spaces), but it fires only from ITDR's built-in Suspicious Activities Rules when a risky command pattern matches — there is no documented REST endpoint for an external XDR/SIEM/SOAR to trigger it on demand. If your use case needs partner-triggered SIA session termination, that capability does not exist today; raise it as a product gap with your Idira Technical Alliances contact rather than searching for an undocumented endpoint.

---

### 7.9 Endpoint Containment (EPM)

To trigger endpoint privilege containment as part of the response, add the endpoint to an EPM static risk group. This uses the EPM API (`Authorization: basic <token>`) and is fully documented in the [EPM SOC Response guide](../../epm/soc-response/development-guide.md). Do not duplicate that logic here; call it as a step in the playbook.

---

### 7.10 Secure Cloud Access (SCA) — session revocation

Secure Cloud Access documentation moved into the platform's "Manage" space in the April 2026 docs reorg (`docs.cyberark.com/manage/latest/en/content/sca/`). Its API landing page (`sca/automation/apis.htm`) confirms six SCA API families exist: **Access API**, Authentication API, Cloud scan API, Integrations API, Web app creation API. (Policy revocation for SCA goes through the shared **Access Control Policies API** described in Section 7.8, not a separate SCA-only policy API.) All require OAuth2 token authentication (`sca_oauth2-server-setup.htm`).

The Access API's session-revocation operations are named on the `api-docs.cyberark.com/sca-api` reference (Access tag):

| Operation | Confirmed method + path shape | What it does |
|:---|:---|:---|
| Get sessions | `GET /access/sessions` | List active SCA sessions (tenant-wide) |
| Get sessions by user | `GET /access/user/{id}/sessions` | List active sessions for one user |
| Revoke session by ID | `POST /access/sessions/revoke` | End one specific session |
| Revoke all sessions for a user | `POST /access/sessions/user/{id}/revoke` | End every active session for one user |

**How confident is this:** the operation names and their method (GET/POST) come directly from the ReadMe.io-hosted reference's own operation IDs (`get-access-sessions`, `get-access-user-id-sessions`, `post-access-sessions-revoke`, `post-access-sessions-user-id-revoke`), which ReadMe generates from the underlying OpenAPI spec's method and path. That's a reliable signal for *which operations exist and roughly what they do* — but the exact path structure (whether `{id}` sits where shown above), the request body for the revoke calls (session ID field name, single vs. bulk), and full response schema were **not independently rendered** — `api-docs.cyberark.com/sca-api` requires an authenticated session, which this pass didn't have. Every other host in this guide has a publicly readable reference; SCA's does not.

**Before building against SCA:** get an authenticated `api-docs.cyberark.com/sca-api` session (your Idira Technical Alliances contact can provision this) and confirm the exact request/response schema for the four operations above against a live tenant call — do not ship against the path shapes in the table without that confirmation.

> **Added 2026-09-17 — one more thing to confirm in the same pass.** As of 2026-09-14 SCA also brokers **Zero Standing Privileges access to Kubernetes clusters (EKS, AKS) through a native CLI**, alongside the cloud-console access this section was written against. Whether a Kubernetes CLI session appears in `GET /access/sessions` — and whether "revoke all sessions for a user" terminates it — is **not stated in the release note and was not verified here**. If your playbook's containment claim covers a customer's cloud infrastructure access, confirm Kubernetes session coverage explicitly during the live-tenant check above; do not assume revoking console sessions ends CLI-brokered cluster access.

---

### 7.11 Machine Identity Actions (Secrets Manager SaaS / Conjur Cloud)

Secrets Manager SaaS (Conjur Cloud) has its own machine-identity containment actions, separate from Privileged Access Manager SaaS's human-account credential actions in Section 7.7. Use these when the compromised identity is a workload (application, script, CI/CD job, service account) rather than a human user.

**Authenticate first** — this service uses its own JWT, not the ISPSS Bearer token used elsewhere in this guide. The exact authenticate request shape (workload vs. user principal) was not confirmed in this pass — see Section 5.3. Once you have a JWT, use it as `Authorization: Token token="<jwt>"` (not `Bearer`, not `basic`) on every call below.

**Delete a workload** — revokes a compromised machine identity's ability to authenticate and retrieve secrets. Not reversible; the workload must be re-onboarded to restore access.

```bash
curl -X DELETE \
  "https://<subdomain>.secretsmgr.cyberark.cloud/api/workloads/<url-encoded-identifier>" \
  -H "Authorization: Token token=\"<jwt>\"" \
  -H "Accept: application/x.secretsmgr.v2beta+json"
```

| Field | Required | Description |
|:---|:---:|:---|
| `identifier` | Yes | URL-encoded `<policy-branch>/<workload-name>`. For example, workload `github-dev` under branch `data/app-path` encodes to `data%2Fapp-path%2Fgithub-dev`. |

Requires update permissions on the workload's policy. Returns `204` on success, `404` if the workload doesn't exist, `403` if the caller lacks permission.

**Delete an authenticator** — revokes an entire authentication method (every workload using it loses access at once). Use this for a broader compromise — a leaked JWT signing key or AWS IAM trust relationship — not a single flagged workload.

```bash
curl -X DELETE \
  "https://<subdomain>.secretsmgr.cyberark.cloud/api/authenticators/<type>/<name>" \
  -H "Authorization: Token token=\"<jwt>\"" \
  -H "Accept: application/x.secretsmgr.v2beta+json"
```

| Field | Required | Description |
|:---|:---:|:---|
| `type` | Yes | One of `jwt`, `azure`, `aws_iam`, `certificate` |
| `name` | Yes | The authenticator's name |

Requires membership in the `Authn_Admins` group (or `Conjur_Cloud_Admins`). Returns `204` on success. **This is a wide-blast-radius action** — deleting an authenticator cuts off every workload that authenticates through it, not just the one your alert flagged. Reserve it for a confirmed authenticator-level compromise (e.g. a leaked signing key), not as a default response to a single suspicious workload.

> **What was not confirmed:** whether Secrets Manager SaaS exposes a reversible "suspend" or "remove from group" action as an alternative to outright deletion. The Group Membership API (`ccl-api-group-member.htm`) documents adding a member (`POST /api/groups/{identifier}/members`); no removal/DELETE variant was found in the docs mirror used for this research. If a reversible containment option matters for your use case, confirm with your Idira Technical Alliances contact before assuming deletion is the only lever.

---

## 8. Integration Workflow

```
Partner platform detects an identity-related threat (alert / detection / correlation rule)
        │
        ▼
Playbook selects the response action(s) by severity and exposure context
        │
        ▼
[Auth] Obtain the correct token(s):
  ISPSS Bearer (Identity / Privileged Access Manager SaaS / SIA) · EPM basic token · Secrets Manager SaaS JWT (its own authenticate call)
        │
        ▼
[Resolve] username → user ID (GetUserByName) · account name → account ID (Get Accounts) · user → SessionGuid (LiveSessions) · workload/authenticator identifier (known from alert context)
        │
        ▼
[Act] Run one action or a "Red Button" set:
  Lock user (SetUserState) · Force logout (SignOutEverywhere) · Terminate session · Rotate credential (Change) ·
  Remove role · Disable SIA policy · Vault flagged account · Delete workload/authenticator (Secrets Manager) · Contain endpoint (EPM)
        │
        ▼
[Feedback] Collect per-action status (success / partial / failure) → incident timeline
        │
        ▼
[Reversible, where applicable] Unlock, resume session, re-add role after investigation closes
```

---

## 9. Integration Patterns

| Pattern | When to use |
|:---|:---|
| **Single surgical action** | Analyst triggers one action during investigation (for example, terminate one session) without full containment. |
| **Red Button (full containment)** | High-confidence incident: run a predefined set (lock user, force logout, terminate sessions, rotate exposed credential, remove privileged role) in one playbook step, collecting per-action status. |
| **Severity-routed** | Map the partner alert severity to action scope: high → full containment, medium → lock + logout only, low → notify. |
| **Exposure-aware branching** | Use the partner platform's exposure context (production vs development, data sensitivity) to decide whether to disable a SIA policy or only rotate the credential. |

Because v1 is stateless execution, the partner playbook owns sequencing, rollback, and idempotency. Log the target IDs, action, alert ID, and timestamp at each step to build an audit trail linkable to the source incident. Some platforms (for example, Cortex XSIAM) can also deploy default correlation rules that fire these actions; treat that as a platform-specific enhancement, not a core requirement.

---

## 10. Error Handling

| HTTP status | Meaning | Action |
|:---|:---|:---|
| `200` | Success | Log the target ID, action, and alert ID; verify state change where relevant |
| `400` | Validation error | Parse the error body; check for a malformed ID or wrong field name (for example, `ChangeCredsForGroup`) |
| `401` | Token invalid or wrong auth model | Confirm the correct model for the target: `Bearer` for ISPSS services, `basic` for EPM, `Token token="<jwt>"` for Secrets Manager SaaS. Re-authenticate and retry once |
| `403` | Insufficient permissions | Verify the required role/rights (system-admin or user-management for Identity, `DpaAdmin` for SIA, Safe permissions for Privileged Access Manager SaaS, `Authn_Admins`/`Conjur_Cloud_Admins` for Secrets Manager authenticator deletion) |
| `404` | Target not found | User, account, session GUID, policy ID, workload, or authenticator not resolved; re-run the resolve step |
| `409` | Conflict | Target already in the requested state (for example, already locked); treat as idempotent, log and continue |
| `429` | Rate limited | Exponential backoff; do not retry in a tight loop |
| `500` | Server error | Log the full response, retry after backoff, alert if persistent |

---

## 11. Pre-Development Checklist

**Authentication**
- [ ] Identity OAuth confidential client created with system-administrator or user-management rights
- [ ] ISPSS `platformtoken` call tested; returns an `access_token`; `Bearer` header confirmed for Identity / Privileged Access Manager SaaS / SIA
- [ ] SIA `DpaAdmin` role confirmed on the service account (if SIA actions in scope)
- [ ] EPM auth configured with `basic <token>` header (if endpoint action in scope)
- [ ] Secrets Manager SaaS authenticate call tested; JWT returned; `Token token="<jwt>"` header confirmed (if machine-identity actions in scope) — do not reuse the ISPSS Bearer token here
- [ ] Service-account credentials stored in a secrets manager, not in playbook or connector code

**Target resolution**
- [ ] Alert payload confirmed to carry username, account identifier, hostname, and/or workload/authenticator identifier as needed
- [ ] `GetUserByName` returns the user unique ID
- [ ] `Get Accounts` resolves the account ID for rotate/verify
- [ ] `LiveSessions` returns `SessionGuid` and the `CanTerminate`/`CanSuspend` flags
- [ ] Workload/authenticator identifier resolution confirmed (policy-branch path, URL-encoded correctly) — if machine-identity actions in scope

**Action logic**
- [ ] Each action returns per-action status; partial-success handling implemented
- [ ] `ChangeCredsForGroup` field name validated against the target tenant
- [ ] `[TBD]` field-name items confirmed against your tenant Swagger: `SignOutEverywhere` body key, `GetUserByName` key casing, Privileged Access Manager SaaS session-termination permission model
- [ ] Reversible actions (unlock, resume, re-add role) tested where the playbook offers rollback
- [ ] Idempotency handled (409 on already-locked / already-member; 404 treated as already-deleted for workload/authenticator delete)
- [ ] Delete-workload / delete-authenticator calls gated behind a confirmed-compromise check — these are not reversible; do not include them in a default/low-severity response path
- [ ] Telemetry header values (`in`, `it`, `vn`) set to describe the partner platform and agreed with the Idira Technical Alliances contact
- [ ] Logging captures target ID, action, alert ID, and API response per step

---

## 12. Resources

**Authentication**
- [Idira Identity Security Platform API authentication (ISPSS)](https://docs.cyberark.com/setup/latest/en/content/ispss-deployment/ispss/ispss-api-authentication.htm)
- [Create an API token](https://api-docs.cyberark.com/create-api-token/docs/create-api-token)

**Identity workforce APIs**
- [CDirectory Service API](https://api-docs.cyberark.com/identity-docs-api/docs/cdirectory-service-api) — `GetUserByName`, `GetUser`, `SetUserState`, `ChangeUser`
- [User Management API](https://api-docs.cyberark.com/identity-docs-api/docs/user-mgmt-api) — `SignOutEverywhere`, `SetCloudLock`
- [SaaS Manage API](https://api-docs.cyberark.com/identity-docs-api/docs/saas-manage-api) — `RemoveUsersAndGroupsFromRole`
- [Auth Profile API](https://api-docs.cyberark.com/identity-docs-api/docs/auth-profile-api) — authentication profiles for MFA policy

**Privileged sessions and credentials (Privileged Access Manager SaaS)**
- [Get live sessions](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/getlivesessions.htm)
- [Terminate active session](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/pta-psm-terminatesession.htm)
- [Suspend/resume active session](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/suspend-resumesession.htm)
- [Accounts API actions](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/api-account-actions-lp.htm)
- [Add account](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/add%20account%20v10.htm)
- [Change credentials immediately](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/change-credentials-immediately.htm)
- [Verify credentials](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/verify-credentials-v9-10.htm)

> Session, account, and credential API paths are shared between Idira Privileged Access Manager SaaS and Self-Hosted. This guide targets the Privileged Access Manager SaaS host and Bearer auth; confirm each endpoint against your Privileged Access Manager SaaS tenant Swagger (`/PasswordVault/swagger`) before shipping.

**Secure Infrastructure Access (SIA)**
- [SIA access policies](https://docs.cyberark.com/setup/latest/en/content/privileged-access/apis/dpa_policies.htm)
- [SSH session termination](https://docs.cyberark.com/manage/latest/en/content/privileged-access/admin/ssh-session-termination.htm) — automatic/ITDR-triggered only, not partner-callable; see Section 7.8

**Machine identity (Secrets Manager SaaS / Conjur Cloud)**
- [Delete workload](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-delete-workload.htm)
- [Delete authenticator](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-del-auth.htm)
- [Group membership (add member; no removal endpoint found)](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-group-member.htm)
- [REST APIs landing page](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-rest-apis-lp.htm)

**Secure Cloud Access (SCA)**
- [SCA APIs overview](https://docs.cyberark.com/manage/latest/en/content/sca/automation/apis.htm) — confirms the Access API family; endpoint detail requires an authenticated session at [api-docs.cyberark.com/sca-api](https://api-docs.cyberark.com/sca-api)

**Related guide**
- [EPM SOC Response development guide](../../epm/soc-response/development-guide.md)

**Sandbox and contact**
- [C3 Integrations Platform](https://c3.cyberark.cloud)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`
