# Idira Self-Service Guide for Credential Rotation

**Workflow:** Credential Rotation  
**Dev Kit:** CPM REST API Plugin  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira_Credential_Rotation_Self-Service_Guide.pdf  
**Version:** 1.3  
**Last Updated:** 2026-10-08

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

CHAIN NAMES ARE FIXED CPM VERBS, LOWERCASE, AND NOT FREE TEXT: `verifypass`, `logon`, `changepass`,
`prereconcilepass`, `reconcilepass`, `deletepass`, `deletepassafterreconcile` (Section 4).
`changepass` is the only required operation; Verify is recommended and Reconcile optional
(Section 2). `deletepass` and `deletepassafterreconcile` remove the previous credential after a
Change or Reconcile, and are strongly recommended for `ManagementType=AccessKeys` platforms where the
target creates a new key rather than rotating one (check 5.5). Requests inside a chain execute top to bottom, so a
`LoginRequest` that obtains a token must precede the request that uses it.

PLACEHOLDER SYNTAX IS `{{Name}}` — DOUBLE BRACES (Section 4). Runtime values supplied by CPM include
`{{Address}}`, `{{Username}}`, `{{password}}` (current) and `{{newpassword}}`. Scope a value to a
specific linked account with `{{AccountType\Name}}` — `targetaccount`, `logonaccount`,
`reconcileaccount`, `extraaccount`, `masteraccount`, `usageaccount`, `platform` (lowercase) — or try
several in order with `{{logonaccountORtargetaccount\username}}` (OR uppercase). Modifiers follow a
pipe and chain with colons: `{{Password|JsonEscape}}`, `{{Name|JsonEscape:urlEncode}}`; the four
modifiers are `JsonEscape`, `urlEncode`, `toUpper`, `toLower`. A placeholder that names a
`<Parameter>` resolves only after that parameter has been declared or parsed earlier in the flow.

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

AUTH HEADER: THE FRAMEWORK IS WIDER THAN CERTIFICATION — THE CHECKLIST GOVERNS. The framework accepts
`Basic {{username}}:{{password}}`, `Bearer {{token}}`, or any header the target needs (Section 5).
Check 4.2 restricts certified plugins to Basic or Bearer. If the target API accepts only `Token`,
`X-API-Key` or another scheme, raise it with the Idira Technical Alliances contact before
certification.

DEPLOYMENT: PRIVILEGE CLOUD AND SELF-HOSTED BOTH USE THE SAME FRAMEWORK (Section 3). Download the
REST API Application CPM Plugin Framework zip from the Marketplace, import it as a sample platform
(Privilege Cloud: Manage space > Administration > Platform Management > Import Platform;
Self-Hosted: PVWA > Administration > Platform Management), duplicate the sample platform, and place
the platform's configuration XML in the CPM `bin` folder. Sections 8–10 show the Self-Hosted on-box
paths; on Privilege Cloud the CPM runs on the customer's connector server.

THE FRAMEWORK FILES (Section 3), ALL GRADED: `CyberArk.Extensions.Generic.Plugin.RestAPI.dll` and
`CyberArk.Extensions.Generic.Infra.RestAPI.dll` (checks 2.1, 2.2), plus
`CyberArk.Extensions.Plugin.RestAPI.dll`. These are real file names — they keep `CyberArk`.
`validationPattern` is a `<Parameter>` attribute in the `<Parameters>` section: a regex applied to the
parameter's final value, failing the plugin at runtime if it does not match (check 6.2).
`ManagementType` decides who generates the new credential: `Password` (CPM generates it) or
`AccessKeys` (the target generates it — declare `<Parameter name="newpassword" path="…">` from the
response, and add the `KeyID` required property to the platform).

KNOWN GAP — DO NOT FILL IT IN FROM MEMORY: telemetry. Checks 7.1–7.6 grade an `x-cybr-telemetry`
header and `it=CredentialRotation`, and this guide does not describe where a CPM plugin would send
it. Raise it with your Idira Technical Alliances contact before certification.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the plugin
- certification-checklist.md — what the plugin is graded on; read it during the build
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Supporting Documentation

- [Create CPM plugins for REST API applications](https://docs.cyberark.com/manage/latest/en/content/privilege-cloud/plugins/cpm-plugins-rest-api.htm) — Privilege Cloud ([PAM Self-Hosted](https://docs.cyberark.com/pam-self-hosted/latest/en/content/plugins/cpm-plugins-rest-api.htm))
- [REST API infrastructure development guide](https://docs.cyberark.com/manage/latest/en/content/privilege-cloud/plugins/cpm-plugins-rest-api-infrastructure.htm) — every element and attribute of the configuration file
- [Placeholders in REST API Infrastructure](https://docs.cyberark.com/manage/latest/en/content/privilege-cloud/plugins/cpm-plugins-rest-api-placeholders.htm) — placeholder syntax, account scopes and modifiers

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

### Prerequisites and Deployment

**On the CPM server** (Self-Hosted CPM, or the CPM on a Privilege Cloud connector server):

- .NET Framework 4.8
- The latest Credentials Management .NET SDK and REST API Application Plugin Framework in the CPM `bin` folder

**Get the framework.** Download the latest REST API Application CPM Plugin Framework from the Idira Marketplace and extract `Plugin.RestAPIFramework-vXX.X.X.X-Master.zip`. It contains:

| File | Purpose |
|:---|:---|
| `Policy-SampleRestAPIPlatform.ini`, `Policy-SampleRestAPIPlatform.xml` | The sample platform |
| `SampleRestAPIPlatformConfiguration.xml` | The sample configuration file — copy it per platform; it lives in the CPM `bin` folder |
| `CyberArk.Extensions.Generic.Infra.RestAPI.dll` | The REST API infrastructure logic |
| `CyberArk.Extensions.Generic.Plugin.RestAPI.dll` | The generic plugin that executes a platform's configuration file |
| `CyberArk.Extensions.Plugin.RestAPI.dll` | Shared REST API helper used by many plugins |

These file names keep `CyberArk` — do not rebrand them.

**Create your platform.**

1. Import the framework zip as a platform — Privilege Cloud: **Manage space › Administration › Platform Management › Import Platform**; Self-Hosted: **PVWA › Administration › Platform Management**.
2. Duplicate the imported sample REST API platform and rename it.
3. Under **Automatic Password Management › Additional Policy Settings**, set:
   - `ConfigurationFilePath` — your configuration file name in the CPM `bin` folder (must end `.xml`)
   - `ManagementType` — `Password` (CPM generates the new credential) or `AccessKeys` (the target generates it; add the `KeyID` required property under UI & Workflows › Properties, with a dummy value if the target has no key ID)
   - `TLSVersion` (optional) and `Debug=Yes` during development

See [Create CPM plugins for REST API applications](https://docs.cyberark.com/manage/latest/en/content/privilege-cloud/plugins/cpm-plugins-rest-api.htm).

---

## 4. Understanding the REST API Framework XML Structure

The XML configuration file for a CPM plugin is comprised of four key sections:

### `<Parameters>`

Defines global parameters for plugin execution. Each `<Parameters>` element can contain `<Parameter>` sub-elements used throughout the XML.

| Attribute | Purpose |
|:---|:---|
| `name` | Required, unique. Referenced elsewhere as `{{name}}` |
| `path` | Where to read the value from a response (JSONPath for JSON bodies) |
| `searchMethod` / `searchMethodArgument` | Post-process the value, for example with a `regex` |
| `secure="true"` | Masks the value in logs — required for tokens, secrets and parsed passwords (check 4.1) |
| `validationPattern` | Regex applied to the final value; the plugin fails at runtime if it does not match. Only on parameters in the `<Parameters>` section (check 6.2) |

A parameter has either a literal value or a `path`, never both (check 6.1).

```xml
<RestPlugin>
  <Parameters>
    <Parameter name="VerifyURL">https://{{Address}}/VerifyEndpoint</Parameter>
    <Parameter name="ChangeURL">https://{{Address}}/ChangeEndpoint</Parameter>
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

Defines API calls, covering requests and responses. The `<APICall>` element contains `<Request>` (name, HTTP method — `Get`, `Post`, `Put`, `Delete` or `Patch`) and `<Responses>` (at least one `<Response>`; if no response matches at runtime, the plugin errors). Responses can be "valid" (success) or "error" (sends an error to CPM).

Every `<Request>` must contain a `<Headers>` element, even an empty one, and an absolute `<URL>`. `<Body>` may be text, JSON or XML.

```xml
  <APICalls>
    <APICall>
      <Request name="VerifyRequest" method="POST">
        <URL>{{VerifyURL}}</URL>
        <Headers>
          <Header key="Content-Type">application/json</Header>
        </Headers>
        <Body>
          {
            "Username": "{{Username}}",
            "Password": "{{Password|JsonEscape}}"
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

Represents CPM actions. In each chain, API Requests are declared for top-to-bottom execution. The chain `name` is a fixed, lowercase CPM action:

| Chain | When CPM runs it |
|:---|:---|
| `verifypass` | Verify the stored credential |
| `logon` | Log on with the account |
| `changepass` | Change the credential (required) |
| `prereconcilepass` | Prepare for reconciliation |
| `reconcilepass` | Reset the credential using the reconcile account |
| `deletepass` | Delete the previous credential after a successful Change — AccessKeys platforms |
| `deletepassafterreconcile` | Delete the previous credential after a successful Reconcile — AccessKeys platforms |

For `ManagementType=AccessKeys` platforms where the target creates new keys rather than rotating them, implement `deletepass` and `deletepassafterreconcile` so old keys do not accumulate (check 5.5).

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

### Placeholders

Placeholders use double braces and resolve at runtime:

| Form | Meaning |
|:---|:---|
| `{{ParameterName}}` | Looks in the target account, then the platform; otherwise a `<Parameter>` declared earlier in the flow |
| `{{password}}`, `{{newpassword}}`, `{{keyid}}` | Current credential, new credential, AccessKeys key ID |
| `{{AccountType\ParameterName}}` | A specific account: `targetaccount`, `logonaccount`, `reconcileaccount`, `extraaccount`, `masteraccount`, `usageaccount`, `platform` |
| `{{logonaccountORtargetaccount\username}}` | First match, left to right (`OR` uppercase, account types lowercase) |
| `{{Name\|JsonEscape:urlEncode}}` | Modifiers, applied left to right: `JsonEscape`, `urlEncode`, `toUpper`, `toLower` |

Give locally defined parameters names that do not exist on the target account — CPM parameters are resolved first and would override them.

---

## 5. Key Considerations for Integration Development

- **Authentication Methods:** Access token authentication is a common and more secure method where a client first sends credentials to a login endpoint to receive an access token. This token is then included in the Authorization header of subsequent API requests for a limited time. The framework supports `Authorization: Basic {{username}}:{{password}}`, `Authorization: Bearer {{BearerToken}}`, and a header in whatever form the target API requires (for example `<Header key="Authorization">{{authToken}}</Header>`). **For certification, check 4.2 restricts plugins to Basic or Bearer** — if your target API accepts only another scheme, raise it with your Idira Technical Alliances contact before you build.

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

Sections 8–10 use the Self-Hosted CPM paths. On Privilege Cloud, the same `bin` folder is on the CPM of the customer's connector server.

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
   - Start from the sample platform files in the framework zip (`Policy-SampleRestAPIPlatform.ini` and `.xml`, Section 3). Copy and rename them to `Policy-YourPluginName.ini` and `Policy-YourPluginName.xml`.
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
| 1.3 | 2026-10-08 | **[Fixed]** Placeholder syntax is `{{Name}}` (double braces) throughout; every example used `((Name))`, which the framework does not resolve. **[Added]** Prerequisites and deployment (Section 3) for both Privilege Cloud and Self-Hosted, including the framework files by their real names (`CyberArk.Extensions.Generic.Plugin.RestAPI.dll`, `CyberArk.Extensions.Generic.Infra.RestAPI.dll`); `ManagementType`; all seven chain actions including `deletepass` and `deletepassafterreconcile`; parameter attributes including `secure` and `validationPattern`; placeholder scopes and modifiers; that `<Headers>` is mandatory in every request; working reference links. **[Updated]** Authentication guidance states what the framework supports and what check 4.2 accepts. A plugin written with `((…))` placeholders must be updated | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the misread that makes every other detail moot: this kit ships **no partner code** — the deliverable is an XML configuration file the CPM framework executes, so generated client code in any language is the wrong artefact — and the direction is outbound, with Idira calling the partner, the inverse of the Secrets Management kits. It records the four mandatory XML sections against the checks that grade each, that chain names are fixed lowercase CPM verbs (`verifypass` / `changepass` / `reconcilepass`), the `((Name))` placeholder syntax with its `|JsonEscape` modifier, the easily-omitted `secure="true"` attribute, the local `run_NETInvoker_API.cmd` harness with its `[extrapass3]` reconciliation section, three-file packaging, and that the literal `CyberArk` in the installed filesystem paths must not be rebranded or every command in Sections 8–10 breaks. Three things are recorded rather than resolved: a **discrepancy** — Section 8's `SearchURL` uses `{{Username}}` in braces where every other example uses `((…))`; a **contradiction** — Section 5 permits `Token` and `X-API-Key` header formats while check 4.2 restricts certified plugins to Basic or Bearer, and the checklist governs; and the **deployment-scope** question, since every procedure here is on-box Windows Self-Hosted while the checklist certifies Privilege Cloud. Five graded identifiers are recorded as gaps with no implementation path in this guide: both `Idira.Extensions.Generic.*.RestAPI.dll` assemblies, `Deletepass` / `Deletepassafterreconcile`, `validationPattern`, and telemetry in its entirety. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed; the gaps and conflicts are documented, not closed. — Idira Technical Alliances |
