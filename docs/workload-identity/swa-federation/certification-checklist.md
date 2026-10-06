# Idira Secure Workload Access Certification Checklist

**Workflow:** Workload Identity  
**Dev Kit:** SWA Federation  
**Type:** Certification Checklist  
**Status:** Preview — not a settled gate yet  
**Version:** 1.0  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-05  

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — the graded artifact for the SWA Federation kit.
WORKFLOW: Workload Identity
DEV KIT: SWA Federation
PAIRS WITH: development-guide.md in this directory. That file states how to build the integration;
this file states what is checked. Read both.
TELEMETRY it VALUE: WorkloadIdentity — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Do not derive the header from this checklist alone.

THIS CHECKLIST IS PREVIEW AND IS NOT A SETTLED GATE. Do not tell a partner that passing it certifies
the integration, and do not promise a Marketplace listing on it. The kit's development guide has one
deliberate gap — the step-level federation exchange, its Section 6 — and §4 below cannot be fully
graded until that exchange is confirmed for the partner's specific build. Every other section is
gradeable as written. Confirm the current gate with an Idira Technical Alliances contact before a
partner submits against this file.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 2.3). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
    Confirm first   — cannot be graded until the Section 6 exchange is confirmed for this build.
- Recommended is optional to pass, not optional to read.
- `Confirm first` is specific to this Preview kit and appears in §4 only.

THE CENTRAL CHECK IS 2.1, AND IT IS THE WHOLE POINT OF THE KIT. Identity must be attested from
platform-supplied evidence, not asserted with a pre-shared secret. An integration that distributes a
static credential and calls it workload identity fails here regardless of how the rest scores.

PRECEDENCE: where this checklist and development-guide.md disagree, this file governs what is
graded — and the disagreement is a defect worth reporting. Do not silently pick one.

WHAT THIS FILE IS NOT: not an API reference, and not a test suite. Many checks are assessed by a
human reviewer against evidence the partner supplies — a demonstration, a document, a log sample —
and cannot be confirmed from source code alone.

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Overview

This checklist defines what Idira reviews in a Secure Workload Access federation integration — one
where the partner's platform establishes workload identity that Idira consumes.

> **Preview status.** This kit is marked **Preview** in [`index.md`](../../index.md): it is not a
> certifiable path yet. The checks below are the intended gate and are worth building against now,
> but confirm the current requirements with your Idira Technical Alliances contact before submitting.
> Section 4 in particular depends on the federation exchange described in
> [`development-guide.md`](development-guide.md) Section 6, which is confirmed per build rather than
> published here.

Items marked **Required** are gate criteria. Items marked **Recommended** are best-practice
validations that reviewers note but do not block on. Items marked **Confirm first** cannot be graded
until the federation exchange is confirmed for your build.

---

## 2. Workload Identity & Attestation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Workload identity is **attested from platform-supplied evidence** — not asserted with a pre-shared secret, shared account, or static API key | Required | Idira docs — Secrets Manager SaaS: authenticate workloads using SPIFFE (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | The attestation method matches the platform the workload actually runs on (EC2 Instance Identity Document, Google Cloud, or Kubernetes `k8s_jwt`) rather than being selected by preference | Required | Idira docs — Secrets Manager SaaS: authenticate workloads using SPIFFE (URL pending) |
| 2.3 | Platform was checked for an attestation path **before** any fallback method was adopted — a workload holding no SVID today is not evidence that no path exists | Required | House rule — certification programme |
| 2.4 | Where no attestation path exists, the fallback follows the documented order: client certificate, then JWT, then API key as a last resort | Required | Idira docs — Secrets Manager SaaS: Workload API authentication (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 2.5 | Integration holds only the privilege its access pattern requires — no broader scope requested for convenience | Required | OWASP ASVS 5.0.0 V13.3.2 |
| 2.6 | Attestation failure **fails closed** — the integration does not fall back to a static credential automatically when attestation is rejected | Required | House rule — certification programme |
| 2.7 | Node time synchronisation is required and documented for any node running SWA Agent | Recommended | House rule — certification programme |

---

## 3. Credential Hygiene

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | **No static key, token, or secret embedded** in any workload or agent image, manifest, container layer, or configuration file | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 3.2 | Any credential used for a fallback path (2.4) is retrieved at runtime from a secrets manager — not hardcoded and not in environment variables | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 3.3 | SVIDs, tokens, and attestation evidence are never written to logs or debug output | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 3.4 | Credentials and tokens are passed in headers or the request body — never in a URL or query string | Required | OWASP ASVS 5.0.0 V14.2.1 |
| 3.5 | No SVID is extracted from its platform context and forwarded for use elsewhere | Required | House rule — certification programme |

---

## 4. SVID Lifecycle

> These checks depend on the federation exchange confirmed per build — see
> [`development-guide.md`](development-guide.md) Section 6. Build against them; confirm the graded
> form before submission.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | SVID renewal is implemented, and no code path caches an SVID beyond its validity window | Required | OWASP ASVS 5.0.0 V14.2.2 |
| 4.2 | An SVID that expires mid-operation triggers renewal and a single retry — not an extended cache lifetime | Required | OWASP ASVS 5.0.0 V14.2.2 |
| 4.3 | No SVID is treated as a long-term credential or persisted across restarts | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 4.4 | A validity-window failure is handled as a possible clock-skew signal and distinguished from a permission failure | Recommended | House rule — certification programme |
| 4.5 | The SVID presentation sequence matches the mechanism confirmed for this build, and was not inferred from the SPIFFE specification or SPIRE material | Confirm first | Idira docs — Secrets Manager SaaS: authenticate workloads using SPIFFE (URL pending) |
| 4.6 | The SVID types the integration presents are accepted types for this mechanism | Confirm first | Idira docs — Secrets Manager SaaS: authenticate workloads using SPIFFE (URL pending) |

---

## 5. Telemetry Header

| # | Check | Requirement |
|:--|:------|:------------|
| 5.1 | `x-cybr-telemetry` header present on every API request | Required |
| 5.2 | Header value is Base64 URL-encoded | Required |
| 5.3 | `in` (IntegrationName) field populated | Required |
| 5.4 | `it` (IntegrationType) field set to `WorkloadIdentity` | Required |
| 5.5 | `iv` (IntegrationVersion) field populated and matches released version | Required |
| 5.6 | `vn` (VendorName) field populated with partner's legal entity name | Required |

---

## 6. Transport Security

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | All Idira API traffic over TLS, with no insecure or unencrypted fallback | Required | OWASP ASVS 5.0.0 V12.2.1 |
| 6.2 | TLS 1.2 minimum | Required | OWASP ASVS 5.0.0 V12.1.1 |

---

## 7. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | The attestation method attempted and its outcome are logged for every identity issued | Required | House rule — certification programme |
| 7.2 | Attestation failures are distinguishable from authorization failures in the logs | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 7.3 | A fallback decision under 2.4 is logged explicitly, naming the method used and why no attestation path applied | Required | House rule — certification programme |
| 7.4 | Integration emits a summary per run: identities issued, renewals, attestation failures, fallbacks | Recommended | House rule — certification programme |

---

## 8. Documentation

| # | Check | Requirement |
|:--|:------|:------------|
| 8.1 | Partner documents which platforms the integration supports and the attestation method used on each | Required |
| 8.2 | Partner documents the SVID renewal strategy, including behaviour on expiry mid-operation | Required |
| 8.3 | Partner documents the fallback path and the conditions that trigger it, or states that no fallback exists | Required |
| 8.4 | Partner states which component in their architecture holds the workload identity and where in the request path it is presented | Required |
| 8.5 | Partner confirms in writing that the terminology refers to **Secure Workload Access**, not the Secure Web Application Connectors Framework | Recommended |
| 8.6 | Partner provides a sample log line for an issued identity and for a rejected attestation, with values anonymized | Recommended |

---

## 9. Functional Validation

| # | Check | Requirement |
|:--|:------|:------------|
| 9.1 | A workload on a supported platform attests successfully and receives an SVID, with no credential pre-provisioned to it | Required |
| 9.2 | The same workload authenticates to Idira using that identity | Required |
| 9.3 | Renewal is observed across at least one SVID validity boundary without an operational failure | Required |
| 9.4 | Attestation is rejected when evidence does not match the configured method, and the integration fails closed per 2.6 | Required |
| 9.5 | A cloned or redeployed workload does not inherit a usable identity from its source | Recommended |

---

## 10. Demonstration

| # | Check | Requirement |
|:--|:------|:------------|
| 10.1 | **Demonstration provided — 10.2 or 10.3 satisfies this** | Required |
| 10.2 | Demo video recorded (2–5 minutes) showing a workload attesting and then authenticating to Idira with the issued identity | One of 10.2 / 10.3 |
| 10.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end attestation-to-authentication flow | One of 10.2 / 10.3 |

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

> **This kit is Preview.** It is not a certifiable path yet, so this checklist is not a settled gate
> and submitting it does not open a certification review. Complete it as a build target and confirm
> the current position with your Idira Technical Alliances contact before you submit anything —
> including checks 4.5 and 4.6, which carry a `Confirm first` level for that reason.

| Step | What to do |
|:---|:---|
| **1. Fill in the attestation above** | Partner name, integration name, version, date, and a contact who can answer review questions |
| **2. Email your submission** | Send to `cybr-bizdevtech@paloaltonetworks.com` with your tracking reference in the subject line. Attach this completed checklist, your integration documentation, and any test results this checklist asks for. There is no upload portal |
| **3. Deliver the demonstration** | Mandatory. Include a shareable link to your 2–5 minute demo video, **or** state in the email that you want the live walkthrough call and your Idira Technical Alliances contact will schedule it |
| **4. Expect an outcome** | While the kit is Preview, expect a conversation about the federation exchange rather than a pass or fail. Once it is Available: either certification approval, or an itemized gap list to remediate and resubmit — review restarts on resubmission rather than resuming mid-way |

**Then: get listed.** Listing follows certification, and certification is not open on a Preview kit — so do not plan a launch date against this path yet. Listing content has its own standards when you get there — title format, short description, and overview structure — in [`marketplace-standards.md`](../../marketplace-standards.md). Note that it does not yet carry a use-case bucket for workload identity; ask your Idira Technical Alliances contact which bucket your listing will use rather than filing under *Other / Not Sure*. The whole path end to end is in [The Partner Integration Journey](../../journey.md).

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-05 | **[Added]** v1.0 — First publication, pairing with the SWA Federation development guide as the single kit in the new `workload-identity/` workflow. Published as **Preview**, so it is explicitly not a settled gate and must not be presented as one. The gradeable substance is §2 attestation, §3 credential hygiene, §4.1–4.4 SVID lifecycle, §5 telemetry, §6 transport, §7 logging, §8 documentation and §9 functional validation; 2.1 is the central check, since an integration that distributes a static credential and calls it workload identity fails on the kit's whole premise. Two checks — 4.5 and 4.6, the SVID presentation sequence and the accepted SVID types — carry a `Confirm first` level that exists only in this kit, because the step-level federation exchange is documented in the authenticated Secrets Manager SaaS space and the development guide deliberately does not reproduce it; grading them against an inferred sequence would certify a guess. Security checks carry a `Source` naming the OWASP ASVS 5.0.0 control or the Idira document behind them, with `House rule` where the requirement is programme policy; cells reading `(URL pending)` carry no link because guessing a documentation URL is prohibited. | Idira Technical Alliances |
