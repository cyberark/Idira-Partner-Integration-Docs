# Idira EPM — Ticketing & JIT Admin Elevation Certification Checklist

**Workflow:** EPM
**Use Case:** Ticketing — Just-in-Time admin elevation gated on an approval workflow
**Idira Product:** Idira Endpoint Privilege Manager
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
WORKFLOW: EPM
DEV KIT: Ticketing — Just-in-Time admin elevation gated on an approval workflow.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: JIT — see ../../telemetry-reference.md for the transform, reference code,
and test vectors.

READ THIS FIRST: THIS KIT GRANTS ADMINISTRATOR RIGHTS. A defect here does not degrade a feature,
it hands out standing local admin. The checklist grades the revocation and expiry paths exactly as
strictly as the grant path, and section 6 grades the trustworthiness of the approval itself. This
kit has NO Recommended items for that reason — every check is a functional path or a security
control, and there is nothing here a reviewer would merely note.

PICK THE RIGHT KIT FIRST — three EPM kits and one platform-wide kit are easily confused:
- This kit: gate JIT admin elevation through a ticketing approval workflow.
- ../soc-response/: XDR/SOAR-triggered endpoint privilege containment (the opposite direction).
- ../audit-events/: stream EPM audit events out. Its it value is EPMAudit.
- ../../audit-service/siem-integration/: platform-wide audit events, it value SIEM.
Check 2.3 grades confirming this is not SOC Response or Audit Events. Start at
../decision-guide.md if unsure.

CROSS-KIT TRAP ON AUDITING: here, `Audit: true` is required on EVERY policy and must never be
disabled, including in production (check 5.6). The Central Credential Provider kit grades the
INVERSE — its audit logging is required to be disabled for production. Do not carry either
setting across. Get it wrong here and an elevation grant leaves no trail.

EXACT VALUES AND CONSTANTS — all graded:
- `PolicyType` is `40` on every create request (check 5.3). A magic constant; there is no enum
  to derive it from.
- `IsAppliedToAllComputers` MUST be `false`, with the target resolved through `Executors`
  (check 5.4). Setting it true applies admin elevation tenant-wide. This is the single most
  damaging error available in this kit — never generate it, not even as a placeholder or example.
- `Duration` is bounded to 1–120 hours AND must be the approved duration, not a fixed maximum
  (check 5.5). Defaulting to 120 fails even though 120 is in range.
- `TargetLocalGroups` and `Accounts` each carry at least one entry, scoped to the requesting user
  and the approved group only (check 5.8). Empty or wildcard scoping fails.
- Set IDs are resolved at runtime via `GET /Sets` and agent IDs via Get endpoints
  (`POST /Sets/<SetId>/Endpoints/search`) (check 5.1), never hardcoded.
- Revocation is `DELETE /Sets/<SetId>/Policies/Server/<PolicyId>` and must be tested on ALL THREE paths: ticket
  rejection, early ticket closure, and incident-triggered revocation (check 5.11).
- Policy `Name` must include the ticket reference, requesting user, and timestamp (check 6.5), and
  the returned `PolicyId` must be stored against the originating ticket (check 5.9). Together these
  are how an auditor walks an active elevation back to its approval.

APPROVAL INTEGRITY (section 6) IS WHERE GENERATED CODE FAILS:
- A policy is created ONLY on a recorded approval by an authorized approver — never on ticket
  creation, and never on the requester's own action (check 6.1). A webhook wired to ticket-created
  rather than ticket-approved is a self-approving elevation path.
- The elevation target cannot change between approval and policy creation (check 6.4). Re-reading
  a mutable ticket field after approval is the documented failure mode; use the approved values.
- Idempotency is graded (check 5.12): a repeated approval webhook must not create a second
  overlapping policy for the same ticket. Ticketing platforms retry webhooks routinely.

SECTION 8 CANNOT BE SATISFIED AGAINST MOCKS. It requires the full lifecycle on a real EPM tenant
across five paths — approval, expiry, rejection, early revocation, and incident revocation — plus
confirming `KillRunningApps: true` terminates running admin processes and that the activity is
attributable to the ticket in EPM audit data.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 5.4). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block. This kit has none.
    One of X / Y    — either item satisfies the requirement; both are not needed.

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

This checklist is the document your Ticketing / JIT integration is graded against. Read it during the build, not at submission — it is published alongside the [Development Guide](development-guide.md) deliberately so you know the criteria while you can still act on them.

The integration under review creates time-bound EPM JIT elevation policies from an approved ticket, and revokes them on rejection, early closure, or incident. Because a defect here grants standing admin rights rather than temporary ones, the revocation and expiry paths are graded as strictly as the grant path.

Every check in this document is **Required** — a single failure blocks certification — except the demonstration in section 10, where either format satisfies the requirement. Unlike other kits in this repository, nothing here is graded as Recommended: every check is a functional path or a security control on a privilege-granting flow.

---

## 2. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Confirmed via the [EPM Decision Guide](../decision-guide.md) that Ticketing / JIT is the correct integration path | Required | House rule — certification programme |
| 2.2 | Confirmed the partner platform is a ticketing or ITSM system with a real approval workflow — not an unattended automation that self-approves | Required | House rule — certification programme |
| 2.3 | Confirmed this is **not** SOC Response (endpoint containment) or EPM Audit Events — both are separate kits with their own checklists | Required | House rule — certification programme |
| 2.4 | Official Idira EPM documentation reviewed and best practices applied | Required | House rule — certification programme |
| 2.5 | At least one production or pilot customer identified for the integration before certification | Required | House rule — certification programme |

---

## 3. EPM Tenant Prerequisites

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | A provisioned Idira EPM tenant (production or partner sandbox) used for development and testing | Required | House rule — certification programme |
| 3.2 | A configured OAuth 2.0 Web Application entity exists in the Idira Identity directory | Required | House rule — certification programme |
| 3.3 | Access to the EPM management console and the EPM APIs confirmed for resolving Set IDs and endpoint agent IDs | Required | House rule — certification programme |
| 3.4 | JIT Access and Elevation policy capability confirmed available on the tenant | Required | House rule — certification programme |
| 3.5 | Audit settings enabled on the tenant for JIT policy activity | Required | House rule — certification programme |

---

## 4. Authentication & Credential Handling

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | OAuth 2.0 `client_credentials` flow used, with a dedicated service (non-interactive) account | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm); OWASP ASVS 5.0.0 V13.2.1 |
| 4.2 | Token expiry handled — token refreshed or re-requested before it lapses, not on every API call | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 4.3 | Client ID and Client Secret stored in a secrets manager — not hardcoded, not in environment variables, not in a config file in source control | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 4.4 | No tokens, credentials, or secrets written to log or debug output | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 4.5 | The service account holds only the permissions required to create, read, update, and delete JIT policies — no broader EPM privilege | Required | OWASP ASVS 5.0.0 V13.3.2 |

---

## 5. API Implementation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | `GET /Sets` used to resolve the Set ID and Get endpoints (`POST /Sets/<SetId>/Endpoints/search`) to resolve the target computer's agent ID at runtime — agent IDs and Set IDs are **not** hardcoded | Required | [docs: Get sets list](https://docs.cyberark.com/epm/latest/en/content/webservices/getsetslist.htm); [docs: Get endpoints](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-apis/get-endpoints.htm) |
| 5.2 | `POST /Sets/<SetId>/Policies/Server` used to create the elevation policy only after the approval event fires | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.3 | `PolicyType` set to `40` on every create request | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.4 | `IsAppliedToAllComputers` set to `false`, with the target resolved through `Executors` — a JIT policy is never applied tenant-wide | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.5 | `Duration` is bounded and within the supported `1`–`120` hour range, and is the approved duration rather than a fixed maximum | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.6 | `Audit: true` set on every policy — never disabled, including in production | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.7 | `KillRunningApps` behaviour chosen deliberately, documented, and tested for both settings | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.8 | `TargetLocalGroups` and `Accounts` each carry at least one entry, scoped to the requesting user and the approved group only | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.9 | Returned `PolicyId` stored against the originating ticket so every elevation is traceable to an approval | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.10 | `GET /Sets/<SetId>/Policies/Server/<PolicyId>` used to verify policy state rather than assuming create succeeded | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.11 | `DELETE /Sets/<SetId>/Policies/Server/<PolicyId>` implemented and tested on **all three** revocation paths: ticket rejection, early ticket closure, and security-incident-triggered revocation | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.12 | Idempotency handled — a repeated approval webhook does not create a second overlapping policy for the same ticket | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.13 | Error handling implemented for `401` (token expired), `403` (insufficient permissions), `404` (policy not found), `429` (rate limit) | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |
| 5.14 | Rate-limit (`429`) backoff is exponential — no tight retry loops | Required | [docs: Just in Time access and elevation policy](https://docs.cyberark.com/epm/latest/en/content/webservices/jitpolicydefinition.htm) |

---

## 6. Approval Integrity

The grant is only as trustworthy as the approval behind it.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | An elevation policy is created **only** in response to a recorded approval by an authorized approver — never on ticket creation, and never on a requester's own action | Required | OWASP ASVS 5.0.0 V8.2.1 |
| 6.2 | The approver identity is captured and retained on the ticket record | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 6.3 | The requesting user, target computer, requested duration, and business justification are all captured on the ticket before approval routing | Required | House rule — approval integrity |
| 6.4 | The elevation target cannot be altered between approval and policy creation — the integration uses the approved values, not values re-read from a mutable field afterwards | Required | House rule — approval integrity |
| 6.5 | Policy `Name` includes the ticket reference, requesting user, and timestamp so any active policy resolves back to its approval | Required | House rule — approval integrity |

---

## 7. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API request, Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | `x-cybr-telemetry` header included on all EPM API requests | Required | House rule — telemetry |
| 7.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 7.3 | `in` (IntegrationName) field populated and describes the partner platform | Required | House rule — telemetry |
| 7.4 | `it` (IntegrationType) field set to `JIT` | Required | House rule — telemetry |
| 7.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required | House rule — telemetry |
| 7.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required | House rule — telemetry |
| 7.7 | `in`, `it`, and `vn` values agreed with the Idira Technical Alliances contact before submission | Required | House rule — telemetry |

---

## 8. Functional Validation

Test the full lifecycle on a real EPM tenant, not against mocks.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | **Approval path** — request → ticket → approval → policy created → user is in the local Administrators group on the target endpoint | Required | House rule — certification programme |
| 8.2 | **Expiry path** — duration elapses → elevation is removed automatically → user is no longer in the group | Required | House rule — certification programme |
| 8.3 | **Rejection path** — request → ticket → rejection → no policy is created (or an already-created policy is deleted) | Required | House rule — certification programme |
| 8.4 | **Early revocation path** — active elevation → ticket closed early → `DELETE` issued → elevation removed immediately | Required | House rule — certification programme |
| 8.5 | **Incident revocation path** — active elevation → external revoke trigger → elevation removed regardless of remaining duration | Required | House rule — certification programme |
| 8.6 | `KillRunningApps: true` verified: running administrative processes terminate on expiry or revocation | Required | House rule — certification programme |
| 8.7 | Elevation activity appears in EPM audit data and is attributable to the ticket | Required | House rule — certification programme |

---

## 9. Documentation Review

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 9.1 | Integration setup steps documented end to end, written for the customer who will deploy it | Required | House rule — certification programme |
| 9.2 | Prerequisites documented for customer IT and EPM administrators: tenant access, OAuth app registration, service account, Set/Agent ID retrieval | Required | House rule — certification programme |
| 9.3 | Approval workflow configuration documented — who approves, how approver groups are set, what happens on rejection | Required | House rule — certification programme |
| 9.4 | Duration policy documented, including the customer-configurable maximum and the `1`–`120` hour bound | Required | House rule — certification programme |
| 9.5 | `KillRunningApps` behaviour documented so customers understand what happens to open admin sessions at expiry | Required | House rule — certification programme |
| 9.6 | Revocation paths documented, including how a customer forces immediate revocation during an incident | Required | House rule — certification programme |
| 9.7 | Documentation uses current Idira product terminology — `Idira Endpoint Privilege Manager`, not `CyberArk EPM` | Required | House rule — certification programme |
| 9.8 | Partner attests the integration is tested against the current Idira EPM APIs | Required | House rule — certification programme |

---

## 10. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 10.1 | Demo video recorded (2–5 minutes) showing the full cycle: request → approval → elevation active → expiry or revocation | One of 10.1 / 10.2 | House rule — demonstration |
| 10.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same full cycle | One of 10.1 / 10.2 | House rule — demonstration |

---

## 11. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 11.1 | Best practices reviewed and reflected in the current integration version | Required | House rule — recertification |
| 11.2 | EPM JIT policy API changes reviewed in the EPM release notes | Required | House rule — recertification |
| 11.3 | Integration tested against the latest EPM agent version and the latest version of the partner ticketing platform | Required | House rule — recertification |
| 11.4 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 11.5 | Documentation updated — version numbers, API paths, parameter names, field references | Required | House rule — recertification |

---

## 12. Attestation

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
| 2026-10-08 | **[Fixed]** v2.3 — Checks 5.2, 5.10 and 5.11 grade the documented policy paths under `/Sets/<SetId>/Policies/Server`; the `/Policies/JIT` paths they named do not exist. Check 5.1 resolves agent IDs with Get endpoints rather than `GET /Sets`. **[Added]** A `Source` on every check. An integration graded against v2.2 paths could not pass | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v2.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v2.1 — A `Source` column on §4 (Authentication & Credential Handling) and §6 (Approval Integrity), naming the authority behind each of those 10 checks. Vocabulary and verbatim ASVS control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). §6 is the one section in the corpus where the mapping is knowingly incomplete: 6.3–6.5 are time-of-check-time-of-use controls that most likely belong to ASVS 5.0.0 **V2 Validation and Business Logic**, but no V2 control text has been read, and citing an ID from memory is prohibited — they carry `House rule — approval integrity`, which under-states them. That gap is recorded in the reference file rather than papered over, because a house rule reads to a partner as ours to waive and these are not. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-09-30 | **[Restructured]** v2.0 — Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land. The demonstration is expressed as **One of 10.1 / 10.2** rather than a nested checkbox. The telemetry section was **partially** gradeable and is now fully graded: it previously held a field-reference table plus three loose checkboxes, so the per-field requirements (`in`, `it`, `iv`, `vn`) were stated but never scored; it is now seven numbered checks (7.1–7.7), with the reference table replaced by a pointer to `telemetry-reference.md`. **No check was re-levelled to Recommended.** This is the only kit where that is stated as a deliberate position rather than an outcome: every check is a functional path or a security control on a flow that grants administrator rights, so there is nothing a reviewer would merely note. Added an AI context block covering the exact constants (`PolicyType` 40, `IsAppliedToAllComputers` false, the 1–120 hour bound), the approval-integrity failure modes a generated webhook falls into, and the cross-kit auditing trap — `Audit: true` is mandatory here while the Central Credential Provider kit grades the inverse. No check was removed and no requirement was loosened | Idira Technical Alliances |
| 2026-08-14 | **[Added]** Initial version — the graded certification criteria for the Ticketing / JIT kit, previously listed as in development and obtainable only by asking your Idira Technical Alliances contact. Promotes and expands the development guide's §10 Certification Guidelines into the standard checklist structure, and adds two sections the inline list did not cover: Approval Integrity (§6) and the five-path lifecycle validation (§8). Both are warranted because a defect on this path grants standing admin rights rather than temporary ones | Idira Technical Alliances |
