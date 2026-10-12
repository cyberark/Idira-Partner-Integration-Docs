# Idira Audit Service Development Guide

**Workflow:** Audit Service  
**Dev Kit:** SIEM Integration  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Audit_Self_Service_Guide.pdf  
**Version:** 1.3  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Audit Service — the Identity Security Platform's audit event stream.
WORKFLOW: Audit Service
USE CASE: SIEM Integration — a partner SIEM, analytics or forensics platform POLLS Idira audit events
  and ingests them. Events flow OUT of Idira only.
INTEGRATION PATTERN: REST poll. Two-call stream: POST createQuery, then POST results.
AUTH METHOD: OAuth 2.0 against the Idira Identity tenant, plus a SEPARATE SIEM API Key. Two distinct
  credentials — see the warning below.
AUTH HEADER FORMAT: BOTH headers on every stream call — `Authorization: Bearer <access_token>` AND
  `x-api-key: <SIEM API key>` (Section 4)
BASE URL: https://<subdomain>.audit.cyberark.cloud/api/audits/stream/
TOKEN ENDPOINT: POST https://<identity-tenant-id>.id.cyberark.cloud/oauth2/token/<your-app-id>  (client_credentials)
TELEMETRY: it=SIEM — see ../../telemetry-reference.md. NOT documented in this guide; see KNOWN GAPS.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

DIRECTION IS THE FIRST THING TO GET RIGHT, AND CHECK 2.2 GRADES IT EXPLICITLY. This kit CONSUMES
Idira audit events. It does not act on them inside Idira. If the partner platform also triggers
response actions back into Idira — disable a user, revoke a session — that is a different kit with
its own checklist: ../../identity-response/response-actions/. A single integration doing both needs
both checklists, not a merged one.

TWO CREDENTIALS, NOT ONE. An agent reliably collapses these into a single secret and they are
separate, obtained from separate places, and graded separately:
1. OAuth2 Client ID + Client Secret + token URL — from an OAuth2 Server web app in Identity
   Administration (Manage > Inventory > Targets > Applications), Client Creds auth method, token
   type `jwtRS256`, scope `isp.audit.events:read`, and an Advanced-tab script that sets
   `tenant_id` and `aud=cyberark.isp.audit` (Section 3, Step 2.2). Without the script the token is
   not accepted by Audit.
2. A SIEM API Key — from the Setup space: Integrations > Export to SIEM > Create SIEM integration.
   IT IS SHOWN ONCE and cannot be re-displayed. A tenant can hold at most TWO third-party SIEM
   integrations, so yours uses one of the customer's two slots.
Check 3.7 requires the SIEM API Key in a secrets manager — not an environment variable, not a config
file in source control. Check 3.8 requires that none of the three ever reach log or debug output.

THE SERVICE USER'S RIGHTS DECIDE WHETHER ANY DATA COMES BACK (Section 3, Step 2.1):
- It must be a dedicated API user, never an interactive user's credentials (check 3.2).
- "Is OAuth confidential client" must be checked (check 3.3).
- It MUST hold the **Read Only System Administration** role right (check 3.4). Without it the
  integration authenticates, its connection test passes, and every query returns ZERO events with no
  error. Report Management looks like the right choice and is not — it grants no audit data.
- Nothing broader than that.

LIMITS (Section 4): the stream APIs can be called once a minute; results page at 500 events; the
API returns events from the previous 7 days only — an outage longer than 7 days loses events that
cannot be recovered.

THE OPERATIONAL CONTRACT LIVES IN THE CHECKLIST. Section 4 shows the calls and bodies; every
behavioural requirement lives in certification-checklist.md §4 and §5:
pagination to completion (4.6), `401`/`403`/`429` handling with EXPONENTIAL backoff and no tight retry
loop (4.7, 4.8), resume from the last successful position so a transient failure loses no events
(4.9), deduplication on a stable event identifier across polling cycles (5.1), timestamps preserved as
Idira emitted them in UTC and never re-stamped to ingestion time (5.2), and an unmapped field logged
rather than silently dropped (5.4). A generated integration that polls and inserts will fail most of
§4 and §5 while looking complete against this guide.

EVENT SCHEMA (Section 4): each event carries `uuid` (use it to deduplicate — check 5.1), `timestamp`,
`applicationCode`, `serviceName`, `auditCode`, `auditType`, `actionType`, `action`, `username`,
`userId`, `source`, `target`, `sessionId`, `customEventData[]` and more. Per-service audit codes are
in the Audit docs. The docs describe `timestamp` as Unix seconds while their example value is in
milliseconds — detect the unit rather than assuming it, and preserve it as emitted (check 5.2).

FUNCTIONAL VALIDATION IS THREE CONCRETE ACTIONS (Section 5, graded as checks 8.1–8.3): a failed
login, a Show/Copy on a test account (produces the high-priority "Fetch credential" event), and a
secure-session launch. Check 8.5 adds a fourth an agent will not infer — stop the integration,
generate events, restart, and prove no gap and no duplicates.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build, and read
  §4/§5 for the operational contract this guide does not state
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors
- ../../identity-response/response-actions/ — the opposite direction, if the platform also acts

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Integration Benefits

The integration of **Palo Alto Networks Idira™** with partner solutions provides a unified security posture by streaming critical identity and privileged access events into your security ecosystem. This allows for real-time monitoring of identity-based threats and centralized forensic analysis through the **Idira™ Identity Security Platform, by Palo Alto Networks**.

---

## 2. Before You Begin

Before starting the configuration, ensure the following requirements are met:

- An active Idira tenant
- An administrator whose role has the **Show Export to SIEM in Administration space** right (assigned by default to the Administration Role and global auditor) — needed to create the SIEM integration in Step 2.3
- A tool for API testing, such as Postman, Bruno, or cURL

---

## 3. Idira Product Configuration

### Step 1: Initial Tenant Setup and User Management

1. **First-Time Login:** Access your Idira portal using the link provided in your "Welcome to Idira" email.
2. **MFA Configuration:** Set your initial administrator password and follow the on-screen prompts to configure multi-factor authentication (MFA).

---

### Step 2: Idira Audit Service API Prerequisites

To poll the Idira Audit Service you need a dedicated service user, an OAuth2 web app, and a SIEM API key. Full procedure: [Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm).

#### 2.1 Create and Configure the OAuth2 Server Web App

1. In Identity Administration, go to **Manage › Inventory › Targets › Applications** and click **Add Web Apps**.
2. On the **Custom** tab, add the **OAuth2 Server** web app.
3. **Settings** tab — enter an **Application ID** (this is `<your-app-id>` in the token URL).
4. **Tokens** tab — set **Token Type** to `jwtRS256` and make sure the **Client Creds** auth method is selected.
5. **Scope** tab — add a scope named `isp.audit.events:read`.
6. **Advanced** tab — paste this script and save:

   ```
   setClaim('tenant_id', TenantData.Get("CybrTenantID"));
   setClaim('aud', 'cyberark.isp.audit');
   ```

#### 2.2 Create the Dedicated Service User

1. Go to **Inventory › Identities › Users › Add User**. In **Status**, select **is OAuth confidential client**, then create the user (for example `api-user-siem`).
2. In **Users › Sets › All Service Users**, open the user, select **Application Settings**, and add the OAuth2 Server web app.
3. Grant the user the **Read Only System Administration** role right.

> **Without Read Only System Administration, every query returns zero events — and nothing reports an error.** The integration authenticates and the connection test passes. The **Report Management** right does not grant access to audit event data either. See [Export audit activities to SIEM applications](https://docs.cyberark.com/setup/latest/en/content/setup-space/ecosystem-integration/integrate-siem-main.htm).

4. Back on the OAuth2 Server web app, open **Permissions**, add the service user, and select **Grant**, **View**, **Run** and **Automatically Deploy**.

#### 2.3 Generate the SIEM API Key

1. Go to the **Setup** space › **Integrations › Export to SIEM**.
2. Click **Create › Create SIEM integration**, enter a name and optional description, and click **Apply**.
3. **Copy the API key immediately — it is shown once.** Also copy the **API base URL** shown for the integration.

A tenant can hold **at most two** third-party SIEM integrations, and an integration's name and description cannot be edited afterwards. Tell your customer that your integration uses one of their two slots.

---

## 4. Technical Details: Managing Audit Data

> **Note:** These endpoints currently retain the `cyberark.cloud` domain.

**Limits:** the stream APIs can be called **once a minute**; `results` returns pages of **500** events; the SIEM integration API returns events from the **previous 7 days** only.

### Step 1 — Get an access token

```bash
curl -u "<client-id>:<client-secret>" \
  -X POST \
  -d "grant_type=client_credentials&scope=isp.audit.events:read" \
  https://<identity-tenant-id>.id.cyberark.cloud/oauth2/token/<your-app-id>
```

The response carries `access_token` and `token_type: Bearer`. Reuse it until it expires (check 3.6).

### Step 2 — Create the query (call once)

```bash
curl -X POST "https://<audit-api-base-url>/api/audits/stream/createQuery" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -H "x-api-key: <siem-api-key>" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{
    "query": {
      "pageSize": 500,
      "selectedFields": ["uuid", "timestamp", "application_code", "audit_code", "audit_type",
                         "action_type", "action", "username", "user_id", "source", "target",
                         "session_id", "service_name", "message", "custom_data"],
      "filterModel": {
        "date": { "dateFrom": "2026-10-01 00:00:00", "dateTo": "2026-10-02 00:00:00" },
        "applicationCode": [{ "op": "include", "params": ["DPA"] }]
      },
      "sortModel": [{ "field_name": "timestamp", "direction": "asc" }]
    }
  }'
```

`<audit-api-base-url>` is the API base URL shown on your SIEM integration in Export to SIEM (it has the form `<subdomain>.audit.cyberark.cloud`). Dates use `YYYY-MM-DD HH:MM:SS`. The response is `{"cursorRef": "<string>"}`.

**Server-side filters** (check 4.4): `filterModel.applicationCode` (service), `filterModel.auditType` (status), `filterModel.ActionType` (for example `Login`, `Retrieve`, `Rotate`), `userName`, `action`. See [SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) for the filter types and the application-code list.

### Step 3 — Fetch results, page by page

```bash
curl -X POST "https://<audit-api-base-url>/api/audits/stream/results" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -H "x-api-key: <siem-api-key>" \
  -H "x-cybr-telemetry: <telemetry>" \
  -d '{"cursorRef": "<cursorRef from the previous call>"}'
```

The response is `{"data": [ ...events... ], "paging": {"cursor": {"cursorRef": "<next>"}}}`. Pass each returned `cursorRef` to the next `results` call; pages are fetched one at a time (check 4.6). Persist the last cursor and the last event processed so a restart resumes rather than skips (check 4.9).

### Event fields

Each event includes, among others: `uuid` (stable identifier — deduplicate on it, check 5.1), `timestamp`, `applicationCode`, `serviceName`, `auditCode`, `auditType`, `actionType`, `action`, `message`, `username`, `userId`, `source`, `target`, `targetAccount`, `safe`, `sessionId` and `customEventData[]` (title/value pairs). Per-service audit codes: [Audit events and codes](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/product-audits/audit_events_and_codes.htm).

> **Timestamp unit.** The docs describe `timestamp` as a Unix timestamp in seconds, while their example value (`1745573887741`) is in milliseconds. Detect the unit from the value's magnitude and store it as emitted, in UTC (check 5.2).

### Telemetry

Send `x-cybr-telemetry` with `it=SIEM` on every request — see the [Telemetry Header Reference](../../telemetry-reference.md).

> **Ready-made SIEM plugins.** Idira publishes Microsoft Sentinel and IBM QRadar plugins on the Marketplace. If your platform is one of those, start there rather than building a new integration.

---

## 5. Troubleshooting and Testing

To validate the integration, perform the following actions in the Idira tenant to generate audit events:

- **Failed Login:** Attempt to log in with an incorrect password to trigger a security monitoring event.
- **Retrieve Credential:** In Idira Privileged Access Manager SaaS, click "Show" or "Copy" on a test account to generate a high-priority "Fetch credential" event.
- **Session Initiation:** Launch a secure session to verify session initiation events.

---

## 6. Support Information

For issues regarding the Idira Audit Service or platform configuration, please contact Technical Support. For Palo Alto Networks infrastructure issues, visit the Palo Alto Networks Customer Support portal.

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-08 | **[Fixed]** The service user must hold the **Read Only System Administration** right — without it every query returns zero events with no error. The SIEM API key is created in the Setup space under Integrations › Export to SIEM. The token request is a `POST` with the `client_credentials` grant. **[Added]** OAuth2 web app configuration (token type `jwtRS256`, the Advanced-tab claim script, app permissions); both request headers (`Authorization: Bearer` and `x-api-key`); the `createQuery` and `results` request and response bodies with paging by `cursorRef`; server-side filters; the event fields and audit-code reference; limits (once a minute, 500 per page, 7-day retention, two SIEM integrations per tenant); telemetry. An integration whose service user has only Auditor roles must add Read Only System Administration | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with direction — this kit **consumes** Idira audit events and never acts on them inside Idira, which check 2.2 grades explicitly against the Identity Response kit — and with the two-credential trap an agent reliably collapses into one: the OAuth2 Client ID/Secret from the Identity Administration portal and the separate SIEM API Key from SIEM Management, which is shown once. It records the graded shape of the service user (dedicated API user, "Is OAuth Confidential client" checked, exactly the Global Auditor plus per-service Auditor roles), that the `cyberark.cloud` domain on both hosts is deliberate and must not be "corrected" to an `idira` domain, and that every behavioural requirement — pagination, `429` exponential backoff, resume-from-position, deduplication on a stable event id, UTC timestamps, unmapped fields logged rather than dropped — lives in the checklist's §4/§5 rather than in this guide. Three graded requirements are recorded as gaps rather than invented: the `client_credentials` grant type, the `Authorization: Bearer <token>` header format, and telemetry (`x-cybr-telemetry`, Base64url, `it=SIEM`), none of which this guide states. There is also no published event schema despite check 5.3 grading a field mapping. **[Fixed]** The `**Dev Kit:**` header field had literal escaped asterisks (`\*\*Dev Kit:\*\*`) surviving the PDF conversion, so it rendered as visible asterisks rather than bold. **[Added]** the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
