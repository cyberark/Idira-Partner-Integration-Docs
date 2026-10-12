# Idira EPM — SOC Response (XDR/SOAR) Development Guide

**Workflow:** EPM
**Use Case:** SOC Response — XDR/SOAR Endpoint Containment
**Idira Product:** Endpoint Privilege Manager (EPM)
**Type:** Development Guide
**Version:** 1.6
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-08

---

> **Not sure this is the right guide?** See the [EPM Decision Guide](../decision-guide.md) first.
> Use this guide if: your platform is an XDR, SOAR, or SIEM and you want to trigger privilege-restriction policies on Windows endpoints in response to threat alerts.

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Endpoint Privilege Manager (EPM) — manages application and user privileges on Windows endpoints via agent-based policy enforcement.
WORKFLOW: EPM
USE CASE: SOC Response — XDR/SOAR platforms trigger EPM to add a suspicious endpoint to a static risk group, applying pre-configured restrictive policies. Analyst removes the endpoint post-investigation to restore baseline.
INTEGRATION PATTERN: REST API — SOAR calls EPM APIs to resolve endpoint ID, find the risk group ID, then add/remove the endpoint from the group.
AUTH METHOD: OAuth 2.0 client_credentials flow via Idira Identity Administration (8-step setup — see Section 4)
AUTH HEADER FORMAT: Authorization: basic <Token>  (note: "basic", not "Bearer")
BASE URL: https://<EPM_Server>.epm.cyberark.com/  (EPM_Server = subdomain from EPM console URL, e.g. "na101")
TOKEN ENDPOINT: https://<sub-domain>.id.cyberark.cloud/oauth2/token/<app-alias>
TELEMETRY: Required on all requests — x-cybr-telemetry header, Base64url-encoded key=value pairs
SANDBOX: C3 Integrations Platform — request access at cybr-bizdevtech@paloaltonetworks.com
CONTACT: cybr-bizdevtech@paloaltonetworks.com

KEY CONSTRAINTS:
- EPM Windows agents version 26.4+ required — integration will not work on older agents
- Windows and Windows Server endpoints only — macOS/Linux not supported by this use case
- Endpoint management service APIs must be enabled in the EPM tenant
- Two policy packages must be imported before the static groups can enforce restrictions: SOC_Response_Application_Policies.epmp and SOC_Response_User_Policies.epmp
- MFA must be configured on the EPM tenant for medium-risk policies to function
- Static group names are case-sensitive: High_Risk_Endpoint and Medium_Risk_Endpoint
- SetId is required in the URL for ALL API calls — retrieve it once via the Get sets list API and cache it
- All four SOC response API calls use POST (including the delete/remove call)

WORKFLOW SUMMARY (4 API calls — all POST):
  1. POST /EPM/API/<Version>/Sets/<SetId>/Endpoints/search  → resolve endpoint id from hostname/IP (body: {"filter": "name EQ \"<hostname>\""})
  2. POST /EPM/API/v2/Sets/<SetId>/endpoints/groups/search  → resolve GroupId for High_Risk_Endpoint or Medium_Risk_Endpoint (body: {"filter": "name EQ \"High_Risk_Endpoint\" AND type EQ \"Static\""})
  3. POST /EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids  → add endpoint to risk group (body: {"membersIds": ["<endpointId>"]})
  4. POST /EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids/remove  → remove endpoint post-investigation (body: {"membersIds": ["<endpointId>"]})

RESPONSE TIERS:
- High_Risk_Endpoint: blocks all unsigned executables, scripts, MSU files, installers, risky downloads + blocks all privilege elevation
- Medium_Risk_Endpoint: blocks elevation of sensitive tools from risky sources + requires MFA for remaining elevation attempts

TERMINOLOGY (use these exact names in code and docs):
- CyberArk EPM → Idira EPM / Idira Endpoint Privilege Manager
- CyberArk Privilege Cloud → Idira Privileged Access Manager SaaS

FILES IN THIS DIRECTORY:
- development-guide.md — this file — full integration guide
- certification-checklist.md — requirements checklist for Idira certification review
- ../decision-guide.md — helps partners decide which EPM integration to build
-->

---

## 1. Why This Integration Matters

Modern attacks rarely rely on malware — 79% of cyberattacks in 2024 used malware-free techniques such as stolen credentials and living-off-the-land tools (CrowdStrike Global Threat Report 2025). Privilege escalation via access token manipulation or elevation control abuse frequently occurs within hours of initial access — a window manual SOC response cannot close. Connecting an XDR or SOAR platform directly to EPM's endpoint containment API turns a detection signal into an automated privilege-restriction action, reducing attacker dwell time and limiting blast radius without requiring an analyst to act before the damage is done.

**Industry drivers:**
- **Credential abuse is the top breach vector for the second consecutive year:** stolen account use represented 30% of all IBM X-Force incidents in 2024; Verizon DBIR 2024 confirms ~31% of breaches involved stolen credentials — making automated privilege revocation the highest-ROI SOAR response action.
- **Zero Trust mandates require automated endpoint enforcement:** NIST SP 800-207, CISA Zero Trust Maturity Model v2 (2023), and US Executive Order 14028 collectively require dynamic, automated least-privilege enforcement at the device layer — converting EPM from a compliance checkbox into a mandated automated response capability.
- **NIS2 and DORA extend the mandate to EU markets:** NIS2 (effective October 2024, 18 critical sectors) and DORA (effective January 2025, all EU financial entities) require automated access control and incident response, structurally expanding regulatory demand well beyond the US federal market.
- **MITRE ATT&CK maps privilege escalation as the critical pivot:** T1134 (Access Token Manipulation) and T1548 (Abuse Elevation Control Mechanism) are documented in active campaigns including Volt Typhoon (OT/critical infrastructure) and multiple ransomware chains — EPM policy enforcement directly interrupts these techniques at the endpoint.
- **Ransomware losses reinforce urgency:** The Change Healthcare breach (Feb 2024, $872M+ in disclosed losses) and the MGM/Caesars incidents (Sep 2023) both involved privilege escalation chains; HHS 2024 Cybersecurity Performance Goals now explicitly cite privileged access management as a required essential control for health systems.

**Customer demand signals:**
- Integration guides for SentinelOne and Palo Alto Cortex XDR are published on the Idira Marketplace, confirming active field demand.
- Financial services (PCI-DSS 4.0, DORA, SOX), healthcare (HHS CPGs), and US federal/DoD contractors (EO 14028, CMMC 2.0) represent the highest-concentration verticals.
- BeyondTrust and Delinea publish SOAR integrations for vault/session workflows but do not address real-time XDR-triggered endpoint privilege containment — this capability is an unaddressed gap across all major PAM/EPM vendors.

---

## 2. What the Customer Sees

When a SOAR playbook triggers the integration, the target endpoint is silently added to a static risk group in EPM. The agent running on that endpoint immediately picks up the new group membership and enforces the pre-loaded restrictive policy package — without requiring a restart or manual intervention.

The SOC analyst sees the endpoint in the `High_Risk_Endpoint` or `Medium_Risk_Endpoint` group in the EPM management console. Post-investigation, the analyst (or an automated playbook step) removes the endpoint from the group, restoring its baseline policy.

| EPM Console Field | Source |
|:------------------|:-------|
| Computer Name | Resolved from alert hostname/IP via Get Endpoints API |
| Risk Group | `High_Risk_Endpoint` or `Medium_Risk_Endpoint` (static) |
| Policy enforcement | Automatic on group membership change |
| Restoration | DELETE group membership call |

---

## 3. Prerequisites

### Idira Environment

| Requirement | Detail |
|:------------|:-------|
| EPM agent version | 26.4 or later on all target Windows endpoints |
| Endpoint types | Windows and Windows Server only |
| Endpoint management service | Must be enabled in the EPM tenant — see [Enhanced endpoint management support](https://docs.cyberark.com/epm/latest/en/content/intro/extend-soc-response-options.htm#Beforeyoubegin) |
| Policy packages imported | `SOC_Response_Application_Policies.epmp` and `SOC_Response_User_Policies.epmp` must be imported before go-live — download from the Idira Marketplace |
| Static groups created | `High_Risk_Endpoint` and `Medium_Risk_Endpoint` must exist in the EPM tenant — see [Set up EPM for SOC response](https://docs.cyberark.com/epm/latest/en/content/intro/extend-soc-response-options.htm#SetupEPMforSOCresponse) |
| Audit settings | Enabled for all SOC response policies |
| MFA | Configured on the EPM tenant if medium-risk policies are in scope |
| Identity Administration access | Required to create the service user and OAuth web app (Steps 1–4 in Section 4) |
| Sandbox | C3 Integrations Platform — request access at `cybr-bizdevtech@paloaltonetworks.com` |

### Partner Environment

| Requirement | Detail |
|:------------|:-------|
| Platform type | XDR, SOAR, or SIEM with outbound webhook or playbook action capability |
| Outbound connectivity | SOAR/XDR platform must reach `https://<epm-tenant>.epm.cyberark.com` |
| Alert data available | Alert payload must include hostname or IP of the suspicious endpoint |
| OAuth credential store | Secure storage for EPM Client ID and Client Secret (not in playbook code) |

---

## 4. Authentication

EPM uses an OAuth 2.0 client credentials flow configured through **Idira Identity Administration**. You need three things before making any API call: a service user, an OAuth web app bound to that user, and your EPM server name. Full reference: [Set up API authentication for EPM REST APIs using Identity](https://docs.cyberark.com/epm/latest/en/content/webservices/authenticate-with-identity-administration.htm).

### 4.1 One-time setup (8 steps)

**Step 1 — Create a service user**

In Identity Administration, go to **Core Services → Users → Add User**. Set a login name, display name, and password. Under Status, enable **Is OAuth confidential client**, **Is Service User**, and **Password never expires**. Save.

**Step 2 — Assign the service user to an EPM role**

Go to **Core Services → Roles**, open the EPM role with the permissions this integration needs (at minimum: *View Only* for Computers; *Move Computer to Group* for containment actions), and add the service user as a member.

> The required permissions per API call are:
> - Get Endpoints: *Computers → View Only*
> - Search Groups: *Computers → View Only*
> - Add/Delete group members: *Computers → Move Computer to Group*

**Step 3 — Create a custom EPM API web app**

Go to **Apps & Widgets → Web Apps → Add Web Apps**, search for **EPM**, and add **Idira EPM API Client**. Confirm, then close the wizard.

**Step 4 — Configure token expiration and bind the service user**

On the new web app, open the **Tokens** tab, set the desired expiration period, and save. Open the **Permissions** tab, click **Add**, select the service user, confirm, and save. The web app status should change from *Ready to Deploy* to **Deployed**.

**Step 5 — Find your Identity sub-domain**

Your token endpoint is `https://<sub-domain>.id.cyberark.cloud/oauth2/token/<app-alias>`. The `<sub-domain>` is your Identity Administration tenant sub-domain (e.g. `aax4917`). The `<app-alias>` is the alias shown on the web app page.

**Step 6 — Request a token**

```bash
curl -u "<service-user>@<tenant-domain>:<password>" \
  -X POST \
  -d "grant_type=client_credentials" \
  https://<sub-domain>.id.cyberark.cloud/oauth2/token/<app-alias>
```

A successful response returns a JWT access token:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "Bearer",
  "expires_in": <seconds>
}
```

**Step 7 — Find your EPM server name**

Log in to the EPM management console. In the browser address bar, copy the subdomain before `.epm.cyberark.com`. If the URL is `https://na101.epm.cyberark.com/...`, your EPM server name is `na101`.

**Step 8 — Get your SetId**

All EPM API calls require a `SetId` in the URL. Retrieve it once and cache it:

```bash
curl -X GET \
  "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets" \
  -H "Authorization: basic <access_token>"
```

See [Get sets list](https://docs.cyberark.com/epm/latest/en/content/webservices/getsetslist.htm) for the full response schema. Store the `Id` value for your target set — you will use it in every subsequent call.

### 4.2 Using the token

Include the token in every EPM API request:

```
Authorization: basic <access_token>
```

> **Important:** EPM APIs use `basic <token>`, not `Bearer <token>`. Using `Bearer` will result in a `401`.

Token lifetime is set in the web app Tokens tab. Re-request before expiry — do not request a new token on every API call, and never log or store tokens on disk.

---

## 5. Telemetry Header (Required)

Every API request must include the `x-cybr-telemetry` header, Base64 URL-encoded:

```
in=<IntegrationName>&it=SOCResponse&iv=<version>&vn=<VendorName>
```

| Field               | Key  | Required | Example                       |
| :------------------ | :--- | :------: | :---------------------------- |
| Integration Name    | `in` |   Yes    | `in=SentinelOne SOC Response` |
| Integration Type    | `it` |   Yes    | `it=SOCResponse`              |
| Integration Version | `iv` |   Yes    | `iv=1.0`                      |
| Vendor Name         | `vn` |   Yes    | `vn=SentinelOne`              |
| Vendor Version      | `vv` |    No    | `vv=23.4`                     |

---

## 6. Integration Workflow

```
XDR/SOAR detects threat alert with endpoint hostname/IP
        │
        ▼
SOAR playbook triggers EPM integration action
        │
        ▼
[One-time at startup] Retrieve SetId
GET /EPM/API/<Version>/Sets  →  cache SetId
        │
        ▼
Step 1: Resolve endpoint id
POST /EPM/API/<Version>/Sets/<SetId>/Endpoints/search
  Body: { "filter": "name EQ \"<hostname>\"" }
        │
        ▼
Step 2: Resolve GroupId (cache at startup)
POST /EPM/API/v2/Sets/<SetId>/endpoints/groups/search
  Body: { "filter": "name EQ \"High_Risk_Endpoint\" AND type EQ \"Static\"" }
  (or "Medium_Risk_Endpoint" depending on alert severity)
        │
        ▼
Step 3: Add endpoint to risk group
POST /EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids
  Body: { "membersIds": ["<endpointId>"] }
        │
        ▼
EPM agent enforces restrictive policy on endpoint immediately
        │
        ▼
[Investigation complete]
        │
        ▼
Step 4: Remove endpoint from risk group
POST /EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids/remove
  Body: { "membersIds": ["<endpointId>"] }
        │
        ▼
EPM agent restores baseline policy
```

---

## 7. Core API Operations

> **Updated 2026-09-08 — set management is being retired on a published timeline.** EPM is folding into the Identity Security Platform, and the console now carries hard dates: **2026-10-31** My Computers support ends · **2026-12-31** access removed · **2027-01-01** EPM set management disabled · **2027-03** standalone console access revoked. Separately, sets with no agents migrate to the new endpoint management service in release **26.9.1**, which **shipped 2026-09-27** — this migration is now live, not pending. In that release, existing sets with no endpoints have endpoint groups activated automatically, and new sets include them by default.
>
> Every operation in this section is addressed as `Sets/<SetId>/…`. **Do not treat `SetId` as a permanent identifier** — resolve it at startup, cache it for the run only, and re-resolve on a `404`. Build the set lookup as one replaceable function rather than threading `SetId` through the integration, so the migration is a single change point.

> All four SOC response calls use **POST**. Replace `<Version>` with the current EPM API version (e.g. `25.2.0.0`) — omitting it defaults to the latest. `<EPM_Server>` is the subdomain from your EPM console URL (e.g. `na101`). `<SetId>` must be retrieved once at startup via Get sets list — see Section 4.1 Step 8.
>
> Full API reference: [Endpoint management APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-apis/endpointmgmntapis.htm) · [Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm)

### 7.1 Get Endpoints (Resolve endpoint id)

Resolves the internal EPM endpoint `id` from a hostname or IP address. This id is required for the group membership calls. Full reference: [Get endpoints](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-apis/get-endpoints.htm).

```bash
curl -X POST \
  "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets/<SetId>/Endpoints/search" \
  -H "Authorization: basic <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <Base64url-encoded telemetry>" \
  -d '{"filter": "name EQ \"<hostname>\""}'
```

Filter by IP address instead: `"filter": "ip EQ \"<ip-address>\""`

**Response — relevant fields:**

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | UUID | Use this as `endpointId` in group membership calls |
| `name` | String | Hostname as registered in EPM |
| `version` | String | Agent version — verify ≥ 26.4 |
| `platform` | String | Must be `Windows` |

> **Best practice:** If the filter returns multiple results, narrow it with `AND platform EQ Windows`. Log the `id` used per alert for auditability.
>
> **Updated 2026-09-28 — platform filtering does not resolve duplicate endpoint *records*.** EPM 26.9.1 ships a **Remove duplicate endpoints** bulk action and an **Endpoints with duplicates** report type. A duplicate record is one machine registered twice, so it carries the same `platform` value — adding `AND platform EQ Windows` cannot disambiguate it. **Never contain an arbitrary match:** if more than one endpoint remains after filtering, fail the playbook step and surface the ambiguity to the analyst. Containing the wrong endpoint is worse than a delayed containment. Have the EPM administrator clear duplicates via the **Endpoints with duplicates** report before go-live.

---

### 7.2 Search Endpoint Groups by Filter V2 (Resolve GroupId)

Retrieves the `id` of a named static group. Call once per group name at startup and cache the result — group IDs are stable unless the group is deleted and recreated, and the endpoint group APIs allow only **10 calls per 2 minutes**. Full reference: [Search endpoint groups by filter (V2)](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/search-groups-by-filter-v2.htm).

```bash
curl -X POST \
  "https://<EPM_Server>.epm.cyberark.com/EPM/API/v2/Sets/<SetId>/endpoints/groups/search" \
  -H "Authorization: basic <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <Base64url-encoded telemetry>" \
  -d '{"filter": "name EQ \"High_Risk_Endpoint\" AND type EQ \"Static\""}'
```

Run the same call substituting `Medium_Risk_Endpoint` for the second group.

**Response — relevant fields:**

| Field | Type | Description |
|:------|:-----|:------------|
| `id` | UUID | Use as `<GroupId>` in Add/Delete member calls |
| `name` | String | Confirm matches `High_Risk_Endpoint` or `Medium_Risk_Endpoint` |
| `type` | String | Must be `Static` |
| `membersCount` | Integer | Current number of endpoints in the group |

> **Note:** This replaces the deprecated V1 Search endpoint groups API. Always use the V2 path (`/v2/`) shown above.

> **Best practice:** Cache both `GroupId` values at startup. Refresh only if a subsequent call returns a 404 on the group.

---

### 7.3 Add Static Group Members by IDs (Containment — Enforce Policy)

Adds the endpoint to the risk group. The EPM agent picks up the policy change on its next sync. Full reference: [Add static group members by IDs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/add-static-group-members-by-id.htm).

```bash
curl -X POST \
  "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids" \
  -H "Authorization: basic <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <Base64url-encoded telemetry>" \
  -d '{"membersIds": ["<endpointId>"]}'
```

**Request body:**

| Field | Type | Required | Description |
|:------|:-----|:--------:|:------------|
| `membersIds` | UUID[] | Yes | One or more endpoint `id` values to add. Maximum 5,000 per call. |

The response returns a JSON array of the endpoint IDs that were successfully added. Log this alongside the alert ID.

> **Best practice:** Add only the endpoint from the current alert. Do not batch-add across unrelated incidents.

---

### 7.4 Delete Static Group Members by IDs (Restoration — Lift Policy)

Removes the endpoint from the risk group, restoring its baseline policy. Full reference: [Delete static group members by IDs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/delete-static-group-members-by-id.htm).

> **Warning:** This immediately removes the restrictive policy from the endpoint. Only call this after the investigation is confirmed complete.

```bash
curl -X POST \
  "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids/remove" \
  -H "Authorization: basic <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "x-cybr-telemetry: <Base64url-encoded telemetry>" \
  -d '{"membersIds": ["<endpointId>"]}'
```

**Request body:**

| Field | Type | Required | Description |
|:------|:-----|:--------:|:------------|
| `membersIds` | UUID[] | Yes | One or more endpoint `id` values to remove. Maximum 5,000 per call. |

The response returns a JSON array of the endpoint IDs that were successfully removed.

---

## 8. Response Tiers

Select the risk group based on the severity of the triggering alert:

| Group | Severity | What EPM Enforces |
|:------|:---------|:------------------|
| `High_Risk_Endpoint` | High — confirmed or likely active threat | Blocks all unsigned executables, scripts, MSU files, and risky downloads. Blocks all privilege elevation attempts. |
| `Medium_Risk_Endpoint` | Medium — suspicious activity, investigation required | Blocks elevation of sensitive tools from risky sources. Requires MFA for any remaining elevation attempts. |

The policy packages (`SOC_Response_Application_Policies.epmp` and `SOC_Response_User_Policies.epmp`) must be imported in the EPM tenant before these groups enforce any restrictions. Empty groups do not enforce policies.

---

## 9. Integration Patterns

| Pattern | When to use |
|:--------|:------------|
| **Alert-triggered containment** | SOAR playbook fires on XDR alert; automatically adds endpoint to risk group; analyst manually closes the incident and triggers restoration. |
| **Fully automated round-trip** | SOAR playbook adds endpoint on alert, runs automated investigation steps, then automatically removes endpoint if investigation finds no threat (use with caution — set a minimum dwell time). |
| **Severity-routed** | Playbook maps XDR alert severity (High/Medium/Low) to EPM group: High → `High_Risk_Endpoint`, Medium → `Medium_Risk_Endpoint`, Low → no action or notify only. |

Log the `ComputerId`, `GroupId`, alert ID, and timestamp at each step. This creates a complete audit trail linkable back to the XDR incident.

---

## 10. Error Handling

| HTTP Status | Meaning | Action |
|:------------|:--------|:-------|
| `200` | Success | Log `ComputerId` and `GroupId` used; confirm policy sync with EPM console if needed |
| `400` | Validation error | Parse error body — likely malformed `ComputerId` GUID or missing required field |
| `401` | Token expired or invalid | Re-authenticate using `client_credentials` flow and retry once |
| `403` | Insufficient permissions | Verify the service account has EPM endpoint management permissions |
| `404` | Endpoint or group not found | Endpoint: agent not registered in EPM or below version 26.4. Group: verify static group exists in EPM tenant. |
| `409` | Conflict — endpoint already a member | Endpoint is already in the group; idempotent — log and continue |
| `429` | Rate limited | Exponential backoff — do not retry in a tight loop. Limits: endpoint group APIs 10 calls per 2 minutes; add/remove members 5 per second and 500 per 5 minutes; Get endpoints 1,000 per 5 minutes and 5 per second. Put several endpoints in one `membersIds` call during an incident rather than one call per host. See [API limitations](https://docs.cyberark.com/epm/latest/en/content/webservices/webservicesintro.htm) |
| `500` | Server error | Log full response; retry after backoff; alert SOC if persistent |

---

## 11. Pre-Development Checklist

**EPM Tenant Setup**
- [ ] Endpoint management service APIs enabled in the EPM tenant
- [ ] EPM Windows agents on target endpoints are version 26.4 or later
- [ ] Both policy packages imported: `SOC_Response_Application_Policies.epmp` and `SOC_Response_User_Policies.epmp`
- [ ] Static groups `High_Risk_Endpoint` and `Medium_Risk_Endpoint` created and confirmed in EPM tenant
- [ ] All four SOC response policies set to Active and assigned to the correct endpoint groups (see setup table in Idira Docs)
- [ ] MFA configured in EPM tenant (required for medium-risk policy)
- [ ] Audit settings enabled for all four SOC response policies

**Authentication Setup (Section 4)**
- [ ] Service user created in Identity Administration with *Is OAuth confidential client*, *Is Service User*, *Password never expires* enabled
- [ ] Service user assigned to an EPM role with *Computers → View Only* and *Computers → Move Computer to Group* permissions
- [ ] Custom EPM API web app created in Identity Administration with status **Deployed**
- [ ] Service user added to the web app Permissions tab
- [ ] Identity sub-domain and app alias confirmed — token endpoint URL tested and returns a JWT
- [ ] Token format confirmed as `Authorization: basic <token>` — not `Bearer`
- [ ] Service user credentials stored in a secrets manager — not in playbook code or environment variables

**Integration Logic**
- [ ] `SetId` retrieved via Get sets list API and cached at startup
- [ ] `GroupId` for both `High_Risk_Endpoint` and `Medium_Risk_Endpoint` retrieved and cached at startup
- [ ] Alert payload confirmed to include hostname or IP address of the affected endpoint
- [ ] Severity-to-group mapping logic defined and documented
- [ ] Restoration path (remove call) tested end-to-end — confirm policy is lifted on group member removal
- [ ] Idempotency handled — duplicate add (endpoint already in group) does not cause error
- [ ] Telemetry header values agreed with your Idira Technical Alliances contact before certification submission

---

## 12. Resources

**Setup**
- [Extend SOC response options with EPM — Idira Docs](https://docs.cyberark.com/epm/latest/en/content/intro/extend-soc-response-options.htm) — prerequisites, policy package setup, static group creation, per-platform integration guides

**Authentication**
- [Set up API authentication for EPM REST APIs using Identity](https://docs.cyberark.com/epm/latest/en/content/webservices/authenticate-with-identity-administration.htm) — full 8-step setup: service user, OAuth web app, token request, verification
- [Idira Identity API authentication](https://docs.cyberark.com/setup/latest/en/content/ispss-deployment/ispss/ispss-api-authentication.htm) — broader ISPSS authentication reference

**API Reference**
- [Automate tasks with EPM web services](https://docs.cyberark.com/epm/latest/en/content/webservices/webservicesintro.htm) — overview and entry point
- [API commands](https://docs.cyberark.com/epm/latest/en/content/webservices/api%20commands.htm) — full API index
- [Get sets list](https://docs.cyberark.com/epm/latest/en/content/webservices/getsetslist.htm) — retrieve SetId
- [Endpoint management APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-apis/endpointmgmntapis.htm) — Get endpoints and related
- [Get endpoints](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-apis/get-endpoints.htm) — resolve endpoint id from hostname/IP
- [Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) — group management index
- [Search endpoint groups by filter (V2)](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/search-groups-by-filter-v2.htm) — resolve GroupId
- [Add static group members by IDs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/add-static-group-members-by-id.htm) — containment call
- [Delete static group members by IDs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/delete-static-group-members-by-id.htm) — restoration call
- [EPM query language](https://docs.cyberark.com/epm/latest/en/content/webservices/epmquerylanguage.htm) — filter syntax reference

**Sandbox & Contact**
- [C3 Integrations Platform](https://c3.cyberark.cloud)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.6 | 2026-10-08 | **[Added]** The rate limits that shape a containment design: endpoint group APIs 10 calls per 2 minutes (the reason to cache group IDs), add/remove members 5 per second and 500 per 5 minutes, Get endpoints 1,000 per 5 minutes and 5 per second; and batching endpoints into one `membersIds` call during an incident | Idira Technical Alliances |
| 1.5 | 2026-10-05 | **[Removed]** Two author-to-author editorial comments that were addressed to Idira teams rather than to a partner. They were invisible on the rendered page and fully visible to a partner's AI agent, which reads the raw markdown — so the audience this corpus is built for was reading notes written for us. Both restated a caveat the visible guidance already carries, and nothing a partner acts on changed: `SetId` is still resolved at runtime behind one replaceable function, and an ambiguous endpoint match must still fail the playbook step rather than contain an arbitrary host. The two open product questions they tracked are now tracked where they have an owner and a review trigger. A publish-guard check now fails the build on this class of comment | Idira Technical Alliances |
| 1.4 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. Also added this change log — the file previously carried none, so no revision before this one is recorded. — Idira Technical Alliances |
