# Idira Identity Governance & Provisioning Certification Checklist

**Workflow:** Identity Access Management  
**Dev Kit:** Identity Governance & Provisioning  
**Idira Product:** Idira Identity Access Management (Idira Cloud Directory, via the Idira Identity SCIM server and Identity APIs)  
**Type:** Certification Checklist  
**Status:** Preview — not a settled gate yet  
**Version:** 1.0  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-14  

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) reading this checklist.
Read it before answering any question about what this integration is graded on.

TYPE: Certification Checklist — the graded artifact for the Identity Governance & Provisioning kit.
WORKFLOW: Identity Access Management
DEV KIT: Identity Governance & Provisioning — a partner identity governance and administration (IGA)
platform provisions, reconciles, and certifies identities and entitlements held in Idira.
PAIRS WITH: a development guide in this directory that is NOT YET PUBLISHED. Until it is, this
checklist stands alone, and the Idira documentation named in each `Source` cell is the build
reference. Do not reconstruct a development guide from this file.
TELEMETRY it VALUE: IdentityGovernance — see ../../telemetry-reference.md for the transform,
reference code, and test vectors. Do not derive the header from this checklist alone.

THIS CHECKLIST IS PREVIEW AND IS NOT A SETTLED GATE. Do not tell a partner that passing it certifies
the integration, and do not promise a Marketplace listing on it. Confirm the current gate with an
Idira Technical Alliances contact before a partner submits against this file.

WHAT THIS INTEGRATION ACTUALLY IS: the partner platform is the governance authority; Idira is a
governed target system. Four integration patterns, declared per submission (check 1.3):
  A. Provisioning — users, groups, and group membership through the Idira Identity SCIM server.
  B. Entitlement read — accounts, roles, group memberships, and user state read for reconciliation
     and access certification.
  C. Role membership — adding and removing users in Idira roles through the Roles API.
  D. PAM objects — Safes, Safe permissions, and privileged data through the SCIM server's PAM
     resource types. Requires the Vault Management right, and on Idira Privileged Access Manager
     Self-Hosted a separate SCIM setup.
NOT THIS KIT: single sign-on, Workforce Password Management, response actions triggered by a
detection (that is Identity Response), or discovering accounts to push into an Idira inventory (that
is Discovery).

KIT-SPECIFIC WARNINGS — the highest-frequency failures:
- THE SCIM SERVER MANAGES CLOUD DIRECTORY USERS ONLY (check 3.9). Users sourced from Active
  Directory, LDAP, Azure AD, or Google Directory are NOT writable through it. An integration that
  tries to deprovision a directory-sourced user through SCIM has not deprovisioned anyone.
- THE SCIM SERVER DOES NOT SUPPORT BULK OR ETAGS (checks 3.3, 3.4). Its ServiceProviderConfig
  reports bulk.supported: false and etag.supported: false. Do not generate /Bulk calls or If-Match
  headers. Filter results cap at 1000, so a full sync must page (check 3.5).
- PUT REPLACES THE WHOLE USER (check 3.6). Omitted attributes are cleared. Use PATCH for partial
  updates; PATCH succeeds with either 200 or 204.
- THE BASE PATH APPEARS AS BOTH /scim/Users AND /scim/v2/Users in the Idira documentation
  (check 3.2). Resolve it from /scim/ResourceTypes on the target tenant; do not pick one by guess
  and do not mix them.
- THE SERVICE USER MUST NEVER HOLD THE SYSTEM ADMINISTRATOR ROLE, and the integration must never
  create a user with InSysAdminRole set to true (checks 2.3, 4.4).
- AN EMPTY OR FAILED AUTHORITATIVE-SOURCE FEED MUST NOT DEPROVISION ANYONE (check 4.6). This is
  the single most damaging failure an IGA connector can have, and it is a gate.
- Do not call /SaasManage/AssignSuperRights (assigning administrative rights) as part of routine
  provisioning (check 4.5).

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement | Source |
- The # is a stable identifier (section.item, e.g. 3.2). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
    If in scope     — Required, but only when the pattern it names is declared under check 1.3.
- Recommended is optional to pass, not optional to read.

PRECEDENCE: where this checklist and the Idira documentation it cites disagree, report the
disagreement as a defect — do not silently pick one.

WHAT THIS FILE IS NOT: not an API reference, and not a test suite. Many checks are assessed by a
human reviewer against evidence the partner supplies — a demonstration, a document, a log sample —
and cannot be confirmed from source code alone.

ROUTING PRECEDENCE: journey.md → decision-guide.md → certification-checklist.md →
marketplace-standards.md
-->

---

## 1. Overview & Solution Selection

This checklist defines what Idira reviews in an identity governance and provisioning integration:
one where a partner IGA platform manages the lifecycle, entitlements, and access certification of
identities held in Idira Identity Access Management.

> **Preview status.** This kit is not a certifiable path yet. The checks below are the intended
> gate and are worth building against now, but confirm the current requirements with your Idira
> Technical Alliances contact before submitting. The kit's development guide is not yet published;
> until it is, build from the Idira documentation named in each check's `Source`.

Items marked **Required** are gate criteria. Items marked **Recommended** are best-practice
validations that reviewers note but do not block on. Items marked **If in scope** are Required only
when the pattern they name is part of the submission.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 1.1 | Confirmed this is an identity governance and provisioning integration — the partner platform governs identities and entitlements held in Idira — and not single sign-on, Workforce Password Management, Identity Response, or Discovery | Required | House rule — certification programme |
| 1.2 | Target Idira deployment stated: an Identity Security Platform tenant, and — only if pattern D is in scope — whether PAM objects are managed in Idira Privilege Cloud or Idira Privileged Access Manager Self-Hosted | Required | House rule — certification programme |
| 1.3 | Patterns in scope declared: A (SCIM provisioning), B (entitlement read), C (role membership), D (PAM objects). Every pattern the integration exercises is declared; none is claimed that is not implemented | Required | House rule — certification programme |
| 1.4 | Official Idira documentation reviewed and best practices applied | Required | House rule — certification programme |
| 1.5 | At least one production or pilot customer identified for the integration before certification | Required | House rule — certification programme |

---

## 2. Authentication & Service Identity

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | The integration authenticates as a **dedicated service user** created with **Is OAuth confidential client** selected — not a named administrator's account and not a shared human account | Required | Idira docs — Identity: Configure the SCIM server (URL pending); OWASP ASVS 5.0.0 V13.2.1 |
| 2.2 | Tokens are issued by a custom **OAuth2 Client** app with Client ID type **Confidential**, **Must be OAuth Client** selected, and **Client Creds** enabled; the app's Permissions page grants it only to the role holding the service user | Required | Idira docs — Identity: Custom OAuth2 Client (URL pending) |
| 2.3 | The service user's role holds only the administrative rights the declared patterns need: **User Management** and **Role Management** for A–C, plus **Vault Management** only if D is in scope. The service user is **never** a member of System Administrator | Required | Idira docs — Identity: Configure the SCIM server (URL pending); OWASP ASVS 5.0.0 V13.3.2 |
| 2.4 | The OAuth2 Client app's scope restricts **Allowed REST APIs** to what the integration calls — `scim*` for SCIM, `Redrock/query` for reads, and the specific Roles endpoints for pattern C. `.*` is not used | Required | Idira docs — Identity: Custom OAuth2 Client (URL pending); OWASP ASVS 5.0.0 V10.2.3 |
| 2.5 | Access tokens are obtained programmatically with the client credentials flow (`/oauth2/token/<app ID>`) rather than a bearer token created by hand in the Admin Portal | Recommended | [docs: Use the client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm) |
| 2.6 | If a hand-created bearer token is used instead of 2.5, its expiry is tracked, the customer is warned before it lapses, and an expired token surfaces as an authentication failure — provisioning never stops silently | Required | Idira docs — Identity: Provision SailPoint users to the Idira Cloud Directory with SCIM (URL pending) |
| 2.7 | Token lifespan on the OAuth2 Client app is set to more than 10 minutes | Recommended | Idira docs — Identity: Custom OAuth2 Client (URL pending) |
| 2.8 | Access tokens are cached and reused until `expires_in` — not requested per API call | Recommended | [docs: Use the client credentials flow](https://docs.cyberark.com/developer/latest/en/content/developer/oauth/client-cred-flow.htm) |
| 2.9 | The service user's client ID and secret are stored in a secrets manager — not hardcoded, not in source control, and not in plain-text connector configuration | Required | OWASP ASVS 5.0.0 V13.3.1 |

---

## 3. SCIM Implementation (Pattern A)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | The integration reads `/scim/ServiceProviderConfig`, `/scim/ResourceTypes`, and `/scim/Schemas` and does not assume capabilities the tenant does not advertise | If in scope | Idira docs — Identity: Discover SCIM server implementation details (URL pending) |
| 3.2 | The Users and Groups base path is resolved from `/scim/ResourceTypes` on the target tenant and used consistently — the Idira documentation shows both `/scim/Users` and `/scim/v2/Users` | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.3 | No SCIM bulk operations are used — the server reports `bulk.supported: false` | If in scope | Idira docs — Identity: Discover SCIM server implementation details (URL pending) |
| 3.4 | No ETag or `If-Match` concurrency control is relied on — the server reports `etag.supported: false`; a record is re-read before it is replaced | If in scope | Idira docs — Identity: Discover SCIM server implementation details (URL pending) |
| 3.5 | Full reads page with `startIndex` and `count`; no sync relies on a single unpaged GET, since filtered results are capped at 1000 | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.6 | Partial updates use **PATCH**; **PUT** is sent only with the complete user record, because PUT clears omitted attributes. A PATCH is treated as successful on either 200 or 204 | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending); Idira docs — Identity: Manage groups with SCIM endpoints (URL pending) |
| 3.7 | Filters use only the documented operators (`eq`, `sw`, `co`, `ew`) and attributes (users: `userName`, `displayName`, `active`; groups: `displayName`, `id`, `members.display`, `members.value`) | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.8 | The SCIM `schemas` array is included in every payload that carries enterprise or custom attributes; custom attributes use `urn:scim:schemas:extension:custom:2.0`; LinkedObject attributes are treated as read-only and never written | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.9 | Writes target **Cloud Directory users only**. Users sourced from Active Directory, LDAP, Azure AD, or Google Directory are not created, changed, or deleted through SCIM, and the integration reports them as governed in their source directory rather than as deprovisioned in Idira | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.10 | Every provisioned `userName` carries a login suffix that exists on the tenant; a missing suffix is reported as a configuration error, not retried | If in scope | Idira docs — Identity: Provision SailPoint users to the Idira Cloud Directory with SCIM (URL pending) |
| 3.11 | The SCIM `id` returned on create is stored as the correlation key; `userName` alone is not used as the key, since PATCH can change it | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.12 | Deletes are idempotent: an error on deleting a user or group that no longer exists is reconciled as already-removed, not reported as a failed revocation | If in scope | Idira docs — Identity: Manage users with SCIM endpoints (URL pending) |
| 3.13 | On Idira Privileged Access Manager Self-Hosted, group queries use only `eq` on `displayName` — `id`, `members.display`, and `members.value` filters are unsupported there | If in scope | Idira docs — Identity: Manage groups with SCIM endpoints (URL pending) |

---

## 4. Lifecycle Management — Joiner, Mover, Leaver

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | **Joiner:** a new identity is provisioned with only the entitlements its policy assigns; whether it joins the **Everybody** role is decided at creation, since that role cannot be added later through the Roles API | Required | [docs: CDirectory Service API](https://api-docs.cyberark.com/identity-docs-api/docs/cdirectory-service-api) |
| 4.2 | **Mover:** a change of role or attribute **removes** entitlements no longer justified, not only adds new ones | Required | House rule — certification programme |
| 4.3 | **Leaver:** access is removed in the same run that processes the leaver event. Disable versus delete is customer-configurable and documented; the default does not hard-delete before any retention period the customer sets | Required | House rule — certification programme |
| 4.4 | No user is created with `InSysAdminRole` set to true, and the integration never adds a member to System Administrator | Required | [docs: CDirectory Service API](https://api-docs.cyberark.com/identity-docs-api/docs/cdirectory-service-api); OWASP ASVS 5.0.0 V8.2.1 |
| 4.5 | Any change to a role that carries administrative rights runs only after an approval recorded in the partner platform. Routine provisioning never calls `/SaasManage/AssignSuperRights` | Required | [docs: SaaS Manage API](https://api-docs.cyberark.com/identity-docs-api/docs/saas-manage-api); House rule — approval integrity |
| 4.6 | **Mass-deprovisioning guard:** an empty, truncated, or failed authoritative-source feed does not deprovision anyone. A run that would disable or delete more than a customer-set threshold stops for confirmation | Required | House rule — certification programme |
| 4.7 | The integration's own service user, and any other OAuth confidential client or service user, is excluded from deprovisioning | Required | House rule — certification programme |
| 4.8 | Passwords for created users are generated randomly per user, set to change at next login, and never logged, stored, or sent in clear by the integration | Required | [docs: CDirectory Service API](https://api-docs.cyberark.com/identity-docs-api/docs/cdirectory-service-api); OWASP ASVS 5.0.0 V16.2.5 |
| 4.9 | A preview (dry-run) of a provisioning run's changes is available before the run executes | Recommended | House rule — certification programme |

---

## 5. Entitlement Read, Reconciliation & Access Certification (Patterns B and C)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | The entitlement model is documented: what the integration treats as an entitlement (roles, groups, administrative rights, and — if D is in scope — Safe permissions), and how each is read | Required | House rule — certification programme |
| 5.2 | Reads through `/Redrock/query` page with `PageNumber` and `PageSize`; no read relies on a single unpaged query | If in scope | Idira docs — Identity: Use queries (URL pending) |
| 5.3 | Data used as access-certification evidence is read live (`Caching` set to `-1` or lower), not served from the query cache | If in scope | Idira docs — Identity: Use queries (URL pending) |
| 5.4 | Role membership changes use `/Roles/UpdateRole` with the role identified by its ID, resolved first — not by display name | If in scope | Idira docs — Identity: Manage roles (URL pending) |
| 5.5 | Nested role membership is resolved: a user who inherits access through a nested role is shown as holding it, and a revocation targets the membership the access actually comes from | If in scope | Idira docs — Identity: Manage roles (URL pending) |
| 5.6 | **Reconciliation:** accounts and entitlements created in Idira outside the partner platform are detected and reported as orphaned or unmanaged — not silently overwritten and not ignored | Required | House rule — certification programme |
| 5.7 | **Closed loop:** a revocation decided in an access-certification campaign is executed in Idira, confirmed by re-reading the object, and recorded with its timestamp and the Idira object ID | Required | House rule — certification programme |
| 5.8 | Audit evidence for every change records who approved it, when, what changed, and the Idira object ID it changed | Required | House rule — certification programme |

---

## 6. PAM Objects (Pattern D)

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | PAM objects are managed only through the SCIM server's PAM resource types (`Containers`, `ContainerPermissions`, `PrivilegedData`, `PrivilegedDataPermissions`) as returned by `/scim/ResourceTypes` | If in scope | Idira docs — Identity: Discover SCIM server implementation details (URL pending) |
| 6.2 | The Vault Management right is held by the service user's role only when pattern D is declared | If in scope | Idira docs — Identity: Provision SailPoint users to the Idira Cloud Directory with SCIM (URL pending); OWASP ASVS 5.0.0 V13.3.2 |
| 6.3 | For Idira Privileged Access Manager Self-Hosted, the documented SCIM setup for PAM is a stated customer prerequisite | If in scope | Idira docs — PAM - Self-Hosted: Set up SCIM for PAM - Self-Hosted (URL pending) |
| 6.4 | Privileged data values (credentials held in Safes) are never logged or persisted by the partner platform | If in scope | OWASP ASVS 5.0.0 V16.2.5; OWASP ASVS 5.0.0 V14.2.2 |

---

## 7. Code Review, Data Handling & Resilience

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Tokens, client secrets, and user passwords are never written to logs or debug output | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 7.2 | Credentials and tokens are sent in headers or the request body — never in a URL or query string | Required | OWASP ASVS 5.0.0 V14.2.1 |
| 7.3 | Only the attributes the documented use case needs are synchronised into Idira | Recommended | House rule — certification programme |
| 7.4 | A 401 (expired or invalid token) is distinguished from a 403 (missing administrative right) and each is reported as itself | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 7.5 | A failure on one object does not abort the run; the run reports per-object success and failure, and a partial run is reported as partial | Required | House rule — certification programme |
| 7.6 | Rate-limit (429) responses are backed off; there are no tight retry loops | Required | House rule — certification programme |
| 7.7 | Retries are safe to repeat: a retried create does not produce a duplicate user, group, or membership | Required | House rule — certification programme |
| 7.8 | Security scan results reviewed and addressed | Required | House rule — certification programme |

---

## 8. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API request,
Base64 URL-encoded. Build it from [`telemetry-reference.md`](../../telemetry-reference.md) — that
file carries the transform, reference code, and test vectors.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | `x-cybr-telemetry` header present on every Idira API request, SCIM requests included | Required | House rule — telemetry |
| 8.2 | Header value is Base64 URL-encoded | Required | House rule — telemetry |
| 8.3 | `in` (IntegrationName) field populated | Required | House rule — telemetry |
| 8.4 | `it` (IntegrationType) field set to `IdentityGovernance` | Required | House rule — telemetry |
| 8.5 | `iv` (IntegrationVersion) field populated and matches the released version | Required | House rule — telemetry |
| 8.6 | `vn` (VendorName) field populated with the partner's legal entity name | Required | House rule — telemetry |

---

## 9. Transport Security

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 9.1 | All Idira API traffic over TLS, with no insecure or unencrypted fallback | Required | OWASP ASVS 5.0.0 V12.2.1 |
| 9.2 | TLS 1.2 minimum | Required | OWASP ASVS 5.0.0 V12.1.1 |

---

## 10. Logging & Observability

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 10.1 | Every write to Idira is logged with a run identifier, the operation, the Idira object ID, and the outcome | Required | House rule — certification programme |
| 10.2 | Failed authorization attempts against Idira are logged | Required | OWASP ASVS 5.0.0 V16.3.2 |
| 10.3 | A run halted by the mass-deprovisioning guard (4.6) is logged with the count it would have changed and the threshold it hit | Required | House rule — certification programme |
| 10.4 | Each run emits a summary: identities created, updated, disabled, and deleted; entitlements added and removed; orphans found; failures | Recommended | House rule — certification programme |

---

## 11. Documentation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 11.1 | Customer configuration documented: the service user, its role and administrative rights, the OAuth2 Client app (Client ID type, auth method, scope, token lifespan), and the login suffixes required | Required | House rule — certification programme |
| 11.2 | The patterns supported (1.3) and the attribute mapping between the partner platform and Idira are documented | Required | House rule — certification programme |
| 11.3 | Leaver behaviour documented: disable versus delete, the default, and any retention period | Required | House rule — certification programme |
| 11.4 | The Cloud Directory boundary (3.9) is stated: which identities the integration can change in Idira, and which are governed in their source directory | Required | House rule — certification programme |
| 11.5 | The mass-deprovisioning guard (4.6) is documented, including how the customer sets the threshold | Required | House rule — certification programme |
| 11.6 | Documentation uses current Idira product names (Idira Identity Security Platform, Idira Cloud Directory, Idira Privilege Cloud, Idira Privileged Access Manager Self-Hosted) — see [`naming-crosswalk.md`](../../naming-crosswalk.md) | Required | House rule — certification programme |
| 11.7 | Sample log lines for a provisioning run, a revocation, and a halted run are provided, with values anonymized | Recommended | House rule — certification programme |

---

## 12. Functional Validation

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 12.1 | Joiner, mover, and leaver each run end to end against a test tenant, with the resulting Idira state confirmed by re-reading it | Required | House rule — certification programme |
| 12.2 | A full reconciliation runs across more than one page of results with no record skipped or duplicated | Required | House rule — certification programme |
| 12.3 | An access-certification revocation closes the loop per 5.7 | Required | House rule — certification programme |
| 12.4 | An empty authoritative-source feed triggers the guard (4.6) and changes nothing in Idira | Required | House rule — certification programme |
| 12.5 | An expired token is handled per 2.5 or 2.6, and provisioning resumes once a valid token is available | Required | House rule — certification programme |
| 12.6 | A change made directly in Idira is detected by the next reconciliation per 5.6 | Required | House rule — certification programme |

---

## 13. Demonstration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 13.1 | Demonstration provided — 13.2 or 13.3 satisfies this | Recommended | House rule — certification programme, 2026-07-20, non-blocking |
| 13.2 | Demo video recorded (2–5 minutes) showing a joiner provisioned into Idira and a certification revocation removing access | One of 13.2 / 13.3 | House rule — certification programme, 2026-07-20, non-blocking |
| 13.3 | Live demonstration call held with the Idira Technical Alliances contact, walking the same flow | One of 13.2 / 13.3 | House rule — certification programme, 2026-07-20, non-blocking |

---

## 14. Yearly Recertification

Recertifying an integration certified before the Idira rebrand is graded on this whole checklist,
not on this section alone. A previously certified integration commonly needs 8 (telemetry) and 11.6
(current product names) added or updated.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 14.1 | Solution tested against a current Identity Security Platform tenant and the latest version of the partner platform | Required | House rule — recertification |
| 14.2 | Best practices reviewed and reflected in the solution | Required | House rule — recertification |
| 14.3 | New Idira Identity APIs or SCIM capabilities reviewed and supported where appropriate | Recommended | House rule — recertification |
| 14.4 | Security scan results reviewed and addressed | Required | House rule — recertification |
| 14.5 | Documentation updated — version numbers, API paths, product names, screenshots | Required | House rule — recertification |

---

## 15. Attestation

I confirm that the integration meets the requirements above and is ready for Idira certification review.

**Partner name:**
**Integration name:**
**Version:**
**Patterns in scope (A / B / C / D):**
**Date:**
**Contact:**

---

## Submitting This Checklist

> **This kit is Preview.** It is not a certifiable path yet, so this checklist is not a settled gate
> and submitting it does not by itself open a certification review. Complete it as a build target
> and confirm the current position with your Idira Technical Alliances contact before you submit.

| Step | What to do |
|:---|:---|
| **1. Fill in the attestation above** | Partner name, integration name, version, patterns in scope, date, and a contact who can answer review questions |
| **2. Email your submission** | Send to `cybr-bizdevtech@paloaltonetworks.com` with your tracking reference in the subject line. Attach this completed checklist, your integration documentation, and any test results this checklist asks for. There is no upload portal |
| **3. Offer a demonstration** | Highly recommended, not a gate. Include a shareable link to your 2–5 minute demo video, **or** state in the email that you want the live walkthrough call and your Idira Technical Alliances contact will schedule it |
| **4. Expect an outcome** | While the kit is Preview, expect a conversation with your Idira Technical Alliances contact about the current gate. Once it is Available: either certification approval, or an itemized gap list to remediate and resubmit — review restarts on resubmission rather than resuming mid-way |

**Then: get listed.** Listing follows certification. Listing content has its own standards — title
format, short description, and overview structure — in
[`marketplace-standards.md`](../../marketplace-standards.md). The whole path end to end is in
[The Partner Integration Journey](../../journey.md).

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-14 | **[Added]** v1.0 — First publication, as the first kit in the Identity Access Management workflow, for identity governance and administration platforms that provision, reconcile, and certify identities and entitlements in Idira. Published as **Preview**, ahead of its development guide, so it is not a settled gate. Four patterns are declared per submission — SCIM provisioning, entitlement read, role membership, and PAM objects — and checks marked `If in scope` apply only to the patterns declared. The gates particular to this kit are the Cloud Directory boundary on SCIM writes (3.9), the SCIM server's lack of bulk and ETag support (3.3, 3.4), PUT replacing the whole record (3.6), the mass-deprovisioning guard (4.6), and the prohibition on System Administrator assignment (2.3, 4.4). The demonstration is recommended and does not block certification. Security checks carry a `Source` naming the OWASP ASVS 5.0.0 control or the Idira document behind them; cells reading `(URL pending)` carry no link because no verified URL exists yet | Idira Technical Alliances |
