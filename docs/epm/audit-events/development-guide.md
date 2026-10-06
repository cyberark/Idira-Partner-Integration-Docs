# Idira Endpoint Privilege Manager Audit Integration

**Workflow:** Audit Service  
**Dev Kit:** EPM Audit  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_EPM_Audit_Self-Service_Guide.pdf  
**Version:** 1.3  
**Last Updated:** 2026-10-05

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
BASE URL: https://<dispatcher>.epm.cyberark.com/EPM/API/<Version>/   — regional, per tenant
TOKEN ENDPOINT: POST https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
TELEMETRY: it=EPMAudit — see ../../telemetry-reference.md. NOT documented in this guide; see GAPS.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THREE HOSTS, AND TWO OF THEM ARE ROUTINELY CONFUSED. This is the most expensive mistake in the kit
and the guide flags it itself (Section 8, "Common mistake"):
- `https://<TENANT>.id.cyberark.cloud` — Identity. TOKEN ONLY.
- `https://<dispatcher>.epm.cyberark.com` — the DISPATCHER. Every API call. `<dispatcher>` is a
  regional identifier assigned to the tenant (`na123`, `na228`, `eu14`), found in the EPM console
  under tenant settings. It is also the value to put in a third-party configurator's "EPM server URL"
  field, including the Splunk Add-on's.
- `login.epm.cyberark.com` — WRONG for everything here. Using the EPM Login Server URL as the API
  base returns `invalid client` or `token request failed`, which reads as a credential fault and is
  not one.

DISTINGUISH THIS KIT FROM ../../audit-service/siem-integration/. Both carry `Workflow: Audit Service`
and both are SIEM-facing polls, and they are NOT interchangeable: that kit consumes platform-wide
Identity Security Platform audit events from `*.audit.cyberark.cloud` with `it=SIEM`; this one
consumes EPM-specific events from the EPM dispatcher with `it=EPMAudit`. A partner ingesting both
needs both integrations and both checklists.

THE AUTH CALL'S SHAPE, EXACTLY (Section 6): credentials go in HTTP Basic (`curl -u`), and
`grant_type=client_credentials` goes in the form body. The response (Section 7) carries
`access_token`, `token_type` and `expires_in` — honour `expires_in` and re-request on expiry rather
than per call (check 2.4). Checks 2.1–2.3 grade the grant type, that the user is a dedicated
non-interactive service account, and that the token comes from the `.id.` host.

THE EXAMPLE CREDENTIALS IN SECTION 6 ARE PLACEHOLDERS, NOT VALUES. `curl -u "<partner>api:Cyberark1"`
carries a sandbox-style default password, and `AAX4917` in Sections 4 and 6 is an example tenant id.
Neither is the partner's. Never copy either into code, a config file or a test fixture — check 4.2
grades that secrets are not hardcoded, and a committed `Cyberark1` fails it on sight.

THE TWO OPERATIONS, IN DEPENDENCY ORDER (Section 8):
  1. GET /EPM/API/<Version>/Sets                            -> resolve the Set ids
  2. GET /EPM/API/<Version>/Sets/<setId>/Events/Search       -> the audit events
Call 2 needs a `setId` from call 1. `<Version>` is a literal path segment and this guide does not
enumerate the valid values — see GAPS.

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

RATE LIMITS ARE TWO INDEPENDENT BUDGETS, NOT ONE (Section 8, EPM console v26.7.0 onward). Policy audit
and sign-in events are metered separately from general event and file management, and each category
allows 1,000 requests per 5 minutes and 100,000 events extracted per 24 hours. Consuming one budget
does not reduce the other. Size the polling interval so a normal day stays inside BOTH, and handle
`429` with exponential backoff — check 5.1 grades `401`, `403` and `429` handling together.

TWO MORE GRADED BEHAVIOURS THIS GUIDE DOES NOT DESCRIBE: deduplicate events across polling cycles
(check 5.2) and use API-side filtering rather than dumping the raw stream (check 3.3, Recommended).
Neither has a procedure here; the checklist is the contract.

KNOWN GAPS — DO NOT FILL THEM IN FROM MEMORY:
- Telemetry. Checks 7.1–7.6 grade the `x-cybr-telemetry` header, its Base64url encoding and
  `it=EPMAudit`; this guide does not mention telemetry anywhere. Both are open corpus findings.
  ../../telemetry-reference.md carries the transform and test vectors — cite it from there.
- `<Version>`. The API version path segment is never enumerated in this guide.
- Event schema, query parameters and error tables. Section 9 defers all three to the EPM audit-events
  docs page. That is the one reference link in this kit that resolves to a real page rather than a
  portal front page — use it, and say the detail is not in this guide.

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

Before initiating configuration, ensure that your environment meets the following baseline technical criteria:

- Administrative access to a provisioned **Idira Endpoint Privilege Manager** tenant environment (production customer instance or designated partner testing sandbox)
- A dedicated service (non-interactive) identity account specifically provisioned for programmatic API authorization
- A configured OAuth 2.0 Web Application entity within your identity management directory module
- A valid, high-entropy Client ID and Client Secret pair mapped directly to the authorization service user
- Administrative UI console access permissions to the core management interface of the Idira Endpoint Privilege Manager dashboard

---

## 4. Identify Your Tenant

To target your API requests accurately, you must retrieve your unique system tenant identifier from within the core identity administrative console. Please locate your identifier string using the following standard deployment architecture context:

- Identity Service Platform Authority Endpoint: `https://AAX4917.id.cyberark.cloud`

---

## 5. Identity OAuth Token Endpoint Specification

The canonical global URL layout syntax utilized for obtaining transactional authorization tokens is structured as follows:

```
https://<TENANT>.id.cyberark.cloud/oauth2/token/<APP_NAME>
```

---

## 6. Obtain Bearer Token (Client Credentials Flow)

Programmatic authentication across the platform strictly utilizes the standard OAuth 2.0 `client_credentials` grant type flow pattern. This execution requires standard HTTP Basic authentication using the configured client credentials payload over TLS.

```bash
curl -u "<partner>api:Cyberark1" \
  -X POST \
  -d "grant_type=client_credentials" \
  https://AAX4917.id.cyberark.cloud/oauth2/token/EPMAPI<partner>
```

---

## 7. Token Response Architecture

A structurally successful authentication query returns a standardized JSON document containing:

- `access_token` — the bearer token for subsequent API calls
- `token_type` — the explicit token type designation
- `expires_in` — token lifetime in seconds

This returned `access_token` payload must be mapped directly as the authorization Bearer token string inside the HTTP header for all subsequent functional calls directed to the Idira Endpoint Privilege Manager application suite.

---

## 8. Interrogating Idira Endpoint Privilege Manager Audit APIs

> **Updated 2026-09-08 — set management is being retired on a published timeline.** EPM is folding into the Identity Security Platform, and the console now carries hard dates: **2026-10-31** My Computers support ends · **2026-12-31** access removed · **2027-01-01** EPM set management disabled · **2027-03** standalone console access revoked. Separately, sets with no agents migrate to the new endpoint management service in release **26.9.1**, which **shipped 2026-09-27** — this migration is now live, not pending. In that release, existing sets with no endpoints have endpoint groups activated automatically, and new sets include them by default.
>
> Every operation in this section is addressed as `Sets/<SetId>/…`. **Do not treat `SetId` as a permanent identifier** — resolve it at startup, cache it for the run only, and re-resolve on a `404`. Build the set lookup as one replaceable function rather than threading `SetId` through the integration, so the migration is a single change point.

The base URL for all EPM API calls is your tenant's **dispatcher URL**. This takes the format:

```
https://<dispatcher>.epm.cyberark.com/
```

Where `<dispatcher>` is a regional server identifier assigned to your tenant, for example `na123`, `na228`, `eu14`. Find your dispatcher URL in the EPM management console under tenant settings.

> **Common mistake:** Do not use the EPM login server URL (for example, `login.epm.cyberark.com` or any URL shown in the "EPM Login Server" field). That URL is for user authentication only and will return an `invalid client` or `token request failed` error when used as the API base URL. The dispatcher URL is the correct value for all API calls and for the EPM server URL field in third-party integration configurators (such as the Splunk Add-on).

Example dispatcher URL:

```
https://na228.epm.cyberark.com/
```

### Inventory Resolution (Get Sets)

To discover and enumerate the valid security policy scope configurations (Sets) assigned to the tenant system context:

```bash
curl -X GET https://na228.epm.cyberark.com/EPM/API/<Version>/Sets \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Event Streaming Retrieval (Get Audit Data)

To request filtered transactional logs, administrative modifications, and privilege elevation audit events within a given structural group:

```bash
curl -X GET https://na228.epm.cyberark.com/EPM/API/<Version>/Sets/<setId>/Events/Search \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

### Rate Limits

> **Updated 2026-07-29:** As of EPM management console v26.7.0, event-retrieval request limits are split into **two independent categories** — policy audit and sign-in events have their own thresholds, separate from general event and file management. Each category allows:

| Limit | Value |
|:---|:---|
| Requests | 1,000 per 5 minutes |
| Events extracted | 100,000 per 24 hours |

Budget each category separately — consuming the general event budget does not reduce your policy-audit budget, and vice versa. Size your polling interval so a normal day stays inside both. Handle `429` with exponential backoff (required by the [Certification Checklist](certification-checklist.md)).

---

## 9. Comprehensive Technical Reference

For comprehensive parameters, specific object modeling schema definitions, and granular error condition tables, please consult Idira Docs (formerly CyberArk Docs):

[https://docs.cyberark.com/epm/latest/en/content/webservices/auditseventsapis.htm](https://docs.cyberark.com/epm/latest/en/content/webservices/auditseventsapis.htm)

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-05 | **[Removed]** An author-to-author editorial comment addressed to Idira teams rather than to a partner. It was invisible on the rendered page and fully visible to a partner's AI agent, which reads the raw markdown. It restated a caveat the visible guidance already carries — resolve `SetId` at runtime behind one replaceable function, against the published set-management retirement dates — so nothing a partner acts on changed. The open product question it tracked is now tracked where it has an owner. A publish-guard check now fails the build on this class of comment | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the three hosts and the two that are routinely confused — Identity for the token, the regional **dispatcher** for every API call, and `login.epm.cyberark.com` which is wrong for both and fails with an `invalid client` error that reads as a credential fault — and with the disambiguation against `audit-service/siem-integration`, which shares the Audit Service workflow but consumes platform-wide events from a different host under a different `it` value. It records that the Section 6 example credentials (`Cyberark1`, tenant `AAX4917`) are placeholders that check 4.2 would fail if committed, the two operations in dependency order, that `SetId` must be resolved at runtime behind one replaceable function against the published set-management retirement dates, and that the rate limits are **two independent budgets** rather than one. The set-management API question is carried through as explicitly open: the retirement dates are stated for the console and the endpoint management service, and whether the `Sets/<SetId>/…` REST paths change is not known, so an agent must not invent a replacement path or advise re-architecting. Three gaps are recorded rather than filled: telemetry in its entirety (`x-cybr-telemetry`, Base64url, `it=EPMAudit`), the unenumerated `<Version>` path segment, and the event schema and error tables that Section 9 defers to the EPM docs page. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
