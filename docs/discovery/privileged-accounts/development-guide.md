# Idira Discovery Service Partner Development Guide

**Workflow:** Discovery  
**Dev Kit:** Privileged Accounts  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Discovery_Self-Service_Guide.pdf
**Version:** 1.3
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Privileged Access Manager SaaS — the discovered-accounts inventory and onboarding path.
WORKFLOW: Discovery
USE CASE: Privileged Accounts — a partner scanner pushes the privileged accounts it discovers into Idira Privileged Access Manager SaaS and keeps that inventory current.
INTEGRATION PATTERN: REST — four HTTP calls against the Privilege Cloud Discovered Accounts service.
AUTH METHOD: OAuth 2.0 client credentials against Idira Identity; token sent as `Authorization: Bearer` (Section 4)
BASE URL: https://<subdomain>.privilegecloud.cyberark.cloud/api/
TELEMETRY: it=Privileged-Account-Discovery — see ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS IS THE ONE DISCOVERY KIT THAT IS NOT ON THE DISCOVERY CONTEXT GraphQL API. The other three
(../ai-agents/, ../machine-identities/, ../secrets/) all POST GraphQL documents to
https://<tenant>.app.cyberark.cloud/api/discovery/graphql with a Bearer token and the
"Machines External Data Contributor" role. NONE of that applies here. This kit uses Privilege Cloud
REST, a different host, and a different role model. Do not carry an endpoint, an auth pattern, or a
role name across from them in either direction.

THE ROLES ARE SPLIT BY OPERATION — ONE ROLE IS NOT ENOUGH:
- **Privilege Cloud Discovery Source** — required to ADD accounts, and it permits only that.
- **Privilege Cloud Administrator, Basic Administrator or Lite Administrator** — required to READ
  the inventory, CHECK existence and ONBOARD. Use the least-privileged one that covers what you
  implement (Lite where sufficient).
An integration that adds AND checks or reads needs Discovery Source plus one administrator role. A
403 on add means Discovery Source is missing; a 403 on get/check/onboard means the administrator
role is missing.

THE OPERATIONS, IN DEPENDENCY ORDER (all under https://<subdomain>.privilegecloud.cyberark.cloud):
  1. POST /api/discovered-accounts/check-existence   -> is the account already present? (≤1,000 per call)
  2. PUT  /api/discovered-accounts/                   -> ADD a discovered account (the push)
  3. GET  /api/discovered-accounts/                   -> read the inventory back (paged: offset/limit, default 50)
  4. POST /api/discovered-accounts/{id}/onboard       -> move one into a Safe and Platform (optional)
Every path is lower-case and case-sensitive. Call 4 needs an `id` read from call 3 — it is not a value
the partner system knows or can construct.

THE ADD BODY (call 2): `type`, `subType`, `identifiers` (key/value — these define uniqueness, e.g.
`address` + `username`) and `source` (the scanning product — check 4.1) are mandatory; `isPrivileged`,
`customProperties` and `tags` (≤20, each ≤100 characters) are optional. Supported type/subType pairs
are in the Types of accounts table (Section 2).

A COMPLETE INTEGRATION: check existence, add new accounts, and read the inventory back to reconcile
(paging through every page). Whichever subset is built must be documented in the certification
checklist.

DO NOT USE THE CLASSIC API. `/PasswordVault/api/DiscoveredAccounts` (the Pending Accounts list) is the
classic Discovery API, which Idira has announced for deprecation. This kit is built on the Discovered
Accounts service only.

STILL NOT IN THIS GUIDE — DO NOT FILL IN FROM MEMORY: the full response schemas and the onboard
payload. Section 6 links the reference page for each operation.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — which Discovery dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Use Cases at a Glance

This integration pushes privileged accounts your scanner discovers into Idira Privilege Cloud and keeps that inventory current, using the Discovered Accounts service REST API.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Check account existence | Test whether accounts are already present before adding them | [5.1](#51-check-discovered-account-existence) |
| 2 | Add a discovered account | Push a newly discovered privileged account into the inventory | [5.2](#52-add-a-discovered-account) |
| 3 | Get discovered accounts | Read the inventory back to reconcile it against your scan | [5.3](#53-get-all-discovered-accounts) |
| 4 | Onboard a discovered account | Move a discovered account into a Safe and Platform (optional) | [5.4](#54-onboard-a-discovered-account) |

A complete discovery integration typically implements check, add and get. Document which operations your integration implements in the certification checklist.

> **Classic Discovery API.** The `/PasswordVault/api/DiscoveredAccounts` API (Pending Accounts list) is the classic Discovery functionality, which Idira has announced will be deprecated and unavailable to new Privilege Cloud customers. Build against the Discovered Accounts service in this guide.

---

## 2. Supported Account Types

The account `type`, `subType` and `identifiers` you send must match a supported mapping. The current table — Windows Local, Windows Domain, Windows Loosely-connected, Mac Loosely-connected, Unix Loosely-connected, and cloud password types — is in [Types of accounts that can be sent via API](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-apis/discovery-api-types.htm).

> **Stop and ask before building for other sources.** The add API documents `subType` with the single valid value `loosely`. If your scanner discovers account types outside the loosely-connected endpoint set, confirm with your Idira Technical Alliances contact that they can be submitted before you build for them.

---

## 3. REST API User Persona

The integration's service user needs roles that match the operations it calls:

| Role | Grants | Needed for |
|:---|:---|:---|
| **Idira Privilege Cloud Discovery Source** | Add discovered accounts — and only that | Section 5.2 |
| Idira Privilege Cloud **Administrator**, **Basic Administrator** or **Lite Administrator** | Read, check existence, onboard | Sections 5.1, 5.3, 5.4 |

Assign Discovery Source plus the least-privileged administrator role that covers the operations you implement. A user holding only Discovery Source can add accounts but every check, get and onboard call returns 403.

---

## 4. Getting Started with the REST API

Create a dedicated service user (an OAuth confidential client) in Identity Administration and an OAuth2 client-credentials web app for it, then request a token:

```bash
curl -u "<client-id>:<client-secret>" \
  -X POST \
  -d "grant_type=client_credentials" \
  https://<tenant>.id.cyberark.cloud/oauth2/token/<app-id>
```

The response carries `access_token` and `token_type: Bearer`. Send it on every call as `Authorization: Bearer <access_token>`, reuse it until it expires, and re-request then. See [the client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm).

Every request must also carry the `x-cybr-telemetry` header with `it=Privileged-Account-Discovery` — see the [Telemetry Header Reference](../../telemetry-reference.md).

> **Operational Recommendation:** It is highly recommended to become familiar with manual scanning workflows within the user interface before proceeding to the REST API for automation development.

---

## 5. Managing Discovered Accounts

All URLs are lower-case and case-sensitive.

### 5.1 Check Discovered Account Existence

Checks whether accounts with the given identifiers already exist. Up to 1,000 accounts per call. Requires an administrator role (Section 3).

```
POST https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/check-existence
```

> The reference page renders this path ending `check-existenc`. If `check-existence` returns 404 on your tenant, raise it with your Idira Technical Alliances contact rather than guessing.

Reference: [Check discovered account existence](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-check.htm)

### 5.2 Add a Discovered Account

Adds one discovered account to the Discovered Accounts list. Requires the Discovery Source role.

```
PUT https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{
  "type": "windows",
  "subType": "loosely",
  "identifiers": { "address": "host01.example.com", "username": "localadmin" },
  "isPrivileged": true,
  "source": "<YourProduct>",
  "customProperties": { "osVersion": "Windows 11 Pro", "enabled": true },
  "tags": ["finance", "prod"]
}
```

| Field | Mandatory | Notes |
|:---|:---|:---|
| `type` | Yes | Account type (Section 2) |
| `subType` | Yes | Documented valid value: `loosely` |
| `identifiers` | Yes | Key/value pairs that define the account's uniqueness |
| `source` | Yes | The product that discovered the account — appears as the Discovery Source |
| `isPrivileged` | No | `true` / `false` / `null` |
| `customProperties` | No | Additional key/value context for the customer |
| `tags` | No | String or list; at most 20, each at most 100 characters |

The response returns the discovered account's `id`. Reference: [Add a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-add.htm)

### 5.3 Get All Discovered Accounts

Returns the discovered accounts inventory. Requires an administrator role.

```
GET https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/?offset=0&limit=50
```

Optional query parameters: `search`, `searchOnAllFields`, `offset` (default 0), `limit` (default 50), `sort`, `filter`. **Page through every result** — with the default limit, a reconciliation that reads one page compares against the first 50 accounts only. Reference: [Get all discovered accounts](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-getall.htm)

### 5.4 Onboard a Discovered Account

Moves a discovered account into the system's active accounts in a target Safe and Platform. Requires an administrator role. The `id` must come from Section 5.3.

```
POST https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/{discoveredAccount-id}/onboard
```

Reference: [Onboard a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-onboard.htm)

### 5.5 Accounts that disappear from your source

The certification checklist requires stale accounts to be reported to the customer (check 6.2). The service also has get-one, delete, ignore and restore operations — see [Discovered accounts](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice.htm). Do not delete or ignore accounts on the customer's behalf unless your documentation says so and the customer has enabled it.

---

## 6. Reference

- [Discovered accounts REST APIs](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice.htm)
- [Types of accounts that can be sent via API](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-apis/discovery-api-types.htm)
- [Client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm)
- [Telemetry Header Reference](../../telemetry-reference.md)

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-08 | **[Fixed]** Added the missing add operation — `PUT /api/discovered-accounts/` with its body — which is the call that pushes a discovered account; the section previously titled "Add" documented onboard. Corrected the check-existence path to sit under `/api/discovered-accounts/`. Corrected the role model: Discovery Source permits add only, and check, get and onboard need a Privilege Cloud administrator role. **[Added]** Paging on get (default 50), the 1,000-account cap on check-existence, the supported account types, the token request and Bearer header, telemetry, and a note to avoid the classic Discovery API. An integration provisioned with Discovery Source alone must add an administrator role to check or reconcile | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the fact that this is the one Discovery kit *not* on the Discovery Context GraphQL API — it uses Privilege Cloud REST on a different host with a different role model — because the three sibling kits are otherwise a tempting source of an auth pattern that does not apply. It also names the one role of the four in Section 3 that can actually add accounts, the dependency order of the three calls, and, explicitly, what this guide does **not** document: no token endpoint, no auth header format, no request or response schema, and no telemetry requirement despite the checklist grading one. Those gaps are recorded so an agent declines to invent the values rather than borrowing them from the GraphQL kits. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
