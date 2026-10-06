# Idira Self-Service Guide for Credential Rotation

**Workflow:** Credential Rotation  
**Dev Kit:** CPM REST API Plugin  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Credential_Rotation_Self-Service_Guide.pdf  
**Version:** 1.2  
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Central Policy Manager (CPM) — the REST API plugin framework for credential rotation.
WORKFLOW: Credential Rotation
USE CASE: CPM REST API Plugin — Idira rotates a credential on the partner's target application by
  calling that application's own API, driven by a plugin the partner authors.
INTEGRATION PATTERN: AN XML CONFIGURATION FILE. NOT a REST client. See the first warning below.
AUTH METHOD: whatever the TARGET application's API requires — the plugin authenticates outbound to the
  partner's product, not inbound to Idira. Check 4.2 constrains it; see the CONTRADICTION below.
BASE URL: none. There is no Idira endpoint in this kit.
TELEMETRY: it=CredentialRotation — see ../../telemetry-reference.md. NOT documented in this guide;
  see KNOWN GAPS.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS KIT SHIPS NO PARTNER CODE. THE DELIVERABLE IS XML. The CPM framework makes every HTTP call; the
partner supplies an XML file describing the calls, the parsing rules and the error mapping. There is
no SDK to import, no client library to write, and no process of the partner's that runs at rotation
time. An agent asked to "build the integration" here must produce a plugin XML file plus its two
platform files — Python, Java or C# client code is the wrong artefact entirely, however well written.

THE DIRECTION IS OUTBOUND, AND IT IS THE OPPOSITE OF THE SECRETS MANAGEMENT KITS. Here IDIRA CALLS
THE PARTNER. The four ../../secrets-management/ kits are the reverse — the partner's application calls
Idira to retrieve a secret. Nothing about auth, hosts or headers transfers between the two directions.

THE FOUR MANDATORY XML SECTIONS, IN ORDER (Section 4, graded as check 3.1): `<Parameters>`,
`<ErrorMessages>`, `<APICalls>`, `<Chains>`. All four are required even when a section is thin.
- `<Parameters>` — names must be unique (3.2). A parameter may NOT carry both a hardcoded value and a
  dynamic `path` attribute (6.1).
- `<ErrorMessages>` — names must be unique (3.3); each needs `returnCode`, `name` and `description`
  (5.3). Every `<Response type="error">` must link to one of these globals (5.2).
- `<APICalls>` — at least one `<APICall>` (3.4), each with at least one `<Response>` (3.5). Use
  `<Validate>` when a status code alone does not prove the transaction succeeded (6.3).
- `<Chains>` — at least one `<Chain>` (3.6), each invoking at least one `<Request>` (3.7).

CHAIN NAMES ARE FIXED CPM VERBS, LOWERCASE, AND NOT FREE TEXT: `verifypass`, `changepass`,
`reconcilepass` (Sections 4, 8 and 9). `changepass` is the only required operation; Verify is
recommended and Reconcile optional (Section 2). Requests inside a chain execute top to bottom, so a
`LoginRequest` that obtains a token must precede the request that uses it.

PLACEHOLDER SYNTAX IS `((Name))` — DOUBLE PARENTHESES, NOT BRACES — with an optional pipe modifier:
`((Password|JsonEscape))` for a value going into a JSON body. Runtime values supplied by CPM include
`((Address))`, `((Username))` and `((Password))`.
  DISCREPANCY IN THIS GUIDE, FLAG RATHER THAN GUESS: Section 8's `SearchURL` example uses
  `{{Username}}` in braces while every other example in the file uses `((…))`. The two are not
  interchangeable syntaxes as far as this guide establishes. Confirm with the Idira Technical Alliances contact before coding
  against the brace form.

SECURITY ATTRIBUTE THAT IS EASY TO OMIT AND IS GRADED: any `<Parameter>` that holds an access token,
a transient secret or a password parsed out of a response needs `secure="true"` (check 4.1). The
Section 4 example shows it on `BearerToken`; a generated plugin that parses a token without it fails.

LOCAL TEST HARNESS — CPM SERVER, NOT PVWA (Section 9). An INI file `User_Test_API.ini` beside the
plugin supplies the test values: `[targetaccount]` (username / password / newpassword / address),
`[extrapass3]` for the RECONCILIATION account's credentials, and `[extrainfo]` carrying
`ConfigurationFilePath` and `Debug=Yes`. Run `run_NETInvoker_API.cmd <chain>` from the Password
Manager directory; success is literally `The plugin ended successfully (RC=0)`. Debug logs land in
`…\Password Manager\Logs\Third Party`.

PACKAGING IS THREE FILES, NOT ONE (Section 10): the plugin XML, `Policy-<Name>.ini` (carrying
`PolicyID`, `PolicyName`, `ConfigurationFilePath`) and `Policy-<Name>.xml` (Policy ID and
PlatformBaseID both set to the plugin name), zipped and imported via PVWA ADMINISTRATION > Platform
Management. Restart the "Idira Password Manager" service afterwards.

THE `CyberArk` IN THE FILESYSTEM PATHS IS CORRECT — DO NOT REBRAND IT. Paths are literally
`C:\Program Files (x86)\CyberArk\Password Manager\…`. The installed directory name did not change with
the product name. Rewriting it to `Idira` breaks every command in Sections 8–10.

A CONTRADICTION BETWEEN THIS GUIDE AND THE CHECKLIST — THE CHECKLIST GOVERNS. Section 5 says the
Authorization header format "will depend on the target API's specification" and offers
`Token <token_value>` and `X-API-Key <token_value>` as examples. Check 4.2 restricts certified plugins
to Basic or Bearer transport. If the target API accepts only `Token` or `X-API-Key`, do not assume the
guide's permission carries — raise it with the Idira Technical Alliances contact before certification.

DEPLOYMENT SCOPE IS AN OPEN QUESTION ON THIS KIT. Every procedure here is on-box Windows Self-Hosted —
`C:\Program Files (x86)\…`, `services.msc`, PVWA — while the certification checklist certifies a
Privilege Cloud / SaaS deployment. The guide never states how a partner does any of this against
Privilege Cloud. This is a recorded advisory finding in the corpus check, not an oversight in this
block. Do not invent a SaaS procedure; route the question to the Idira Technical Alliances contact.

KNOWN GAPS — DO NOT FILL THEM IN FROM MEMORY. Five graded identifiers do not appear in this guide, and
all are open findings in the corpus check:
- `Idira.Extensions.Generic.Plugin.RestAPI.dll` and `Idira.Extensions.Generic.Infra.RestAPI.dll` —
  checks 2.1 and 2.2 require the plugin to extend both assemblies; the guide never names either.
- `Deletepass` and `Deletepassafterreconcile` — check 5.5 requires both for AccessKeys target systems;
  the guide documents only verify / change / reconcile.
- `validationPattern` — check 6.2 requires it on `<Parameters>` where data-type validation applies; the
  guide's parameter attribute list names only `name`, `path` and `searchMethod`.
- Telemetry. Checks 7.1–7.6 grade the `x-cybr-telemetry` header, Base64url encoding and
  `it=CredentialRotation`; this guide does not mention telemetry anywhere.
Every reference link in Section 1 resolves to the docs.cyberark.com portal front page rather than a
specific page, so following one does not recover the missing detail. Say it is not documented here and
point at the checklist and the Idira Technical Alliances contact.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the plugin
- certification-checklist.md — what the plugin is graded on; read it during the build
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Supporting Documentation

- [Create CPM plugins for REST API applications | Idira® Docs](https://docs.cyberark.com)
- [REST API infrastructure development guide | Idira Docs](https://docs.cyberark.com)
- [Placeholders in REST API Infrastructure | Idira Docs](https://docs.cyberark.com)

---

## 2. Use Cases at a Glance

This integration is a CPM (Central Policy Manager) plugin that lets Idira automatically manage credentials for your target application. A plugin implements up to three credential operations — build the ones your application's API supports.

| # | Capability | What it does | Required? |
|:--|:---|:---|:--:|
| 1 | Verify | Confirms the stored credential is still valid on the target application | Recommended |
| 2 | Change | Rotates the credential to a new value on both the target application and the vault | Required |
| 3 | Reconcile | Resets the credential from a privileged reconciliation account when it is out of sync | Optional |

Each operation is defined as a `<Chain>` in the plugin's XML configuration (see Section 4). At minimum a plugin must implement Change; Verify and Reconcile are strongly recommended for a complete lifecycle. Document which operations your plugin implements in the certification checklist.

---

## 3. Integration Development Workflow

Developing a CPM plugin with the REST API framework typically follows a structured approach:

1. **Verify API Support:** Confirm that the target application's API supports essential functions like account verification, password changes, and reconciliation. This also includes validating connectivity between the CPM and the REST API endpoint.
2. **Document API Calls:** Meticulously document all necessary API calls for each CPM action (verify, change, and reconcile). This documentation should cover requests, expected responses, and any runtime data such as authentication tokens, account details, and API endpoint addresses.
3. **Create and Test Configuration File:** Create the configuration file in XML format. This file defines how the CPM interacts with the target application's API. Partners can optionally test this XML configuration file during development.
4. **Package and Test:** Package the XML configuration file along with relevant platform files (INI and XML) into a zip file. This package is then imported into the Idira Password Vault Web Access (PVWA) for comprehensive testing.

---

## 4. Understanding the REST API Framework XML Structure

The XML configuration file for a CPM plugin is comprised of four key sections:

### `<Parameters>`

Defines global parameters for plugin execution. Each `<Parameters>` element can contain `<Parameter>` sub-elements used throughout the XML. Parameters have mandatory attributes like `name` and optional ones like `path` or `searchMethod`.

```xml
<RestPlugin>
  <Parameters>
    <Parameter name="VerifyURL">https://((Address))/VerifyEndpoint</Parameter>
    <Parameter name="ChangeURL">https://((Address))/ChangeEndpoint</Parameter>
  </Parameters>
  ...
```

### `<ErrorMessages>`

Defines global error messages for plugin execution, regardless of state. The `<ErrorMessages>` element contains `<ErrorMessage>` sub-elements, including error data and CPM return codes.

```xml
  <ErrorMessages>
    <ErrorMessage name="GeneralError" returnCode="9999" description="This is a general Error"/>
  </ErrorMessages>
  ...
```

### `<APICalls>`

Defines API calls, covering requests and responses. The `<APICall>` element contains `<Request>` (name, HTTP method) and `<Responses>` (instructions for parsing, with at least one `<Response>` sub-element). Responses can be "Valid" (success) or "Error" (issue, sends error to CPM).

```xml
  <APICalls>
    <APICall>
      <Request name="VerifyRequest" method="POST">
        <URL>((VerifyURL))</URL>
        <Headers>
          <Header key="Content-Type">application/json</Header>
        </Headers>
        <Body>
          {
            "Username": "((Username))",
            "Password": "((Password|JsonEscape))"
          }
        </Body>
      </Request>
      <Responses>
        <Response name="VerifyValidResponse" type="valid" format="json" statusCode="200">
          <Parse>
            <ParseBody>
              <Parameter name="BearerToken" path="Result.Token" secure="true"/>
            </ParseBody>
          </Parse>
        </Response>
        <Response name="GeneralForbiddenResponse" type="error" statusCode="403">
          <Validate>
            <Body>
              <Object path="ErrorCode" searchMethod="regex" searchMethodArgument="PASWS013E"/>
            </Body>
          </Validate>
          <Parse>
            <ParseBody>
              <Parameter name="GeneralForbiddenError" path="ErrorCode"/>
              <Parameter name="GeneralForbiddenErrorDescription" path="ErrorMessage"/>
            </ParseBody>
          </Parse>
          <ErrorMessage name="GeneralForbiddenErrorMessage" returnCode="8400" description="Error from API: "/>
        </Response>
        <Response name="GeneralErrorResponse" type="error" statusCode="500">
          <ErrorMessage name="GeneralError"/>
        </Response>
      </Responses>
    </APICall>
  </APICalls>
  ...
```

### `<Chains>`

Represents CPM actions. In each chain, API Requests are declared for top-to-bottom execution.

```xml
  <Chains>
    <Chain name="verifypass">
      <Request name="VerifyRequest" />
    </Chain>
    <Chain name="changepass">
      <Request name="VerifyRequest" />
      <Request name="ChangeRequest" />
    </Chain>
  </Chains>
</RestPlugin>
```

---

## 5. Key Considerations for Integration Development

- **Authentication Methods:** Access token authentication is a common and more secure method where a client first sends credentials to a login endpoint to receive an access token. This token is then included in the Authorization header of subsequent API requests for a limited time. The exact format for including the access token in the Authorization header (e.g., `Token <token_value>`, `X-API-Key <token_value>`) will depend on the target API's specification.

- **Error Handling:** Implementing robust error handling is critical for any integration. Identifying and properly categorizing HTTP error codes and messages from the target API response is crucial for effective diagnosis, troubleshooting, and improving the user experience. The `<ErrorMessages>` section in the XML configuration allows for defining custom error messages and return codes to the CPM.

- **JSONPath for Data Extraction:** When parsing API responses in JSON format, JSONPath is a query language used to extract specific parts of a JSON object or array. You can verify and test your JSONPath expressions using online tools such as [jsonpath.com](https://jsonpath.com).

---

## 6. Hands-on Development and Testing Steps for Partners

These steps provide a generalized workflow for partners developing and testing CPM REST API plugins. Specific paths and commands might vary based on your development environment and the target application.

---

## 7. Step 1: Verify API Support and Connectivity

Before developing, ensure the target application's API can perform the necessary actions (verify, change, reconcile) and that your CPM server can reach it.

1. **Review API Documentation:** Consult the target application's official REST API documentation (e.g., Swagger UI, developer portal) to understand endpoints, request formats, and response structures for login/token acquisition, verification, password change, and user search/reconciliation.
2. **Access Your CPM Server:** Log in to your Windows server where the Idira Central Policy Manager (CPM) is installed, typically with an administrative account.
3. **Open Command Prompt/PowerShell:** Launch a Windows Command Prompt or PowerShell window as an administrator.
4. **Test Connectivity and API Calls (using curl):**

   Test basic connectivity:
   ```bash
   curl -i -X GET https://YOUR_API_BASE_URL_GOES_HERE/
   ```
   Expected Result: A `HTTP/1.1 200 OK` response, indicating successful connectivity.

   Test token acquisition (Login API):
   ```bash
   curl -i -X POST -H "Content-Type: application/json" \
     -d '{"username": "testuser", "password": "currentPassword1"}' \
     https://YOUR_API_BASE_URL_GOES_HERE/auth
   ```
   Expected Result: A `HTTP/1.1 201 Created` response with a JSON body containing a token or similar field. Note this token value and its JSON path (e.g., `$.token`).

   Test a verified API call (e.g., verify user details with token):
   ```bash
   curl -i -X GET -H "Content-Type: application/json" \
     -H "Authorization: Token <your_obtained_access_token_from_api>" \
     https://YOUR_API_BASE_URL_GOES_HERE/users/1
   ```
   Expected Result: A `HTTP/1.1 200 OK` response with user details for ID 1.

5. **Document findings:** Note down successful API responses, relevant HTTP status codes for both success and various failure scenarios, and the exact JSON paths for any data you need to extract (e.g., `$.token`, `$.id`, `$.code` for errors).

---

## 8. Step 2: Create/Update the Plug-in Configuration File (XML)

1. **Navigate to the CPM Plugin Directory:** Open File Explorer and go to `C:\Program Files (x86)\CyberArk\Password Manager\bin`.
2. **Open the XML File:** Open your plugin's XML file (e.g., `YourPluginName.xml`) in a text editor (like Notepad++ or VS Code). If it doesn't exist, create a new file with this name.
3. **Define Parameters:** Modify the `<Parameters>` section to include the URLs for your API endpoints:

```xml
<Parameters>
  <Parameter name="LoginURL">https://YOUR_API_BASE_URL_GOES_HERE/auth</Parameter>
  <Parameter name="VerifyURL">https://YOUR_API_BASE_URL_GOES_HERE/users/verify</Parameter>
  <Parameter name="ChangeURL">https://YOUR_API_BASE_URL_GOES_HERE/users/change</Parameter>
  <Parameter name="SearchURL">https://YOUR_API_BASE_URL_GOES_HERE/users?username={{Username}}</Parameter>
  <Parameter name="ReconcileURL">https://YOUR_API_BASE_URL_GOES_HERE/users/</Parameter>
</Parameters>
```

4. **Define Error Messages:** Populate the `<ErrorMessages>` section:

```xml
<ErrorMessages>
  <ErrorMessage name="IncorrectPassword" returnCode="8001" description="Incorrect Password"/>
  <ErrorMessage name="LoginFailed" returnCode="8004" description="Failed to obtain access token"/>
</ErrorMessages>
```

5. **Define API Calls:** Implement the `<APICalls>` section based on your API documentation:
   - **LoginRequest:** Defines how CPM obtains the access token for the target account.
   - **ReconLoginRequest:** Similar to LoginRequest, but for the reconciliation account's credentials.
   - **VerifyRequest, ChangeRequest, SearchRequest, ReconcileRequest:** Configure the URL, Headers, Body, and Responses for each.

6. **Define Chains:** Populate the `<Chains>` section:

```xml
<Chains>
  <Chain name="verifypass">
    <Request name="LoginRequest"/>
    <Request name="VerifyRequest"/>
  </Chain>
</Chains>
```

7. Save the XML file.

---

## 9. Step 3: Manual Testing of the XML Configuration File

Test your plugin's logic directly on the CPM server before deploying to PVWA.

1. **Create a Parameter File (INI):** In `C:\Program Files (x86)\CyberArk\Password Manager\bin`, create a file named `User_Test_API.ini`.

2. **Populate the INI file:**

```ini
[targetaccount]
username=john.doe
password=currentPassword1
newpassword=newPassword2
address=YOUR_API_BASE_URL_GOES_HERE

[extrapass3] ; For reconciliation account credentials
username=admin.user
password=adminPassword1

[extrainfo]
ConfigurationFilePath=YourPluginName.xml
Debug=Yes ; Enable debug logs for troubleshooting
```

3. **Open Command Prompt/PowerShell as Administrator** and navigate to the CPM directory:
```
cd C:\Program Files (x86)\CyberArk\Password Manager
```

4. **Execute the plugin for verification:**
```
run_NETInvoker_API.cmd verifypass
```
Expected Result: `The plugin ended successfully (RC=0)`. If it fails, check the CPM debug logs at `C:\Program Files (x86)\CyberArk\Password Manager\Logs\Third Party`.

5. **Test password change:**
   - Edit `User_Test_API.ini`: Update `password` to the current one and `newpassword` to a different value.
   - Run: `run_NETInvoker_API.cmd changepass`
   - Expected Result: `The plugin ended successfully (RC=0)`.

6. **Test reconciliation:**
   - Edit `User_Test_API.ini`: Update `password` under `[targetaccount]` to a "broken" state. Ensure `[extrapass3]` contains correct reconciliation account credentials.
   - Run: `run_NETInvoker_API.cmd reconcilepass`
   - Expected Result: `The plugin ended successfully (RC=0)`.

---

## 10. Step 4: Package and Test Through the PVWA

1. **Prepare Platform Files:**
   - Navigate to your plugin development folder.
   - Locate generic `Policy-Dummy.ini` and `Policy-Dummy.xml` files. Copy and rename them to `Policy-YourPluginName.ini` and `Policy-YourPluginName.xml`.
   - Edit `Policy-YourPluginName.ini`:
   ```ini
   PolicyID=YourPluginName
   PolicyName=YourPlugin REST API Plugin
   ConfigurationFilePath=YourPluginName.xml
   ```
   - Edit `Policy-YourPluginName.xml`: Update Policy ID and PlatformBaseID to `YourPluginName`.

2. **Package the Files into a ZIP:** Select `YourPluginName.xml`, `Policy-YourPluginName.ini`, and `Policy-YourPluginName.xml` and compress into `YourPluginName.zip`.

3. **Import the Platform into PVWA:**
   - Log in to the Idira Password Vault Web Access (PVWA) as an administrator.
   - Navigate to ADMINISTRATION > Platform Management.
   - Click the Import Platform button and select `YourPluginName.zip`.

4. **Add an Account in PVWA:**
   - Navigate to Accounts View and click Add Account.
   - System type: Application.
   - Platform: YourPlugin REST API Plugin.
   - Safe: Select an existing safe or create a new one.
   - Account properties: Username, Address (API base URL), Password.

5. **Restart CPM Service:**
   - Open Services (`services.msc`), locate Idira Password Manager, right-click and select Restart.

6. **Test CPM Actions via PVWA:** Select the account, then click Verify, Change, and (if linked) Reconcile.

7. **Check Status and Troubleshoot:**
   - Observe Compliance Status and Last Verified/Changed/Reconciled timestamps.
   - If any action fails, enable debugging: ADMINISTRATION > Platform Management > YourPlugin REST API Plugin > Automatic Password Management > Additional Policy Settings > set Debug to Yes.
   - Review debug logs at `C:\Program Files (x86)\CyberArk\Password Manager\Logs\Third Party`.

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the misread that makes every other detail moot: this kit ships **no partner code** — the deliverable is an XML configuration file the CPM framework executes, so generated client code in any language is the wrong artefact — and the direction is outbound, with Idira calling the partner, the inverse of the Secrets Management kits. It records the four mandatory XML sections against the checks that grade each, that chain names are fixed lowercase CPM verbs (`verifypass` / `changepass` / `reconcilepass`), the `((Name))` placeholder syntax with its `|JsonEscape` modifier, the easily-omitted `secure="true"` attribute, the local `run_NETInvoker_API.cmd` harness with its `[extrapass3]` reconciliation section, three-file packaging, and that the literal `CyberArk` in the installed filesystem paths must not be rebranded or every command in Sections 8–10 breaks. Three things are recorded rather than resolved: a **discrepancy** — Section 8's `SearchURL` uses `{{Username}}` in braces where every other example uses `((…))`; a **contradiction** — Section 5 permits `Token` and `X-API-Key` header formats while check 4.2 restricts certified plugins to Basic or Bearer, and the checklist governs; and the **deployment-scope** question, since every procedure here is on-box Windows Self-Hosted while the checklist certifies Privilege Cloud. Five graded identifiers are recorded as gaps with no implementation path in this guide: both `Idira.Extensions.Generic.*.RestAPI.dll` assemblies, `Deletepass` / `Deletepassafterreconcile`, `validationPattern`, and telemetry in its entirety. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps and conflicts are documented, not closed. — Idira Technical Alliances |
