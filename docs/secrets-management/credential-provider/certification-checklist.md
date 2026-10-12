# Credential Provider (CP) — Certification Checklist

**Workflow:** Secrets Management  
**Integration:** Credential Provider (CP)  
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
DEV KIT: Credential Provider (CP) — agent-based local secret retrieval.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.

TELEMETRY — READ THIS BEFORE GENERATING ANY HEADER CODE:
CP has no REST API. The x-cybr-telemetry values are still required, but they are supplied as
wrapper or configuration metadata at certification submission, NOT sent as an HTTP header
(check 3.7, and §13 of the development guide). Do not generate header-injection code for this
kit. The assigned it value is CP — see ../../telemetry-reference.md for the registry.

KIT-SPECIFIC WARNINGS:
- CP is agent-based and local. CCP is the agentless REST sibling with a different kit, a
  different it value, and a real HTTP header requirement. Do not carry code between them.
- Audit logging is graded as DISABLED for production (check 3.2), which is the inverse of the
  usual expectation. Enabled-by-default logging fails this check.
- Dual-account support is graded (checks 3.3, 3.4) and requires `VirtualUsername` in the query,
  not the resolved account name. Returning the inactive account of a pair is a silent failure.
- Idira SDKs must be referenced from their default installation path, never vendored into the
  partner's package (check 3.5).
- Current terminology is CP. "AIM" is a retired name and is graded against in check 5.1.
  See ../../naming-crosswalk.md.

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

To achieve Idira certification for a Credential Provider (CP) integration, your solution must pass all required checks below before Marketplace listing. Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on. Where two items share a **One of** requirement, satisfying either one is enough.

Work through this checklist **during** development, not at submission. It is the document your integration is graded against.

---

## 2. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | CP confirmed as the correct solution via the [Decision Guide](../decision-guide.md) | Required | House rule — certification programme |
| 2.2 | Official Idira documentation best practices reviewed and applied | Required | House rule — certification programme |
| 2.3 | Integration is tolerant to temporarily incorrect secrets during rotation | Required | House rule — certification programme |
| 2.4 | Recommended authentication methods applied and tested (OS User, Allowed Machines; Path and Hash where the application can satisfy them) | Required | [docs: Application authentication methods](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/application-authentication-methods-general.htm) |

---

## 3. Code Review

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | Sensitive data (secrets, tokens, API keys) not printed to log or debug files | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 3.2 | Audit trail and logging for CP is disabled for production use — enabled only for troubleshooting | Required | Idira docs — Credential Providers: CP audit and debug logging (URL pending) |
| 3.3 | Dual accounts supported — free-text query accepted from the customer's configuration | Required | [docs: Managing dual accounts](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/cv_managing-dual-accounts.htm) |
| 3.4 | `VirtualUsername` used in dual-account queries, so the active account is always returned | Required | [docs: Managing dual accounts](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/cv_managing-dual-accounts.htm) |
| 3.5 | Idira SDKs are referenced from the default installation location — not packaged with the partner's software | Required | Idira docs — Credential Providers: application SDK deployment (URL pending) |
| 3.6 | Secret rotation handling implemented (retry after 5 seconds, or poll `PasswordChangeInProcess`) | Required | [docs: CLI Application Password SDK syntax](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/cli-application-password-sdk-egssyntax.htm) |
| 3.7 | `x-cybr-telemetry` field values supplied in the wrapper or configuration metadata submitted at certification. CP has no REST API, so these are not sent as an HTTP header — see §13 of the Development Guide | Required | House rule — 2026-08-13 KPI decision |
| 3.8 | User and error messaging is clear and actionable | Recommended | House rule — certification programme |

---

## 4. Application ID and Authentication

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | Application ID follows the format `<Partner Name>-<Product Name>` | Required | House rule — certification programme |
| 4.2 | Allowed Machines and OS User authentication methods configured and tested | Required | [docs: Application authentication methods](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/application-authentication-methods-general.htm); OWASP ASVS 5.0.0 V13.3.2 |
| 4.3 | Authentication mechanism changes restart the CP service | Required | Idira docs — Credential Providers: CP configuration (URL pending) |

---

## 5. Documentation Review

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | Documentation uses current Idira terminology (CP, not AIM) | Required | House rule — certification programme |
| 5.2 | Safe and policy requirements documented for customer configuration — including both Safe memberships: the provider user (List, Retrieve, View Safe Members) and the application (Retrieve) | Required | [docs: Provisioning privileged application accounts](https://docs.cyberark.com/credential-providers/latest/en/content/ccp/provisioning-privileged-application-accounts.htm) |
| 5.3 | Application ID authentication recommendations provided | Required | House rule — certification programme |
| 5.4 | Integration requirements and installation steps provided | Required | House rule — certification programme |

---

## 6. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Demo video recorded (2–5 minutes) showing end-to-end credential retrieval via CP | One of 6.1 / 6.2 | House rule — demonstration |
| 6.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end retrieval flow | One of 6.1 / 6.2 | House rule — demonstration |

---

## 7. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Best practices reviewed and reflected in the solution | Required | House rule — recertification |
| 7.2 | Solution tested with the latest version of Idira CP | Required | House rule — recertification |
| 7.3 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 7.4 | Documentation updated (diagrams, version numbers, screenshots removed or refreshed) | Required | House rule — recertification |
| 7.5 | New CP functionality reviewed and adopted where appropriate | Recommended | House rule — recertification |

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
| 2.3 | 2026-10-08 | **[Updated]** Check 2.4 adds Path and Hash authentication where the application can satisfy them. Check 5.2 requires both Safe memberships — the provider user and the application. Pending documentation links are now cited. **[Added]** A `Source` on every check | Idira Technical Alliances |
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances | House rule — certification programme |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §3 (Code Review) and §4 (Application ID and Authentication), naming the authority behind each of those 11 checks. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). Only 3.1 resolves to a security framework control; every other graded row here is a CP product contract or programme policy, which is the honest shape for a kit with no REST API — a partner integrates against an installed SDK, so most of what is graded is deployment and configuration behaviour rather than code the partner writes. Note that the sibling CCP kit's cells for the same checks differ: its 3.3 and 3.4 carry the verified GetPassword REST link, which does not apply here. No requirement, level or wording changed. — Idira Technical Alliances | House rule — certification programme |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Two checks are now **Recommended** rather than gates — 3.8 (message quality) and 7.5 (adopting new functionality); both are practices a reviewer notes, not correctness failures. The demonstration requirement moved out of Documentation Review into its own section 6 and is expressed as **One of 6.1 / 6.2** rather than a nested checkbox. Added an AI context block, including an explicit warning that CP supplies telemetry values as submission metadata rather than as an HTTP header. No check was removed and no requirement was loosened beyond the two re-levelled above. — Idira Technical Alliances | House rule — certification programme |
