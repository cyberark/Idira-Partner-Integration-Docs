# Security Baseline — Requirement Sources and OWASP ASVS Mapping

**Type:** Cross-Cutting Reference
**Version:** 1.1
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-01

---

<!--
## AI CONTEXT BLOCK
This is the NORMATIVE reference for the `Source` column on every certification checklist's graded
table, and for which OWASP ASVS control backs a security requirement. Read it before filling a
`Source` cell or defending a security finding to a partner.

PURPOSE: a certification checklist grades a partner against requirements. Until 2026-10-01 no
checklist recorded where any requirement came from — verified by word-boundary grep across all 15:
zero citations of NIST, OWASP, CIS, ISO 27001, CVSS, SP 800 or ASVS. So a security gate and an
internal policy preference were indistinguishable on the page, and a partner pushing back on either
got the same unsourced answer. The `Source` column fixes that; this file is the controlled
vocabulary for it.

DECISION LOGIC: one source per check, and the order is not a preference — it is precedence.
An Idira public doc wins wherever one exists. An ASVS control is the fallback for a SECURITY
requirement no Idira doc covers. "House rule" is the honest label for everything else. Never promote
a house rule to a doc citation or an ASVS control to make a requirement sound firmer.

DO NOT cite an ASVS control from memory. ASVS 5.0.0 RENUMBERED the 4.0.x chapters — logging moved
from V7 to V16, and V1 changed meaning entirely. A 4.0.x control ID cited against 5.0.0 points at
the wrong requirement. Section 2 carries verbatim text for exactly the controls this corpus uses;
anything outside it must be read from the published standard before it is cited.

DO NOT reach for ASVS where the requirement is not actually a security control. Section 3 is the
list of checks that LOOK security-shaped and have no ASVS basis — telemetry, token-expiry handling,
retry/backoff, demonstration. Mislabelling one of those as a security control is the specific
failure this file exists to prevent.

ROUTING PRECEDENCE: journey.md -> decision-guide.md -> workflow decision-guide.md ->
development-guide.md -> certification-checklist.md -> marketplace-standards.md. This file is
cross-cutting: it is referenced FROM stage 3 (build) and graded AT stage 4 (certification).
-->

---

> **What this is.** Every graded row in a `certification-checklist.md` carries a **`Source`** cell
> naming the authority behind the requirement. This file defines the three allowed shapes and maps
> the corpus's security requirements to the OWASP ASVS controls that back them.
>
> Partners: this is why a requirement applies to you, and it is the thing to argue with if you think
> a requirement is wrong. A check sourced to an Idira doc or an ASVS control is not ours to waive. A
> check sourced to a house rule is.

---

## 1. The `Source` vocabulary

| Shape | Cell format | Use when |
|:---|:---|:---|
| **Idira public doc** | `[docs: <short label>](url)` | A documented API contract or product behaviour backs the requirement |
| **Idira public doc, link pending** | `Idira docs — <service>: <topic> (URL pending)` | Same authority, but no verified URL exists yet — see below |
| **Security framework** | `OWASP ASVS 5.0.0 V13.3.1` | It is a security requirement and no Idira public doc covers it |
| **Idira house rule** | `House rule — <decision>` | Internal policy: telemetry, demonstration, recertification, attestation, reference-customer |

One source per row. Where two genuinely apply, the Idira doc comes first and the second follows
after a `;`.

**Why the unlinked form exists, and why it is not a fourth authority.** A requirement grounded in an
Idira API contract is *not ours to waive* whether or not we have fetched its URL — collapsing it into
`House rule` would tell a partner the requirement is negotiable when it is not, which is the exact
error in the consequential direction. So it stays the doc shape, unlinked. It is a **deliberately
temporary state**: a deep documentation URL is only published here once it has been fetched and
confirmed to resolve, so an unlinked cell means the authority is known and the stable URL is not
yet. If you need the underlying document for one of these rows, ask your Idira Technical Alliances
contact rather than searching for it — a plausible-looking documentation path is often the wrong one.

**Precedence, not preference.** An Idira public doc always wins — it is what the partner built
against. ASVS is the fallback for a security requirement our own docs do not cover. `House rule` is a
complete and honest answer, not an admission of weakness; what is dishonest is dressing one up as
something else.

An empty cell means **unsourced house rule**.

---

## 2. ASVS control mapping

Pinned to **OWASP ASVS 5.0.0**. Text is verbatim from the published standard; the level column is
ASVS's own (L1/L2/L3), and is *not* an Idira requirement level — our grading level stays in the
checklist's own `Level` column.

| Requirement shape in our checklists | ASVS control | L | Verbatim control text |
|:---|:---|:---|:---|
| Credentials stored in a secrets manager / key vault; never hardcoded, never in source control or build artifacts | **V13.3.1** | L2 | "Verify that a secrets management solution, such as a key vault, is used to securely create, store, control access to, and destroy backend secrets. These could include passwords, key material, integrations with databases and third-party systems, keys and seeds for time-based tokens, other internal secrets, and API keys. Secrets must not be included in application source code or included in build artifacts." |
| Least privilege on the Idira credential / service account's scope | **V13.3.2** | L2 | "Verify that access to secret assets adheres to the principle of least privilege." |
| Machine-to-machine auth uses a service account and short-lived tokens (`client_credentials`), not a static API key or shared privileged account | **V13.2.1** | L2 | "Verify that communications between backend application components that don't support the application's standard user session mechanism, including APIs, middleware, and data layers, are authenticated. Authentication must use individual service accounts, short-term tokens, or certificate-based authentication and not unchanging credentials such as passwords, API keys, or shared accounts with privileged access." |
| Secrets, tokens and credential values never written to logs or debug output | **V16.2.5** | L2 | "Verify that when logging sensitive data, the application enforces logging based on the data's protection level. For example, it may not be allowed to log certain data, such as credentials or payment details. Other data, such as session tokens, may only be logged by being hashed or masked, either in full or partially." |
| Credentials and tokens passed in headers or the body, never in a URL or query string | **V14.2.1** | L1 | "Verify that sensitive data is only sent to the server in the HTTP message body or header fields, and that the URL and query string do not contain sensitive information, such as an API key or session token." |
| Retrieved secrets not cached beyond use; purged after use | **V14.2.2** | L2 | "Verify that the application prevents sensitive data from being cached in server components, such as load balancers and application caches, or ensures that the data is securely purged after use." |
| All Idira API traffic over TLS, no insecure fallback | **V12.2.1** | L1 | "Verify that TLS is used for all connectivity between a client and external facing, HTTP-based services, and does not fall back to insecure or unencrypted communications." |
| TLS 1.2 minimum | **V12.1.1** | L1 | "Verify that only the latest recommended versions of the TLS protocol are enabled, such as TLS 1.2 and TLS 1.3. The latest version of the TLS protocol must be the preferred option." |
| OAuth client requests only the scopes the integration needs | **V10.2.3** | L3 | "Verify that the OAuth client only requests the required scopes (or other authorization parameters) in requests to the authorization server." |
| Integration honours Idira's permission model rather than assuming broad access | **V8.2.1** | L1 | "Verify that the application ensures that function-level access is restricted to consumers with explicit permissions." |
| Failed authorization attempts logged | **V16.3.2** | L2 | "Verify that failed authorization attempts are logged. For L3, this must include logging all authorization decisions, including logging when sensitive data is accessed (without logging the sensitive data itself)." |

**V13.2.1 is the one to read twice.** It does not merely permit `client_credentials` — it rules out
"unchanging credentials such as passwords, API keys, or shared accounts with privileged access" for
exactly this class of backend-to-backend call. Where a kit grades a partner on using the OAuth
service-account flow rather than a static key, this is the control, and it is not an Idira
stylistic preference.

### Known gaps in this mapping

The eleven controls above are the ones whose text has been read. Two requirement shapes in the corpus
are **probably** ASVS controls and are deliberately **not** cited as such, because the rule against
citing a control from memory outranks the wish for a tidy mapping:

| Requirement shape | Where | Why it is not cited yet |
|:---|:---|:---|
| Approval integrity — an elevation is created only against a recorded approval, and the approved values cannot be altered between approval and action | `epm/ticketing-jit` §6 | A business-logic / time-of-check-time-of-use control. ASVS 5.0.0 **V2 Validation and Business Logic** is the likely chapter; no control text from it has been read, so those rows carry `House rule — approval integrity` instead |
| Input validation on values read from a partner platform before they are sent to an Idira API | several kits' data-quality sections | Same chapter, same reason |

Sourced as a house rule, a requirement reads as ours to waive — which **under-states** these two. That
is the safe direction to be wrong in, and it is visible here rather than buried. Closing the gap means
reading the V2 controls and promoting the cells, not relabelling them from memory.

### Version pinning

ASVS **5.0.0 renumbered the 4.0.x chapters**, so a 4.0.x control ID cited against 5.0.0 points at a
different requirement: logging moved from V7 to V16, and V1 went from "Architecture, Design and
Threat Modeling" to "Encoding and Sanitization". Cite the version in the cell (`OWASP ASVS 5.0.0
V13.3.1`) and never carry a bare `V7.x`-style ID forward from older material. 5.0.0 chapters: V1
Encoding and Sanitization, V2 Validation and Business Logic, V3 Web Frontend Security, V4 API and
Web Service, V5 File Handling, V6 Authentication, V7 Session Management, V8 Authorization, V9
Self-contained Tokens, V10 OAuth and OIDC, V11 Cryptography, V12 Secure Communication, V13
Configuration, V14 Data Protection, V15 Secure Coding and Architecture, V16 Security Logging and
Error Handling, V17 WebRTC.

---

## 3. Checks with no ASVS basis — do not force one

These look security-shaped and are not security controls. Sourcing them to ASVS would be a
fabricated citation, and presenting one to a partner as a security defect is wrong on the facts.

| Check | What it actually is | Correct `Source` |
|:---|:---|:---|
| `x-cybr-telemetry` header present and correctly built | Adoption / KPI measurement | `House rule — 2026-08-13 KPI decision` |
| Demonstration or demo video | Partner-enablement artifact, **non-blocking** | `House rule — certification programme, 2026-07-20, non-blocking` |
| Token-expiry handling, 401 refresh, retry and backoff, pagination, resume | API contract and resilience — correctness, not security | The Idira doc for that API |
| Yearly recertification, attestation, reference customer | Programme policy | `House rule — certification programme` |

**The demonstration row is the live example of why this file exists.** The certification programme
settled on 2026-07-20 that a demonstration is **highly recommended but not a gate**. Some checklists
in this corpus still word it as mandatory; where a checklist and this file disagree, **this file is
authoritative** and a missing demonstration must never be the reason an integration is declined. If
you are asked to treat one as blocking, raise it with your Idira Technical Alliances contact.

---

## Change Log

| Version | Date | Change | Author |
|:---|:---|:---|:---|
| 1.1 | 2026-10-01 | **[Added]** The unlinked form of the Idira-doc shape (`Idira docs — <service>: <topic> (URL pending)`), for a requirement backed by a product contract whose URL has not been fetched and confirmed. Without it the backfill had only two honest options: guess a deep URL (against a standing vault rule, and undetectable — R6 checks link shape only and never fetches) or mislabel a non-negotiable contract as a waivable house rule. | Idira Technical Alliances |
| 1.0 | 2026-10-01 | **[Added]** Initial reference: `Source` column vocabulary, OWASP ASVS 5.0.0 mapping for the corpus's eleven security requirement shapes with verbatim control text, version-pinning rule, and the list of checks that have no ASVS basis. | Idira Technical Alliances |
