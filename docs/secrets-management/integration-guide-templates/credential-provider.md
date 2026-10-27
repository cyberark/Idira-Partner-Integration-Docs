---
title: "{Vendor} {Product} integration with Idira Credential Providers"
vendor: "{Vendor}"
idira_products: [secrets-management]
idira_services: [cp, ccp]   # keep only the variants you support
archetype: credential-retrieval
audience: Security Administrator
built_by: partner          # partner, idira-rd, or community
stage: release
last_verified: "{LastVerifiedDate}"
# source_legacy_id: migrated guides only. Idira sets this field; partners leave it commented out.
---

> **Draft for partner feedback.** This template is open for review and may change before it is final. Send feedback to your Idira Technical Alliances contact. Delete this note when you copy the template.

<!-- AUTHOR GUIDANCE (this block and every AUTHOR comment are hidden in the published guide; Idira removes them at publish)

WHO WRITES WHAT
- PRE-WRITTEN: every sentence, step, table row, and code sample without a {Placeholder}. Idira verified these against current Idira documentation. Do not reword them. Delete only what an AUTHOR comment tells you to delete.
- PARTNER FILLS: every {Placeholder}. Placeholders are one {PascalCase} word. Curly braces inside JSON code samples are not placeholders.
- CUSTOMER SUPPLIES: every <angle-bracket> value. Leave these as they are.

VARIANTS AND DEPLOYMENT MODELS
- Items labeled "Credential Provider only" or "Central Credential Provider only" apply to that variant. If you support one variant, delete the items for the other, and then delete the "Applies to" labels and columns.
- Where Self-Hosted and SaaS differ, a step has a "Self-Hosted:" line and a "SaaS:" line. Keep both.
- Keep only the authentication methods {Product} supports in Configure Idira, Step 2.

STYLE
- Second person, imperative, present tense. No marketing claims and no em dashes. Use your product's UI labels in bold, exactly as they appear on screen.

BEFORE YOU SUBMIT
- This command must return nothing: perl -0pe 's/<!--.*?-->//gs' <your-file>.md | grep -oE '\{[A-Z][A-Za-z0-9]+\}'
- Send your business and technical contacts to Idira separately. They are not published.
-->

# {Vendor} {Product} integration with Idira Credential Providers

## Solution Summary

<!-- AUTHOR: PARTNER FILLS {SolutionDescription}: two to four sentences on what {Product} uses the credential for and when. Fill the diagram slot and every row of the table. {DiagramFile} shows where the Credential Provider or Central Credential Provider sits in your product's architecture. {IntegrationLocation}: endpoint, mid-tier server, or central server, for example "One central server per site". -->

{SolutionDescription}

{Product} retrieves these credentials at runtime from Idira® Credential Providers by Palo Alto Networks instead of storing them in its own configuration. The credentials stay in Safes in Idira Privileged Access Manager Self-Hosted or Idira Privileged Access Manager SaaS, where they can be rotated on a schedule.

- **Credential Provider:** an agent on the {Product} machine. {Product} calls it through the Application Password SDK (C, Java, or .NET) or the CLI Application Password SDK.
- **Central Credential Provider:** an agentless REST web service, `AIMWebService`, on a Windows IIS server that also runs a Credential Provider.

![{Product} credential retrieval flow with Idira Credential Providers]({DiagramFile})

| Retrieval behavior | {Product} |
|:---|:---|
| What triggers a retrieval | {RetrievalTrigger} |
| How often {Product} retrieves | {RetrievalFrequency} |
| Whether {Product} caches the credential | {ProductCaching} |
| Whether {Product} shows the credential to its own users, and to whom | {CredentialExposure} |
| Where {Product} calls Idira from, and how many instances in a typical deployment | {IntegrationLocation} |

---

## Vendor and application

| Field | Value |
|:---|:---|
| {Product} versions | {VendorVersions} |
| {Vendor} documentation | {VendorDocsURL} |

---

## Before you begin

### Idira requirements

- **Credential Provider:** installed on each {Product} machine and connected to your Vault. See [Install the Credential Provider](https://docs.cyberark.com/credential-providers/latest/en/content/cp%20and%20ascp/installing-cp.htm).
- **Central Credential Provider:** installed on a Windows IIS server with its Credential Provider, connected to your Vault, with SSL required on `AIMWebService`. See [Install the Central Credential Provider](https://docs.cyberark.com/credential-providers/latest/en/content/ccp/installation.htm).
- **Permissions:**
  - **Self-Hosted:** a Password Vault Web Access (PVWA) user with the **Manage Users** permission.
  - **SaaS:** an Idira Identity Security Platform user with the **Privilege Cloud Administrators** role.
  - **Both:** the **Add accounts** and **Manage Safe Members** authorizations in the Safe that holds the credentials.

### {Product} requirements

<!-- AUTHOR: PARTNER FILLS every row. Write "None" where a row does not apply. {ProductNetworkPath}: each {Product} component that calls the Central Credential Provider, and the port, or "Runs on the Credential Provider machine". -->

| Requirement | Details |
|:---|:---|
| Network path from {Product} to Idira | {ProductNetworkPath} |
| Certificate format {Product} accepts, and where it stores the certificate | {ProductCertificateFormat} |
| {Product} role that configures the integration | {ProductAdminRole} |
| Vault user {Product} uses to add or update accounts, if any, and its Safe authorizations | {ProductVaultWriteAccess} |
| Other prerequisites | {ProductOtherPrerequisites} |

---

## Configuration

Complete **Configure Idira**, and then **Configure {Product}**.

### Configure Idira

<!-- AUTHOR: PRE-WRITTEN. Fill only the {Placeholders}. {AppID} is the application ID you recommend, for example "CCP_Vendor_Product": English letters, digits, and underscores, fewer than 128 characters, no ampersand. -->

#### Step 1: Add the application

1. Sign in:
   - **Self-Hosted:** to PVWA, as a user with the **Manage Users** permission.
   - **SaaS:** to the Idira Identity Security Platform, as a user with the **Privilege Cloud Administrators** role.
2. Open the application list:
   - **Self-Hosted:** click **Applications** > **Add Application**.
   - **SaaS:** in the **Manage** space, go to **Inventory** > **Identities** > **CP Applications**, and click **Add Application**.
3. In **Name**, enter `{AppID}`. In **Description**, enter `{Product}`.
4. Click **Add**.

If you use a different application ID, use it wherever `{AppID}` appears. It must be unique and under 128 characters, with no non-English letters and no ampersand (`&`).

#### Step 2: Add application authentication

1. On the application's **Authentication** tab, click **Add**.
2. Add each method {Product} uses. Use OS user or allowed machines authentication, or both, in addition to any other method.

   | Method | Applies to | Value |
   |:---|:---|:---|
   | **OS user** | Both variants | The OS user that runs {Product}: {ProductServiceAccount}. On Windows, include the domain: `<DOMAIN>\<username>`. On the Central Credential Provider, {Product} sends this user's Windows credentials through IIS Windows authentication. |
   | **Application path** | Credential Provider only | The full path of the {Product} file that calls the Credential Provider: {ProductExecutablePath}. To register a folder, select **Path is folder**. |
   | **Hash** | Credential Provider only | The hash of {ProductHashTarget}, from the GetAppInfo utility for how {Product} calls the Credential Provider: `AIMGetAppInfo` (CLI), `JavaAIMGetAppInfo` (Java), `NetAIMGetAppInfo` (.NET Framework), or `NetCoreAAMGetAppInfo` (.NET Core). On Windows, the first two are in `ApplicationPasswordProvider\Utils`. On UNIX, they are in `/opt/CARKaim/bin`. |
   | **Certificate Serial Number** | Central Credential Provider only | The serial number of the client certificate {Product} presents. Only `a-f`, `A-F`, `0-9`, and `#`. |

   To register more machines, OS users, paths, or hashes than the application's 4,000-character limit allows, select **Allow extended authentication restrictions** on the application.

3. **Certificate attribute (Central Credential Provider only):** this method is not available on the **Authentication** tab. Add it once with the REST API, as the user from Step 1. The bearer or session token authorizes this one administrative call only. {Product} does not use a token to retrieve credentials.
   - **Self-Hosted:** `POST https://<pvwa-server>/PasswordVault/WebServices/PIMServices.svc/Applications/{AppID}/Authentications/`, with `Authorization: <session token from Logon>`
   - **SaaS:** `POST https://<subdomain>.privilegecloud.cyberark.cloud/PasswordVault/WebServices/PIMServices.svc/Applications/{AppID}/Authentications/`, with `Authorization: Bearer <token>`

   ```http
   POST <address-for-your-deployment>
   Content-Type: application/json

   {
     "authentication": {
       "AuthType": "certificateattr",
       "Subject": ["<attribute>=<value>"],
       "Issuer": ["<attribute>=<value>"],
       "SubjectAlternativeName": ["DNS Name=<value>"]
     }
   }
   ```

#### Step 3: Add allowed machines

On the application's **Allowed Machines** tab, add the IP address, hostname, DNS name, or CIDR subnet of each machine that sends requests for {Product}: {ProductMachines}

#### Step 4: Add the accounts to a Safe

Add each account {Product} needs to the Safe for {Product}: {AccountTypes}

- **Self-Hosted:** in PVWA, add the accounts to the Safe.
- **SaaS:** in the **Manage** space, go to **Inventory** > **Means of access** > **Managed accounts**, and click **Add account**. Select the system type, platform, and Safe, and enter the account properties.

#### Step 5: Add the Safe members

1. Open the Safe's members:
   - **Self-Hosted:** in PVWA, go to **Policies** > **Access Control (Safes)**, select the Safe, and click **Members**.
   - **SaaS:** in the **Manage** space, go to **Policies** > **Access to target** > **Safes**. Select the Safe, click **Members** > **Add Members**, and set **Source** to **System component users**.
2. Add these members:

   | Member | Authorizations |
   |:---|:---|
   | The provider user of each Credential Provider that serves {Product}, `Prov_<hostname>` by default. For the Central Credential Provider, the provider user on the IIS server. | **List accounts**, **Retrieve accounts**, **View Safe Members** |
   | The application `{AppID}` | **Retrieve accounts** |

3. If several Credential Providers serve {Product}, add their provider users to a group, and add the group to the Safe once with the same authorizations.
4. If the Safe uses object-level access, give the provider users and the application access to each account {Product} retrieves.

#### Step 6: Configure IIS

**Applies to:** Central Credential Provider only.

<!-- AUTHOR: Keep the item for each authentication method {Product} uses with the Central Credential Provider, delete the other, and renumber. -->

On the Central Credential Provider server, in IIS Manager, select **Sites** > **Default Web Site** > **AIMWebService**, and then:

1. **Client certificate:** in **SSL Settings**, under **Client certificates**, select **Require**. Import the CA that signed the {Product} client certificate into the server's trusted certificate store.
2. **OS user:** make sure the **Windows Authentication** role service is installed. Enable **Authentication** > **Windows Authentication**. In **Advanced Settings**, disable **Kernel mode authentication**. In **Providers**, keep only **Negotiate** and the provider your organization requires, for example **Negotiate:Kerberos**. Disable all other authentication types.
3. Run `iisreset`.

### Configure {Product}

#### Step 1: Install the {Product} integration

<!-- AUTHOR: PARTNER FILLS. Mandatory. Where the customer gets the integration package and how to install it, in numbered steps. If the integration is built in to {Product}, write "The integration is built in to {Product}. Nothing to install." -->

{ProductInstallSteps}

#### Step 2: Connect {Product} to Idira

<!-- AUTHOR: PARTNER FILLS. Choose ONE option, delete the other and its label.
     Option A: link to your published configuration guide. It must use the application ID and the query rules from this guide.
     Option B: write the steps here, keep the mapping table, and add one screenshot per slot. Delete mapping rows for a variant you do not support.
     Keep the query rules, query patterns, and request parameters with either option. -->

**Option A**

Follow the [{Product} configuration guide]({ProductConfigDocsURL}). Use the application ID `{AppID}`, and define each query by the query rules below.

**Option B**

As a {Product} user with the {ProductAdminRole} role:

1. Go to **{IntegrationMenuPath}**, enter these values, and save:

   | Idira value | Applies to | Where you get it | {Product} field |
   |:---|:---|:---|:---|
   | Central Credential Provider URL | Central Credential Provider only | `https://<ccp-server>/AIMWebService/api/Accounts`, on the IIS server that hosts `AIMWebService`, not the Vault | {CCPAddressField} |
   | Application ID | Both variants | `{AppID}`, from Configure Idira, Step 1 | {AppIDField} |
   | Client certificate and private key | Central Credential Provider only | The certificate from Configure Idira, Step 2 | {ClientCertificateField} |
   | CA certificate | Central Credential Provider only | The CA that signed the IIS server certificate, not the client certificate | {CACertificateField} |
   | Java Application Password SDK location | Credential Provider only | Linux: `/opt/CARKaim/sdk`. Windows: `<CP installation path>\CyberArk\ApplicationPasswordSdk`. | {SDKPathField} |

   ![{Product} connection settings for Idira Credential Providers]({ScreenshotConnection})

2. Go to **{ObjectMenuPath}**. For each object, enter the query properties that identify its account, and save: {QueryFields}

   ![{Product} credential query settings]({ScreenshotObject})

**Query rules**

- The query includes the application ID and at least one other property. Include `Safe`, and `Object` or `UserName`: without `Safe` or `Object`, the query runs as a regular-expression search, which is slower.
- The query must match exactly one account.

**Query patterns**

<!-- AUTHOR: PARTNER FILLS. One row per kind of credential {Product} retrieves, with the properties {Product} sends. Common patterns: domain or standard credentials (UserName, Address, and PolicyID, plus Safe); local Windows or UNIX accounts (UserName and PolicyID, plus Safe, with Address set to the machine {Product} is working on); credentials that UserName, Address, and PolicyID cannot identify uniquely (Safe and Object). -->

| Credential {Product} retrieves | Properties {Product} sends |
|:---|:---|
| {CredentialUseCase} | {QueryProperties} |
- `Folder` is supported only in Idira Privileged Access Manager Self-Hosted.

**Request parameters**

<!-- AUTHOR: PARTNER FILLS the last column. Write "Not exposed" if {Product} does not let the customer set the parameter. If {Product} uses only the Credential Provider, delete this table. -->

**Applies to:** Central Credential Provider only.

| Parameter | What it does | {Product} field |
|:---|:---|:---|
| `Reason` | The reason for the retrieval, recorded in the Credential Provider audit log | {ReasonField} |
| `ConnectionTimeout` | How many seconds the Central Credential Provider tries to retrieve the password from the Vault. Default: 30 | {ConnectionTimeoutField} |
| `QueryFormat` | `Exact` (default) or `Regexp` | {QueryFormatField} |
| `FailRequestOnPasswordChange` | Whether the request fails while a password change is in progress. Default: `False` | {FailRequestField} |

Send `Reason` with each request, so the audit log records why {Product} retrieved the password.

---

## Validate the integration

<!-- AUTHOR: PARTNER FILLS. Validate in {Product}, not in Idira. -->

In {Product}:

1. **Connection:** {ProductConnectionTest}
2. **Retrieval:** {ProductRetrievalTest}
3. **Password change:** change a test account's password in Idira Privileged Access Manager, and confirm {Product} uses the new password: {RotationBehavior}
4. **Audit:** {ProductAuditLog}

---

## Troubleshooting

<!-- AUTHOR: The Idira rows are PRE-WRITTEN. Delete rows for a variant or method you do not support. PARTNER FILLS the last row with the most common {Product}-side failure. Add rows if needed. -->

Check the Credential Provider `APPConsole.log` and `APPTrace.log` first. For the Central Credential Provider web service, turn on logging in its `Web.config` to write `AIMWSTrace.log`, and turn it off and delete the log when you finish troubleshooting.

| Symptom | Applies to | Cause | Fix |
|:---|:---|:---|:---|
| `APPAP306E` App failed on authentication check (403) | Both variants | The request does not match a registered authentication method. | Compare the OS user, path, hash, machine, or certificate with the **Authentication** and **Allowed Machines** tabs. |
| `APPAP008E` User is not defined (403) | Both variants | The application ID does not exist. | Check that `{AppID}` matches the application **Name** exactly. |
| `APPAP004E` Safe not found (404) | Both variants | The Safe name is wrong, or a member from Configure Idira, Step 5, is missing. | Check the Safe name and the Safe members. |
| `APPAP227E`, `APPAP228E`, or `APPAP229E` Too many objects (400) | Both variants | The query matches more than one account. | Add `Safe` and `Object`, or more properties. |
| `APPAP282E` Password is currently being changed by the CPM (500) | Both variants | A password change is in progress. | Retry after a short wait. |
| `APPAP007E` or `APPBC007E` Connection failed | Both variants | The Credential Provider cannot reach the Vault. | Check that the Credential Provider service is running and TCP 1858 to the Vault is open. |
| A removed permission still works | Both variants | The Credential Provider returns the password from its cache. | Wait for the next cache refresh, or force one with `appprvmgr`. |
| `AIMWS030E` Invalid query format (400) | Central Credential Provider only | The query contains unsupported characters. | Remove `;` from values, and `+`, `&`, or `%` from URL values. |
| 401 from IIS | Central Credential Provider, OS user only | Windows Authentication is off on `AIMWebService`, or {Product} sent no Windows credentials. | Complete the OS user item in Configure Idira, Step 6. |
| TLS error to the Central Credential Provider | Central Credential Provider only | {Product} does not trust the IIS server certificate, or uses the client certificate as its CA bundle. | Give {Product} the CA that signed the IIS server certificate. |
| {PartnerSymptom} | Both variants | {PartnerCause} | {PartnerFix} |

---

## Known issues and limitations

<!-- AUTHOR: PARTNER FILLS. Keep the sentence if there are none. Otherwise list one per bullet: each known issue, with affected versions and the workaround, and each limitation, meaning anything a customer could expect the integration to do that it does not. -->

No known issues or limitations.

---

## Support

<!-- AUTHOR: PARTNER FILLS. Publish a support channel, not named individuals. -->

| Area | Supported by | Contact |
|:---|:---|:---|
| {Product} configuration, behavior, and errors | {Vendor} | {SupportURL}, {SupportEmail}, {SupportPhone}, {SupportHours} |
| Credential Providers, Vault, applications, and Safes | Idira Technical Support | Your usual Technical Support channel |
