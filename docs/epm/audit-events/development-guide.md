# Idira Endpoint Privilege Manager Audit Integration

**Workflow:** Audit Service  
**Dev Kit:** EPM Audit  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_EPM_Audit_Self-Service_Guide.pdf  
**Version:** 1.4  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Endpoint Privilege Manager (EPM) — the audit and privilege event API.
WORKFLOW: Audit Service
USE CASE: EPM Audit — a SIEM, observability or analytics platform POLLS EPM audit and privilege
  elevation events and ingests them. Events flow OUT of EPM only.
INTEGRATION PATTERN: REST poll. Resolve a Set, then query events within it.
AUTH METHOD: OAuth 2.0 `client_credentials`, sent as HTTP Basic over TLS (Section 6)
AUTH HEADER FORMAT: Authorization: Bearer <ACCESS_TOKEN>
BASE URL: https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/   — <EPM_Server> is the subdomain of the tenant's EPM console URL
TOKEN ENDPOINT: POST https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded. it=EPMAudit — Section 8 and ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THREE HOSTS, AND TWO OF THEM ARE ROUTINELY CONFUSED. This is the most expensive mistake in the kit
and the guide flags it itself (Section 8, "Common mistake"):
- `https://<TENANT>.id.cyberark.cloud` — Identity. TOKEN ONLY.
- `https://<EPM_Server>.epm.cyberark.com` — the EPM SERVER. Every API call. `<EPM_Server>` is the
  subdomain in the tenant's EPM management console URL: if the console is
  `https://na101.epm.cyberark.com/...`, the server name is `na101`. It is also the value to put in a
  third-party configurator's "EPM server URL" field. The EPM docs call this the EPM server name and
  distinguish it from the "dispatcher" used by the legacy EPM logon API — do not use the word
  dispatcher for it.
- `login.epm.cyberark.com` — WRONG for everything here. Using the EPM Login Server URL as the API
  base returns `invalid client` or `token request failed`, which reads as a credential fault and is
  not one.

DISTINGUISH THIS KIT FROM ../../audit-service/siem-integration/. Both carry `Workflow: Audit Service`
and both are SIEM-facing polls, and they are NOT interchangeable: that kit consumes platform-wide
Identity Security Platform audit events from `*.audit.cyberark.cloud` with `it=SIEM`; this one
consumes EPM-specific events from the EPM server with `it=EPMAudit`. A partner ingesting both
needs both integrations and both checklists.

THE AUTH CALL'S SHAPE, EXACTLY (Section 6): the service user's credentials go in HTTP Basic
(`curl -u "<service-user>@<tenant-domain>:<password>"`), and `grant_type=client_credentials` goes in
the form body. The service user must be an OAuth confidential client, a member of the EPM role that
defines the API permissions, and bound to an "Idira EPM API Client" web app (Section 3). The token is
then sent as `Authorization: Bearer <ACCESS_TOKEN>`. The response (Section 7) carries
`access_token`, `token_type` and `expires_in` — honour `expires_in` and re-request on expiry rather
than per call (check 2.4). Checks 2.1–2.3 grade the grant type, that the user is a dedicated
non-interactive service account, and that the token comes from the `.id.` host.

EVERY VALUE IN ANGLE BRACKETS IS A PLACEHOLDER. `AAX4917` in Section 4 is an example Identity
sub-domain and `na101` an example EPM server name. Never hardcode the service user's password in
code, a config file or a test fixture — check 4.2 grades that secrets are not hardcoded.

THE OPERATIONS, IN DEPENDENCY ORDER (Section 8):
  1. GET  /EPM/API/<Version>/Sets                                  -> resolve the Set ids
  2. POST /EPM/API/<Version>/Sets/<setId>/Events/Search             -> raw events
     POST /EPM/API/<Version>/Sets/<setId>/policyaudits/search       -> policy audit events
     POST /EPM/API/<Version>/Sets/<setId>/signinaudits/search       -> sign-in audit events
Every search call is a POST with `Content-Type: application/json` and an optional JSON body
`{"filter": "<EPM query language>"}`. It is NOT a GET — a GET to a search path fails. Each family
also has an aggregated form (`.../aggregations/search`). Call 2 needs a `setId` from call 1.
`<Version>` is `x.x.x.x` (for example `24.12.0.0`), optional, and defaults to the latest version;
the minimum for the event search calls is `21.12.0.0`.

PAGINATE OR LOSE EVENTS. A search returns 250 results by default and at most 1,000 (`limit`). The
response carries `nextCursor`; pass `nextCursor=start` on the first call and the returned value on
each next call until no cursor is returned. To read everything for a time window, filter on
`arrivalTime` (ISO-8601 UTC — the time EPM received the event, not when it occurred) and follow
`nextCursor`. A poll that reads only the first page silently drops the rest (check 5.4).

ADMIN AUDIT IS NOT IN THIS KIT. The EPM set/account admin-audit APIs are deprecated and EPM directs
admin-audit consumers to the Identity Security Platform SIEM integration API — that is
../../audit-service/siem-integration/. Events/Search does not return administrative changes.

`SetId` IS NOT A PERMANENT IDENTIFIER (Section 8's own note). Resolve it at startup, cache it for the
run only, re-resolve on a `404`, and put the lookup behind ONE replaceable function rather than
threading the id through the integration. EPM set management is retiring on published dates —
2026-10-31 My Computers support ends, 2026-12-31 access removed, 2027-01-01 EPM set management
disabled, 2027-03 standalone console access revoked — and release 26.9.1 shipped 2026-09-27 migrating
agentless sets to the new endpoint management service.
  OPEN AND DELIBERATELY UNANSWERED: those dates are stated for the EPM CONSOLE and the endpoint
  management service. Whether the `Sets/<SetId>/…` REST paths change, get proxied, or are replaced is
  NOT known — the guide carries a standing TODO on exactly this. Do not advise a partner to
  re-architect, and do not invent a replacement path. Route it to EPM product via the Idira Technical Alliances contact.

RATE LIMITS ARE THREE INDEPENDENT BUDGETS, NOT ONE (Section 8). Event and file APIs; policy audit
and sign-in events; and event calls filtered to `ManualRequest`/`ElevationRequest` each allow 1,000
requests per 5 minutes, 5 requests per second, and 100,000 events extracted per 24 hours. Consuming
one budget does not reduce another. Size the polling interval so a normal day stays inside every
budget you use, and handle `429` with exponential backoff — check 5.1 grades `401`, `403` and `429`
handling together.

TWO MORE GRADED BEHAVIOURS: deduplicate events across polling cycles (check 5.2 — track the last
`arrivalTime` processed and the cursor) and use API-side filtering rather than dumping the raw
stream (check 3.3, Recommended — Section 8 shows the filter syntax).

KNOWN GAPS — DO NOT FILL THEM IN FROM MEMORY:
- Event schema and error tables. Section 9 links the EPM pages for each search API; the field-level
  schema and the full filter vocabulary live there, not in this guide.

SIBLING KITS — three EPM kits, easily confused:
- ../soc-response/: the opposite direction — a SOC platform ACTS on EPM rather than reading from it.
- ../ticketing-jit/: just-in-time elevation via a ticketing system. NOTE THE CROSS-KIT AUDITING TRAP —
  that kit requires `Audit: true` on every policy, never disabled, including in production, while the
  ../../secrets-management/ Credential Provider kits require audit logging DISABLED for production.
  Both are correct in their own kit; do not carry either setting across.
- ../decision-guide.md — which EPM dev kit to build against.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — which EPM dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **Not sure this is the right guide?** See the [EPM Decision Guide](../decision-guide.md) first.
> Use this guide if: your platform is a SIEM, observability, or analytics tool and you want to ingest EPM audit and privilege events.

---

## 1. Overview

This guide provides comprehensive, step-by-step technical instructions for technology partners integrating with Idira® Endpoint Privilege Manager by Palo Alto Networks to cleanly and programmatically retrieve security audit events using supported production REST APIs.

The operational focus is establishing secure, non-interactive enterprise authentication using the unified Idira Identity Security Platform (leveraging underlying Idira Identity, formerly CyberArk Identity, infrastructure) and subsequently performing structured resource queries against the dedicated Idira Endpoint Privilege Manager audit event logging engine.

---

## 2. Use Cases at a Glance

This integration lets a SIEM, observability, or analytics platform pull Idira Endpoint Privilege Manager audit and privilege events into its own pipeline. It is a read/pull integration built on two capabilities.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Authenticate (service account) | Obtain a bearer token via the OAuth client-credentials flow for non-interactive access | [6](#6-obtain-bearer-token-client-credentials-flow) |
| 2 | Query audit events | Retrieve structured EPM audit and privilege events from the audit API | [8](#8-interrogating-idira-endpoint-privilege-manager-audit-apis) |

The typical pattern is a scheduled poll: authenticate once, then query events on an interval and forward them into your platform. Size your polling interval against the published rate limits (see [8](#8-interrogating-idira-endpoint-privilege-manager-audit-apis)). Document your polling interval and event scope in the certification checklist.

---

## 3. Prerequisites

Before you start, confirm:

- Administrative access to Identity Administration and to an **Idira Endpoint Privilege Manager** tenant (production instance or partner sandbox), with the EPM tenant connected to the Identity Security Platform
- Which **EPM role** defines the minimum permissions your integration needs — the service user inherits its API permissions from this role (check 4.1)

Then set up API authentication in Identity Administration:

1. **Create a service user** — Manage › Inventory › Users › Add User. In **Status**, select **Is OAuth confidential client**, **Is Service User** and **Password never expires**.
2. **Assign the service user to the EPM role** you chose above.
3. **Create the API web app** — Manage › Inventory › Targets › Applications › Add Application, search for **EPM**, and add **Idira EPM API Client**. Configure the Settings tab and save.
4. **Set token lifetime and bind the user** — on the web app's **Tokens** tab choose the token expiration period; on **Permissions**, add the service user. Confirm the app shows **Deployed**.

See [Set up API authentication for EPM REST APIs using Identity](https://docs.cyberark.com/epm/latest/en/content/webservices/authenticate-with-identity-administration.htm).

---

## 4. Identify Your Tenant

You need two values:

- **Identity sub-domain** — in Identity Administration, click your user name › **About**. It has the form `<sub-domain>.id.cyberark.cloud` (for example `AAX4917.id.cyberark.cloud`). This is the token host only.
- **EPM server name** — log in to the EPM management console and copy the subdomain before `.epm.cyberark.com` in the address bar. If the URL is `https://na101.epm.cyberark.com/management-options`, the server name is `na101`. Every API call goes to this host.

---

## 5. Identity OAuth Token Endpoint Specification

```
https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
```

`<APP_NAME>` is the application ID (alias) of the Idira EPM API Client web app you created in Section 3.

---

## 6. Obtain Bearer Token (Client Credentials Flow)

Authentication uses the OAuth 2.0 `client_credentials` grant. Send the service user's credentials as HTTP Basic over TLS:

```bash
curl -u "<service-user>@<tenant-domain>:<password>" \
  -X POST \
  -d "grant_type=client_credentials" \
  https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
```

Every value in angle brackets is yours to supply; never hardcode the password (check 4.2).

---

## 7. Token Response Architecture

A successful request returns a JSON document containing:

- `access_token` — a JWT; send it as `Authorization: Bearer <ACCESS_TOKEN>` on every EPM call
- `token_type` — `Bearer`
- `expires_in` — token lifetime in seconds, set on the web app's Tokens tab

Reuse the token until it expires and request a new one then — not per call (check 2.4). To verify the setup, decode the JWT: `app_id` should match your web app and `user_roles` should include the EPM role.

---

## 8. Interrogating Idira Endpoint Privilege Manager Audit APIs

> **Updated 2026-09-08 — set management is being retired on a published timeline.** EPM is folding into the Identity Security Platform, and the console now carries hard dates: **2026-10-31** My Computers support ends · **2026-12-31** access removed · **2027-01-01** EPM set management disabled · **2027-03** standalone console access revoked. Separately, sets with no agents migrate to the new endpoint management service in release **26.9.1**, which **shipped 2026-09-27** — this migration is now live, not pending. In that release, existing sets with no endpoints have endpoint groups activated automatically, and new sets include them by default.
>
> Every operation in this section is addressed as `Sets/<SetId>/…`. **Do not treat `SetId` as a permanent identifier** — resolve it at startup, cache it for the run only, and re-resolve on a `404`. Build the set lookup as one replaceable function rather than threading `SetId` through the integration, so the migration is a single change point.

All EPM API calls go to your **EPM server**:

```
https://<EPM_Server>.epm.cyberark.com/
```

`<EPM_Server>` is the subdomain of your EPM console URL (Section 4), for example `na101`.

> **Common mistake:** Do not use the EPM login server URL (for example, `login.epm.cyberark.com` or any URL shown in the "EPM Login Server" field). That URL is for user authentication only and will return an `invalid client` or `token request failed` error when used as the API base URL. The EPM server URL is the correct value for all API calls and for the EPM server URL field in third-party integration configurators.

**`<Version>`** is a version number in `x.x.x.x` format (for example `24.12.0.0`). It is optional and defaults to the latest version; EPM recommends omitting it. The event search APIs require at least `21.12.0.0`.

### Inventory Resolution (Get Sets)

```bash
curl -X GET "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets" \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

The response lists `Sets[]` with `Id` and `Name`. Use `Id` as `<setId>` below.

### Event Retrieval

Each event family has its own search API. All of them are **POST** with a JSON body:

| Event family | Method + path (after `/EPM/API/<Version>/Sets/<setId>/`) | Reference |
|:---|:---|:---|
| Raw events (elevation, trust, installation, …) | `POST Events/Search` | [Get detailed raw events](https://docs.cyberark.com/epm/latest/en/content/webservices/getdetailedrawevents.htm) |
| Aggregated events | `POST events/aggregations/search` | [Get aggregated events](https://docs.cyberark.com/epm/latest/en/content/webservices/getaggregatedevents.htm) |
| Policy audit events | `POST policyaudits/search` | [Get policy audit raw event details](https://docs.cyberark.com/epm/latest/en/content/webservices/getpolicyauditraweventdetails.htm) |
| Aggregated policy audits | `POST policyaudits/aggregations/search` | [Get aggregated policy audits](https://docs.cyberark.com/epm/latest/en/content/webservices/getaggregatedpolicyaudits.htm) |
| Sign-in audit events | `POST signinaudits/search` | [Get detailed sign-in audit events](https://docs.cyberark.com/epm/latest/en/content/webservices/getdetailedsigninauditevents.htm) |
| Aggregated sign-in audits | `POST signinaudits/aggregations/search` | [Get aggregated sign-in audit events](https://docs.cyberark.com/epm/latest/en/content/webservices/getaggregatedsigninauditevents.htm) |
| File events (optional) | `POST Files/Aggregations/search`, `POST Files/FileInstances/Search` (minimum `22.6.0.0`) | [Get aggregated files](https://docs.cyberark.com/epm/latest/en/content/webservices/getaggregatedfiles.htm) |

```bash
curl -X POST "https://<EPM_Server>.epm.cyberark.com/EPM/API/<Version>/Sets/<setId>/Events/Search?nextCursor=start&limit=1000" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"filter": "eventType IN ElevationRequest,Trust AND arrivalTime GE 2026-10-01T00:00:00Z"}'
```

The response is `{"events": [...], "filteredCount": <n>, "returnedCount": <n>, "nextCursor": "<string>"}`.

**Pagination.** `limit` defaults to 250 and accepts 1–1,000. Pass `nextCursor=start` on the first call, then the `nextCursor` returned by each response, unchanged, on the next call. Stop when no cursor is returned. To read a complete time window, filter on `arrivalTime` (ISO-8601, UTC — the time EPM received the event) and follow the cursor.

**Filtering.** The `filter` body field uses the [EPM query language](https://docs.cyberark.com/epm/latest/en/content/webservices/epmquerylanguage.htm) — for example `eventType IN ElevationRequest,Trust`, `fileName EQ "notepad.exe"`, combined with `AND`/`OR`.

**Administrative audit is a different integration.** The EPM set and account admin-audit APIs are deprecated, and EPM directs consumers to the Identity Security Platform SIEM integration API. Build that with the [Audit Service SIEM Integration kit](../../audit-service/siem-integration/development-guide.md).

### Telemetry Header (Required)

Every request to EPM must carry the `x-cybr-telemetry` header: a Base64url-encoded string of `key=value` pairs with `it=EPMAudit`, plus `in` (integration name), `iv` (integration version) and `vn` (vendor name). The transform, the field rules and test vectors are in the [Telemetry Header Reference](../../telemetry-reference.md). Checks 7.1–7.6 grade it.

### Rate Limits

> **Updated 2026-10-08:** event-retrieval limits are **three independent categories**, and each also has a per-second cap.

| Category | Requests | Burst | Events extracted |
|:---|:---|:---|:---|
| Event and file APIs | 1,000 per 5 minutes | 5 per second | 100,000 per 24 hours |
| Policy audit and sign-in events | 1,000 per 5 minutes | 5 per second | 100,000 per 24 hours |
| Event APIs filtered to `ManualRequest` / `ElevationRequest` | 1,000 per 5 minutes | 5 per second | 100,000 per 24 hours |

Budget each category separately — consuming one does not reduce another. Size your polling interval so a normal day stays inside every budget you use. Handle `429` with exponential backoff (required by the [Certification Checklist](certification-checklist.md)). See [API limitations](https://docs.cyberark.com/epm/latest/en/content/webservices/webservicesintro.htm).

---

## 9. Comprehensive Technical Reference

- [Audit and event APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/auditseventsapis.htm) — index of the event search APIs, with full parameters, schemas and error codes
- [Get sets list](https://docs.cyberark.com/epm/latest/en/content/webservices/getsetslist.htm)
- [EPM query language](https://docs.cyberark.com/epm/latest/en/content/webservices/epmquerylanguage.htm)
- [Set up API authentication for EPM REST APIs using Identity](https://docs.cyberark.com/epm/latest/en/content/webservices/authenticate-with-identity-administration.htm)
- [Automate tasks with EPM web services](https://docs.cyberark.com/epm/latest/en/content/webservices/webservicesintro.htm) — API limitations

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.4 | 2026-10-08 | **[Fixed]** The event search call is `POST` with a JSON `filter` body, not `GET`; the example now shows the working request. **[Added]** The policy-audit, sign-in-audit, aggregated and file event search APIs; pagination with `limit` and `nextCursor` (default page 250, maximum 1,000) and windowing on `arrivalTime`; filter syntax; the `<Version>` format. **[Updated]** The API host is the EPM server name — the subdomain of your EPM console URL — rather than a "dispatcher"; Identity setup now names the Idira EPM API Client app, the EPM role and the service-user format; rate limits are three independent categories with a 5-per-second cap. Admin audit is routed to the Audit Service SIEM Integration kit, and the telemetry header is now documented in Section 8. A GET-based integration built to v1.3 must switch to POST | Idira Technical Alliances |
| 1.3 | 2026-10-05 | **[Removed]** An author-to-author editorial comment addressed to Idira teams rather than to a partner. It was invisible on the rendered page and fully visible to a partner's AI agent, which reads the raw markdown. It restated a caveat the visible guidance already carries — resolve `SetId` at runtime behind one replaceable function, against the published set-management retirement dates — so nothing a partner acts on changed. The open product question it tracked is now tracked where it has an owner. A publish-guard check now fails the build on this class of comment | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the three hosts and the two that are routinely confused — Identity for the token, the regional **dispatcher** for every API call, and `login.epm.cyberark.com` which is wrong for both and fails with an `invalid client` error that reads as a credential fault — and with the disambiguation against `audit-service/siem-integration`, which shares the Audit Service workflow but consumes platform-wide events from a different host under a different `it` value. It records that the Section 6 example credentials (`Cyberark1`, tenant `AAX4917`) are placeholders that check 4.2 would fail if committed, the two operations in dependency order, that `SetId` must be resolved at runtime behind one replaceable function against the published set-management retirement dates, and that the rate limits are **two independent budgets** rather than one. The set-management API question is carried through as explicitly open: the retirement dates are stated for the console and the endpoint management service, and whether the `Sets/<SetId>/…` REST paths change is not known, so an agent must not invent a replacement path or advise re-architecting. Three gaps are recorded rather than filled: telemetry in its entirety (`x-cybr-telemetry`, Base64url, `it=EPMAudit`), the unenumerated `<Version>` path segment, and the event schema and error tables that Section 9 defers to the EPM docs page. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
