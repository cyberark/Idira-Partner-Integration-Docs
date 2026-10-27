# Identity Response Actions — Certification Checklist

**Workflow:** Identity Response
**Use Case:** Identity Response Actions — XDR / SIEM / SOAR partner integration
**Idira Product:** Idira Identity Security Platform
**Type:** Certification Checklist
**Version:** 2.4
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-27

### Change Log

- **[Updated]** v2.4 — Brought in line with live testing of the Identity workforce calls (2026-10-22, development guide v1.8). **[Added]** check 3.18: the resolved target is never the integration's own service account, because a `GetUserByName` call with the wrong body key returns the caller's own record with `success: true`. **[Added]** check 3.19: every Identity response is checked for `success: false`, because Identity returns HTTP 200 on failure. **[Updated]** check 3.15 drops the `409` premise, since Identity returns `success: true` on a repeated action. **[Updated]** check 3.11 drops the two now-confirmed keys (`GetUserByName` and `SignOutEverywhere`) and keeps the three still open. — Idira Technical Alliances

- **[Added]** v2.3 — A `Source` on every check: the Idira documentation page behind each API check in §3, and the certification programme for the rest. No requirement, level or wording changed. — Idira Technical Alliances
- **[Fixed]** v2.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances
- **[Added]** v2.1 — A `Source` column on §2 (Code Review & Data Handling), naming the authority behind each of its 6 checks. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). 2.4 is the row the column earns its place on: this kit spans ISPSS services and EPM, whose token formats differ, so "use the right auth model per target" is an API contract on two separate services — not a security preference a partner could satisfy by picking one. No requirement, level or wording changed. — Idira Technical Alliances
- **[Restructured]** v2.0 — Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land — the demonstration stayed in section 5 and is now expressed as **One of 5.6 / 5.7** instead of a nested checkbox. The telemetry section was **partially** gradeable and is now fully graded: it previously held a field-reference table plus two loose checkboxes, so the per-field requirements were stated but never scored; it is now seven numbered checks (4.1–4.7), with the reference table replaced by a pointer to `telemetry-reference.md`. Four checks are now **Recommended** rather than gates — 2.3 (message quality), 2.5 (token request cadence), 3.14 (reversible actions, already conditional on the playbook offering rollback), and 6.2 (adopting new actions where appropriate). Added an AI context block, leading with the two things unique to this kit: `it` is chosen from three values rather than fixed, and this is the only kit that spans four Idira services with three different auth headers. No check was removed and no requirement was loosened beyond the four re-levelled above; the `[TBD]`-resolution gate and both no-overclaim gates are unchanged. — Idira Technical Alliances
- **[Fixed]** v1.5 — Corrected the relative path on the v1.4 row's `naming-crosswalk.md` link. It was written as a bare filename from a kit subdirectory two levels below the file it targets, so it resolved to a non-existent sibling and 404'd for any partner who followed it. — Idira Technical Alliances
- **[Fixed]** v1.4 — Renamed Privilege Cloud to Idira Privileged Access Manager SaaS in prose, per the current product naming. Documented API names, role and persona names, and hostnames are deliberately unchanged and are explained in [`naming-crosswalk.md`](../../naming-crosswalk.md) §3. — Idira Technical Alliances
- **[Added]** Machine-identity actions (delete workload, delete authenticator — Secrets Manager SaaS / Conjur Cloud) to the scope-of-actions list and API implementation checks. — Idira Technical Alliances
- **[Fixed]** Solution Selection scope statement now names Secrets Manager SaaS explicitly and flags SCA/SIA-session-termination as not-yet-buildable rather than silently omitting them. — Idira Technical Alliances
- **[Added]** SCA session-revocation operations named (revoke one session, revoke all sessions for a user) with a gate requiring schema confirmation against a live tenant before certification, since the reference portal is gated. Also added "add to discovered accounts" and "get account details by ID" to the scope list. — Idira Technical Alliances

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — this is the graded artifact.
WORKFLOW: Identity Response
DEV KIT: Identity Response Actions — a partner XDR/SIEM/SOAR platform triggers response actions
in Idira.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.

TELEMETRY it VALUE — THIS KIT IS THE EXCEPTION: `it` is not a fixed per-kit constant here. The
partner picks SOAR, SIEM, or XDR to match their own platform category (check 4.4). Every other
kit in the corpus has one assigned value; do not invent "IdentityResponse". See
../../telemetry-reference.md, which records all three as valid for this kit.

WHAT THIS INTEGRATION ACTUALLY IS: outbound action execution, not data collection. The partner
platform is the trigger; Idira is acted upon. SaaS services only (check 1.2) — PAM Self-Hosted is
explicitly out of scope, so do not carry a Self-Hosted pattern in here.

THIS KIT SPANS FOUR SERVICES WITH THREE DIFFERENT AUTH HEADERS. Getting this wrong is the
highest-frequency failure:
- ISPSS shared services and PAM SaaS: Bearer token.
- EPM (endpoint containment): `Authorization: basic <token>` — see ../../epm/soc-response/.
- Secrets Manager SaaS: `Authorization: Token token="<jwt>"` from its OWN authenticate endpoint,
  never the ISPSS Bearer token (check 3.8).
Check 2.4 grades using each auth model only against its correct target.

KIT-SPECIFIC WARNINGS:
- TWO ACTIONS MUST NOT BE CLAIMED AS IMPLEMENTED. SIA in-progress session termination has no
  partner-callable API at all (check 1.6). SCA session revocation may only be claimed if the
  submitter verified the request/response schema against a live tenant, because the public
  reference is gated and was never independently verified during dev-kit authoring
  (checks 1.7, 3.10). Do not generate code for either from the operation name alone.
- THIS CHECKLIST STILL HAS UNRESOLVED [TBD] ITEMS AND RESOLVING THEM IS A GATE (check 3.11):
  the MFA step-up mechanism, the PAM SaaS session-termination permission model, and the Secrets
  Manager SaaS authenticate request shape. If you are asked for any of these, say they are
  unconfirmed — do not fill them in. The Identity body keys are CONFIRMED (guide v1.8):
  GetUserByName {"username"}, SetUserState {"ID","state"} (lowercase), SignOutEverywhere ?id= (body {"ID"} also accepted),
  ChangeUser by "ID".
- A WRONG GetUserByName KEY RETURNS THE CALLER'S OWN RECORD, NOT AN ERROR (check 3.18). Code that
  resolves a target must reject a result whose Uuid is the integration's own service account.
- IDENTITY RETURNS HTTP 200 ON FAILURE (check 3.19). Grade on the body's "success" flag, never on
  the status code alone. A repeated action returns success:true, not 409 (check 3.15).
- Session actions use `SessionGuid`, never the numeric `SessionID` (check 3.2), and
  `CanTerminate` / `CanSuspend` must be checked first, with SSH/OPM excluded from suspend
  (check 3.3).
- `ExemptUserFromMfa` must NEVER be called as a response action (check 3.12). This is an
  absolute prohibition, not a best practice.
- Delete-workload and delete-authenticator are NON-REVERSIBLE and must be gated behind a
  confirmed-compromise check, not placed in a default or low-severity response path (check 5.3).
- Retrieved credential values must never be persisted to disk or the playbook context
  (check 2.2) — the playbook context is the part people forget.
- Every action resolves its target first (check 3.1). No action takes a raw name.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 3.2). Cite it when reporting status.
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
| 1.1 | Confirmed this is an Identity Response integration: a partner XDR / SIEM / SOAR trigger runs identity, privileged-session, credential, access-policy, or machine-identity response actions in Idira | Required | House rule — certification programme |
| 1.2 | Confirmed the integration targets Idira SaaS services only (Idira Privileged Access Manager SaaS, Identity Security Platform shared services, Secrets Manager SaaS) — PAM Self-Hosted is out of scope | Required | House rule — certification programme |
| 1.3 | Official Idira documentation reviewed and best practices applied | Required | House rule — certification programme |
| 1.4 | At least one production or pilot customer identified for the integration before certification | Required | House rule — certification programme |
| 1.5 | Scope of actions in this release documented (which of: lock user, force logout, expire password, remove role, terminate/suspend session, rotate/verify credential, vault account, flag account into discovery inventory, disable SIA policy, delete workload, delete authenticator, revoke SCA session(s), contain endpoint) | Required | House rule — certification programme |
| 1.6 | Confirmed the submission does NOT claim SIA in-progress session termination as an implemented action (automatic/ITDR-triggered only — no partner-callable API exists for it) | Required | House rule — certification programme |
| 1.7 | If SCA session revocation is claimed as implemented: confirmed the submitter independently verified the exact request/response schema against a live tenant call (not just the operation name) — the public reference for this API is gated and was not independently verified during dev-kit authoring | Required | House rule — certification programme |

---

## 2. Code Review & Data Handling

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Secrets, tokens, and credentials are not written to logs or debug files | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 2.2 | Retrieved credential values (from rotate/vault flows) are never persisted to disk or the playbook context | Required | OWASP ASVS 5.0.0 V14.2.2 |
| 2.3 | User and error messaging is clear and reflects per-action success, partial success, and failure | Recommended | House rule — certification programme |
| 2.4 | Each auth model used only against its correct target (Bearer for ISPSS services, basic for EPM) | Required | [docs: EPM Web Services SDK](https://docs.cyberark.com/epm/latest/en/content/landingpages/lpdeveloper.htm); Idira docs — Identity Security Platform: service authentication (URL pending) |
| 2.5 | Access tokens requested only on expiry — not per operation call | Recommended | Idira docs — Identity Security Platform: access token lifetime (URL pending) |
| 2.6 | Security scan results reviewed and addressed | Required | House rule — certification programme |

---

## 3. API Implementation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | Target resolution implemented before every action: `GetUserByName` → user ID, `Get Accounts` → account ID, `LiveSessions` → SessionGuid, `access-policies` → policy ID | Required | [docs: Get live sessions](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/getlivesessions.htm); [docs: CDirectory Service API](https://api-docs.cyberark.com/identity-docs-api/docs/cdirectory-service-api) |
| 3.2 | Session actions use `SessionGuid`, not the numeric `SessionID` | Required | [docs: Terminate active session](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/pta-psm-terminatesession.htm) |
| 3.3 | `CanTerminate` / `CanSuspend` flags checked before issuing session actions; SSH/OPM sessions excluded from suspend | Required | [docs: Suspend/resume active session](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/suspend-resumesession.htm) |
| 3.4 | Credential rotate uses the CPM `Change` endpoint; `ChangeCredsForGroup` field name validated against the target tenant | Required | [docs: Change credentials immediately](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/change-credentials-immediately.htm) |
| 3.5 | Rotation success confirmed by reading `lastVerifiedDateTime` / `lastModifiedDateTime` after `Verify` | Required | [docs: Verify credentials](https://docs.cyberark.com/privilege-cloud-shared-services/latest/en/content/webservices/verify-credentials-v9-10.htm) |
| 3.6 | SIA policy revocation sets `status: "Disabled"` (or DELETE) and requires `DpaAdmin` | Required | [docs: SIA access policies](https://docs.cyberark.com/setup/latest/en/content/privileged-access/apis/dpa_policies.htm) |
| 3.7 | Delete-workload uses the URL-encoded `<policy-branch>/<workload-name>` identifier; delete-authenticator uses `<type>/<name>` with `<type>` one of `jwt`/`azure`/`aws_iam`/`certificate` | Required | [docs: Delete workload](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-delete-workload.htm); [docs: Delete authenticator](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-del-auth.htm) |
| 3.8 | Secrets Manager SaaS calls use `Authorization: Token token="<jwt>"` from its own authenticate endpoint — never the ISPSS Bearer token | Required | [docs: API key authentication](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/conjur_api_api-key-authn.htm) |
| 3.9 | "Add to discovered accounts" (`PUT /api/discovered-accounts/`) requires the "Privilege Cloud Discovery Source" role and includes the required `type`/`subType`/`identifiers`/`source` fields | Required | [docs: Add a discovered account](https://docs.cyberark.com/manage/latest/en/content/discovery/discovery-discoveredaccountsservice-add.htm) |
| 3.10 | If SCA session revocation is implemented, the exact request body (session ID field name, single vs. bulk) was confirmed against a live tenant call, not assumed from the operation name | Required | [docs: SCA APIs overview](https://docs.cyberark.com/manage/latest/en/content/sca/automation/apis.htm) |
| 3.11 | Remaining `[TBD]` items resolved before submission: MFA step-up mechanism, Idira Privileged Access Manager SaaS session-termination permission model, Secrets Manager SaaS authenticate request shape (workload vs. user principal) | Required | House rule — certification programme |
| 3.12 | `ExemptUserFromMfa` is never called as part of a response action | Required | House rule — certification programme |
| 3.13 | Every action returns a per-action status surfaced to the partner incident timeline | Required | House rule — certification programme |
| 3.14 | Reversible actions (unlock, resume session, re-add role) implemented and tested where the playbook offers rollback | Recommended | House rule — certification programme |
| 3.15 | Idempotency handled: repeating an action on a target already in that state (already locked, already removed) does not fail the playbook. Identity returns `success: true` for a repeat, not `409` | Required | House rule — certification programme |
| 3.16 | Destructive actions (delete SIA policy, remove role) are scoped to the target entity — no unfiltered calls | Required | House rule — certification programme |
| 3.17 | Rate-limit (429) backoff implemented; no tight retry loops | Required | House rule — certification programme |
| 3.18 | Target resolution uses `GetUserByName` with the body key `username`, and the integration refuses to act when the resolved `Uuid` is its own service account or the returned `Name` does not match the requested user — a wrong body key returns the caller's own record with `success: true` | Required | House rule — certification programme (verified live, 2026-10-22) |
| 3.19 | Every Identity API response is checked for `"success": false`; an HTTP 200 alone is never treated as a completed action | Required | House rule — certification programme |

---

## 4. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API request, Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that file carries the transform, the valid `IntegrationType` values for this kit, reference code, and test vectors.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | `x-cybr-telemetry` header included on all Idira API requests | Required | House rule — telemetry |
| 4.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 4.3 | `in` (IntegrationName) field populated and describes the partner platform | Required | House rule — telemetry |
| 4.4 | `it` (IntegrationType) field set to `SOAR`, `SIEM`, or `XDR` — whichever matches the partner platform's category | Required | House rule — telemetry |
| 4.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required | House rule — telemetry |
| 4.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required | House rule — telemetry |
| 4.7 | `in`, `it`, and `vn` values agreed with the Idira Technical Alliances contact before certification submission | Required | House rule — telemetry |

---

## 5. Documentation Review

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | Documentation uses current Idira product terminology (Idira Identity Security Platform, Idira Privileged Access Manager SaaS, Secure Infrastructure Access, Idira Secrets Manager SaaS — not DPA, not Conjur Cloud) | Required | House rule — certification programme |
| 5.2 | Required customer configuration documented: service-account rights, Safe permissions, session-monitoring rights, `DpaAdmin` role, `Authn_Admins`/`Conjur_Cloud_Admins` group membership (if machine-identity actions in scope) | Required | House rule — certification programme |
| 5.3 | Delete-workload and delete-authenticator are documented as non-reversible and gated behind a confirmed-compromise check, not included in a default/low-severity response path | Required | House rule — certification programme |
| 5.4 | Authentication documented for each service in scope, with the correct header format called out | Required | House rule — certification programme |
| 5.5 | Any platform-specific enhancement (for example, default correlation rules) documented as optional, not core | Required | House rule — certification programme |
| 5.6 | Demo video recorded (2–5 minutes) showing at least one end-to-end response action from a partner-platform trigger | One of 5.6 / 5.7 | House rule — demonstration |
| 5.7 | Live demonstration call held with the Idira Technical Alliances contact, showing at least one end-to-end response action from a partner-platform trigger | One of 5.6 / 5.7 | House rule — demonstration |

---

## 6. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Best practices reviewed and reflected in the solution | Required | House rule — recertification |
| 6.2 | New Idira response actions or APIs reviewed, tested, and supported where appropriate | Recommended | House rule — recertification |
| 6.3 | Solution tested with the latest version of the partner platform | Required | House rule — recertification |
| 6.4 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 6.5 | Documentation updated — version numbers, API paths, field references (especially any `[TBD]` items now confirmed) | Required | House rule — recertification |

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
