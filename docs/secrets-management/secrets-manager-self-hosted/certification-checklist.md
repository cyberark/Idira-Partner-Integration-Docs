# Secrets Manager Self-Hosted — Certification Checklist

**Workflow:** Secrets Management  
**Integration:** Secrets Manager Self-Hosted  
**Type:** Certification Checklist  
**Version:** 2.3  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Secrets Management
DEV KIT: Secrets Manager Self-Hosted
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: SecretsManagerSH — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Do not derive the header from this checklist alone.
Note this value differs from the SaaS kit's (SecretsManager). They are not interchangeable.

KIT-SPECIFIC WARNINGS:
- Leader/Follower topology is graded (check 2.6). Reads go to Followers; writes and policy
  loads go to the Leader only. An integration that sends everything to one node passes
  functional testing against a single-node dev instance and fails certification.
- If the same codebase targets both Self-Hosted and Secrets Manager SaaS, the SaaS requests
  need the /api URL suffix and the `data` policy branch (check 2.7). The paths are not the same.
- Current terminology is Secrets Manager Self-Hosted / Conjur Enterprise. "DAP" is a retired
  name and is graded against in check 3.1. See ../../naming-crosswalk.md.

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

To achieve Idira certification for a Secrets Manager Self-Hosted integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on. Where two items share a **One of** requirement, satisfying either one is enough.

Work through this checklist **during** development, not at submission. It is the document your integration is graded against.

---

## 2. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Secrets Manager Self-Hosted confirmed as the correct solution via the [Decision Guide](../decision-guide.md) | Required | House rule — certification programme |
| 2.2 | Official Idira documentation best practices reviewed and applied | Required | House rule — certification programme |
| 2.3 | Integration is tolerant to temporarily incorrect secrets during rotation | Required | House rule — certification programme |
| 2.4 | API key authentication used only when no other authenticator (cloud IAM, JWT, Kubernetes, client certificate) is available | Required | [docs: Secrets Manager Self-Hosted REST API](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/developer/lp_rest_api.htm) |

---

## 3. Code Review

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | Sensitive data (secrets, tokens, API keys) not printed to log or debug files | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 3.2 | A workload identity is defined per integration client — no shared identities | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 3.3 | All read operations target Followers — writes and policy loads target the Leader only | Required | Idira docs — Secrets Manager Self-Hosted: Leader and Follower roles (URL pending) |
| 3.4 | If the integration is built for both Secrets Manager Self-Hosted and Secrets Manager SaaS: `/api` URL suffix used in Secrets Manager SaaS requests, and the `data` policy branch used for user data | Required | [docs: Secrets Manager SaaS REST API](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm) |
| 3.5 | Secret rotation handling implemented | Required | Idira docs — Secrets Manager Self-Hosted: secret rotation (URL pending) |
| 3.6 | Security scan results reviewed and addressed | Required | House rule — certification programme |
| 3.7 | `x-cybr-telemetry` header included on all API requests | Required | House rule — 2026-08-13 KPI decision |
| 3.8 | User and error messaging is clear and actionable | Recommended | House rule — certification programme |
| 3.9 | Access tokens requested only on expiry — not per secret retrieval | Recommended | [docs: API key authentication](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/developer/conjur_api_api-key-authn.htm) |
| 3.10 | Batch secret retrieval used where multiple static secrets are needed | Recommended | [docs: Batch secret retrieval](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/developer/conjur_api_batch_retrieve.htm) |

---

## 4. Documentation Review

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | Documentation uses current Idira terminology (Secrets Manager Self-Hosted / Conjur Enterprise, not DAP) | Required | House rule — certification programme |
| 4.2 | Solution overview and architecture documented | Required | House rule — certification programme |
| 4.3 | Policy structure and workload identity setup instructions provided | Required | House rule — certification programme |
| 4.4 | Authentication method documented and recommended options explained | Required | House rule — certification programme |
| 4.5 | Safe and policy requirements for customer configuration provided | Required | House rule — certification programme |

---

## 5. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | Demo video recorded (2–5 minutes) showing end-to-end secret retrieval from Secrets Manager Self-Hosted | One of 5.1 / 5.2 | House rule — demonstration |
| 5.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end retrieval flow | One of 5.1 / 5.2 | House rule — demonstration |

---

## 6. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Best practices reviewed and reflected in the solution | Required | House rule — recertification |
| 6.2 | Solution tested with the latest version of Secrets Manager Self-Hosted | Required | House rule — recertification |
| 6.3 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 6.4 | Documentation updated (version numbers, API paths, diagrams) | Required | House rule — recertification |
| 6.5 | New Secrets Manager Self-Hosted functionality reviewed and adopted where appropriate | Recommended | House rule — recertification |

---

## 7. Attestation

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
| 2.3 | 2026-10-08 | **[Updated]** Check 2.4 adds client certificate to the authenticators that come before an API key. Check 3.9 cites the 8-minute token lifetime. Check 3.10 drops the unsourced 50-per-batch maximum. **[Added]** A `Source` on every check | Idira Technical Alliances |
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances | House rule — certification programme |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §3 (Code Review), naming the authority behind each of its 10 checks. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). 3.3 is the row the column clarifies most: reads-to-Followers / writes-to-Leader looks like a hardening rule and is not one — it is how the self-hosted topology works, and an integration that writes to a Follower fails on correctness, not on security posture. It is sourced to the Leader/Follower documentation accordingly. 3.4 carries the verified Secrets Manager SaaS REST landing, since that row grades only the SaaS half of a dual-target integration. No requirement, level or wording changed. — Idira Technical Alliances | House rule — certification programme |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Four checks are now **Recommended** rather than gates — 3.8 (message quality), 3.9 (token request cadence), 3.10 (batch retrieval), 6.5 (adopting new functionality); all four are practices a reviewer notes, not correctness failures. The demonstration requirement moved to its own section 5 and is expressed as **One of 5.1 / 5.2** rather than a nested checkbox. Added an AI context block. No check was removed and no requirement was loosened beyond the four re-levelled above. — Idira Technical Alliances | House rule — certification programme |
