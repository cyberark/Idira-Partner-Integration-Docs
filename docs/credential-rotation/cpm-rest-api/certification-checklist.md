# Idira Credential Rotation Certification Checklist

**Workflow:** Credential Rotation  
**Dev Kit:** CPM REST API Plugin  
**Type:** Certification Checklist  
**Version:** 2.2  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-02  
**Converted from:** Idira_Credential_Rotation_Certification_Checklist.doc

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Credential Rotation
DEV KIT: CPM REST API Plugin
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: CredentialRotation — see ../../telemetry-reference.md for the transform,
reference code, and test vectors.

WHAT THIS INTEGRATION ACTUALLY IS: not a service that calls an Idira API. It is an XML
configuration consumed by two Idira framework assemblies running inside the customer's Central
Policy Manager. Almost every check below grades the structure of that XML, not application code.
An agent that generates a REST client here has misread the kit.

KIT-SPECIFIC WARNINGS:
- The plugin extends Idira.Extensions.Generic.Plugin.RestAPI.dll and
  Idira.Extensions.Generic.Infra.RestAPI.dll (checks 2.1, 2.2). Those assembly names are exact.
- The XML needs all four sections — <Parameters>, <ErrorMessages>, <APICalls>, <Chains> — and
  each has its own minimum-content rule (section 3). A configuration that omits one does not
  partially pass; it fails schema validity.
- Every sensitive parameter carries secure="true" (check 4.1). This includes values extracted
  from a response at runtime, not only statically declared ones.
- A parameter may not carry both a hardcoded value and a dynamic path attribute (check 6.1).
  This is a frequent generated-config error and it is graded.
- The whole of section 5.5 applies only to AccessKeys target systems. Do not implement
  Deletepass / Deletepassafterreconcile for other target types.

KNOWN DEFECT IN THIS KIT: the development guide does not document the telemetry requirement that
section 7 grades. Build the header from ../../telemetry-reference.md, which is authoritative.
This gap is tracked; it is not a licence to skip the header.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 3.4). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
- This kit has no Recommended items. It grades schema conformance, where a partial structure is
  a failure rather than a style preference.

PRECEDENCE: where this checklist and development-guide.md disagree, this file governs what
is graded — and the disagreement is a defect worth reporting. Do not silently pick one.

WHAT THIS FILE IS NOT: not an API reference, and not a test suite. Many checks are assessed
by a human reviewer against evidence the partner supplies — a demonstration, a document, a
configuration sample — and cannot be confirmed from source code alone.

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Overview — Certified CPM REST API Plugin

To achieve formal Idira® certification and ensure seamless integration within the Idira® PAM ecosystem — Idira Privileged Access Manager SaaS and Idira Privileged Access Manager Self-Hosted — all partner-developed Central Policy Manager (CPM) plugins must strictly satisfy the architectural, structural, and validation requirements outlined below.

Every check in this document is **Required** — a single failure blocks certification — except the demonstration in section 8, where either format satisfies the requirement. Work through the checklist **during** development, not at submission.

Official Reference Documentation: [REST API Infrastructure Development Architecture Guide | Idira® Docs](https://docs.cyberark.com)

---

## 2. Core Plugin Framework Implementation

| # | Check | Requirement |
|:--|:------|:------------|
| 2.1 | Plugin strictly utilizes and extends the `Idira.Extensions.Generic.Plugin.RestAPI.dll` core framework assembly | Required |
| 2.2 | Plugin strictly utilizes and extends the `Idira.Extensions.Generic.Infra.RestAPI.dll` underlying infrastructure engine | Required |

---

## 3. Configuration File Structure & Schema Validity

| # | Check | Requirement |
|:--|:------|:------------|
| 3.1 | The XML configuration structural schema contains all four foundational mandatory sections: `<Parameters>`, `<ErrorMessages>`, `<APICalls>`, and `<Chains>` | Required |
| 3.2 | All target parameter identifiers within the `<Parameters>` block are unique and distinct | Required |
| 3.3 | All standardized error definitions within the `<ErrorMessages>` block map to unique naming identifiers | Required |
| 3.4 | The functional `<APICalls>` structural block declares at least one fully formed operational `<APICall>` element | Required |
| 3.5 | The `<Responses>` processing block nested inside each `<APICall>` contains a minimum of one explicit `<Response>` resolution rule | Required |
| 3.6 | The orchestration `<Chains>` execution block incorporates at least one valid operational `<Chain>` routine | Required |
| 3.7 | Each individual `<Chain>` execution sequence invokes at least one transactional `<Request>` element | Required |

---

## 4. Secure Data Handling, Transmission and Auditing

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | All high-value sensitive variables (including access tokens, transient secrets, and payload passwords extracted from responses) are explicitly designated with the `secure="true"` attribute within the `<Parameter>` context for production environments | Required | Idira docs — CPM REST plugin: parameter definitions (URL pending); OWASP ASVS 5.0.0 V16.2.5 |
| 4.2 | Cryptographic authentication methods are strictly restricted to standardized secure Basic or Bearer token transport mechanisms | Required | OWASP ASVS 5.0.0 V14.2.1 |

---

## 5. Functional Completeness & Operational Robustness

| # | Check | Requirement |
|:--|:------|:------------|
| 5.1 | The plugin configuration establishes comprehensive interoperability across standard REST API HTTP verbs: `GET`, `POST`, `PUT`, `DELETE`, and `PATCH` | Required |
| 5.2 | Every distinct error handler block defined as `<Response type="error">` is explicitly linked to a corresponding global `<ErrorMessage>` definition | Required |
| 5.3 | All target error structures accurately expose a distinct `returnCode`, an explicit numeric or alphanumeric `name`, and a human-readable `description` | Required |
| 5.4 | Payload parsers natively map and process data exchanges using clean, strictly structured JSON, XML, or normalized plaintext body formats | Required |
| 5.5 | For specialized AccessKeys target systems executing lifecycle rotations, both the `Deletepass` and `Deletepassafterreconcile` operations are implemented to automatically purge legacy or stale key assets upon successful rollover | Required |

---

## 6. Validation & Schema Parsing Accuracy

| # | Check | Requirement |
|:--|:------|:------------|
| 6.1 | Parameters are cleanly declared; no parameter element may concurrently leverage both a hardcoded value and a dynamic path attribute | Required |
| 6.2 | Parameters configured within the global `<Parameters>` container explicitly define a `validationPattern` to handle rigorous data type validation where applicable | Required |
| 6.3 | The targeted `<Validate>` contextual evaluation block is systematically deployed inside responses when standard HTTP status codes are insufficient to definitively guarantee transaction validity | Required |

---

## 7. Partner Integration Telemetry Standards

All certified partner integrations must inject marketplace telemetry into every transaction via the HTTP header key `x-cybr-telemetry`, encoded in Base64 URL-safe format. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors.

| # | Check | Requirement |
|:--|:------|:------------|
| 7.1 | `x-cybr-telemetry` header present on every API transaction | Required |
| 7.2 | Header value is Base64 URL-encoded | Required |
| 7.3 | `in` (IntegrationName) field populated | Required |
| 7.4 | `it` (IntegrationType) field set to `CredentialRotation` | Required |
| 7.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required |
| 7.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required |

---

## 8. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement |
|:--|:------|:------------|
| 8.1 | Demo video recorded (2–5 minutes) showing an end-to-end credential rotation against the target system via the CPM plugin | One of 8.1 / 8.2 |
| 8.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end rotation flow | One of 8.1 / 8.2 |

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
| **2. Email your submission** | Send to `cybr-bizdevtech@paloaltonetworks.com` with your tracking reference in the subject line. Attach this completed checklist, your plugin XML, your integration documentation, and any test results this checklist asks for. There is no upload portal |
| **3. Deliver the demonstration** | Mandatory. Include a shareable link to your 2–5 minute demo video, **or** state in the email that you want the live walkthrough call and your Idira Technical Alliances contact will schedule it |
| **4. Expect an outcome** | Either certification approval, or an itemized gap list to remediate and resubmit — review restarts on resubmission rather than resuming mid-way. Ask your Idira Technical Alliances contact for the current review window if you are working to a launch date |

**Then: get listed.** Certification approval is not the final step. Your integration is published to the Idira Marketplace and the partner directory, and listing content has its own standards — title format, short description, and overview structure. Read [`marketplace-standards.md`](../../marketplace-standards.md) before writing that content, not after it is returned. The whole path end to end is in [The Partner Integration Journey](../../journey.md).

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §4 (Secure Data Handling, Transmission and Auditing), naming the authority behind both of its checks. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). This is the corpus's smallest graded security section and the one where the column changes the most: 4.1 reads as plugin boilerplate until it is sourced to V16.2.5, at which point a missing `secure="true"` is a logging-exposure finding with quotable control text behind it rather than a style note. Also renamed the header field `**Source:**` to `**Converted from:**`, which pointed at the original `.doc` and collided with the new column's meaning. No requirement, level or wording changed. — Idira Technical Alliances |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land. **The telemetry section was ungradeable and is now graded** — it previously held only a field-reference table with no checkboxes, so a partner or agent self-scoring this checklist mechanically never scored the telemetry requirement at all; it is now six numbered checks (7.1–7.6). The demonstration is expressed as **One of 8.1 / 8.2** rather than a nested checkbox. No check was re-levelled to Recommended: this checklist grades XML schema conformance, where a partial structure is a failure rather than a style preference. Added an AI context block, including an explicit note that this kit is an XML configuration rather than a REST client, and that the development guide does not yet document the telemetry requirement section 7 grades. No check was removed and no requirement was loosened. — Idira Technical Alliances |
