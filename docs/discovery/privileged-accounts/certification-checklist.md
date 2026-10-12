# Idira Discovery Service Certification Checklist

**Workflow:** Discovery  
**Dev Kit:** Privileged Accounts  
**Type:** Certification Checklist  
**Version:** 1.3  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-08  
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
| 2.1 | OAuth 2.0 flow used to retrieve the bearer token from the Idira Identity Security Platform | Required | [docs: Client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | A dedicated automated API user is used — no interactive or shared human accounts | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 2.3 | Integration user holds **Idira Privilege Cloud Discovery Source** (the only role that can add accounts) plus the least-privileged Privilege Cloud administrator role (Lite, Basic or full Administrator) that covers the check, get and onboard operations it implements — no broader privilege | Required | [docs: Add a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-add.htm); [docs: Check discovered account existence](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-check.htm); OWASP ASVS 5.0.0 V13.3.2 |
| 2.4 | Client secret is retrieved at runtime from a secrets manager — not hardcoded or in environment variables | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 2.5 | Access tokens are never stored persistently (disk, database, logs) | Required | OWASP ASVS 5.0.0 V14.2.2; V16.2.5 |
| 2.6 | Token expiry is handled proactively by refresh or re-request, not only on a 401 | Recommended | [docs: Client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm) |

---

## 3. Telemetry Header

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | `x-cybr-telemetry` header present on every API request | Required | House rule — telemetry |
| 3.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 3.3 | `in` (IntegrationName) field populated | Required | House rule — telemetry |
| 3.4 | `it` (IntegrationType) field set to `Privileged-Account-Discovery` | Required | House rule — telemetry |
| 3.5 | `iv` (IntegrationVersion) field populated and matches released version | Required | House rule — telemetry |
| 3.6 | `vn` (VendorName) field populated with partner's legal entity name | Required | House rule — telemetry |

---

## 4. Data Quality — Discovered Account Records

| #   | Check                                                                                                                        | Requirement |
| :-- | :--------------------------------------------------------------------------------------------------------------------------- | :---------- |
| 4.1 | The `source` field is set on every add request, identifying the scanning product (e.g. `Wiz`, `ServiceNow`) | Required | [docs: Add a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-add.htm) |
| 4.2 | Account `type`, `subType` and `identifiers` submitted match a supported mapping in the Types of accounts reference | Required | [docs: Types of accounts that can be sent via API](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-apis/discovery-api-types.htm) |
| 4.3 | Every onboard request targets an explicitly chosen Safe and Platform — never an undocumented default                         | Required    | House rule — certification programme |
| 4.4 | Field mapping from the partner's scan record to the documented onboarding parameters is complete and consistent between runs | Required    | House rule — certification programme |
| 4.5 | No PII or sensitive values are placed in name, description, or custom property fields                                        | Required    | House rule — certification programme |
| 4.6 | Custom properties are populated where available, to give the customer additional context on the discovered account           | Recommended | House rule — certification programme |
| 4.7 | Account naming is human-readable and traceable back to the asset in the partner's own console                                | Recommended | House rule — certification programme |

---

## 5. Onboarding & Duplicate Handling

| #   | Check                                                                                                                                                      | Requirement |
| :-- | :--------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- |
| 5.1 | The check-existence operation is called before adding, so an already-present account is not re-submitted blindly — at most 1,000 accounts per call | Required | [docs: Check discovered account existence](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-check.htm) |
| 5.2 | `discoveredAccount-id` is retrieved dynamically from the `/api/discovered-accounts` response — never cached across runs or hardcoded | Required | [docs: Onboard a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-onboard.htm) |
| 5.3 | Repeated runs over an unchanged source inventory do not create duplicate accounts in Idira                                                                 | Required    | House rule — certification programme |
| 5.4 | The API result for each account is surfaced in the partner's logs or UI, distinguishing *account already exists* / *account updated* / *new account added* | Required    | House rule — certification programme |
| 5.5 | Requests are batched or paced so a large scan does not exhaust API limits in a single burst                                                                | Recommended | House rule — certification programme |

---

## 6. Reconciliation & Inventory Currency

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | The get-discovered-accounts operation is used to read back inventory — paging through every result with `offset`/`limit` — and reconcile it against the partner's current scan results | Required | [docs: Get all discovered accounts](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-getall.htm) |
| 6.2 | Accounts that no longer exist in the source system are reported to the customer as stale rather than left silently in place | Required | House rule — certification programme |
| 6.3 | Reconciliation is tested end to end: an account removed at source is visibly flagged on the next run | Required | House rule — certification programme |
| 6.4 | Sync schedule is configurable by the customer rather than fixed by the integration | Recommended | House rule — certification programme |

> **Note:** This kit's documented REST operations cover read, existence check, and onboard. Removal of an onboarded account is a customer-side Idira Privileged Access Manager SaaS action, so certification asks the integration to *surface* staleness, not to delete accounts itself.

---

## 7. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Integration logs the account identifier and API outcome for every account submitted | Required | House rule — certification programme |
| 7.2 | HTTP error responses are captured and logged with the returned detail, not swallowed | Required | House rule — certification programme |
| 7.3 | Rate limit (429) responses trigger exponential backoff — no tight retry loops | Required | House rule — certification programme |
| 7.4 | Authentication and authorization failures (401, 403) are logged distinctly from data errors, so a misconfigured persona is diagnosable | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 7.5 | Integration emits a summary log per run: total discovered, total submitted, total already present, any failures | Recommended | House rule — certification programme |

---

## 8. Inventory Validation (Functional Test)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | After a push, submitted accounts are visible in the Discovered Accounts view in the Idira Privileged Access Manager SaaS UI | Required | House rule — certification programme |
| 8.2 | The Discovery Source column correctly attributes the accounts to the partner product | Required | House rule — certification programme |
| 8.3 | Onboarded accounts land in the intended Safe and against the intended Platform | Required | House rule — certification programme |
| 8.4 | Integration has been tested against a real scan of a live target, not only synthetic payloads | Required | House rule — certification programme |
| 8.5 | Custom properties are visible in the account detail view | Recommended | House rule — certification programme |

---

## 9. Documentation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 9.1 | Partner documents which operations the integration implements (check existence / add / get / onboard) | Required | House rule — certification programme |
| 9.2 | Partner documents the account-type and field mapping between their scan record and the Idira onboarding parameters | Required | House rule — certification programme |
| 9.3 | Partner documents the sync schedule or trigger mechanism | Required | House rule — certification programme |
| 9.4 | Partner documents the required API persona and setup steps a customer must complete | Required | House rule — certification programme |
| 9.5 | Partner provides a sample payload representing a real discovered account, with values anonymized | Recommended | House rule — certification programme |

---

## 10. Demonstration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 10.1 | **Demonstration provided — 10.2 or 10.3 satisfies this** | Required | House rule — demonstration |
| 10.2 | Demo video recorded (2–5 minutes) showing discovery through to the account appearing in Idira's Discovered Accounts queue | One of 10.2 / 10.3 | House rule — demonstration |
| 10.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end discovery-to-queue flow | One of 10.2 / 10.3 | House rule — demonstration |

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
| 2026-10-08 | **[Fixed]** v1.3 — Check 2.3 no longer requires Discovery Source alone: that role permits add only, and check existence, get and onboard need a Privilege Cloud administrator role, so the check now requires both at least privilege. **[Updated]** Checks 4.1, 4.2, 5.1 and 6.1 name the documented fields, the account-type reference, the 1,000-account check-existence cap and paging; 9.1 names all four operations. A `Source` on every check | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v1.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v1.1 — A `Source` column on §2 (Authentication & Security) and §7 (Logging & Observability), naming the authority behind each of those 11 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira documentation where it is a product contract, and `House rule` where it is our own programme policy. Until now no check in this repository recorded where it came from, so a security control and an internal preference were indistinguishable on the page. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). Cells reading `(URL pending)` carry no link because the Privilege Cloud discovery API has no entry in the vault's verified deep-links index, and guessing a doc URL is prohibited. Three supporting changes: the header field `**Source:**` is renamed `**Converted from:**`, because in a file that now has a `Source` *column* about a requirement's authority, a header field of the same name pointing at the original `.docx` is a collision between two different meanings; §2's table is re-laid out in the compact pipe style the other fourteen checklists use (it was the only padded-alignment table in the corpus, and adding a column meant re-padding every row regardless); and the `Version` / `Last Updated` header fields and this Change Log are added, which this checklist had never carried — a Rule 1 and Rule 4 gap shared by all four Discovery checklists. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-06-24 | **[Added]** v1.0 — First publication of the Privileged Accounts certification checklist, converted from the source `.docx`. The file carried no version history before 2026-10-01, so edits between this date and then are recorded only in git | Idira Technical Alliances |
