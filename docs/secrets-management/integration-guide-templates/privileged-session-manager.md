---
title: "{Vendor} {Target} session connector for Idira Privileged Access Manager"
vendor: "{Vendor}"
idira_products: [pam]
idira_services: [psm]
archetype: session-management
audience: PAM Administrator
built_by: partner          # partner, idira-rd, or community
stage: release
last_verified: "{LastVerifiedDate}"
# source_legacy_id: migrated guides only. Idira sets this field; partners leave it commented out.
---

> **Draft for partner feedback.** This template is open for review and may change before it is final. Send feedback to your Idira Technical Alliances contact. Delete this note when you copy the template.

<!-- AUTHOR GUIDANCE (this block and every AUTHOR comment are hidden in the published guide; Idira removes them at publish)

WHO WRITES WHAT
- PRE-WRITTEN: every sentence, step, table row, and code sample without a {Placeholder}. Idira verified these against current Idira documentation. Do not reword them. Delete only what an AUTHOR comment tells you to delete.
- PARTNER FILLS: every {Placeholder}. Placeholders are one {PascalCase} word.
- CUSTOMER SUPPLIES: every <angle-bracket> value. Leave these as they are.

CONNECTOR
- The connector ships as one Privileged Session Manager connector package (zip) that the customer imports through Manage Connectors. Universal connectors are written in AutoIt.
- The package must not contain malicious code, and must not expose or store sensitive data on the Privileged Session Manager server.

DEPLOYMENT MODELS
- Where Self-Hosted and SaaS differ, a step has a "Self-Hosted:" line and a "SaaS:" line. Keep both.

STYLE
- Second person, imperative, present tense. No marketing claims and no em dashes. Use {Target}'s UI labels in bold, exactly as they appear on screen.

BEFORE YOU SUBMIT
- This command must return nothing: perl -0pe 's/<!--.*?-->//gs' <your-file>.md | grep -oE '\{[A-Z][A-Za-z0-9]+\}'
- Send your business and technical contacts to Idira separately. They are not published.
-->

# {Vendor} {Target} session connector for Idira Privileged Access Manager

## Solution Summary

<!-- AUTHOR: PARTNER FILLS {SolutionDescription}: two to four sentences on which sessions the connector opens and why. Fill the diagram slot and every row of the table. {DiagramFile} shows the user, the Privileged Session Manager server running the client, the Vault, and {Target}, with the protocol and port to {Target}. -->

{SolutionDescription}

This connector lets the Privileged Session Manager open sessions to {Target}. The connector launches the client on the Privileged Session Manager server and signs in with an account from a Safe in Idira® Privileged Access Manager Self-Hosted or Idira Privileged Access Manager SaaS by Palo Alto Networks. The Privileged Session Manager isolates and records the session.

![Privileged Session Manager session flow to {Target}]({DiagramFile})

| Session | {Target} |
|:---|:---|
| Connection component ID | {ConnectionComponentID} |
| Client on the Privileged Session Manager server | {ClientApplication} |
| Protocol and port to {Target} | {SessionProtocol} |
| Automatic sign-in | {AutoLogon} |

<!-- AUTHOR: {AutoLogon}: "Supported", or what the user sees instead, for example "The user enters the one-time code". -->

---

## Vendor and target

| Field | Value |
|:---|:---|
| {Target} versions | {TargetVersions} |
| {Vendor} documentation | {VendorDocsURL} |

---

## Before you begin

### Idira requirements

- A Privileged Session Manager server that can reach {Target} over {SessionProtocol}.
- A platform for the {Target} accounts.
- In the master policy, the **Session Management** rules **Require privileged session monitoring and isolation** (inactive by default) and **Record and save session activity** (active by default) are active for that platform.
- **Permissions:**
  - **Self-Hosted:** an administrative Password Vault Web Access (PVWA) user, to manage platforms and connectors.
  - **SaaS:** an Idira Identity Security Platform user with the **Privilege Cloud Administrators** role, to manage platforms and connectors.
  - **Both:** sign-in access to each Privileged Session Manager server, to install the client and edit its AppLocker rules, and the **Add accounts** authorization in the Safe for the {Target} accounts.
- The {Vendor} {Target} connector package, downloaded from the Idira Marketplace.

### {Target} requirements

<!-- AUTHOR: PARTNER FILLS every row. Write "None" where a row does not apply. -->

| Requirement | Details |
|:---|:---|
| Client to install on each Privileged Session Manager server | {ClientInstall} |
| Which Privileged Session Manager servers need the client | {PSMServerScope} |
| Permissions the account needs on {Target} | {TargetAccountPermissions} |
| Network path from Privileged Session Manager to {Target} | {TargetNetworkPath} |
| Other prerequisites | {TargetOtherPrerequisites} |

---

## Configuration

Complete **Prepare the Privileged Session Manager servers**, and then **Configure Idira**.

### Prepare the Privileged Session Manager servers

<!-- AUTHOR: Step 1 is PARTNER FILLS. Step 2 is PRE-WRITTEN except {ClientExecutables}. -->

On each Privileged Session Manager server:

#### Step 1: Install the client

{ClientInstallSteps}

#### Step 2: Allow the client in AppLocker

1. In the `Hardening` folder of the Privileged Session Manager installation, remove the read-only permission from `PSMConfigureAppLocker.xml`, and open it.
2. In the `AllowedApplications` section, add one line for each executable the connector runs: {ClientExecutables}

   ```xml
   <Application Name="<name>" Type="Exe" Path="<full-path-to-executable>" Method="Hash" />
   ```

3. Save the file. In PowerShell, in the same `Hardening` folder, run `.\PSMConfigureAppLocker.ps1`.

### Configure Idira

<!-- AUTHOR: PRE-WRITTEN except the {Placeholders}. -->

#### Step 1: Import the connector

<!-- AUTHOR: If your integration ships no connector package and runs alongside an existing connection component instead, for example an agent installed on the Privileged Session Manager server, delete this step. Name that component in {ConnectionComponentID}, describe the agent install in Prepare the Privileged Session Manager servers, and replace the first sentence of the Solution Summary's pre-written paragraph with: "The {Vendor} {Target} integration runs on the Privileged Session Manager server alongside the {ConnectionComponentID} connection component." -->

1. Sign in:
   - **Self-Hosted:** to PVWA, as an administrative user.
   - **SaaS:** to the Idira Identity Security Platform, as a user with the **Privilege Cloud Administrators** role.
2. Open the platform list:
   - **Self-Hosted:** click **Administration** > **Platform Management**.
   - **SaaS:** in the **Manage** space, go to **Policies** > **PAM policies** > **Account platforms**.
3. Next to the platform for the {Target} accounts, click the ellipsis button, and then **Manage Connectors**.
4. If you are prompted, select the Privileged Session Manager server that manages the connectors, and click **Next**.
5. Upload the {Vendor} {Target} connector package.

#### Step 2: Review the connection component parameters

<!-- AUTHOR: PARTNER FILLS. List only the parameters a customer may need to change. Delete the table if there are none. -->

| Parameter | Default | Description |
|:---|:---|:---|
| {ParameterName} | {ParameterDefault} | {ParameterDescription} |

#### Step 3: Add the account

1. Add the {Target} account to its Safe:
   - **Self-Hosted:** in PVWA, click **Accounts** > **Add Account**.
   - **SaaS:** in the **Manage** space, go to **Inventory** > **Means of access** > **Managed accounts**, and click **Add account**.
2. Select the platform from Configure Idira, Step 1, and the Safe, and enter these properties:

   <!-- AUTHOR: PARTNER FILLS. One row per account property the connector uses. -->

   | Property | Value |
   |:---|:---|
   | {PropertyName} | {PropertyValue} |

---

## Validate the integration

<!-- AUTHOR: PARTNER FILLS {SessionValidation}. -->

On a test account:

1. On the account, select the {Target} connection component, and click **Connect**.
2. Confirm the session opens to {Target}: {SessionValidation}
3. Close the session, and confirm its recording is available:
   - **Self-Hosted:** in PVWA, go to **Monitoring** > **Recordings**.
   - **SaaS:** in the **Audit and Reports** space.

---

## Troubleshooting

<!-- AUTHOR: The Idira rows are PRE-WRITTEN. PARTNER FILLS the last row with the most common {Target}-side failure. Add rows if needed. -->

On the Privileged Session Manager server, `PSMConsole.log` in `PSM\Logs` has Privileged Session Manager errors. The connection client log, `<SessionID>.<connection component>.log`, is in `PSM\Logs\Components`.

| Symptom | Cause | Fix |
|:---|:---|:---|
| Windows blocks the client when the session starts | The client executable has no AppLocker allow rule. | Complete **Allow the client in AppLocker**. |
| The connector is not available on the account | The connector is not imported for the account's platform. | Complete Step 1 of **Configure Idira** for that platform. |
| {PartnerSymptom} | {PartnerCause} | {PartnerFix} |

---

## Known issues and limitations

<!-- AUTHOR: PARTNER FILLS. Keep the sentence if there are none. Otherwise list one per bullet: each known issue, with affected versions and the workaround, and each limitation, meaning anything a customer could expect the integration to do that it does not. -->

No known issues or limitations.

---

## Support

<!-- AUTHOR: PARTNER FILLS. Publish a support channel, not named individuals. -->

| Area | Supported by | Contact |
|:---|:---|:---|
| The connector, the client, and {Target} errors | {Vendor} | {SupportURL}, {SupportEmail}, {SupportPhone}, {SupportHours} |
| Privileged Session Manager, Vault, platforms, and Safes | Idira Technical Support | Your usual Technical Support channel |
