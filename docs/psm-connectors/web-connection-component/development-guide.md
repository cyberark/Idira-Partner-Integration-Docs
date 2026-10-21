# Idira Privileged Access Manager Self-Hosted — Web Connection Component Development Guide

**Workflow:** PSM Connectors
**Use Case:** Web Connection Component
**Idira Product:** Idira Privileged Access Manager Self-Hosted
**Type:** Development Guide
**Version:** 1.4
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-20

---

> **Not sure this is the right guide?** This is the only use case in the PSM Connectors workflow today, so no decision guide exists yet.
> Use this guide if: your product is a web application and you want Idira Privileged Session Manager (PSM) to broker, auto-inject credentials into, and record privileged sessions to it, with no Idira REST API involved.

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Privileged Access Manager Self-Hosted — Privileged Session Manager (PSM) component
WORKFLOW: PSM Connectors
USE CASE: Web Connection Component (web application auto-logon + session recording)
INTEGRATION PATTERN: PSM web connection component (browser automation) — NOT a REST/API integration.
  A packaged connection component runs on the customer's PSM server, launches a headless-driven
  Chrome or Edge browser via the WebAppDispatcher, injects vaulted credentials into the target
  application's login web form, and records the session. No Idira REST API is called.
AUTH METHOD: None from the partner side. PSM retrieves the account from the Vault and injects it
  into WebFormFields at connect time. The partner authors the form field mapping, not an auth flow.
BUILD TOOL: PSM Plugin Generator Utility (Web Connector Generator) — records the login flow and
  emits a connection component packaged as a .zip.
BASE COMPONENT: PSM-WebAppSample (all new web connection components are cloned from it).
DISPATCHER: WebAppDispatcher, 32- or 64-bit. From PSM 14.6 OUT-OF-THE-BOX components use the 64-bit
  dispatcher automatically; components downloaded from the Marketplace — which is how a partner
  connector ships — stay in the 32-bit Connector folders unless PVWA is configured to switch.
  Revert to 32-bit by pointing ClientDispatcher at {PSMComponentsFolder32}.
DEPLOY TARGET: Customer's PSM server, via upload of the connector .zip to PVWA, then linked to a platform.
SANDBOX: C3 Integrations Platform — https://c3.cyberark.cloud
CONTACT: cybr-bizdevtech@paloaltonetworks.com

KEY CONSTRAINTS:
- Chrome/Edge browser version on the PSM server and the matching web driver version MUST be identical,
  or the connection fails.
- No Idira REST API and no x-cybr-telemetry header apply to this modality — the telemetry requirement
  in the general dev-kit index is for REST integrations and does not apply here.
- Credentials are never handled by the partner. PSM injects {username}/{password} (or
  {logonaccount\username}/{logonaccount\password}) into WebFormFields at connect time.
- The connector must click the login/submit button (Login, Next, Submit) — do not rely on pressing ENTER.
- RunValidations must be Yes and a (Validation) line must follow the last (Button). With No, PSM
  skips validation and a failed login leaves the session open for the operator to sign in by hand.
- EnforceCertificateValidation must stay Yes (the default). Trust a self-signed target certificate
  on the PSM server; never ship No, which lets PSM inject credentials into an impersonated page.
- PSM must be hardened for web applications (PSMHardening.ps1 -SupportWebApplications) and AppLocker
  rules enabled before any web connector will run.

TERMINOLOGY (use these exact names in code and docs):
- CyberArk PAM Self-Hosted → Idira Privileged Access Manager Self-Hosted
- CyberArk PSM → Idira Privileged Session Manager (PSM)
- CyberArk Marketplace → Idira Marketplace

FILES IN THIS DIRECTORY:
- development-guide.md — this file — full web connection component guide
- certification-checklist.md — requirements checklist for Idira certification review
-->

---

## 1. Why This Integration Matters

Many partner products are web applications with their own login page rather than REST or SSH targets. Security teams that already run Idira Privileged Access Manager Self-Hosted want the same privileged-access controls over those web applications that they have over servers and databases: no shared passwords, no credentials visible to the operator, and a full recording of every privileged session for audit and investigation. A Web Connection Component gives them exactly that. Idira Privileged Session Manager (PSM) brokers the session, retrieves the account from the Vault, injects it into the application's login web form, and records the session, so the operator never sees or handles the credential.

**Industry drivers:**
- Privileged access controls and session recording are required by common audit and compliance frameworks (for example SOX, PCI DSS, and cyber-insurance controls), and web administration consoles are increasingly in scope.
- Enterprises are consolidating privileged access to web-based admin consoles under a single session broker rather than managing per-application logins.
- Session isolation reduces credential exposure on the endpoint, because the vaulted password is injected on the PSM server and never reaches the operator's workstation.

**Customer demand signals:**
- Web administration consoles such as backup and data-protection platforms (for example NetBackup) are a recurring request for web-form-based privileged session brokering. Confirm additional field demand with the Tech Alliances team.

---

## 2. Use Cases at a Glance

This integration lets a partner package a connection component that lets Idira PSM auto-log on to the partner's web application and record the privileged session. It is a browser-automation integration, not an API integration. The capabilities below are the parts a partner authors.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Record the login flow | Capture the login web form (fields and click actions) with the Plugin Generator Utility | [6](#6-record-the-login-flow-plugin-generator-utility) |
| 2 | Map vaulted credentials to form fields | Bind `{username}` / `{password}` (or logon-account parameters) to the WebFormFields so PSM injects them at connect time | [7](#7-inject-vaulted-credentials-into-webformfields) |
| 3 | Confirm and finalize the session | Validate a successful login, handle multi-step or conditional forms, and confirm session recording | [8](#8-confirm-login-and-record-the-session) |
| 4 | Package and deploy | Emit the connection component .zip, upload to PVWA, and link it to a platform | [9](#9-package-deploy-and-link-to-a-platform) |

A partner does not need to build every optional capability (for example conditional multi-step logic) to certify. Document which parts your login flow requires in the certification checklist.

---

## 3. What the Customer Sees

After the connector is deployed and linked to a platform, an operator selects the target web account in PVWA and clicks **Connect**. PSM opens the application in a controlled browser on the PSM server, injects the vaulted credentials into the login web form, and logs the operator in without ever showing them the password. The session is recorded and available to auditors alongside all other PSM sessions.

| What the customer sees | Where it comes from |
|:---|:---|
| A **Connect** option on the web account in PVWA | The connection component linked to the account's platform |
| Automatic login with no visible password | Vaulted credentials injected into WebFormFields by PSM |
| A recorded session in the PSM session list | PSM session recording (browser automation capture) |

---

## 4. Prerequisites

### Idira Environment

| Requirement | Detail |
|:---|:---|
| Idira deployment | Idira Privileged Access Manager - Self-Hosted (PVWA + PSM). The same Secure Web Application Connectors Framework is documented for Idira Privilege Cloud, where PSM runs on the customer's connector servers; the procedures in this guide are written for Self-Hosted. See [Self-Hosted](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm) and [Privilege Cloud](https://docs.cyberark.com/manage/latest/en/content/privilege-cloud/pasimp/psm_webapplication.htm). |
| PSM server prepared for web apps | Run `PSMHardening.ps1` with the `-SupportWebApplications` parameter on the PSM server as an administrator; enable the browser sections of `PSMConfigureAppLocker.xml` and run `PSMConfigureAppLocker.ps1`. |
| Browser + matching web driver | Google Chrome 100 or later, or Microsoft Edge 103 or later (IE mode not supported), 32- or 64-bit, on the PSM server, plus the **matching** web driver (ChromeDriver for Chrome, `msedgedriver.exe` for Edge). Browser and driver versions must be identical, and their bitness must match the dispatcher. Put the driver in the PSM `\Components` folder (32-bit) or `\Components\x64` (64-bit). Deploy the **WebDriverUpgrader** tool to keep drivers current, or manage versions manually. |
| Framework version | The latest Secure Web Application Connectors Framework from the Marketplace. From Chrome/Edge driver 133, use framework **14.6.0.244 or later**. |
| WebAppDispatcher | Deploy the WebAppDispatcher with the current PSM version. From PSM 14.6, **out-of-the-box** connection components use the 64-bit dispatcher automatically; **components downloaded from the Marketplace — including yours — stay in the 32-bit Connector folders** unless PVWA is configured to switch. If a target web app does not support 64-bit, PSM reverts to 32-bit; you can also point ClientDispatcher at `{PSMComponentsFolder32}`. For Edge, download the current WebAppDispatcher from the Idira Marketplace and copy it to the PSM Components folder. **On PSM 15.0 new installations (2026-08-02): the install package no longer bundles connection components** — PVWA, vSphere, SSMS, Azure Portal and others must be downloaded from the Marketplace. Do not assume any baseline component is present on a fresh 15.0 PSM server; verify what is actually in the Components folder before testing your connector. Existing installations upgraded to 15.0 are unaffected. Whether WebAppDispatcher itself is in or out of that exclusion is not stated in the release note — check the Components folder rather than assuming, and ask your Idira Technical Alliances contact if you need it confirmed before you plan the deployment. |
| Sandbox | C3 Integrations Platform — request access at `cybr-bizdevtech@paloaltonetworks.com`. |

### Partner Environment

| Requirement | Detail |
|:---|:---|
| Target web application | A reachable login URL for the partner web application, over HTTPS, with a certificate the PSM server trusts. A self-signed certificate is supported by adding it to the PSM server's trusted certificates — not by turning certificate validation off (see [section 8](#8-confirm-login-and-record-the-session)). |
| Login flow details | Knowledge of the login web form: the username and password fields, the submit control, and any multi-step, SSO, or conditional screens. |
| Plugin Generator Utility | The PSM Plugin Generator Utility installed, used to record the login flow and emit the connector. |
| Test account | A test account in the target application to validate auto-logon and recording end to end. |

---

## 5. How a Web Connection Component Works

Unlike a REST integration, a Web Connection Component is a packaged browser-automation plugin that runs on the customer's PSM server. There is no Idira REST API call and no `x-cybr-telemetry` header in this modality.

```
Operator clicks Connect in PVWA
    ↓
PSM retrieves the target account from the Vault
    ↓
WebAppDispatcher launches Chrome/Edge on the PSM server
    ↓
Connection component navigates to LogonURL
    ↓
WebFormFields inject {username}/{password} into the login form
    ↓  (click Login/Submit; handle any conditional steps)
Validation step confirms a successful login
    ↓
PSM records the browser session → available in the PSM session list
```

The partner authors two things: the **connection component** (cloned from `PSM-WebAppSample`, with a unique `Id` and `DisplayName`) and the **WebForm Settings** (the `LogonURL` and the `WebFormFields` that describe the login flow).

---

## 6. Record the Login Flow (Plugin Generator Utility)

Use the PSM Plugin Generator Utility (the Web Connector Generator) to record the login flow rather than authoring the field map by hand.

1. Start a recording session and drive the login the way an operator would: enter the username, enter the password, and click the login control.
2. Click the login button (**Login**, **Next**, or **Submit**). Do not press ENTER to submit, because the recorder captures button clicks, not the ENTER key.
3. The recorder captures two kinds of actions:
   - **Text actions** — text entered on the site, such as the user name and password. Unless you specify otherwise, the first text input maps to the username and the second maps to the password.
   - **Click actions** — button clicks and other clickable element interactions.
4. Set the connector settings:
   - **Connector name** — this derives the connection component `Id`.
   - **URL** — the login URL, static or dynamic.
   - **Action timeout** — maximum seconds to wait for each action to complete (default 10).
   - **Page load timeout** — maximum seconds to wait for each page to load (default 30).

The utility emits the connector as a `.zip` file in `<Plugin Generator utility installation>\ConnectionComponents`.

---

## 7. Inject Vaulted Credentials into WebFormFields

PSM injects vaulted credentials into the login form using replaceable parameters in the WebFormFields. The partner never handles the credential; the partner only maps which form field receives which vaulted value.

| Replaceable parameter | Injects |
|:---|:---|
| `{username}` | The account's user name |
| `{password}` | The account's password |
| `{logonaccount\username}` | A separate logon account's user name (when a logon account is used) |
| `{logonaccount\password}` | A separate logon account's password |
| `{reconcileaccount\password}` | The reconcile account's password |
| `{extraaccount\password}` | An extra account's password |
| `{masteraccount\newpassword}` | A master account's new password |

In the Plugin Generator Utility, mark the recorded text values as **Dynamic Parameters** so the recorded literal is replaced at runtime with the vaulted value. Dynamic parameters can apply to the URL or to input text fields.

If the account requires a separate logon account, add the **LogonAccount** capability to the connection component's Supported Capabilities and map `{logonaccount\username}` / `{logonaccount\password}` accordingly.

### WebFormFields action syntax

When you adjust the field map directly, WebFormFields use this syntax:

- **Input a value:** `Identifier > Value (SearchBy=Type) (SendSlow=Time)`
- **Click a control:** `Identifier > (Button)`, `(Click)`, or `(ScriptClick)`
- **Validate the result:** `Identifier > (Validation)` or `(Verification)` to confirm a successful login. Validation lines run only when `RunValidations` is `Yes`, and must come after the last `(Button)`
- **Navigate after login:** `(Navigate=URL)` to redirect after logon
- **Conditional logic:** `if ()...end-if`, `else-if ()...end-else-if`, and `else...end-else` blocks, using `Exists` and `Count` conditions for multi-step or variable login screens
- **Frames:** `Identifier > (iFrame) (SearchBy=Type)` to enter a frame before acting on elements inside it
- **Explicit failure:** `Identifier > (Failure) (SearchBy=Type)(Message=Message)` to fail the connection with a clear message when an error element appears
- **MFA:** place `&MFACode&` where a generated MFA code must be entered
- **Timeouts:** `ActionTimeout` (default 10 seconds), `WaitForElementActionableTimeout`, `WaitForElementIsNotVisibleTimeout` and `BrowserDriverCommandTimeout`

> **HTTP targets.** From Chromium 127, Chrome and Edge enable HTTPS-First Mode by default in incognito, which affects login pages served over plain HTTP. Serve the login page over HTTPS.

Bind the username field to `{username}` and the password field to `{password}` (or the logon-account parameters), so the injected value replaces the recorded literal.

---

## 8. Confirm Login and Record the Session

1. Add a validation or verification step (`(Validation)` / `(Verification)`) on an element that only appears after a successful login, so PSM can confirm the logon succeeded rather than assuming it. Place it after the last `(Button)` line. Do not validate on text that is already on the login page — that passes even when the login fails.
2. Set `RunValidations` to `Yes`. With `Yes`, PSM runs the validations at the end of the login process and terminates the session if they fail. With `No`, PSM skips every validation line, and a failed login leaves the session open on the login page, where the operator can sign in by hand with a credential that did not come from the Vault. `RunValidations` set to `Yes` cannot be combined with the `SubmitButton` parameter; use a `(Button)` line in WebFormFields instead.
3. Leave `EnforceCertificateValidation` at `Yes`, its default. PSM then connects only to a target whose certificate it trusts. With `No`, PSM accepts any certificate, so anyone able to intercept the connection can present a fake login page and receive the vaulted credential. If the target uses a self-signed certificate, add that certificate to the trusted certificates on the PSM server — that is the documented fix — and state the step in your configuration guide.
4. For multi-step, SSO, or conditional login pages, wrap the variable steps in `if ()...end-if` / `else...end-else` blocks using `Exists` and `Count` conditions.
5. Test the connector from the Plugin Generator Utility against the test account before packaging.
6. Session recording is handled by the framework: PSM records the browser session through the automation process. Confirm the session appears in the PSM session list after a test connection.

---

## 9. Package, Deploy, and Link to a Platform

1. In the Plugin Generator Utility, confirm a successful test run, then take the connector `.zip` from `<Plugin Generator utility installation>\ConnectionComponents`.
2. Upload the connector `.zip` to PVWA. From PVWA it deploys across the customer's PSM servers.
3. In Platform Management, link the connection component to the target platform: add the component's `Id` under the platform's **UI & Workflows** > **Connection Components** section, and set **Enable** to **Yes**.
4. Confirm the connection component's `Id` and `DisplayName` are unique and that the component is based on `PSM-WebAppSample`.
5. Test **Connect** from PVWA against a vaulted test account and confirm both auto-logon and session recording.

---

## 10. Troubleshooting

| Symptom | Likely cause | Action |
|:---|:---|:---|
| Connection fails to launch the browser | Browser and web driver versions differ | Match the ChromeDriver / `msedgedriver.exe` version to the installed browser version exactly. |
| Browser is blocked from running | AppLocker rules not enabled | Uncomment the browser sections in `PSMConfigureAppLocker.xml` and run `PSMConfigureAppLocker.ps1`. |
| Web app connector not available at all | PSM not hardened for web applications | Run `PSMHardening.ps1 -SupportWebApplications` on the PSM server as an administrator. |
| Login submits before fields are filled | ENTER used instead of a click, or timeouts too short | Record a click on the login control; increase Action timeout / Page load timeout. |
| Connection fails with "Page certificate is untrusted" | The PSM server does not trust the target's certificate | Add the target's certificate to the PSM server's trusted certificates. Do not set `EnforceCertificateValidation` to `No`. |
| Password appears not to inject | Dynamic parameter not mapped | Confirm the field is bound to `{password}` (or the logon-account parameter), not the recorded literal. |
| Edge sessions fail | Wrong or missing WebAppDispatcher | Download the current WebAppDispatcher from the Idira Marketplace and copy it to the PSM Components folder. |

---

## 11. Pre-Development Checklist

- [ ] PSM server hardened for web applications (`PSMHardening.ps1 -SupportWebApplications`)
- [ ] AppLocker browser rules enabled (`PSMConfigureAppLocker.ps1`)
- [ ] Chrome 100+ or Edge 103+ installed on the PSM server with the matching web driver version, bitness matching the dispatcher in use
- [ ] WebAppDispatcher deployed — Marketplace components default to 32-bit; switch in PVWA if you need 64-bit (Edge dispatcher from the Idira Marketplace if needed)
- [ ] Login flow recorded with the Plugin Generator Utility (click the login control, do not press ENTER)
- [ ] Username and password fields mapped to `{username}` / `{password}` (or logon-account parameters) as dynamic parameters
- [ ] LogonAccount capability added to Supported Capabilities if a separate logon account is used
- [ ] Validation / verification step added after the last `(Button)` to confirm a successful login
- [ ] `RunValidations` set to `Yes`
- [ ] `EnforceCertificateValidation` left at `Yes`; any self-signed target certificate trusted on the PSM server
- [ ] Conditional blocks added for any multi-step or SSO login screens
- [ ] Connection component `Id` and `DisplayName` are unique and based on `PSM-WebAppSample`
- [ ] Connector tested end to end (auto-logon + session recording) before packaging
- [ ] Connector `.zip` uploaded to PVWA and linked to a platform (component enabled)

---

## 12. Resources

- [Secure Web Application Connectors Framework](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm)
- [C3 Integrations Platform](https://c3.cyberark.cloud)
- [Web applications for PSM](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psm_webapplication.htm)
- [Generate PSM web connectors with the Plugin Generator Utility](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pcp/pgu-psm-plugins-main.htm)
- [Configure PSM to connect to web applications](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pas%20inst/install_configurepsmservermachineforwebapps.htm)
- [Connection component parameters](https://docs.cyberark.com/pam-self-hosted/latest/en/content/pasimp/psmconnectioncomponents.htm)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.4 | 2026-10-20 | **[Added]** Section 8 now states two settings a component must ship with: `RunValidations` set to `Yes` (otherwise PSM skips every validation line and a failed login leaves the session open for a manual sign-in), and `EnforceCertificateValidation` left at `Yes` (otherwise PSM accepts any target certificate). The partner-environment prerequisite now requires a certificate the PSM server trusts, with the self-signed case handled by trusting the certificate on the PSM server. Added a troubleshooting row for "Page certificate is untrusted" and matching pre-development checklist items. These pair with checklist checks 2.2 and 3.6 | Idira Technical Alliances |
| 1.3 | 2026-10-08 | **[Fixed]** Components downloaded from the Marketplace — including partner connectors — use the 32-bit dispatcher unless PVWA is configured to switch; the 64-bit default from PSM 14.6 applies to out-of-the-box components. The hardening parameter is `-SupportWebApplications`, and the driver tool is WebDriverUpgrader. Browsers may be 32- or 64-bit. **[Added]** Minimum browser versions; framework 14.6.0.244 or later for driver 133+; the x64 driver folder; HTTPS-First Mode in incognito; the iFrame, Failure and MFA WebFormFields commands and the timeout parameters; that the framework is also documented for Privilege Cloud | Idira Technical Alliances |
| 1.2 | 2026-10-05 | **[Fixed]** The WebAppDispatcher prerequisite now states in visible prose that the PSM 15.0 release note does not settle whether WebAppDispatcher itself falls under the connection-component exclusion, and tells you to check what is actually in the Components folder and to ask your Idira Technical Alliances contact if you need it confirmed before planning a deployment. That qualification previously sat in an editorial comment — invisible on the rendered page, fully visible to a partner's AI agent, which reads the raw markdown. The underlying instruction is unchanged: do not assume any baseline component is present on a fresh 15.0 server. Also added this change log — the file previously carried none, so no revision before this one is recorded | Idira Technical Alliances |
