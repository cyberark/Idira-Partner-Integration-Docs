# Web Connection Component — Certification Checklist

**Workflow:** PSM Connectors
**Use Case:** Web Connection Component
**Idira Product:** Idira Privileged Access Manager Self-Hosted
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
WORKFLOW: PSM Connectors
DEV KIT: Web Connection Component
IDIRA PRODUCT: Idira Privileged Access Manager Self-Hosted only (PVWA + PSM). Not SaaS.
PAIRS WITH: development-guide.md in this directory. That file states how to build the
integration; this file states what is checked. Read both.

TELEMETRY: NOT APPLICABLE TO THIS KIT. This is the single exception in the corpus. A Web
Connection Component is browser automation, not a REST client — it makes no Idira API calls, so
there is no x-cybr-telemetry header to send and none is graded. Do not add telemetry code here,
and do not copy a telemetry check in from another kit. See ../../telemetry-reference.md §3, which
records this kit as "Not applicable (no REST API)".

WHAT THIS INTEGRATION ACTUALLY IS: a recorded browser-automation script packaged as a .zip and
uploaded to PVWA. PSM launches a controlled browser on the customer's PSM server, injects vaulted
credentials into the target application's login web form, and records the session. There is no
service to write, no API to call, and no token to manage. An agent that generates an HTTP client
here has misread the kit entirely.

KIT-SPECIFIC WARNINGS:
- The login control must be CLICKED — Login / Next / Submit (check 2.1). Submitting the form with
  ENTER is called out explicitly and fails. This is the most common recording error.
- Credentials are bound as dynamic parameters: {username} / {password}, or
  {logonaccount\username} / {logonaccount\password} (check 3.1). Those literals are exact,
  backslash included. PSM substitutes the vaulted values at connect time.
- Browser and web driver versions must be IDENTICAL (check 5.3), and browser, driver and dispatcher
  bitness must match (Marketplace components default to the 32-bit dispatcher). A version-drifted
  driver is a silent connector failure.
- Success must be verified, not assumed (check 2.2). A script that types credentials and proceeds
  passes a happy-path test and fails certification.
- The operator never sees the injected password (check 3.5), and no credential may appear in the
  session recording (check 4.3) — the recording is a graded artifact, not just a log.

HOW TO READ THIS FILE:
- Every check is a row in a numbered table: | # | Check | Requirement |
- The # is a stable identifier (section.item, e.g. 3.1). Cite it when reporting status.
- Requirement is the grading level:
    Required        — gate. A single failure blocks certification.
    Recommended     — reviewers note it; it does not block.
    One of X / Y    — either item satisfies the requirement; both are not needed.
- This kit has no Recommended items. Every check is a functional, security, or platform
  requirement where a partial result is a failure rather than a style preference.

PRECEDENCE: where this checklist and development-guide.md disagree, this file governs what
is graded — and the disagreement is a defect worth reporting. Do not silently pick one.

WHAT THIS FILE IS NOT: not an API reference, and not a test suite. Many checks are assessed
by a human reviewer against evidence the partner supplies — a demonstration, a document, a
recorded session — and cannot be confirmed from a connector definition alone.

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> This checklist applies to a PSM Web Connection Component (browser-automation auto-logon and session recording). It is not a REST/API integration, so it has no telemetry-header requirement. See the [Web Connection Component Development Guide](development-guide.md).
>
> Every check below is **Required** — a single failure blocks certification — except the demonstration in section 7, where either format satisfies the requirement. Work through the checklist **during** development, not at submission.

---

## 1. Solution Selection

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 1.1 | Confirmed this is a PSM Web Connection Component use case — a web application login automated by PSM, with no Idira REST API involved | Required | House rule — certification programme |
| 1.2 | Official Idira documentation reviewed and best practices applied | Required | House rule — certification programme |
| 1.3 | Connection component is based on `PSM-WebAppSample` with a unique `Id` and `DisplayName` | Required | House rule — certification programme |
| 1.4 | Target deployment confirmed as Idira Privileged Access Manager Self-Hosted (PVWA + PSM) | Required | House rule — certification programme |

---

## 2. WebForm Robustness

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 2.1 | Login flow recorded with the Plugin Generator Utility; the login control is clicked (Login / Next / Submit), not submitted with ENTER | Required | House rule — certification programme |
| 2.2 | A validation or verification step confirms a successful login rather than assuming it | Required | House rule — certification programme |
| 2.3 | Multi-step, SSO, and conditional login screens handled with `if`/`else` blocks using `Exists` / `Count` conditions | Required | House rule — certification programme |
| 2.4 | Action timeout and Page load timeout tuned so the connector does not act before fields or pages are ready | Required | House rule — certification programme |
| 2.5 | Connector tested against a live test account, end to end, before submission | Required | House rule — certification programme |

---

## 3. Credential Handling

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 3.1 | Username and password bound to `{username}` / `{password}` (or `{logonaccount\username}` / `{logonaccount\password}`) as dynamic parameters, so PSM injects vaulted values at connect time | Required | Idira docs — PAM - Self-Hosted: connection component client-specific parameters (URL pending); OWASP ASVS 5.0.0 V13.3.1 |
| 3.2 | No credentials, tokens, or secrets are hard-coded in the connection component or recorded as static literals | Required | OWASP ASVS 5.0.0 V13.3.1 |
| 3.3 | LogonAccount capability added to Supported Capabilities when a separate logon account is required | Required | Idira docs — PAM - Self-Hosted: connection component supported capabilities (URL pending) |
| 3.4 | No credential is written to logs, screenshots, or the recorded session stream | Required | OWASP ASVS 5.0.0 V16.2.5 |
| 3.5 | The operator never sees or handles the injected password | Required | Idira docs — PAM - Self-Hosted: PSM credential injection (URL pending); OWASP ASVS 5.0.0 V13.3.2 |

---

## 4. Session Recording

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 4.1 | A test connection produces a recorded session visible in the PSM session list | Required | House rule — certification programme |
| 4.2 | The recording captures the privileged activity in the target web application | Required | House rule — certification programme |
| 4.3 | No credential values are exposed in the recording | Required | House rule — certification programme |

---

## 5. PSM Server Configuration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 5.1 | PSM server hardened for web applications (`PSMHardening.ps1 -SupportWebApplications`) | Required | [docs: Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) |
| 5.2 | AppLocker browser rules enabled (`PSMConfigureAppLocker.ps1`) | Required | [docs: Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) |
| 5.3 | Browser (Chrome 100+ or Edge 103+) and web driver versions are identical, and their bitness matches the WebAppDispatcher in use | Required | [docs: Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) |
| 5.4 | Correct WebAppDispatcher deployed — Marketplace-downloaded components default to the 32-bit dispatcher unless PVWA is switched to 64-bit; Edge dispatcher from the Idira Marketplace where required | Required | [docs: Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) |
| 5.5 | Required HTTPS certificates for the target application present on the PSM server | Required | [docs: Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) |

---

## 6. Packaging & Platform Configuration

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 6.1 | Connector packaged as a `.zip` and uploaded to PVWA | Required | House rule — certification programme |
| 6.2 | Connection component linked to the target platform — component `Id` added under UI & Workflows, Enable set to Yes | Required | House rule — certification programme |
| 6.3 | Connect tested from PVWA against a vaulted account, confirming both auto-logon and session recording | Required | House rule — certification programme |
| 6.4 | Supported PSM / PAM Self-Hosted version range documented | Required | House rule — certification programme |

---

## 7. Documentation Review

A demonstration is mandatory. Either format satisfies the requirement — you do not need both.

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 7.1 | Documentation uses current Idira product terminology (Idira Privileged Access Manager Self-Hosted; Idira Privileged Session Manager) | Required | House rule — certification programme |
| 7.2 | Required customer configuration documented (platform link, connection component Id, account/logon-account setup) | Required | House rule — certification programme |
| 7.3 | Supported browsers, driver versions, and PSM version range documented | Required | House rule — certification programme |
| 7.4 | Demo video recorded (2–5 minutes) showing auto-logon and session recording end to end | One of 7.4 / 7.5 | House rule — demonstration |
| 7.5 | Live demonstration call held with the Idira Technical Alliances contact, showing auto-logon and session recording end to end | One of 7.4 / 7.5 | House rule — demonstration |

---

## 8. Yearly Recertification

| # | Check | Requirement | Source |
|:--|:------|:------------|:-------|
| 8.1 | Login flow re-validated against the current version of the target web application | Required | House rule — recertification |
| 8.2 | Connector tested with the latest supported PSM / PAM Self-Hosted version and browser/driver versions | Required | House rule — recertification |
| 8.3 | Best practices reviewed and reflected in the connector | Required | House rule — recertification |
| 8.4 | Documentation updated — supported versions, dispatcher, platform steps | Required | House rule — recertification |

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

| Version | Date | Change |
|:---|:---|:---|
| 2.3 | 2026-10-08 | **[Fixed]** Check 5.3 no longer requires a 32-bit browser — 32- and 64-bit browsers are supported when browser, driver and dispatcher bitness match. Check 5.4 states that Marketplace-downloaded components default to the 32-bit dispatcher. **[Added]** A `Source` on every check | Idira Technical Alliances |
| 2.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances | House rule — certification programme |
| 2.1 | 2026-10-01 | **[Added]** A `Source` column on §3 (Credential Handling), naming the authority behind each of its 5 checks. Vocabulary and verbatim ASVS 5.0.0 control text: [`security-baseline-reference.md`](../../security-baseline-reference.md). This is the only kit in the corpus where the security property is delivered by the *platform* rather than by partner code: 3.1 and 3.5 are sourced to the PSM credential-injection contract first and the ASVS control second, because a partner satisfies them by binding the documented dynamic parameters and then doing nothing else — the vault, not their component, keeps the password away from the operator. Every `(URL pending)` cell is waiting on a verified deep link; the PAM - Self-Hosted connection-component pages are not yet in the vault's links index and guessing a doc URL is prohibited. Also **[Fixed]** the v1.1 change log row, which carried four cells under a three-column header (Rule 3). No requirement, level or wording changed. — Idira Technical Alliances | House rule — certification programme |
| 2.0 | 2026-09-30 | **[Restructured]** Migrated from unnumbered checkboxes to the numbered-table format the Discovery kits use: every check now has a stable `section.item` identifier and an explicit grading level. Section numbering is unchanged, so existing references still land — the demonstration stayed in section 7 rather than moving to its own section, and is now expressed as **One of 7.4 / 7.5** instead of a nested checkbox. No check was re-levelled to Recommended: every check here is a functional, security, or platform requirement where a partial result is a failure. Added an AI context block, leading with the fact that this is the corpus's one telemetry-exempt kit and that it is browser automation rather than a REST integration — the two things an agent reading it cold gets wrong. No check was removed and no requirement was loosened. — Idira Technical Alliances | House rule — certification programme |
| 1.1 | 2026-07-29 | Prior revision. — Idira Technical Alliances | House rule — certification programme |
