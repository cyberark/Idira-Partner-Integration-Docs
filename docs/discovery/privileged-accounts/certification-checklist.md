# Idira Discovery Service Certification Checklist

**Workflow:** Discovery  
**Dev Kit:** Privileged Accounts  
**Type:** Certification Checklist  
**Version:** 1.2  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-02  
**Converted from:** Idira_Discovery_Service_Certification_Checklist.docx

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Discovery
DEV KIT: Privileged Accounts
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: Privileged-Account-Discovery — see ../../telemetry-reference.md for the
transform, reference code, and test vectors. Do not derive the header from this checklist alone.

KIT-SPECIFIC WARNING: this is the one Discovery kit that does not use the Discovery Context
GraphQL API. It uses the separate Privilege Cloud REST API, and its authentication flow differs
from the other three Discovery kits. Do not carry an auth pattern across from them.

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

To achieve Idira certification for a Privileged Accounts Discovery integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on.

> **API scope:** This dev kit integrates with the **Idira Privilege Cloud REST API**, not the Discovery Context GraphQL API used by the AI Agents, Machine Identities, and Secrets kits. The checks below reflect the three REST operations in the [Development Guide](development-guide.md): get discovered accounts, check existence, and onboard a discovered account. See the [Discovery Decision Guide](../decision-guide.md) if you are unsure this is the right kit.

---

## 2. Authentication & Security

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | OAuth 2.0 flow used to retrieve the bearer token from the Idira Identity Security Platform | Required | Idira docs — Privilege Cloud Discovery API: authentication (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | A dedicated automated API user is used — no interactive or shared human accounts | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 2.3 | Integration user holds the **Idira Privilege Cloud Discovery Source** role — the only persona permitted to add accounts, and no higher privilege than needed | Required | Idira docs — Privilege Cloud: Discovery Source role (URL pending); OWASP ASVS 5.0.0 V13.3.2 |
| 2.4 | Client secret is retrieved at runtime from a secrets manager — not hardcoded or in environment variables | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 2.5 | Access tokens are never stored persistently (disk, database, logs) | Required | OWASP ASVS 5.0.0 V14.2.2; V16.2.5 |
| 2.6 | Token expiry is handled proactively by refresh or re-request, not only on a 401 | Recommended | Idira docs — Privilege Cloud Discovery API: authentication (URL pending) |

---

## 3. Telemetry Header

| # | Check | Requirement |
|:--|:------|:------------|
| 3.1 | `x-cybr-telemetry` header present on every API request | Required |
| 3.2 | Header value is Base64 URL-encoded | Required |
| 3.3 | `in` (IntegrationName) field populated | Required |
| 3.4 | `it` (IntegrationType) field set to `Privileged-Account-Discovery` | Required |
| 3.5 | `iv` (IntegrationVersion) field populated and matches released version | Required |
| 3.6 | `vn` (VendorName) field populated with partner's legal entity name | Required |

---

## 4. Data Quality — Discovered Account Records

| #   | Check                                                                                                                        | Requirement |
| :-- | :--------------------------------------------------------------------------------------------------------------------------- | :---------- |
| 4.1 | The **Discovery Source** is set on every add request, identifying the scanning product (e.g. `Wiz`, `ServiceNow`)            | Required    |
| 4.2 | Account type submitted is a supported Idira account type per the Account Types reference                                     | Required    |
| 4.3 | Every onboard request targets an explicitly chosen Safe and Platform — never an undocumented default                         | Required    |
| 4.4 | Field mapping from the partner's scan record to the documented onboarding parameters is complete and consistent between runs | Required    |
| 4.5 | No PII or sensitive values are placed in name, description, or custom property fields                                        | Required    |
| 4.6 | Custom properties are populated where available, to give the customer additional context on the discovered account           | Recommended |
| 4.7 | Account naming is human-readable and traceable back to the asset in the partner's own console                                | Recommended |

---

## 5. Onboarding & Duplicate Handling

| #   | Check                                                                                                                                                      | Requirement |
| :-- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- |
| 5.1 | The check-existence operation is called before adding, so an already-present account is not re-submitted blindly                                           | Required    |
| 5.2 | `discoveredAccount-id` is retrieved dynamically from the `/api/discovered-accounts` response — never cached across runs or hardcoded                       | Required    |
| 5.3 | Repeated runs over an unchanged source inventory do not create duplicate accounts in Idira                                                                 | Required    |
| 5.4 | The API result for each account is surfaced in the partner's logs or UI, distinguishing *account already exists* / *account updated* / *new account added* | Required    |
| 5.5 | Requests are batched or paced so a large scan does not exhaust API limits in a single burst                                                                | Recommended |

---

## 6. Reconciliation & Inventory Currency

| # | Check | Requirement |
|:--|:------|:------------|
| 6.1 | The get-discovered-accounts operation is used to read back inventory and reconcile it against the partner's current scan results | Required |
| 6.2 | Accounts that no longer exist in the source system are reported to the customer as stale rather than left silently in place | Required |
| 6.3 | Reconciliation is tested end to end: an account removed at source is visibly flagged on the next run | Required |
| 6.4 | Sync schedule is configurable by the customer rather than fixed by the integration | Recommended |

> **Note:** This kit's documented REST operations cover read, existence check, and onboard. Removal of an onboarded account is a customer-side Idira Privileged Access Manager SaaS action, so certification asks the integration to *surface* staleness, not to delete accounts itself.

---

## 7. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Integration logs the account identifier and API outcome for every account submitted | Required | House rule — certification programme |
| 7.2 | HTTP error responses are captured and logged with the returned detail, not swallowed | Required | House rule — certification programme |
| 7.3 | Rate limit (429) responses trigger exponential backoff — no tight retry loops | Required | Idira docs — Privilege Cloud Discovery API: rate limits (URL pending) |
| 7.4 | Authentication and authorization failures (401, 403) are logged distinctly from data errors, so a misconfigured persona is diagnosable | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 7.5 | Integration emits a summary log per run: total discovered, total submitted, total already present, any failures | Recommended | House rule — certification programme |

---

## 8. Inventory Validation (Functional Test)

| # | Check | Requirement |
|:--|:------|:------------|
| 8.1 | After a push, submitted accounts are visible in the Discovered Accounts view in the Idira Privileged Access Manager SaaS UI | Required |
| 8.2 | The Discovery Source column correctly attributes the accounts to the partner product | Required |
| 8.3 | Onboarded accounts land in the intended Safe and against the intended Platform | Required |
| 8.4 | Integration has been tested against a real scan of a live target, not only synthetic payloads | Required |
| 8.5 | Custom properties are visible in the account detail view | Recommended |

---

## 9. Documentation

| # | Check | Requirement |
|:--|:------|:------------|
| 9.1 | Partner documents which of the three operations the integration implements (get / check existence / add) | Required |
| 9.2 | Partner documents the account-type and field mapping between their scan record and the Idira onboarding parameters | Required |
| 9.3 | Partner documents the sync schedule or trigger mechanism | Required |
| 9.4 | Partner documents the required API persona and setup steps a customer must complete | Required |
| 9.5 | Partner provides a sample payload representing a real discovered account, with values anonymized | Recommended |

---

## 10. Demonstration

| # | Check | Requirement |
|:--|:------|:------------|
| 10.1 | **Demonstration provided — 10.2 or 10.3 satisfies this** | Required |
| 10.2 | Demo video recorded (2–5 minutes) showing discovery through to the account appearing in Idira's Discovered Accounts queue | One of 10.2 / 10.3 |
| 10.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end discovery-to-queue flow | One of 10.2 / 10.3 |

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

> **Building against more than one Discovery kit?** Each kit carries its own checklist and is certified separately — a tool pushing both accounts and secrets submits two completed checklists, not one combined. See the [Discovery decision guide](../decision-guide.md).

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-02 | **[Fixed]** v1.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v1.1 — A `Source` column on §2 (Authentication & Security) and §7 (Logging & Observability), naming the authority behind each of those 11 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira documentation where it is a product contract, and `House rule` where it is our own programme policy. Until now no check in this repository recorded where it came from, so a security control and an internal preference were indistinguishable on the page. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). Cells reading `(URL pending)` carry no link because the Privilege Cloud discovery API has no entry in the vault's verified deep-links index, and guessing a doc URL is prohibited. Three supporting changes: the header field `**Source:**` is renamed `**Converted from:**`, because in a file that now has a `Source` *column* about a requirement's authority, a header field of the same name pointing at the original `.docx` is a collision between two different meanings; §2's table is re-laid out in the compact pipe style the other fourteen checklists use (it was the only padded-alignment table in the corpus, and adding a column meant re-padding every row regardless); and the `Version` / `Last Updated` header fields and this Change Log are added, which this checklist had never carried — a Rule 1 and Rule 4 gap shared by all four Discovery checklists. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-06-24 | **[Added]** v1.0 — First publication of the Privileged Accounts certification checklist, converted from the source `.docx`. The file carried no version history before 2026-10-01, so edits between this date and then are recorded only in git | Idira Technical Alliances |
