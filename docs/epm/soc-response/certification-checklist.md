# SOC Response (XDR/SOAR Endpoint Containment) — Certification Checklist

**Workflow:** EPM
**Use Case:** SOC Response — XDR/SOAR Endpoint Containment
**Idira Product:** Endpoint Privilege Manager (EPM)
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
DEV KIT: SOC Response — XDR/SOAR-triggered endpoint privilege containment.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.
TELEMETRY it VALUE: SOCResponse — see ../../telemetry-reference.md for the transform, reference
code, and test vectors.

WHAT THIS INTEGRATION ACTUALLY IS: a containment action, not a data feed. On a high- or
medium-severity alert the integration MOVES AN ENDPOINT INTO AN EPM STATIC GROUP, and the policy
bound to that group strips the endpoint's privileges. Removing it from the group lifts the policy.
There is no "contain" API — group membership IS the mechanism. Both directions are graded.

PICK THE RIGHT KIT FIRST — three EPM kits and one platform-wide kit are easily confused:
- This kit: XDR/SOAR-triggered endpoint privilege containment.
- ../audit-events/: stream EPM audit events into a partner platform. Its it value is EPMAudit.
- ../ticketing-jit/: gate JIT admin elevation through a ticketing approval workflow.
- ../../audit-service/siem-integration/: platform-wide audit events, it value SIEM.
Start at ../decision-guide.md if unsure.

KIT-SPECIFIC WARNINGS:
- AUTH DIFFERS FROM EVERY OTHER EPM KIT. The token is requested with
  `Authorization: basic <token>` (check 3.4) — lowercase "basic", and NOT Bearer. The sibling
  audit-events kit uses Bearer. This is the single most common cross-kit error here; do not
  normalise it to Bearer because that is what the other kits do.
- Windows and Windows Server only (check 1.3). macOS and Linux endpoints are not supported.
  EPM Windows agent 26.4 or later is a hard floor (check 1.4).
- Search Groups V2 only (check 4.3). The V1 endpoint is deprecated and graded against.
- Group removal is a POST to a `.../members/ids/remove` path (check 4.6), not an HTTP DELETE.
- The add-members request body field is `membersIds` (check 4.5) — plural, no underscore. Exact.
- SetId and both GroupId values are cached at startup, not hardcoded, and GroupId is refreshed
  only on a 404 (checks 4.1, 4.4).
- Idempotency is graded (check 4.9): re-containing an endpoint already in the group must not
  raise. A SOAR playbook retries, so this fires in production and not in a single-shot test.
- The two static group names are literals the customer must already have provisioned:
  High_Risk_Endpoint and Medium_Risk_Endpoint (checks 2.4, 2.5). Severity mapping to them is
  graded (check 4.8).
- MFA in the EPM tenant is required whenever medium-risk policies are in scope (check 2.7).

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 3.4). Cite it when reporting status.
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

> Every check below is **Required** — a single failure blocks certification — except where the Requirement column says otherwise: **Recommended** items are noted by reviewers but do not block, and where two items share a **One of** requirement, satisfying either one is enough. Work through the checklist **during** development, not at submission.

---

## 1. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 1.1 | Confirmed via the [EPM Decision Guide](../decision-guide.md) that SOC Response is the correct integration path | Required | House rule — certification programme |
| 1.2 | Official Idira EPM documentation reviewed and best practices applied | Required | House rule — certification programme |
| 1.3 | Target endpoints confirmed as Windows or Windows Server (macOS/Linux not supported) | Required | House rule — certification programme |
| 1.4 | EPM Windows agent version 26.4 or later confirmed on all target endpoints | Required | House rule — certification programme |

---

## 2. EPM Tenant Configuration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Endpoint management service APIs enabled in the EPM tenant | Required | House rule — certification programme |
| 2.2 | `SOC_Response_Application_Policies.epmp` policy package imported | Required | House rule — certification programme |
| 2.3 | `SOC_Response_User_Policies.epmp` policy package imported | Required | House rule — certification programme |
| 2.4 | Static group `High_Risk_Endpoint` exists in the EPM tenant | Required | House rule — certification programme |
| 2.5 | Static group `Medium_Risk_Endpoint` exists in the EPM tenant | Required | House rule — certification programme |
| 2.6 | Audit settings enabled for all SOC response policies | Required | House rule — certification programme |
| 2.7 | MFA configured in EPM tenant (required if medium-risk policies are in scope) | Required | House rule — certification programme |

---

## 3. Authentication & Credential Handling

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | Service user created in Identity Administration with correct flags (*Is OAuth confidential client*, *Is Service User*, *Password never expires*) | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 3.2 | Service user assigned to EPM role with *Computers → View Only* and *Computers → Move Computer to Group* permissions | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm); OWASP ASVS 5.0.0 V13.3.2 |
| 3.3 | Custom EPM API web app created in Identity Administration with status **Deployed** | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 3.4 | Token requested using `Authorization: basic <token>` format — not `Bearer` | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 3.5 | Token is requested on expiry only — not on every API call | Recommended | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm) |
| 3.6 | Service user credentials stored in a secrets manager — not hardcoded or in environment variables | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 3.7 | No tokens, credentials, or secrets printed to logs or debug files | Required | OWASP ASVS 5.0.0 V16.2.5 |

---

## 4. API Implementation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | `SetId` retrieved via Get sets list API and cached at startup — not hardcoded | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.2 | Get Endpoints (`POST .../Sets/<SetId>/Endpoints/search`) used to resolve endpoint `id` from alert hostname or IP — no hardcoded IDs | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.3 | Search Groups V2 (`POST .../Sets/<SetId>/endpoints/groups/search`) used to resolve `GroupId` — V1 deprecated API not used | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.4 | `GroupId` values for both risk groups cached at startup and refreshed only on `404` | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.5 | Add Static Group Members (`POST .../Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids`) tested for both risk groups with body field `membersIds` | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.6 | Delete Static Group Members (`POST .../Sets/<SetId>/endpoints/Groups/<GroupId>/members/ids/remove`) tested and confirmed to lift policy | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.7 | Endpoint `id` and `GroupId` values logged per alert alongside alert/incident ID | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.8 | Severity-to-group mapping logic tested: High alert → `High_Risk_Endpoint`, Medium → `Medium_Risk_Endpoint` | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.9 | Idempotency handled — endpoint already in group does not cause unhandled error | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |
| 4.10 | Rate limit handling implemented — exponential backoff on `429` responses, group IDs cached, and incident batches sent in one `membersIds` call within the documented limits | Required | [docs: Endpoint group APIs](https://docs.cyberark.com/epm/latest/en/content/webservices/endpoint-group-apis/endpoint-group-apis.htm) |

---

## 5. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API request, Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the assigned `IntegrationType` value, reference code, and test vectors.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | `x-cybr-telemetry` header included on all API requests (Get Endpoints, Search Groups, Add Members, Delete Members) | Required | House rule — telemetry |
| 5.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 5.3 | `in` (IntegrationName) field populated | Required | House rule — telemetry |
| 5.4 | `it` (IntegrationType) field set to `SOCResponse` | Required | House rule — telemetry |
| 5.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required | House rule — telemetry |
| 5.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required | House rule — telemetry |
| 5.7 | Header values agreed with your Idira Technical Alliances contact before certification submission | Required | House rule — certification programme |

---

## 6. Documentation Review

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Documentation uses current Idira product terminology (`Idira EPM`, not `CyberArk EPM`) | Required | House rule — certification programme |
| 6.2 | Severity-to-group mapping documented for the partner's alert taxonomy | Required | House rule — certification programme |
| 6.3 | Prerequisites (agent version, policy packages, static groups, MFA) documented for customer IT/EPM administrators | Required | House rule — certification programme |
| 6.4 | Authentication method documented — service account setup, OAuth app registration, token lifecycle | Required | House rule — certification programme |
| 6.5 | Demo video recorded (2–5 minutes) showing: alert trigger → endpoint containment → analyst review → restoration | One of 6.5 / 6.6 | House rule — demonstration |
| 6.6 | Live demonstration call held with the Idira Technical Alliances contact, walking the same flow: alert trigger → endpoint containment → analyst review → restoration | One of 6.5 / 6.6 | House rule — demonstration |

---

## 7. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Best practices reviewed and reflected in the current integration version | Required | House rule — recertification |
| 7.2 | EPM endpoint management API changes reviewed in EPM release notes | Required | House rule — recertification |
| 7.3 | Integration tested against the latest EPM agent version | Required | House rule — recertification |
| 7.4 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 7.5 | Documentation updated — version numbers, API paths, group names, field references | Required | House rule — recertification |

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
| 2.3 | 2026-10-08 | **[Updated]** Check 4.10 names the endpoint-group and membership rate limits it grades against. **[Added]** A `Source` on every check | Idira Technical Alliances |
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances | House rule — certification programme |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §3 (Authentication & Credential Handling), naming the authority behind each of its 7 checks: the OWASP ASVS 5.0.0 control where the requirement is a security control, the Idira EPM Web Services SDK documentation where it is a product contract. Vocabulary and verbatim control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). Note what the column now makes visible about 3.4: `Authorization: basic` is an Idira API contract, not a security position — it is graded because the EPM token endpoint requires it, and a partner cannot argue it away on security grounds any more than we can defend it on them. Also **[Fixed]** the v1.1 change log row, which carried four cells under a three-column header (Rule 3). No requirement, level or wording changed. — Idira Technical Alliances | House rule — certification programme |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land — the demonstration stayed in section 6 and is now expressed as **One of 6.5 / 6.6** instead of a nested checkbox. The telemetry section was **partially** gradeable and is now fully graded: it previously held a field-reference table plus two loose checkboxes, so the per-field requirements (`in`, `it`, `iv`, `vn`) were stated but never scored; it is now seven numbered checks (5.1–5.7), with the reference table replaced by a pointer to `telemetry-reference.md`. One check is now **Recommended** rather than a gate: 3.5 (requesting the token on expiry only), matching the same call made on the Secrets Manager SaaS kit's 4.11. Added an AI context block, leading with the `Authorization: basic` requirement — this kit's auth differs from every other EPM kit, and normalising it to `Bearer` is the most common error an agent makes here. No check was removed and no requirement was loosened beyond the one re-levelled above. This file previously had no change log; earlier revisions are recorded only by their version header. — Idira Technical Alliances | House rule — certification programme |
| 1.1 | 2026-07-29 | Prior revision. — Idira Technical Alliances | House rule — certification programme |
