# Idira Discovery Service Certification Checklist

**Workflow:** Discovery  
**Dev Kit:** AI Agents  
**Type:** Certification Checklist  
**Version:** 1.2  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-02  

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Discovery
DEV KIT: AI Agents
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: AI-Agent-Discovery — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Do not derive the header from this checklist alone.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 2.3). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
- Recommended is optional to pass, not optional to read.

PRECEDENCE: where this checklist and development-guide.md disagree, this file governs what
is graded — and the disagreement is a defect worth reporting. Do not silently pick one.

WHAT THIS FILE IS NOT: not an API reference, and not a test suite. Many checks are assessed
by a human reviewer against evidence the partner supplies — a demonstration, a document, a
log sample — and cannot be confirmed from source code alone.

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Overview

To achieve Idira certification for an AI Agent Discovery integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on.

---

## 2. Authentication & Security

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | OAuth 2.0 client credentials flow used for all API calls | Required | Idira docs — Discovery & Context API: authentication (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | Access tokens are never stored persistently (disk, database, logs) | Required | OWASP ASVS 5.0.0 V14.2.2; V16.2.5 |
| 2.3 | Client secret is retrieved at runtime from a secrets manager — not hardcoded or in environment variables | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 2.4 | Token refresh logic handles expiry proactively (not only on 401) | Recommended | Idira docs — Discovery & Context API: authentication (URL pending) |
| 2.5 | Integration user holds the **Machines External Data Contributor** role — write-only via API, no higher privilege. The previous Discovery & Context role model (Discovery Source / Secrets Hub) was replaced on 2026-08-06; an integration certified under it must be reassigned | Required | Idira docs — Discovery & Context: roles (URL pending); OWASP ASVS 5.0.0 V13.3.2 |

---

## 3. Telemetry Header

| # | Check | Requirement |
|:--|:------|:------------|
| 3.1 | `x-cybr-telemetry` header present on every API request | Required |
| 3.2 | Header value is Base64 URL-encoded | Required |
| 3.3 | `in` (IntegrationName) field populated | Required |
| 3.4 | `it` (IntegrationType) field set to `AI-Agent-Discovery` | Required |
| 3.5 | `iv` (IntegrationVersion) field populated and matches released version | Required |
| 3.6 | `vn` (VendorName) field populated with partner's legal entity name | Required |

---

## 4. Data Quality — AI Agent Records

| # | Check | Requirement |
|:--|:------|:------------|
| 4.1 | `originId` is a stable, globally unique identifier from the source system (cloud resource ARN, full resource path, or equivalent) | Required |
| 4.2 | `originId` does not change between rescans for the same agent | Required |
| 4.3 | `providerId` accurately identifies the source account/tenant/subscription | Required |
| 4.4 | `providerType` matches one of the standard values or a clearly documented custom value | Required |
| 4.5 | `name` is human-readable and reflects the agent's identity in the source system | Required |
| 4.6 | `type` field is populated for all agent records | Recommended |
| 4.7 | `subType` field populated and reflects the specific framework or cloud service | Recommended |
| 4.8 | `location` field populated (region, namespace, or deployment zone) | Recommended |
| 4.9 | `tags` include at minimum: `env`, `team`, and one classification tag | Recommended |
| 4.10 | `additionalData` includes the IAM role or permission set the agent assumes, and any tools or APIs it can invoke | Recommended |
| 4.11 | No PII or sensitive values in `name`, `description`, `tags`, or `additionalData` | Required |

---

## 5. Upsert & Deduplication Behaviour

| # | Check | Requirement |
|:--|:------|:------------|
| 5.1 | `addReplaceExternalAiAgents` mutation used (not repeated inserts) | Required |
| 5.2 | Repeated pushes of the same `originId` update the record without creating duplicates | Required |
| 5.3 | Batch size does not exceed 100 agents per mutation call | Required |
| 5.4 | `totalProcessedAiAgents` is logged after each batch | Required |

---

## 6. Stale Record Management

| # | Check | Requirement |
|:--|:------|:------------|
| 6.1 | Integration removes records from Idira when agents are deleted or deprovisioned in the source system | Required |
| 6.2 | Delete operations are always scoped — `filter` by `providerId` or `originId`; unfiltered deletes are not used | Required |
| 6.3 | Reconciliation logic is tested: agents removed from source do not persist indefinitely in inventory | Required |

---

## 7. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Integration logs the `originId` and API outcome (processed / error) for every agent pushed | Required | House rule — certification programme |
| 7.2 | Errors from GraphQL `errors[]` array are captured and logged with detail | Required | House rule — certification programme |
| 7.3 | Rate limit (429) responses trigger exponential backoff — no tight retry loops | Required | Idira docs — Discovery & Context API: rate limits (URL pending) |
| 7.4 | Integration emits a summary log per run: total discovered, total pushed, total deleted, any failures | Recommended | House rule — certification programme |

---

## 8. Inventory Validation (Functional Test)

| # | Check | Requirement |
|:--|:------|:------------|
| 8.1 | After a push, pushed records are visible in `Inventory > AI Agents` in the Idira UI | Required |
| 8.2 | Agent `name`, `type`, `location`, and `tags` display correctly in the inventory view | Required |
| 8.3 | After source deletion and reconciliation run, deleted agents are no longer present in inventory | Required |
| 8.4 | `additionalData` fields are visible in the agent detail view | Recommended |

---

## 9. Documentation

| # | Check | Requirement |
|:--|:------|:------------|
| 9.1 | Partner provides a list of all `providerType` values the integration emits | Required |
| 9.2 | Partner documents the sync schedule / trigger mechanism | Required |
| 9.3 | Partner documents the `originId` construction strategy | Required |
| 9.4 | Partner provides a sample payload representing a real discovered agent (with values anonymized) | Recommended |

---

## 10. Demonstration

| # | Check | Requirement |
|:--|:------|:------------|
| 10.1 | **Demonstration provided — 10.2 or 10.3 satisfies this** | Required |
| 10.2 | Demo video recorded (2–5 minutes) showing discovery through to agents appearing in `Inventory > AI Agents` | One of 10.2 / 10.3 |
| 10.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end discovery-to-inventory flow | One of 10.2 / 10.3 |

---

## 11. Attestation

I confirm that the integration meets the requirements above and is ready for Idira certification review.

**Partner name:**
**Integration name:**
**Version:**
**Date:**
**Contact:**

---

## Submitting This Checklist

| Step | What to do |
|:---|:---|
| **1. Fill in the attestation above** | Partner name, integration name, version, date, and a contact who can answer review questions |
| **2. Email your submission** | Send to `cybr-bizdevtech@paloaltonetworks.com` with your tracking reference in the subject line. Attach this completed checklist, your integration documentation, and any test results this checklist asks for. There is no upload portal |
| **3. Deliver the demonstration** | Mandatory. Include a shareable link to your 2–5 minute demo video, **or** state in the email that you want the live walkthrough call and your Idira Technical Alliances contact will schedule it |
| **4. Expect an outcome** | Either certification approval, or an itemized gap list to remediate and resubmit — review restarts on resubmission rather than resuming mid-way. Ask your Idira Technical Alliances contact for the current review window if you are working to a launch date |

**Then: get listed.** Certification approval is not the final step. Your integration is published to the Idira Marketplace and the partner directory, and listing content has its own standards — title format, short description, and overview structure. Read [`marketplace-standards.md`](../../marketplace-standards.md) before writing that content, not after it is returned. The whole path end to end is in [The Partner Integration Journey](../../journey.md).

> **Building against more than one Discovery kit?** Each kit carries its own checklist and is certified separately — a tool pushing both AI agents and machine identities submits two completed checklists, not one combined. See the [Discovery decision guide](../decision-guide.md).

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-02 | **[Fixed]** v1.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v1.1 — A `Source` column on §2 (Authentication & Security) and §7 (Logging & Observability), naming the authority behind each of those 9 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira documentation where it is a product contract, and `House rule` where it is our own programme policy. Until now no check in this repository recorded where it came from, so a security control and an internal preference were indistinguishable on the page. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). Cells reading `(URL pending)` carry no link because the Discovery & Context API has no entry in the vault's verified deep-links index, and guessing a doc URL is prohibited. Also added the `Version` / `Last Updated` header fields and this Change Log, which this checklist had never carried — a Rule 1 and Rule 4 gap shared by all four Discovery checklists. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-06-24 | **[Added]** v1.0 — First publication of the AI Agents certification checklist. The file carried no version history before 2026-10-01, so edits between this date and then are recorded only in git | Idira Technical Alliances |
