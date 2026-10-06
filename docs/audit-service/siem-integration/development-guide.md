# Idira Audit Service Development Guide

**Workflow:** Audit Service  
**Dev Kit:** SIEM Integration  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Audit_Self_Service_Guide.pdf  
**Version:** 1.2  
**Last Updated:** 2026-10-02

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
AUTH HEADER FORMAT: NOT STATED IN THIS GUIDE. The checklist grades `Authorization: Bearer <token>`
  (check 4.3); this guide never shows a request header. See KNOWN GAPS.
BASE URL: https://<subdomain>.audit.cyberark.cloud/api/audits/stream/
TOKEN ENDPOINT: GET https://<identity-tenant-id>.id.cyberark.cloud/oauth2/token/<your-app-id>
TELEMETRY: it=SIEM — see ../../telemetry-reference.md. NOT documented in this guide; see KNOWN GAPS.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

DIRECTION IS THE FIRST THING TO GET RIGHT, AND CHECK 2.2 GRADES IT EXPLICITLY. This kit CONSUMES
Idira audit events. It does not act on them inside Idira. If the partner platform also triggers
response actions back into Idira — disable a user, revoke a session — that is a different kit with
its own checklist: ../../identity-response/response-actions/. A single integration doing both needs
both checklists, not a merged one.

TWO CREDENTIALS, NOT ONE. An agent reliably collapses these into a single secret and they are
separate, obtained from separate portals, and graded separately:
1. OAuth2 Client ID + Client Secret + token URL — from the Identity Administration portal, Apps &
   Widgets > Web Apps > OAuth2 Server, scope `isp.audit.events:read` (Section 3, Step 2.2).
2. A SIEM API Key — from the Idira Privileged Access Manager SaaS portal, Administration > SIEM
   Management > Create SIEM integration. IT IS SHOWN ONCE and cannot be re-displayed.
Check 3.7 requires the SIEM API Key in a secrets manager — not an environment variable, not a config
file in source control. Check 3.8 requires that none of the three ever reach log or debug output.

THE SERVICE USER'S SHAPE IS GRADED, NOT JUST ITS EXISTENCE (Section 3, Step 2.1):
- It must be a dedicated API user, never an interactive user's credentials (check 3.2).
- "Is OAuth Confidential client" must be checked (check 3.3). The guide marks this Crucial.
- Roles are exactly **(Global) Auditor** plus the relevant per-service Auditor role — for Privilege
  Cloud audits and session recordings, the Privilege Cloud Auditor role. Nothing broader (check 3.4).

THE `cyberark.cloud` DOMAIN IS CORRECT AND DELIBERATE (Section 4's own note). Both the audit host and
the Identity token host still carry it post-rebrand. Do not "correct" either to an `idira` domain —
the endpoint would not resolve.

WHAT THE GUIDE DOES NOT COVER BUT THE CHECKLIST GATES — READ THE CHECKLIST FOR THE OPERATIONAL
CONTRACT. This guide is a configuration walkthrough converted from a PDF; it states the three
endpoints and stops. Every behavioural requirement lives in certification-checklist.md §4 and §5:
pagination to completion (4.6), `401`/`403`/`429` handling with EXPONENTIAL backoff and no tight retry
loop (4.7, 4.8), resume from the last successful position so a transient failure loses no events
(4.9), deduplication on a stable event identifier across polling cycles (5.1), timestamps preserved as
Idira emitted them in UTC and never re-stamped to ingestion time (5.2), and an unmapped field logged
rather than silently dropped (5.4). A generated integration that polls and inserts will fail most of
§4 and §5 while looking complete against this guide.

KNOWN GAPS — DO NOT FILL THEM IN FROM MEMORY. Three requirements are graded with no implementation
path in this guide, and all three are open findings in the corpus check:
- The OAuth grant type. Check 3.1 grades the `client_credentials` flow; this guide shows only a GET
  against the token URL and never names a grant.
- The request header format. Check 4.3 grades `Authorization: Bearer <token>`; no request in this
  guide carries a header at all.
- Telemetry. Checks 7.1–7.7 grade the `x-cybr-telemetry` header, its Base64url encoding and `it=SIEM`;
  this guide does not mention telemetry anywhere. ../../telemetry-reference.md carries the transform
  and test vectors — cite it from there rather than presenting it as this guide's own.
There is also no published event schema here, though check 5.3 grades a documented field mapping. If
asked for a field name, an event-type list, or a request or response body, say it is not documented in
this kit and point at the checklist and the Idira Technical Alliances contact.

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
- Administrative access to Idira Docs (formerly CyberArk Docs) for technical reference
- A tool for API testing, such as Postman, Bruno, or cURL
- Idira API Keys and OAuth2 credentials as outlined in the steps below

---

## 3. Idira Product Configuration

### Step 1: Initial Tenant Setup and User Management

1. **First-Time Login:** Access your Idira portal using the link provided in your "Welcome to Idira" email.
2. **MFA Configuration:** Set your initial administrator password and follow the on-screen prompts to configure multi-factor authentication (MFA).
3. **Create Integration Roles:**
   - Navigate to Core Services > Roles in the Identity Administration portal.
   - Create a role named "Integration Developers".
   - Assign administrative rights for User Management and Role Management.
4. **Add Users:** Navigate to Core Services > Users > Add User to invite team members to the tenant.

---

### Step 2: Idira Audit Service API Prerequisites

To securely poll the Idira Audit Service, you must create a dedicated service user and generate credentials.

#### 2.1 Create a Dedicated API User

- Create a user with a name like `api-user-siem`.
- **Crucial:** Select the "Is OAuth Confidential client" checkbox.
- Assign the following roles to this user:
  - **(Global) Auditor:** Allows activity searching and SIEM setup.
  - **Idira™ Privilege Cloud, by Palo Alto Networks Auditor:** Grants access to audits and session recordings.

#### 2.2 Configuring API Access Credentials

1. **OAuth2 Server Web App:**
   - In the Identity Administration portal, go to Apps & Widgets > Web Apps and add the OAuth2 Server application.
   - Permissions: Add the `api-user-siem` created earlier.
   - Scopes: Add a scope named `isp.audit.events:read`.
   - Save: Note the Client ID, Client Secret, and OAuth Token URL.

2. **Generate SIEM API Key:**
   - Switch to the Idira Privileged Access Manager SaaS portal using the service picker.
   - Navigate to Administration > SIEM Management and click Create SIEM integration.
   - **Important:** Copy the generated API Key immediately; it is only shown once.

---

## 4. Technical Details: Managing Audit Data

To query the Idira Audit Service, leverage the following REST API endpoints.

> **Note:** These endpoints currently retain the `cyberark.cloud` domain.

**Token Retrieval:**
```
GET https://<identity-tenant-id>.id.cyberark.cloud/oauth2/token/<your-app-id>
```

**Create Query:**
```
POST https://<subdomain>.audit.cyberark.cloud/api/audits/stream/createQuery
```

**Retrieve Results:**
```
POST https://<subdomain>.audit.cyberark.cloud/api/audits/stream/results
```

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
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with direction — this kit **consumes** Idira audit events and never acts on them inside Idira, which check 2.2 grades explicitly against the Identity Response kit — and with the two-credential trap an agent reliably collapses into one: the OAuth2 Client ID/Secret from the Identity Administration portal and the separate SIEM API Key from SIEM Management, which is shown once. It records the graded shape of the service user (dedicated API user, "Is OAuth Confidential client" checked, exactly the Global Auditor plus per-service Auditor roles), that the `cyberark.cloud` domain on both hosts is deliberate and must not be "corrected" to an `idira` domain, and that every behavioural requirement — pagination, `429` exponential backoff, resume-from-position, deduplication on a stable event id, UTC timestamps, unmapped fields logged rather than dropped — lives in the checklist's §4/§5 rather than in this guide. Three graded requirements are recorded as gaps rather than invented: the `client_credentials` grant type, the `Authorization: Bearer <token>` header format, and telemetry (`x-cybr-telemetry`, Base64url, `it=SIEM`), none of which this guide states. There is also no published event schema despite check 5.3 grading a field mapping. **[Fixed]** The `**Dev Kit:**` header field had literal escaped asterisks (`\*\*Dev Kit:\*\*`) surviving the PDF conversion, so it rendered as visible asterisks rather than bold. **[Added]** the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
