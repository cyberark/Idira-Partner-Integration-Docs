# Idira EPM — Ticketing & JIT Admin Elevation Development Guide

**Workflow:** EPM  
**Dev Kit:** Ticketing — JIT Admin Elevation  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira Docs — JIT Policy Definition API + Idira Marketplace  
**Version:** 1.2  
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Endpoint Privilege Manager (EPM) — the Just-in-Time elevation policy API.
WORKFLOW: EPM
USE CASE: Ticketing — JIT Admin Elevation. A ticketing/ITSM platform gates temporary local-admin
  elevation behind its own approval workflow, then creates a time-bound EPM policy on approval.
INTEGRATION PATTERN: REST. The PARTNER CALLS EPM — create, read, update and delete a JIT policy.
AUTH METHOD: OAuth 2.0 `client_credentials`, sent as HTTP Basic over TLS (Section 4.1)
AUTH HEADER FORMAT: Authorization: Bearer <ACCESS_TOKEN>
BASE URL: https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Policies/JIT
TOKEN ENDPOINT: POST https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs.
  it=JIT — see ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THE DIRECTION IS PARTNER -> EPM, WHICH IS THE OPPOSITE OF THE EPM AUDIT KIT. Here the partner WRITES
policy into EPM. ../audit-events/ READS events out of it. A closed-loop ticketing product often wants
both, and they are separate integrations with separate checklists and separate `it` values (`JIT` here,
`EPMAudit` there).

THE HOST IS THE DISPATCHER, AND THE SIBLING GUIDE CARRIES THE WARNING THIS ONE OMITS.
`<epm-tenant>` in Section 4.2 is the same regional dispatcher value ../audit-events/ documents
(`na228`, `eu14`, …), found in the EPM console under tenant settings. Do NOT use
`login.epm.cyberark.com` or the "EPM Login Server" field — that returns `invalid client` or
`token request failed`, which reads as a credential fault and is not one. See
../audit-events/development-guide.md Section 8 for the full statement of this.

`Audit: true` ALWAYS, AND NEVER DISABLED IN PRODUCTION (Section 10). CROSS-KIT TRAP — THIS KIT GRADES
THE INVERSE OF THE CREDENTIAL PROVIDER KITS: ../../secrets-management/credential-provider/ and
../../secrets-management/central-credential-provider/ both require the CP/CCP audit trail and logging
to be DISABLED for production use, enabled only for troubleshooting. Both positions are correct in
their own kit. Do not carry either setting across in either direction.

THE MAGIC NUMBERS ARE NOT GUESSABLE AND ARE ALL GRADED (Section 7):
- `PolicyType` MUST be `40`. This is the JIT policy type; there is no other valid value here.
- `Action` defaults to `20`.
- `ExecutorType`: `0` = computer group, `1` = single computer.
- `AccountType` on an entry in `Accounts`: `0` = group, `1` = single AD account, `2` = manual,
  `4` = Azure user, `5` = Azure group.
- `AccountType` on an entry in `TargetLocalGroups`: `0`, paired with `DisplayName: "Administrators"`.
- `Duration` is in HOURS, range `1`–`120`. Not minutes, not seconds.

TYPE DISCREPANCY BETWEEN SECTION 6.1's EXAMPLE AND SECTION 7's TABLE — FLAG RATHER THAN GUESS. The
table types `Duration` as Number and `KillRunningApps` as Boolean, while the example body sends
`"Duration": "2"` and `"KillRunningApps": "true"` as QUOTED STRINGS — and sends `"Audit": true`
unquoted in the same object. The three are inconsistent with each other. Send what the example sends
if you must choose, since that is the form known to have been exercised, and confirm with the Idira Technical Alliances contact
before shipping. Do not silently normalise all three to one form and present it as documented.

AN `Executors` ENTRY TAKES AN EPM AGENT ID GUID, NOT A HOSTNAME (Section 7, Section 8). Resolve it
first via `GET /EPM/API/<Version>/Sets`. That call is a hard dependency of policy creation — a
generated integration that accepts a computer name from the ticket and posts it directly will fail.
Set `IsAppliedToAllComputers: false` when targeting specific computers; `IncludeADComputerGroups` is
the alternative to `Executors`, not a supplement to it.

AN ACCOUNT NEEDS `SamName` OR `Sid`, NOT NECESSARILY BOTH (Section 7). `DisplayName` is required
either way and should match `SamName`. `SamName` is `domain\user` format — note the escaped backslash
in JSON (`"domain\\username"`).

DELETE IS NOT OPTIONAL CLEANUP — IT IS THREE GRADED PATHS (Section 6.4, Section 9, checks 8.3/8.4/8.5):
rejection, early ticket closure, and incident-driven revocation regardless of remaining duration. A
successful DELETE returns `HTTP 200 OK`, removes the user from the target local group immediately, and
terminates running admin processes if `KillRunningApps` was `true`. Expiry needs no callback — EPM
removes the elevation itself when the duration lapses.

APPROVAL INTEGRITY IS A WHOLE GRADED SECTION AND THIS GUIDE ONLY GESTURES AT IT. Read
certification-checklist.md §6 before designing the ticket flow. Its non-obvious requirements: a policy
is created ONLY on a recorded approval by an authorized approver — never on ticket creation and never
on the requester's own action (6.1); the approver identity is retained on the ticket (6.2); and the
elevation target CANNOT be altered between approval and policy creation, so the integration must use
the approved values rather than re-reading a mutable field afterwards (6.4). That last one is a real
privilege-escalation hole in an otherwise working integration, and nothing in this guide implies it.

POLICY `Name` IS A TRACEABILITY CONTROL, NOT A LABEL (Section 6.1, check 6.5). It must carry the ticket
reference, the requesting user and a timestamp so any active policy resolves back to its approval.
Check 8.7 closes the loop by requiring the elevation to appear in EPM audit data attributable to the
ticket.

`<Version>` is a literal path segment and this guide does not enumerate the valid values. Section 11's
two reference links resolve to real pages rather than a portal front page — use them for the full
parameter schema and error tables.

SIBLING KITS — three EPM kits:
- ../audit-events/: reads EPM audit events out. it=EPMAudit. Carries the dispatcher-URL warning.
- ../soc-response/: a SOC platform acting on EPM.
- ../decision-guide.md — which EPM dev kit to build against.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build, and read
  §6 (Approval Integrity) and §8 (the five lifecycle paths) before designing the flow
- ../decision-guide.md — which EPM dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **Not sure this is the right guide?** See the [EPM Decision Guide](../decision-guide.md) first.
> Use this guide if: your platform is a ticketing or ITSM system and you want to gate Just-in-Time local admin elevation on an approval workflow.

---

## 1. Overview

This guide describes how to integrate a partner ticketing system (e.g. ServiceNow, Jira, BMC Remedy) with **Idira® Endpoint Privilege Manager (EPM)** to automate Just-in-Time (JIT) admin elevation.

In a JIT elevation workflow, an end user requests temporary administrator access on a managed endpoint. Instead of granting standing admin rights, EPM gates the elevation behind an approval process. The integration with a ticketing system creates a closed loop:

1. User requests elevation on the endpoint.
2. A ticket is created in the partner ticketing system.
3. An approver approves or rejects the ticket.
4. On approval, the partner system calls the EPM API to create or activate a time-bound JIT policy.
5. The user is temporarily added to the local Administrators group for the configured duration.
6. When the policy expires, EPM removes the elevation and optionally terminates running administrative processes.

This integration pattern enables full auditability, approval governance, and least-privilege enforcement across managed endpoints.

---

## 2. Use Case

| Item | Detail |
|:-----|:-------|
| **Use case** | JIT admin elevation via ticketing approval |
| **EPM capability** | Just-in-Time Access and Elevation Policies |
| **Idira solution** | Endpoint Privilege Management |
| **Idira product** | Idira Endpoint Privilege Manager |
| **Integration direction** | Ticketing system → EPM API (policy create/delete) |
| **Partner owns** | Ticket lifecycle, approval UI, webhook/trigger logic |
| **EPM owns** | Policy enforcement on the endpoint agent |

---

## 3. Prerequisites

Before developing the integration, ensure the following:

- Administrative access to a provisioned **Idira EPM** tenant (production or partner sandbox)
- A dedicated service (non-interactive) account for programmatic API authorization
- A configured OAuth 2.0 Web Application entity in the Idira Identity directory
- A valid Client ID and Client Secret pair for the service account
- Access to the EPM management console to retrieve Set IDs and Computer IDs (Agent IDs)
- Familiarity with your ticketing system's webhook or automation capabilities

---

## 4. Authentication

EPM uses the same OAuth 2.0 `client_credentials` flow as all Idira platform APIs.

### 4.1 Obtain Bearer Token

```bash
curl -u "<client_id>:<client_secret>" \
  -X POST \
  -d "grant_type=client_credentials" \
  https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
```

A successful response returns:

```json
{
  "access_token": "<token>",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Use the `access_token` as the `Authorization: Bearer <token>` header on all subsequent EPM API calls. Handle token expiry by re-requesting before it lapses.

### 4.2 Base URL

```
https://<epm-tenant>.epm.cyberark.com/
```

---

## 5. Integration Workflow

```
User requests elevation
        │
        ▼
Ticketing system creates ticket
        │
        ▼
Approver reviews and approves
        │
        ▼
Ticketing system calls EPM API → POST /JIT policy
        │
        ▼
EPM adds user to Administrators group on target computer(s)
        │
        ▼
Duration expires (1–120 hours)
        │
        ▼
EPM removes elevation, optionally kills admin processes
        │
        ▼
Ticketing system receives callback / marks ticket resolved
```

---

## 6. JIT Policy API

### 6.1 Create a JIT Policy (on approval)

Called by the ticketing system when an approver approves the elevation request.

```
POST https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Policies/JIT
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

**Request body:**

```json
{
  "Name": "JIT - <TicketID> - <Username> - <Timestamp>",
  "IsActive": true,
  "IsAppliedToAllComputers": false,
  "PolicyType": 40,
  "Action": 20,
  "Duration": "2",
  "KillRunningApps": "true",
  "Audit": true,
  "Executors": [
    {
      "Id": "<agent-id-guid>",
      "ExecutorType": 1
    }
  ],
  "Accounts": [
    {
      "SamName": "domain\\username",
      "DisplayName": "domain\\username",
      "AccountType": 1
    }
  ],
  "IncludeADComputerGroups": [],
  "TargetLocalGroups": [
    {
      "AccountType": 0,
      "DisplayName": "Administrators"
    }
  ]
}
```

**Recommended naming convention:** Include the ticket ID, requesting user, and timestamp in the `Name` field so policies are traceable back to tickets.

---

### 6.2 Get JIT Policy Details

Called to check the current state of an active elevation policy.

```
GET https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Policies/JIT/<PolicyId>
Authorization: Bearer <ACCESS_TOKEN>
```

---

### 6.3 Update a JIT Policy

Called if the approver extends the duration or modifies scope.

```
PUT https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Policies/JIT/<PolicyId>
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Use the same body structure as the create request, with updated fields.

---

### 6.4 Delete / Revoke a JIT Policy (on rejection or early termination)

Called by the ticketing system when an approver rejects the request, the ticket is closed early, or a security incident triggers immediate revocation.

```
DELETE https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Policies/JIT/<PolicyId>
Authorization: Bearer <ACCESS_TOKEN>
```

A successful response returns `HTTP 200 OK`. The user is immediately removed from the target local group and, if `KillRunningApps` was set to `true`, any running administrative processes are terminated.

---

## 7. JIT Policy Parameters

### Top-Level Policy Fields

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `Name` | String | Yes | Policy name — recommend including ticket ID and username for traceability |
| `IsActive` | Boolean | Yes | Set to `true` to activate the policy immediately |
| `IsAppliedToAllComputers` | Boolean | Yes | Set to `false` when targeting specific computers via `Executors` |
| `PolicyType` | Number | Yes | Must be `40` (JIT type) |
| `Action` | Number | No | Defaults to `20` |
| `Duration` | Number | No | Elevation duration in hours — range: `1`–`120` |
| `KillRunningApps` | Boolean | No | If `true`, admin processes are terminated when policy expires (default: `true`) |
| `Audit` | Boolean | No | If `true`, audit information is collected (default: `true`) |
| `Executors` | Array | Conditional | Target computers or computer groups. Required if `IsAppliedToAllComputers` is `false` |
| `IncludeADComputerGroups` | Array | Conditional | AD groups containing the target computers. Alternative to `Executors` |
| `TargetLocalGroups` | Array | Yes | Local security groups to add the user to — minimum one entry |
| `Accounts` | Array | Yes | Users or groups to elevate — minimum one entry |

### Account Fields

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `SamName` | String | If `Sid` missing | Username in `domain\user` format |
| `Sid` | String | If `SamName` missing | Security Identifier for the account |
| `AccountType` | Number | No | `0` = group, `1` = single AD account, `2` = manual, `4` = Azure user, `5` = Azure group |
| `DisplayName` | String | Yes | Display name shown in EPM agent — recommend matching `SamName` |

### Executor Fields

| Parameter | Type | Required | Description |
|:----------|:-----|:---------|:------------|
| `Id` | GUID | Yes | Internal EPM Agent ID (GUID) of the target computer or group |
| `Name` | String | No | Display name — returned on GET, not stored on create |
| `ExecutorType` | Number | Yes | `0` = computer group, `1` = single computer |

---

## 8. Retrieving Required IDs

Before creating a JIT policy, the integration must resolve the Agent ID and Set ID for the target computer.

### Get Computer Sets (for resolving Agent IDs)

```bash
curl -X GET https://<epm-tenant>.epm.cyberark.com/EPM/API/<Version>/Sets \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

Use the returned Set and computer IDs to populate the `Executors` array in the policy create request.

---

## 9. Recommended Integration Design

### Minimal viable integration (ticketing system → EPM)

1. **Trigger:** End user submits elevation request in the ticketing system, providing their username, target computer name, requested duration, and business justification.
2. **Ticket created:** Ticketing system creates a ticket and routes it to the approver group.
3. **Approval webhook:** On approval, the ticketing system fires a webhook to your integration layer.
4. **Resolve Agent ID:** Integration layer calls EPM `GET /Sets` to resolve the target computer's Agent ID.
5. **Create JIT policy:** Integration layer calls EPM `POST /Policies/JIT` with the resolved Agent ID, username, and approved duration. Store the returned `PolicyId` against the ticket.
6. **Notify user:** Ticketing system notifies the end user that elevation is active and states the expiry time.
7. **Policy expiry:** EPM automatically removes elevation after the duration. No callback needed.
8. **Ticket closure:** Integration layer optionally calls `DELETE /Policies/JIT/<PolicyId>` on ticket closure to ensure revocation even if the duration has not yet elapsed.

### Rejection / revocation path

- On ticket rejection: call `DELETE /Policies/JIT/<PolicyId>` immediately.
- On security incident (e.g. triggered by SIEM alert): call `DELETE /Policies/JIT/<PolicyId>` to force immediate revocation regardless of duration.

---

## 10. Certification Guidelines

> **The graded document is [`certification-checklist.md`](certification-checklist.md)** — read it during the build, not at submission. The summary below is the same criteria in short form; the checklist is what your submission is reviewed against, and it covers two things this list does not: approval integrity, and the five grant/expiry/revocation paths that must each be tested.

When preparing for Idira certification, ensure the integration demonstrates:

- [ ] OAuth 2.0 `client_credentials` flow with dedicated service account (no interactive users)
- [ ] Token expiry handled — refresh or re-request before expiry
- [ ] Policy names include ticket reference for full traceability
- [ ] `Audit: true` always set — do not disable in production
- [ ] `KillRunningApps` behaviour documented and tested
- [ ] Revocation (DELETE) implemented and tested for both rejection and early termination paths
- [ ] Sensitive credentials (Client ID, Client Secret) stored securely — not hardcoded
- [ ] Error handling for common failures: `401` (token expired), `403` (insufficient permissions), `404` (policy not found), `429` (rate limit)
- [ ] Demonstration provided — **either** a demo video (2–5 min) showing the full approval → elevation → expiry/revocation cycle, **or** a live demonstration call with the Idira Technical Alliances contact walking the same cycle
- [ ] `x-cybr-telemetry` header included on all API requests (see below)

### Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header, Base64 URL-encoded:

| Field              | Header Key | Required | Example                       |
| :----------------- | :--------- | :------- | :---------------------------- |
| IntegrationName    | `in`       | Yes      | `in=ServiceNow JIT Elevation` |
| IntegrationType    | `it`       | Yes      | `it=JIT`                      |
| IntegrationVersion | `iv`       | Yes      | `iv=1.0`                      |
| VendorName         | `vn`       | Yes      | `vn=ServiceNow`               |
| VendorVersion      | `vv`       | No       | `vv=Vancouver`                |

---

## 11. Comprehensive Technical Reference

For full parameter schemas, error code tables, and additional API operations, refer to the official Idira Docs:

- [JIT Policy Definition | Idira Docs](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm)
- [EPM Audit Events API | Idira Docs](https://docs.cyberark.com/epm/latest/en/content/webservices/auditseventsapis.htm)

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus — this was the last of the fifteen development guides. It leads with direction (the partner **writes** policy into EPM here, the inverse of the EPM Audit kit that reads events out) and carries across the dispatcher-URL warning the sibling guide states and this one omits. It records the cross-kit auditing trap in both directions — `Audit: true` always and never disabled here, against the Credential Provider kits' requirement that CP/CCP audit logging be **disabled** for production — and enumerates the magic numbers an agent cannot guess: `PolicyType` 40, `Action` 20, `ExecutorType` 0/1, the five `AccountType` values, and `Duration` in hours over a 1–120 range. Two structural points are called out that this guide does not make explicit: an `Executors` entry needs an EPM Agent ID GUID resolved via `GET /Sets` rather than a hostname from the ticket, and `DELETE` is three separately graded paths (rejection, early closure, incident revocation) rather than optional cleanup. It also points at the checklist's §6 Approval Integrity before the ticket flow is designed, naming check 6.4 specifically — the elevation target must not be alterable between approval and policy creation, which is a real privilege-escalation hole in an otherwise working integration and which nothing in this guide implies. One **discrepancy** is recorded rather than resolved: Section 6.1's example body sends `"Duration": "2"` and `"KillRunningApps": "true"` as quoted strings alongside an unquoted `"Audit": true`, while Section 7's table types the first two as Number and Boolean; the block advises following the exercised example and confirming with the Idira Technical Alliances contact rather than silently normalising. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
