# Idira Discovery Service Certification Checklist

**Workflow:** Discovery  
**Dev Kit:** Secrets  
**Type:** Certification Checklist  
**Version:** 1.3  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-08  

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Discovery
DEV KIT: Secrets
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: Secrets-Discovery — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Do not derive the header from this checklist alone.

DO NOT CONFUSE WITH SECRETS MANAGEMENT: this kit discovers secrets that exist elsewhere and
reports them into Idira. The secrets-management/ kits do the opposite — they retrieve a secret
from Idira at runtime. If the partner's product consumes secrets rather than finding them, this
is the wrong kit; see ../../secrets-management/decision-guide.md.

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

To achieve Idira certification for a Secrets Discovery integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on.

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

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | `x-cybr-telemetry` header present on every API request | Required | House rule — telemetry |
| 3.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 3.3 | `in` (IntegrationName) field populated | Required | House rule — telemetry |
| 3.4 | `it` (IntegrationType) field set to `Secrets-Discovery` | Required | House rule — telemetry |
| 3.5 | `iv` (IntegrationVersion) field populated and matches released version | Required | House rule — telemetry |
| 3.6 | `vn` (VendorName) field populated with partner's legal entity name | Required | House rule — telemetry |

---

## 4. Data Quality — Secret Records

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | `originId` is a stable, globally unique identifier from the source system (cloud ARN, full vault path, or equivalent) | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.2 | `originId` does not change between rescans for the same secret | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.3 | `providerId` accurately identifies the source account/tenant/subscription | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.4 | `providerType` matches one of the standard values or a clearly documented custom value | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.5 | `name` is human-readable and reflects the secret's identity in the source system | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.6 | `secretValue` is NOT populated unless the customer has explicitly consented and the use case requires value transmission | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.7 | `type` field is populated for all secret records | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.8 | `subType` field populated and reflects the specific service or format | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.9 | `permanence` field populated (`STATIC` or `DYNAMIC`) for all records | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.10 | `validityTo` populated for all certificates, time-bounded API keys, and cloud access keys with known expiry | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.11 | `username` populated for all database credentials and service account keys | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.12 | `location` field populated (region, vault path, repository, or namespace) | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.13 | `tags` include at minimum: `env`, `team`, and one classification tag (e.g. `rotation-policy`, `compliance`) | Recommended | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 4.14 | No raw secret values, password hashes, or key material in `name`, `description`, `tags`, or `additionalData` | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |

---

## 5. Upsert & Deduplication Behaviour

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | `addReplaceExternalSecrets` mutation used (not repeated inserts) | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 5.2 | Repeated pushes of the same `originId` update the record without creating duplicates | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 5.3 | Each mutation request stays within the documented 64 KB request-size limit, and a response whose processed count is lower than the number sent is treated as a partial failure | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |
| 5.4 | `totalProcessedSecrets` is logged after each batch | Required | [docs: add/replace mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-external-secrets.htm) |

---

## 6. Stale Record Management

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Integration removes records from Idira when secrets are deleted or rotated out in the source | Required | [docs: delete mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-delete-external-secrets.htm) |
| 6.2 | Delete operations are always scoped — `filter` by `providerId` or `originId`; unfiltered deletes are not used | Required | [docs: delete mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-delete-external-secrets.htm) |
| 6.3 | Reconciliation logic is tested: secrets removed from source do not persist indefinitely in inventory — reconciliation uses the integration\'s own record of pushed `originId`s, since the Machines External Data Contributor role cannot read inventory | Required | [docs: delete mutation](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-delete-external-secrets.htm) |

---

## 7. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Integration logs the `originId` and API outcome for every secret pushed — secret values are never logged | Required | OWASP ASVS 5.0.0 V16.2.5 (secret values); House rule — certification programme (run logging) |
| 7.2 | Errors from GraphQL `errors[]` array are captured and logged with detail | Required | House rule — certification programme |
| 7.3 | Rate limit (429) responses trigger exponential backoff — no tight retry loops | Required | Idira docs — Discovery & Context API: rate limits (URL pending) |
| 7.4 | Integration emits a summary log per run: total discovered, total pushed, total deleted, any failures | Recommended | House rule — certification programme |

---

## 8. Inventory Validation (Functional Test)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | After a push, pushed records are visible in `Inventory > Secrets` in the Idira UI | Required | House rule — certification programme |
| 8.2 | Secret `name`, `type`, `permanence`, and `validityTo` display correctly in the inventory view | Required | House rule — certification programme |
| 8.3 | After source deletion and reconciliation run, deleted secrets are no longer present in inventory | Required | House rule — certification programme |
| 8.4 | Near-expiry secrets (within 30 days) surface correctly when filtered by `validityTo` | Recommended | House rule — certification programme |

---

## 9. Documentation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 9.1 | Partner provides a list of all `providerType` and `type` values the integration emits | Required | House rule — certification programme |
| 9.2 | Partner documents the sync schedule / trigger mechanism | Required | House rule — certification programme |
| 9.3 | Partner documents the `originId` construction strategy for each secret type | Required | House rule — certification programme |
| 9.4 | Partner explicitly documents whether `secretValue` is used and under what conditions | Required | House rule — certification programme |
| 9.5 | Partner provides a sample payload representing a real discovered secret (with values anonymized) | Recommended | House rule — certification programme |

---

## 10. Demonstration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 10.1 | **Demonstration provided — 10.2 or 10.3 satisfies this** | Required | House rule — demonstration |
| 10.2 | Demo video recorded (2–5 minutes) showing discovery through to secrets appearing in the Idira inventory view | One of 10.2 / 10.3 | House rule — demonstration |
| 10.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end discovery-to-inventory flow | One of 10.2 / 10.3 | House rule — demonstration |

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

> **Building against more than one Discovery kit?** Each kit carries its own checklist and is certified separately — a tool pushing both secrets and machine identities submits two completed checklists, not one combined. See the [Discovery decision guide](../decision-guide.md).

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-08 | **[Fixed]** v1.3 — Check 5.3 grades the documented 64 KB request-size limit instead of a 100-record batch, which had no published basis. Check 6.3 states that reconciliation uses the integration's own record of what it pushed, because the required Machines External Data Contributor role cannot read inventory. **[Added]** A `Source` on every check | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v1.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v1.1 — A `Source` column on §2 (Authentication & Security) and §7 (Logging & Observability), naming the authority behind each of those 9 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira documentation where it is a product contract, and `House rule` where it is our own programme policy. Until now no check in this repository recorded where it came from, so a security control and an internal preference were indistinguishable on the page. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). §7.1 is the row that shows why the column matters — "secret values are never logged" is ASVS **V16.2.5** and not ours to waive, while the run-logging half of the same row is a house rule that is. Cells reading `(URL pending)` carry no link because the Discovery & Context API has no entry in the vault's verified deep-links index, and guessing a doc URL is prohibited. Also added the `Version` / `Last Updated` header fields and this Change Log, which this checklist had never carried — a Rule 1 and Rule 4 gap shared by all four Discovery checklists. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-06-24 | **[Added]** v1.0 — First publication of the Secrets discovery certification checklist. The file carried no version history before 2026-10-01, so edits between this date and then are recorded only in git | Idira Technical Alliances |
