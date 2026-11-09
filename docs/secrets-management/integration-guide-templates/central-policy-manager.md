---
title: "{Vendor} {Target} password management plugin for Idira Privileged Access Manager"
vendor: "{Vendor}"
idira_products: [pam]
idira_services: [cpm]
archetype: credential-rotation
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

PLUGIN
- The plugin ships as one platform package (zip): the platform policy (.ini), the platform settings (.xml), and any plugin files, such as prompts and process files or DLLs. All files sit in the zip root, with no folders, and the zip is no larger than 20 MB.
- New plugins built on the WSChains framework are not accepted. If you are migrating the guide for an existing WSChains plugin, contact Idira before you submit.
- If you certified the plugin on the Secrets Rotation Service (SRS) instead of the Central Policy Manager, contact Idira before you submit.

DEPLOYMENT MODELS
- Where Self-Hosted and SaaS differ, a step has a "Self-Hosted:" line and a "SaaS:" line. Keep both.
- Delete the rows and steps for actions or linked accounts the plugin does not support.

STYLE
- Second person, imperative, present tense. No marketing claims and no em dashes. Use {Target}'s UI labels in bold, exactly as they appear on screen.

BEFORE YOU SUBMIT
- This command must return nothing: perl -0pe 's/<!--.*?-->//gs' <your-file>.md | grep -oE '\{[A-Z][A-Za-z0-9]+\}'
- Send your business and technical contacts to Idira separately. They are not published.
-->

# {Vendor} {Target} password management plugin for Idira Privileged Access Manager

## Solution Summary

<!-- AUTHOR: PARTNER FILLS {SolutionDescription}: two to four sentences on which {Target} credentials the plugin manages and why. Fill the diagram slot and every row of the table. {DiagramFile} shows the Central Policy Manager, the Vault, and {Target}, and the protocol and port the plugin uses to reach {Target}. -->

{SolutionDescription}

This plugin lets the Central Policy Manager verify, change, and reconcile the passwords of {Target} accounts. The accounts are stored in Safes in Idira® Privileged Access Manager Self-Hosted or Idira Privileged Access Manager SaaS by Palo Alto Networks, and the Central Policy Manager rotates them by the platform's policy.

![Central Policy Manager password management flow for {Target}]({DiagramFile})

| Plugin behavior | {Target} |
|:---|:---|
| Verify | {VerifySupport} |
| Change | {ChangeSupport} |
| Reconcile | {ReconcileSupport} |
| Delete | {DeleteSupport} |
| How the Central Policy Manager connects to {Target} | {ConnectionMethod} |
| Plugin type | {PluginType} |

<!-- AUTHOR: Write "Supported" or "Not supported" for each action, and delete the matching steps under Validate the integration. {ConnectionMethod}: protocol and port, for example "REST API over HTTPS, TCP 443". {PluginType}: for example "Terminal plugin (prompts and process files)" or ".NET plugin". -->

---

## Vendor and target

| Field | Value |
|:---|:---|
| {Target} versions | {TargetVersions} |
| {Vendor} documentation | {VendorDocsURL} |
| Platform ID | {PlatformID} |

---

## Before you begin

### Idira requirements

- A Central Policy Manager that can reach {Target} over {ConnectionMethod}.
- **Permissions:**
  - **Self-Hosted:** an administrative Password Vault Web Access (PVWA) user, to import the platform.
  - **SaaS:** an Idira Identity Security Platform user with the **Privilege Cloud Administrators** role, to import the platform.
  - **Both:** the **Add accounts** authorization in the Safe for the {Target} accounts. To link a reconcile or logon account, also **Retrieve accounts** and **Update password properties**.
- The {Vendor} {Target} platform package, downloaded from the Idira Marketplace.

### {Target} requirements

<!-- AUTHOR: PARTNER FILLS every row. Write "None" where a row does not apply. -->

| Requirement | Details |
|:---|:---|
| Permissions the managed account needs | {TargetAccountPermissions} |
| Network path from the Central Policy Manager to {Target} | {TargetNetworkPath} |
| Prerequisites on the Central Policy Manager server, such as an SDK or runtime | {CPMServerPrerequisites} |
| Other prerequisites | {TargetOtherPrerequisites} |

### Linked accounts

<!-- AUTHOR: PARTNER FILLS. Write "Yes" or "No" in Supported and Required. Delete the table if the plugin uses no linked accounts. -->

| Linked account | Supported | Required | Platforms it can use | Permissions it needs on {Target} |
|:---|:---|:---|:---|:---|
| Logon account | {LogonSupported} | {LogonRequired} | {LogonPlatforms} | {LogonPermissions} |
| Reconcile account | {ReconcileAccountSupported} | {ReconcileAccountRequired} | {ReconcilePlatforms} | {ReconcileAccountPermissions} |

---

## Configuration

Complete **Configure {Target}**, and then **Configure Idira**.

### Configure {Target}

<!-- AUTHOR: PARTNER FILLS. Mandatory. The steps that prepare {Target} for the Central Policy Manager: create the managed and reconcile accounts, grant their permissions, and open the network path. Use numbered steps. Write "No configuration needed in {Target}." if none apply. -->

{TargetConfigurationSteps}

### Configure Idira

<!-- AUTHOR: PRE-WRITTEN except the {Placeholders}. -->

#### Step 1: Create the custom account properties

<!-- AUTHOR: Delete this step if the platform uses no custom account properties. PARTNER FILLS {CustomProperties}: name and type (text, numeric, or list) of each. -->

**Applies to:** Self-Hosted. Do this before you import the platform.

The platform uses these custom account properties: {CustomProperties}

1. Sign in to the PrivateArk Client as a user with the **Manage Vault File Categories** authorization.
2. Click **File** > **Server File Categories**, and then click **New**.
3. Enter the property name and type, and click **OK**. Repeat for each property.

#### Step 2: Import the platform

1. Sign in:
   - **Self-Hosted:** to PVWA, as an administrative user.
   - **SaaS:** to the Idira Identity Security Platform, as a user with the **Privilege Cloud Administrators** role.
2. Open the platform list:
   - **Self-Hosted:** click **Administration** > **Platform Management**.
   - **SaaS:** in the **Manage** space, go to **Policies** > **PAM policies** > **Account platforms**.
3. Click **Import Platform**, and select the {Vendor} {Target} platform package.

The platform `{PlatformID}` appears in the platform list, active. On Self-Hosted, the plugin files are copied to the Central Policy Manager automatically.

If a custom account property is missing from the platform, edit the platform, go to **UI & Workflows** > **Properties**, right-click **Required** or **Optional**, click **Add Property**, and enter the property name.

<!-- AUTHOR: Optional. If {Target} needs a separate platform for each account type, for example to apply a different password policy, keep the next paragraph and describe the account types. Otherwise delete it. -->

To manage several {Target} account types with different policies, duplicate the platform once for each type: click the ellipsis button next to `{PlatformID}`, click **Duplicate**, enter a name and description, and click **Create**. {PlatformPerAccountType}

#### Step 3: Review the platform parameters

<!-- AUTHOR: PARTNER FILLS. List only the plugin parameters a customer may need to change. Delete the table if there are none. -->

In the platform's settings, review these parameters:

| Parameter | Description | Acceptable values | Default |
|:---|:---|:---|:---|
| {ParameterName} | {ParameterDescription} | {ParameterValues} | {ParameterDefault} |

#### Step 4: Add the account

1. Add the {Target} account to its Safe:
   - **Self-Hosted:** in PVWA, click **Accounts** > **Add Account**.
   - **SaaS:** in the **Manage** space, go to **Inventory** > **Means of access** > **Managed accounts**, and click **Add account**.
2. Select the platform `{PlatformID}` and the Safe, and enter these properties:

   <!-- AUTHOR: PARTNER FILLS. One row per account property the platform requires. -->

   | Property | Description | Acceptable values |
   |:---|:---|:---|
   | {PropertyName} | {PropertyDescription} | {PropertyValues} |

#### Step 5: Link the logon and reconcile accounts

<!-- AUTHOR: Delete this step if the plugin does not use a reconcile or logon account. -->

1. Open the account's linked accounts:
   - **Self-Hosted:** in PVWA, in **Accounts View**, click **Additional details & actions in classic interface**, and select the account. In **Account Details**, go to the **CPM** pane.
   - **SaaS:** in **Managed accounts**, select the account, and click the **Details** tab. Go to **Linked Accounts**.
2. Link each account the **Linked accounts** table marks as required.

You can also set a reconcile account on the platform, for all its accounts.

---

## Validate the integration

<!-- AUTHOR: PARTNER FILLS {TargetValidation}. Delete actions the plugin does not support. -->

On a test account:

1. Run **Verify**, and confirm the account's status updates with no error.
2. Run **Change**, and confirm the status updates. Sign in to {Target} with the new password: {TargetValidation}
3. Run **Reconcile**, and confirm the status updates.

---

## Troubleshooting

<!-- AUTHOR: The Idira rows are PRE-WRITTEN. PARTNER FILLS the last row with the most common {Target}-side failure. Add rows if needed. -->

The Central Policy Manager logs are in the `Logs` subfolder of the Password Manager installation folder: `pm.log` has all messages, and `pm_error.log` has warnings and errors. Errors from {Target} are in the third-party log, `<platform>-<Safe>-<folder>-<account>.log`, in `Logs\ThirdParty`.

| Symptom | Cause | Fix |
|:---|:---|:---|
| The third-party log has no detail | The platform's **Debug** parameter is off. | Set the platform's **Debug** parameter to **Yes**, run the action again, and read the third-party log. |
| The import fails | The zip contains folders, or is larger than 20 MB. | Put all files in the zip root, and keep the zip under 20 MB. |
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
| The plugin, {Target} configuration, and {Target} errors | {Vendor} | {SupportURL}, {SupportEmail}, {SupportPhone}, {SupportHours} |
| Central Policy Manager, Vault, platforms, and Safes | Idira Technical Support | Your usual Technical Support channel |
