# Idira Discovery Service Partner Development Guide

**Workflow:** Discovery  
**Dev Kit:** Privileged Accounts  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Discovery_Self-Service_Guide.pdf
**Version:** 1.2
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Privileged Access Manager SaaS — the discovered-accounts inventory and onboarding path.
WORKFLOW: Discovery
USE CASE: Privileged Accounts — a partner scanner pushes the privileged accounts it discovers into Idira Privileged Access Manager SaaS and keeps that inventory current.
INTEGRATION PATTERN: REST — three ordinary HTTP calls against Privilege Cloud.
AUTH METHOD: Token from the Idira Identity Security Platform (see Section 4)
BASE URL: https://<subdomain>.privilegecloud.cyberark.cloud/api/
TELEMETRY: it=Privileged-Account-Discovery — see ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS IS THE ONE DISCOVERY KIT THAT IS NOT ON THE DISCOVERY CONTEXT GraphQL API. The other three
(../ai-agents/, ../machine-identities/, ../secrets/) all POST GraphQL documents to
https://<tenant>.app.cyberark.cloud/api/discovery/graphql with a Bearer token and the
"Machines External Data Contributor" role. NONE of that applies here. This kit uses Privilege Cloud
REST, a different host, and a different role model. Do not carry an endpoint, an auth pattern, or a
role name across from them in either direction.

THE ROLE THAT MATTERS: four roles are listed in Section 3, but only **Idira Privilege Cloud
Discovery Source** carries permission to ADD accounts. An integration provisioned with the other
three can read the inventory and will fail on write. If a partner reports 403 on onboard, this is
the first thing to check.

THE THREE OPERATIONS, IN DEPENDENCY ORDER:
  1. GET  /api/discovered-accounts/            -> read the inventory. URL parameters are optional.
  2. POST /api/check-existence                 -> test whether an account is already present
  3. POST /api/discovered-accounts/{discoveredAccount-id}/onboard
                                               -> onboard into a target Safe and Platform
Call 3 requires an account id that MUST be read from call 1 first. It is not a value the partner
system knows or can construct.

A COMPLETE INTEGRATION IMPLEMENTS ALL THREE: check existence, add new accounts, read the inventory
back to reconcile. Whichever subset is built must be documented in the certification checklist.

KNOWN GAPS IN THIS GUIDE — DO NOT FILL THEM IN FROM MEMORY. This file was converted from a PDF and
is materially thinner than its siblings. It does NOT state:
- the token endpoint or the auth header format (Section 4 describes the intent only)
- any request or response schema, for any of the three calls
- the telemetry header requirement, although the certification checklist grades it
Every reference link in this file resolves to the docs.cyberark.com portal front page rather than a
specific page, so following one does not recover the missing detail. If you are asked for a field
name, a payload shape, or the token endpoint for this kit, say it is not documented here and point
at the certification checklist and the Idira Technical Alliances contact. Do not infer it from the GraphQL Discovery kits — the
API is unrelated.

SUPPORTED ACCOUNT TYPES are not enumerated in this file either; Section 2 defers to the portal.

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

This integration pushes privileged accounts your scanner discovers into Idira Privileged Access Manager SaaS and keeps that inventory current. It exposes three operations against the Discovery REST API — build the ones your use case needs.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Get discovered accounts | Read back the accounts already in the discovery inventory | [5](#5-managing-discovered-accounts) |
| 2 | Check account existence | Test whether an account is already present before adding it | [5](#5-managing-discovered-accounts) |
| 3 | Add a discovered account | Push a newly discovered privileged account into the inventory | [5](#5-managing-discovered-accounts) |

A complete discovery integration typically implements all three: check existence, add new accounts, and get the inventory to reconcile. Document which operations your integration implements in the certification checklist.

---

## 2. Prerequisites for Discovery Integration

Supported account types can be verified via the official reference documentation:

[Idira Docs (formerly CyberArk Docs) — Account Types Reference](https://docs.cyberark.com)

---

## 3. REST API User Persona

The system administrator will configure the automated API user with the following mandatory security roles:

- Idira® Privilege Cloud Administrator
- Idira Privilege Cloud Administrator Basic
- Idira Privilege Cloud Administrator Lite
- Idira Privilege Cloud Discovery Source *(Note: Only this specific persona has permissions to add accounts)*

---

## 4. Getting Started with the REST API

Use this REST API for Discovery to securely retrieve an authentication token from the Idira Identity Security Platform and properly provision the integration user with the appropriate roles.

> **Operational Recommendation:** It is highly recommended to become familiar with manual scanning workflows within the user interface before proceeding to the REST API for automation development.

---

## 5. Managing Discovered Accounts

### Get All Discovered Accounts

To retrieve the specific parameters required for checking an individual discovered account's current state of existence, invoke the following API endpoint:

```
GET https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/
```

URL parameters for this call are optional. Detailed documentation is available here:

[Idira Docs — URL Parameters Guidance](https://docs.cyberark.com)

---

### Check Discovered Accounts Existence

Retrieve a comprehensive list of all discovered accounts along with their real-time state of existence within the vault ecosystem:

```
POST https://<subdomain>.privilegecloud.cyberark.cloud/api/check-existence
```

Body parameters configuration matrix:

[Idira Docs — Body Parameters Mapping](https://docs.cyberark.com)

---

### Add a Discovered Account

Onboard and allocate discovered accounts directly into designated Idira Privileged Access Manager SaaS Safes and target Platforms.

> **Note:** The required `account-id` parameter must be dynamically retrieved beforehand from the primary `/api/discovered-accounts` endpoint response.

```
POST https://<subdomain>.privilegecloud.cyberark.cloud/api/discovered-accounts/{discoveredAccount-id}/onboard
```

Onboarding payload structure and parameter requirements:

[Idira Docs — Account Onboarding Parameters](https://docs.cyberark.com)

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the fact that this is the one Discovery kit *not* on the Discovery Context GraphQL API — it uses Privilege Cloud REST on a different host with a different role model — because the three sibling kits are otherwise a tempting source of an auth pattern that does not apply. It also names the one role of the four in Section 3 that can actually add accounts, the dependency order of the three calls, and, explicitly, what this guide does **not** document: no token endpoint, no auth header format, no request or response schema, and no telemetry requirement despite the checklist grading one. Those gaps are recorded so an agent declines to invent the values rather than borrowing them from the GraphQL kits. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps are documented, not closed. — Idira Technical Alliances |
