# Idira Endpoint Privilege Manager Audit Certification Checklist

**Workflow:** EPM  
**Dev Kit:** Audit Events  
**Type:** Certification Checklist  
**Version:** 2.2  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-02  
**Converted from:** Idira_EPM_Certification_Checklist.docx

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: EPM
DEV KIT: Audit Events — stream EPM audit and privilege events into a partner security platform.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: EPMAudit — see ../../telemetry-reference.md for the transform, reference
code, and test vectors.

PICK THE RIGHT KIT FIRST — three EPM kits and one platform-wide kit are easily confused:
- This kit: EPM-specific audit events into a partner platform.
- ../ticketing-jit/: gate JIT admin elevation through a ticketing approval workflow.
- ../soc-response/: XDR/SOAR-triggered endpoint privilege containment.
- ../../audit-service/siem-integration/: platform-wide audit events, NOT EPM-specific. Its it
  value is SIEM, not EPMAudit.
Start at ../decision-guide.md if unsure.

KIT-SPECIFIC WARNINGS:
- The Bearer token comes from the Idira Identity endpoint, the one carrying `.id.` in its
  hostname (check 2.3) — not from the EPM host.
- A dedicated service/API user is graded (check 2.2). An interactive user fails.
- Duplicate-event avoidance is graded (check 5.2). A poller that re-reads an overlapping window
  without deduplicating fails, and this is not visible in a short test.
- Filtering is graded rather than optional-by-default (check 3.3): raw event dumping is called
  out explicitly in the source wording.

KNOWN DEFECT IN THIS KIT: the development guide does not document the telemetry requirement that
section 7 grades. Build the header from ../../telemetry-reference.md, which is authoritative.
This gap is tracked; it is not a licence to skip the header.

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

This checklist represents the minimum best-practice requirements for partners integrating with Idira® Endpoint Privilege Manager by Palo Alto Networks for the Audit Events use case. It is intentionally concise and focused on correctness, security, and maintainability.

Items marked **Required** are gate criteria — a single failure blocks certification. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on. Where two items share a **One of** requirement, satisfying either one is enough. Work through the checklist **during** development, not at submission.

> **Choosing the right kit:** This kit covers streaming EPM audit events into a partner security platform. For gating JIT admin elevation through a ticketing system see [Ticketing — JIT](../ticketing-jit/certification-checklist.md); for endpoint containment from an XDR or SOAR playbook see [SOC Response](../soc-response/certification-checklist.md). Start at the [EPM Decision Guide](../decision-guide.md) if you are unsure. For streaming platform-wide audit events rather than EPM-specific ones, use the [Audit Service kit](../../audit-service/siem-integration/certification-checklist.md).

---

## 2. Authentication & Identity (Idira Identity Security Platform)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | OAuth 2.0 `client_credentials` flow is used | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | Dedicated service (API) user is used — no interactive users | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 2.3 | Bearer token is retrieved from the Idira Identity (`.id.`) endpoint | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 2.4 | Token expiration is handled (refresh or re-request) | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |

---

## 3. API Usage

| # | Check | Requirement |
|:--|:------|:------------|
| 3.1 | Only documented and supported Idira Endpoint Privilege Manager Audit APIs are used | Required |
| 3.2 | Authorization header uses the Bearer token correctly | Required |
| 3.3 | API filtering is used where available — no raw event dumping | Recommended |

---

## 4. Security Best Practices

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | Permissions follow least-privilege principles | Required | OWASP ASVS 5.0.0 V13.3.2 |
| 4.2 | Secrets are stored securely — not hardcoded | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 4.3 | Integration does not expose sensitive data in logs | Required | OWASP ASVS 5.0.0 V16.2.5 |

---

## 5. Reliability and Data Quality

| # | Check | Requirement |
|:--|:------|:------------|
| 5.1 | Integration handles common errors (401, 403, 429) | Required |
| 5.2 | Duplicate audit events are avoided | Required |
| 5.3 | Integration tested with real Idira Endpoint Privilege Manager policy activity | Required |

---

## 6. Documentation and Attestation

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement |
|:--|:------|:------------|
| 6.1 | Integration setup steps are documented | Required |
| 6.2 | Idira Endpoint Privilege Manager Audit data collected is clearly described | Required |
| 6.3 | Partner attests the integration is tested against current Idira Endpoint Privilege Manager APIs | Required |
| 6.4 | Demo video recorded (2–5 minutes) showing EPM audit events ingested and surfaced in the partner platform end to end | One of 6.4 / 6.5 |
| 6.5 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end ingestion flow | One of 6.4 / 6.5 |

---

## 7. Telemetry Header

All partner integrations require telemetry headers for Idira to analyze Marketplace integration data. The data is sent via an HTTP header named `x-cybr-telemetry`, Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors.

| # | Check | Requirement |
|:--|:------|:------------|
| 7.1 | `x-cybr-telemetry` header present on every API request | Required |
| 7.2 | Header value is Base64 URL-encoded | Required |
| 7.3 | `in` (IntegrationName) field populated | Required |
| 7.4 | `it` (IntegrationType) field set to `EPMAudit` | Required |
| 7.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required |
| 7.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required |

---

## 8. Yearly Recertification

| # | Check | Requirement |
|:--|:------|:------------|
| 8.1 | Best practices reviewed and reflected in the current integration version | Required |
| 8.2 | Integration tested against the latest version of the partner platform | Required |
| 8.3 | Security scan results reviewed and addressed | Required |
| 8.4 | Documentation updated — version numbers, API paths, field references | Required |
| 8.5 | New Idira Endpoint Privilege Manager audit endpoints or event types reviewed, tested, and supported where appropriate | Recommended |

---

## 9. Attestation

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

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-02 | **[Fixed]** v2.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v2.1 — A `Source` column on §2 (Authentication & Identity) and §4 (Security Best Practices), naming the authority behind each of those 7 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira EPM Web Services SDK documentation where it is a product contract. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). §4's three checks are the clearest case for the column in the corpus — "least-privilege", "stored securely", "not exposed in logs" are stated so broadly that a partner could read each as advisory; they are now V13.3.2, V13.3.1 and V16.2.5, with verbatim text a reviewer can quote. Also renamed the header field `**Source:**` to `**Converted from:**`, which pointed at the original `.docx` and collided with the new column's meaning. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land — the demonstration stayed in section 6 rather than moving to its own section, and is now expressed as **One of 6.4 / 6.5** instead of a nested checkbox. **The telemetry section was ungradeable and is now graded** — it previously held only a field-reference table with no checkboxes, so a partner or agent self-scoring this checklist mechanically never scored the telemetry requirement at all; it is now six numbered checks (7.1–7.6). Two checks are now **Recommended** rather than gates: 3.3 (filtering where available) and 8.5 (adopting new endpoints where appropriate), both conditional on availability rather than on partner effort. Added an AI context block, including the kit-selection distinctions and a note that the development guide does not yet document the telemetry requirement section 7 grades. No check was removed and no requirement was loosened beyond the two re-levelled above. | Idira Technical Alliances |
| 2026-08-19 | **[Fixed]** Corrected the workflow label from `Audit Service` to `EPM` and the dev-kit name to `Audit Events`, matching the index and the two sibling EPM kits. Set the telemetry `it` example to `EPMAudit` — it previously read `SIEM`, which is the Audit Service kit's value. Added a kit-selection note distinguishing this kit from Ticketing-JIT, SOC Response, and the platform-wide Audit Service kit. | Idira Technical Alliances |
| 2026-08-19 | **[Added]** Yearly Recertification, Attestation, Submitting This Checklist, and Change Log sections, bringing this kit in line with the structure every other checklist in this repository carries. Partners previously had no stated submission route or recertification obligation in this kit. | Idira Technical Alliances |
