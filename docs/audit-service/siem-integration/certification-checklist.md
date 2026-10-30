# Idira Audit Service (SIEM Integration) — Certification Checklist

**Workflow:** Audit Service
**Use Case:** SIEM Integration — streaming Idira audit events into a partner security platform
**Idira Products:** Idira Identity Security Platform, Audit Service
**Type:** Certification Checklist
**Version:** 2.4
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-30

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Audit Service
DEV KIT: SIEM Integration — stream platform-wide Idira audit events into a partner security
platform.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: SIEM — see ../../telemetry-reference.md for the transform, reference code,
and test vectors.

PICK THE RIGHT KIT FIRST — this kit is confused with two others:
- This kit: PLATFORM-WIDE audit events across Idira services. Its it value is SIEM.
- ../../epm/audit-events/: EPM-SPECIFIC audit events only. Its it value is EPMAudit, not SIEM.
  Do not carry that value in here, and do not carry this one over there.
- ../../identity-response/response-actions/: the partner platform triggers actions back INTO
  Idira. This kit only CONSUMES (check 2.2). If the integration does both, they are two separate
  certifications with two separate checklists — not one submission.

TWO DISTINCT CREDENTIALS, BOTH GRADED. This is the most-missed thing in the kit:
- The OAuth Client ID + Client Secret for the confidential client (checks 3.1, 3.3).
- A SEPARATE SIEM API Key, generated in the Setup space under Integrations > Export to SIEM
  (check 3.7), and sent as the `x-api-key` header on every stream call (check 4.3).
All three must live in a secrets manager — not hardcoded, not in environment variables, not in a
config file in source control (check 3.7) — and none may reach log or debug output (check 3.8).
An integration that handles the OAuth secret properly and leaves the SIEM API Key in config fails.

KIT-SPECIFIC WARNINGS:
- The read pattern is a TWO-CALL STREAM: createQuery, then results (check 4.2). It is not a single
  GET against an events endpoint. Do not generate one.
- The service user must hold the Read Only System Administration role right and nothing broader
  (check 3.4). Without it, every query returns zero events and no error is raised. A tenant-admin
  service user fails.
- The Bearer token comes from the Idira Identity endpoint, the one carrying `.id.` in its hostname
  (check 3.5) — not from the Audit Service host.
- LOSSLESS RESUME IS GRADED TWICE. Check 4.9 requires resuming from the last successful position
  rather than skipping forward, and check 8.5 tests it with a deliberate interruption: stop,
  generate events, restart, then confirm no gap AND no duplicates. A poller that restarts from
  "now" passes every short test and fails this one.
- Deduplicate on a stable event identifier across polling cycles (check 5.1), not on a
  content hash or arrival order.
- Timestamps are preserved as Idira emitted them, in UTC (check 5.2). Re-stamping to ingestion
  time fails, and it is invisible unless a reviewer looks at a specific event.
- An unmapped field or event type is logged, never silently discarded (check 5.4).
- SECTION 8 CANNOT BE SATISFIED WITH SYNTHETIC PAYLOADS. Every applicable check needs a real event
  generated in a live Idira tenant; fixtures do not count. A failed login (8.1) applies to every
  integration. Credential retrieval (8.2) and session initiation (8.3) apply only when the scope
  declared under check 2.4 includes Idira Privileged Access Manager SaaS. An integration scoped to
  Identity Security Platform events certifies on Identity events alone — do not tell a partner it
  needs a PAM SaaS tenant unless PAM SaaS is in its declared scope.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 3.7). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
    Required if in scope — gate only when the scope declared under check 2.4 includes the
                      service the check names; otherwise not applicable.
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

This checklist is the document your Audit Service SIEM integration is graded against. Read it during the build, not at submission — it is published alongside the [Development Guide](development-guide.md) deliberately so you know the criteria while you can still act on them.

Items are the minimum best-practice requirements for a partner platform that polls the Idira Audit Service and surfaces the events to security analysts. Items marked **Required** are gate criteria — a single failure blocks certification, unless explicitly waived in writing by your Idira Technical Alliances contact. Items marked **Recommended** are best-practice validations that reviewers will note but will not block on. Where two items share a **One of** requirement, satisfying either one is enough. Items marked **Required if in scope** are gate criteria only when the scope you declare under check 2.4 includes the Idira service the item names; otherwise they do not apply.

---

## 2. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Confirmed this is an Audit Service integration: your platform **consumes** Idira audit events for monitoring, analytics, or forensics | Required | House rule — certification programme |
| 2.2 | Confirmed this is **not** an Identity Response integration — if your platform also triggers response actions back into Idira, that is a separate kit with its own checklist ([`identity-response/response-actions/`](../../identity-response/response-actions/certification-checklist.md)) | Required | House rule — certification programme |
| 2.3 | Official Idira documentation reviewed and best practices applied | Required | House rule — certification programme |
| 2.4 | Scope of audit data in this release documented (which event categories, which Idira services) | Required | House rule — certification programme |
| 2.5 | At least one production or pilot customer identified for the integration before certification | Required | House rule — certification programme |

---

## 3. Authentication & Identity

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | OAuth 2.0 `client_credentials` flow used for all Audit Service API calls | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm); OWASP ASVS 5.0.0 V13.2.1 |
| 3.2 | A dedicated service (API) user is used — no interactive user credentials | Required | OWASP ASVS 5.0.0 V13.2.1 |
| 3.3 | The service user is created as an **OAuth confidential client** | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 3.4 | The service user holds the **Read Only System Administration** role right — required for the API to return audit events — and no broader privilege | Required | [docs: Export audit activities to SIEM applications](https://docs.cyberark.com/setup/latest/en/content/setup-space/ecosystem-integration/integrate-siem-main.htm); OWASP ASVS 5.0.0 V13.3.2 |
| 3.5 | Bearer token is retrieved from the Idira Identity (`.id.`) token endpoint | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 3.6 | Token expiry is handled — token re-requested on expiry, not on every operation call | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 3.7 | The SIEM API Key generated in the Setup space (Integrations › Export to SIEM) is stored in a secrets manager — not hardcoded, not in environment variables, not in a config file in source control | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 3.8 | Client ID, Client Secret, and the SIEM API Key are never written to log or debug output | Required | OWASP ASVS 5.0.0 V16.2.5 |

---

## 4. API Implementation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | Only documented and supported Idira Audit Service endpoints are used | Required | [docs: SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) |
| 4.2 | `createQuery` / `results` stream pattern used as documented — no undocumented or scraped endpoints | Required | [docs: SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) |
| 4.3 | `Authorization: Bearer <access_token>` and `x-api-key: <siem-api-key>` headers applied on every stream request | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 4.4 | Server-side filtering used where available — the integration does not pull the full event stream and filter locally | Recommended | [docs: SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) |
| 4.5 | Polling interval is configurable by the customer, with a documented default no faster than the once-a-minute API limit | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 4.6 | Pagination handled to completion — each returned `cursorRef` is passed to the next `results` call, and the integration does not silently stop at the first page | Required | [docs: Integrate Audit with third-party SIEM applications](https://docs.cyberark.com/setup/latest/en/content/siem-integration/siem-export-3rd-party.htm) |
| 4.7 | Common error responses handled: `401` (token expired), `403` (insufficient role), `429` (rate limit) | Required | [docs: SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) |
| 4.8 | Rate-limit (`429`) backoff is exponential — no tight retry loops | Required | [docs: SIEM integration API](https://docs.cyberark.com/audit-and-reports/latest/en/content/audit/isp_siem-integration-api.htm) |
| 4.9 | A transient failure does not lose events: the integration resumes from its last successful position rather than skipping forward, and the customer documentation states that the API retains only the previous 7 days | Required | [docs: Export audit activities to SIEM applications](https://docs.cyberark.com/setup/latest/en/content/setup-space/ecosystem-integration/integrate-siem-main.htm) |

---

## 5. Data Quality

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | Duplicate audit events are avoided — the integration deduplicates on a stable event identifier across polling cycles | Required | House rule — certification programme |
| 5.2 | Event timestamps are preserved as emitted by Idira, in UTC, without re-stamping to ingestion time | Required | House rule — certification programme |
| 5.3 | Field mapping from the Idira event schema to the partner platform's schema is documented and stable across releases | Required | House rule — certification programme |
| 5.4 | Events are not silently dropped on a mapping miss — an unmapped field or event type is logged, not discarded without trace | Required | House rule — certification programme |
| 5.5 | Integration tested with real Idira activity, not synthetic payloads only — see §8 | Required | House rule — certification programme |

---

## 6. Security Best Practices

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Permissions follow least-privilege principles | Required | OWASP ASVS 5.0.0 V13.3.2 |
| 6.2 | Retrieved credential values that appear in event payloads (for example a "Fetch credential" event's context) are never persisted beyond the event record or re-emitted to logs | Required | OWASP ASVS 5.0.0 V14.2.2; V16.2.5 |
| 6.3 | Integration does not expose sensitive data in logs or debug output | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 6.4 | Security scan results reviewed and addressed | Required | House rule — certification programme |
| 6.5 | Customer-facing configuration does not require the customer to paste secrets into a plaintext field where the platform offers a credential store | Required | OWASP ASVS 5.0.0 V13.3.1 |

---

## 7. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API request, Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | `x-cybr-telemetry` header included on all Idira API requests | Required | House rule — telemetry |
| 7.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 7.3 | `in` (IntegrationName) field populated and describes the partner platform | Required | House rule — telemetry |
| 7.4 | `it` (IntegrationType) field set to `SIEM` | Required | House rule — telemetry |
| 7.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required | House rule — telemetry |
| 7.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required | House rule — telemetry |
| 7.7 | `in`, `it`, and `vn` values agreed with the Idira Technical Alliances contact before submission | Required | House rule — telemetry |

---

## 8. Functional Validation

Generate real events in the Idira tenant and confirm each arrives and displays correctly in the partner platform. Synthetic payloads do not satisfy this section. Checks 8.2 and 8.3 apply only if the scope you declare under check 2.4 includes Idira Privileged Access Manager SaaS — an integration scoped to Identity Security Platform events does not need a Privileged Access Manager SaaS tenant to certify.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | **Failed login** — attempt a login with an incorrect password; the security-monitoring event arrives | Required | House rule — certification programme |
| 8.2 | **Credential retrieval** — click Show or Copy on a test account in Idira Privileged Access Manager SaaS; the high-priority "Fetch credential" event arrives | Required if in scope (Idira Privileged Access Manager SaaS) | House rule — certification programme |
| 8.3 | **Session initiation** — launch a secure session in Idira Privileged Access Manager SaaS; the session-initiation event arrives | Required if in scope (Idira Privileged Access Manager SaaS) | House rule — certification programme |
| 8.4 | Events are searchable in the partner platform by timestamp, user, and event type | Required | House rule — certification programme |
| 8.5 | Polling recovers cleanly after a deliberate interruption (stop the integration, generate events, restart) with no gap and no duplicates | Required | House rule — certification programme |

---

## 9. Documentation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 9.1 | Integration setup steps documented end to end, written for the customer who will deploy it | Required | House rule — certification programme |
| 9.2 | The audit data collected is clearly described — which event categories and which Idira services | Required | House rule — certification programme |
| 9.3 | Required customer configuration documented: OAuth2 web app (token type, scope, claim script), service-user creation with the Read Only System Administration right, and SIEM API Key generation — including that the integration uses one of the tenant's two SIEM integration slots | Required | House rule — certification programme |
| 9.4 | Field-mapping reference published (Idira field → partner platform field) | Required | House rule — certification programme |
| 9.5 | Documentation uses current Idira product terminology — Idira Identity Security Platform, Idira Privileged Access Manager SaaS, Idira Privileged Access Manager Self-Hosted; not the legacy CyberArk names | Required | House rule — certification programme |
| 9.6 | Partner attests the integration is tested against the current Idira Audit Service APIs | Required | House rule — certification programme |

---

## 10. Demonstration

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 10.1 | Demo video recorded (2–5 minutes) showing Idira audit events ingested and surfaced in the partner platform end to end | One of 10.1 / 10.2 | House rule — demonstration |
| 10.2 | Live demonstration call held with the Idira Technical Alliances contact, walking the same end-to-end ingestion flow | One of 10.1 / 10.2 | House rule — demonstration |

---

## 11. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 11.1 | Best practices reviewed and reflected in the current integration version | Required | House rule — recertification |
| 11.2 | New Idira Audit Service endpoints or event types reviewed, tested, and supported where appropriate | Recommended | House rule — recertification |
| 11.3 | Integration tested against the latest version of the partner platform | Required | House rule — recertification |
| 11.4 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 11.5 | Documentation updated — version numbers, API paths, field references | Required | House rule — recertification |

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
| 2026-10-30 | **[Updated]** v2.4 — Checks 8.2 (credential retrieval) and 8.3 (session initiation) are now **Required if in scope**: they apply only when the scope declared under check 2.4 includes Idira Privileged Access Manager SaaS. An integration scoped to Identity Security Platform events certifies on Identity events and no longer needs a Privileged Access Manager SaaS tenant. Check 8.1 and the rest of §8 are unchanged and still require real events. If your integration ingests Privileged Access Manager SaaS events, nothing changes for you | Idira Technical Alliances |
| 2026-10-08 | **[Fixed]** v2.3 — Check 3.4 now requires the Read Only System Administration role right, without which the API returns no events; the Auditor roles it previously named do not grant audit data access. Check 3.7 names the Setup space as where the SIEM API Key is created. **[Updated]** Check 4.3 grades both the Bearer and `x-api-key` headers; 4.5 adds the once-a-minute floor; 4.6 names `cursorRef` paging; 4.9 adds the 7-day retention note; 9.3 lists the full customer configuration. A `Source` on every check | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v2.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. The `TAM waiver` label is now `Idira Technical Alliances waiver`. | Idira Technical Alliances |
| 2026-10-01 | **[Added]** v2.1 — A `Source` column on §3 (Authentication & Identity) and §6 (Security Best Practices), naming the authority behind each of those 13 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira documentation where it is a product contract, and `House rule` where it is our own programme policy (6.4, security-scan review). Until now no check in this repository recorded where it came from, so a security control and an internal preference were indistinguishable on the page and a partner pushing back on either got the same unsourced answer. The vocabulary and the verbatim control text are in [`security-baseline-reference.md`](../../security-baseline-reference.md). Three §3 cells read `(URL pending)` rather than carrying a link — the Audit Service API has no entry in the vault's verified deep-links index, and guessing a plausible doc URL is prohibited precisely because nothing downstream would catch it. No requirement, level or wording changed | Idira Technical Alliances |
| 2026-09-30 | **[Restructured]** v2.0 — Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land — including §8, which §5.5 cross-references by number. The demonstration is expressed as **One of 10.1 / 10.2** rather than a nested checkbox. The telemetry section was **partially** gradeable and is now fully graded: it previously held a field-reference table plus three loose checkboxes, so the per-field requirements (`in`, `it`, `iv`, `vn`) were stated but never scored; it is now seven numbered checks (7.1–7.7), with the reference table replaced by a pointer to `telemetry-reference.md`. The Overview's "every box must be satisfied or explicitly waived" line was rewritten to explain the three levels, keeping the Idira Technical Alliances waiver route intact for Required items. Two checks are now **Recommended** rather than gates: 4.4 (server-side filtering where available) and 11.2 (adopting new endpoints where appropriate), both conditional on availability rather than on partner effort. Added an AI context block, leading with the SIEM-vs-EPMAudit `it` confusion and the two-distinct-credentials point — an integration that vaults the OAuth secret and leaves the SIEM API Key in config fails 3.7, and that is the most-missed check in the kit. No check was removed and no requirement was loosened beyond the two re-levelled above | Idira Technical Alliances |
| 2026-09-28 | **[Fixed]** v1.2 — Corrected the relative path on the v1.1 row's `naming-crosswalk.md` link. It was written as a bare filename from a kit subdirectory two levels below the file it targets, so it resolved to a non-existent sibling and 404'd for any partner who followed it | Idira Technical Alliances |
| 2026-09-17 | **[Fixed]** v1.1 — Renamed Privilege Cloud to Idira Privileged Access Manager SaaS in prose, per the current product naming. Documented API names, role and persona names, and hostnames are deliberately unchanged and are explained in [`naming-crosswalk.md`](../../naming-crosswalk.md) §3 | Idira Technical Alliances |
| 2026-08-14 | **[Added]** Initial version — the graded certification criteria for the Audit Service SIEM kit, which previously shipped a development guide with no published checklist. Criteria derive from this kit's own development guide (OAuth confidential client, Auditor role scope, SIEM API Key handling, the `createQuery`/`results` stream pattern, and the three real-event validation cases) plus the cross-kit requirements every checklist in this repository carries: telemetry header, no secrets in logs, mandatory demonstration, and yearly recertification | Idira Technical Alliances |
