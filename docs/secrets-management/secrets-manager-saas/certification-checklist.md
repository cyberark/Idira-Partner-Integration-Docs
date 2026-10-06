# Secrets Manager SaaS — Certification Checklist

**Workflow:** Secrets Management  
**Integration:** Secrets Manager SaaS (Conjur Cloud)  
**Type:** Certification Checklist  
**Version:** 2.2  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Secrets Management
DEV KIT: Secrets Manager SaaS (Conjur Cloud)
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: SecretsManager — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Note this value differs from the Self-Hosted kit's
(SecretsManagerSH). They are not interchangeable.

KIT-SPECIFIC WARNINGS:
- Conjur Cloud API URLs carry an /api suffix (check 4.6). The Self-Hosted paths do not. This is
  the single most common cross-kit copy error; the path is exact, character for character.
- User data lives under the `data` policy branch, which exists beneath root by default
  (check 4.7). Writing user data at root fails.
- Query results are capped at 1000 objects and pagination is graded (check 4.8). An integration
  that reads the first page and stops passes a small test tenant and fails a real one.
- Static credentials are graded against (check 4.4): secrets are retrieved live at runtime, never
  embedded in code or config. Where the customer's workloads carry SPIFFE identities, SWA
  federation is required rather than any static credential (check 4.5).

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

To achieve Idira certification for a Secrets Manager SaaS integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on. Where two items share a **One of** requirement, satisfying either one is enough.

Work through this checklist **during** development, not at submission. It is the document your integration is graded against.

---

## 2. Solution Selection

| # | Check | Requirement |
|:--|:------|:------------|
| 2.1 | Secrets Manager SaaS confirmed as the correct solution via the [Decision Guide](../decision-guide.md) | Required |
| 2.2 | Official Idira documentation best practices reviewed and applied | Required |
| 2.3 | Integration is tolerant to temporarily incorrect secrets during rotation | Required |
| 2.4 | API key authentication used only when certificate or JWT authentication is not possible | Required |

---

## 3. Telemetry Header

The `x-cybr-telemetry` header is required on every API request. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors. Do not derive the header from this table alone.

| # | Check | Requirement |
|:--|:------|:------------|
| 3.1 | `x-cybr-telemetry` header present on every API request | Required |
| 3.2 | Header value is Base64 URL-encoded | Required |
| 3.3 | `in` (IntegrationName) field populated | Required |
| 3.4 | `it` (IntegrationType) field set to `SecretsManager` | Required |
| 3.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required |
| 3.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required |

---

## 4. Code Review and Data Handling

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | Sensitive data (secrets, tokens, API keys) not printed to log or debug files | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 4.2 | Dual accounts supported by the solution | Required | Idira docs — Secrets Manager SaaS: dual account support (URL pending) |
| 4.3 | A workload identity is defined for each client — no shared workload IDs | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 4.4 | No static secret or API key embedded in application/agent code or config — secrets retrieved live at runtime | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 4.5 | Where the customer's workloads carry SPIFFE identities, authentication uses SWA federation (SPIFFE) rather than a static credential | Required | Idira docs — Secrets Manager SaaS: workload authentication (SWA / SPIFFE) (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 4.6 | Conjur Cloud API URLs include the `/api` suffix | Required | [docs: Secrets Manager SaaS REST API](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm) |
| 4.7 | `data` policy used for user data (exists under the root policy by default) | Required | Idira docs — Secrets Manager SaaS: policy structure (URL pending) |
| 4.8 | Query size limited to 1000 objects; pagination used for larger queries | Required | [docs: Secrets Manager SaaS REST API](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm) |
| 4.9 | Security scan results reviewed and addressed | Required | House rule — certification programme |
| 4.10 | User and error messaging is clear and actionable | Recommended | House rule — certification programme |
| 4.11 | Access tokens requested only on expiry — not per secret retrieval | Recommended | [docs: Secrets Manager SaaS REST API](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm) |
| 4.12 | Batch secret retrieval used where multiple secrets are needed | Recommended | [docs: Secrets Manager SaaS REST API](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm) |

---

## 5. Documentation Review

| # | Check | Requirement |
|:--|:------|:------------|
| 5.1 | Documentation uses current Idira terminology | Required |
| 5.2 | Safe and policy requirements documented for customer configuration | Required |
| 5.3 | Authentication method documented and recommended options explained | Required |

---

## 6. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement |
|:--|:------|:------------|
| 6.1 | Demo video recorded (2–5 minutes) showing end-to-end secret retrieval from Secrets Manager SaaS | One of 6.1 / 6.2 |
| 6.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end retrieval flow | One of 6.1 / 6.2 |

---

## 7. Yearly Recertification

| # | Check | Requirement |
|:--|:------|:------------|
| 7.1 | Best practices reviewed and reflected in the solution | Required |
| 7.2 | Solution tested with the latest version of Idira Secrets Manager SaaS | Required |
| 7.3 | Security scan results reviewed and addressed | Required |
| 7.4 | Documentation updated (version numbers, API paths, flow diagrams) | Required |
| 7.5 | New functionality reviewed, tested, and supported where appropriate | Recommended |

---

## 8. Attestation

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

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §4 (Code Review and Data Handling), naming the authority behind each of its 12 checks — the largest graded security section in the corpus. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). 4.3 is the row worth reading the control text for: V13.2.1 rules out "shared accounts with privileged access" for backend-to-backend calls in terms, so "a workload identity per client" is not an Idira preference a partner can trade away for a simpler deployment. Four rows carry the verified Secrets Manager SaaS REST landing — URL shape, query limits, pagination and token lifetime are all that page's contract; the `data` policy branch and SWA/SPIFFE federation are documented elsewhere and stay unlinked until those pages are fetched and confirmed. No requirement, level or wording changed. — Idira Technical Alliances |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. **The telemetry section was ungradeable and is now graded** — it previously held only a field-reference table with no checkboxes, so a partner or agent self-scoring this checklist mechanically never scored the telemetry requirement at all; it is now six numbered checks (3.1–3.6) matching the Discovery kits, with the reference table replaced by a pointer to `telemetry-reference.md`. Four checks are now **Recommended** rather than gates — 4.10 (message quality), 4.11 (token request cadence), 4.12 (batch retrieval), 7.5 (adopting new functionality). The demonstration requirement moved out of Documentation Review into its own section 6 and is expressed as **One of 6.1 / 6.2** rather than a nested checkbox. Added an AI context block. No check was removed and no requirement was loosened beyond the four re-levelled above. — Idira Technical Alliances |
