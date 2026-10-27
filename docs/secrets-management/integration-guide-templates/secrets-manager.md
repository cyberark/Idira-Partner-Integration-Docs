---
title: "{Vendor} {Product} integration with Idira Secrets Manager"
vendor: "{Vendor}"
idira_products: [secrets-management]
idira_services: [secrets-manager-self-hosted, secrets-manager-saas]   # keep only the models you certified
archetype: secrets-manager
audience: DevOps / Security Engineer
built_by: partner          # partner, idira-rd, or community
stage: release
last_verified: "{LastVerifiedDate}"
# source_legacy_id: migrated guides only. Idira sets this field; partners leave it commented out.
---

> **Draft for partner feedback.** This template is open for review and may change before it is final. Send feedback to your Idira Technical Alliances contact. Delete this note when you copy the template.

<!-- AUTHOR GUIDANCE (this block and every AUTHOR comment are hidden in the published guide; Idira removes them at publish)

WHO WRITES WHAT
- PRE-WRITTEN: every sentence, step, table row, and code sample without a {Placeholder}. Idira verified these against current Idira documentation. Do not reword them. Delete only what an AUTHOR comment tells you to delete.
- PARTNER FILLS: every {Placeholder}. Placeholders are one {PascalCase} word. Curly braces inside JSON or YAML code samples are not placeholders.
- CUSTOMER SUPPLIES: every <angle-bracket> value. Leave these as they are.

DEPLOYMENT MODELS AND AUTHENTICATORS
- Where Self-Hosted and SaaS differ, a step has a "Self-Hosted:" line and a "SaaS:" line. If you certified only one deployment model, delete the other model's lines and columns. Otherwise keep both.
- Configure Idira, Step 1, has pre-written blocks for three authenticators: API key, JWT, and client certificate. Delete the blocks for authenticators you did not certify.
- If you certified AWS IAM, Azure, GCP, Kubernetes, or OIDC authentication, contact Idira before you submit, so Idira can add the verified block for it.

STYLE
- Second person, imperative, present tense. No marketing claims and no em dashes. Use your product's UI labels in bold, exactly as they appear on screen.

BEFORE YOU SUBMIT
- This command must return nothing: perl -0pe 's/<!--.*?-->//gs' <your-file>.md | grep -oE '\{[A-Z][A-Za-z0-9]+\}'
- Send your business and technical contacts to Idira separately. They are not published.
-->

# {Vendor} {Product} integration with Idira Secrets Manager

## Solution Summary

<!-- AUTHOR: PARTNER FILLS {SolutionDescription}: two to four sentences on which secrets {Product} reads and what it uses them for. Fill the diagram slot and every row of the table. {DiagramFile} shows where {Product} calls Secrets Manager in your product's architecture: a Follower, the SaaS tenant, or Edge. {IntegrationLocation}: endpoint, mid-tier server, or central server, for example "One central server per site". -->

{SolutionDescription}

{Product} retrieves these secrets at runtime from Idira® Secrets Manager by Palo Alto Networks instead of storing them in its own configuration. In Secrets Manager, {Product} is a workload (`host`). The workload authenticates, receives a short-lived access token, and uses it to retrieve secrets (`variable` resources).

- **Idira Secrets Manager, Self-Hosted:** a cluster you run. The Leader handles writes, such as policy and secret updates. Read-only Followers behind a load balancer handle all client requests.
- **Idira Secrets Manager, SaaS:** a tenant Idira hosts. Optionally, Secrets Manager Edge gives workloads local, read-only access.

Secrets can be native Secrets Manager variables, or accounts synced from Safes in Idira Privileged Access Manager. A synced Safe gets one variable for each account password and one for each account property.

![{Product} secret retrieval flow with Idira Secrets Manager]({DiagramFile})

| Retrieval behavior | {Product} |
|:---|:---|
| What triggers a retrieval | {RetrievalTrigger} |
| How often {Product} retrieves | {RetrievalFrequency} |
| How {Product} reuses the access token | {ProductTokenHandling} |
| Whether {Product} caches the secret | {ProductCaching} |
| Whether {Product} shows the credential to its own users, and to whom | {CredentialExposure} |
| Where {Product} calls Secrets Manager from, and how many instances in a typical deployment | {IntegrationLocation} |

---

## Vendor and application

| Field | Value |
|:---|:---|
| {Product} versions | {VendorVersions} |
| {Vendor} documentation | {VendorDocsURL} |

---

## Before you begin

### Idira requirements

- **Self-Hosted:**
  - At least one Follower behind a Layer 7 load balancer, `https://<follower-lb>`, and the CA certificate that signed it.
  - The Secrets Manager CLI, signed in as a user who can load policy into the target branch (`create` privilege on the branch).
  - Your organization account name, `<account>`, set when the cluster was configured.
  - For secrets from Idira Privileged Access Manager: Vault Synchronizer syncs the Safe. It creates a `delegation/consumers` group with `read` and `execute` on all of the Safe's variables.
- **SaaS:**
  - Your tenant address, `https://<subdomain>.secretsmgr.cyberark.cloud/api`.
  - Membership in `Authn_Admins` to create authenticators. Members of `Conjur_Cloud_Admins` also have this access.
  - The Secrets Manager CLI, signed in as a Secrets Manager admin user, to load policy.
  - For secrets from Idira Privileged Access Manager: the Safe is synced, and the `Conjur Sync` user is a Safe member with **Use accounts**, **Retrieve accounts**, **List accounts**, and **Access Safe without confirmation**.
  - For client certificate authentication: a Secrets Manager Edge instance reachable from {Product}.

### {Product} requirements

<!-- AUTHOR: PARTNER FILLS every row. Write "None" where a row does not apply. {ProductNetworkPath}: each {Product} component that calls Secrets Manager, and whether it calls a Follower, the SaaS tenant, or Edge. -->

| Requirement | Details |
|:---|:---|
| Network path from {Product} to Secrets Manager | {ProductNetworkPath} |
| Certificate format {Product} accepts, and where it stores the certificate | {ProductCertificateFormat} |
| {Product} role that configures the integration | {ProductAdminRole} |
| Identity {Product} uses to write secrets or policy, if any, and its privileges | {ProductWriteAccess} |
| Other prerequisites | {ProductOtherPrerequisites} |

---

## Connection values

<!-- AUTHOR: PARTNER FILLS {WorkloadName}, the workload name you recommend, for example "vendor-product", and the secrets table below. The connection values table is PRE-WRITTEN. -->

This guide uses the workload name `{WorkloadName}`. If you use a different name, use it wherever `{WorkloadName}` appears.

| Value | Self-Hosted | SaaS |
|:---|:---|:---|
| Base URL | `https://<follower-lb>` | `https://<subdomain>.secretsmgr.cyberark.cloud/api`, or `https://<edge-domain>/api` for Edge |
| Account | `<account>` | `conjur` |
| Workload ID | `<policy-branch>/{WorkloadName}` | `data/<branch>/{WorkloadName}`, or `data/{WorkloadName}` |
| Login in the authenticate URL | `host/` plus the workload ID, URL-encoded: `host%2Fapps%2Fvendor-app` | `host/` plus the workload ID, URL-encoded: `host%2Fdata%2Fvendor-app` |
| Native variable ID | `<policy-branch>/<variable-name>` | `data/<branch>/<variable-name>` |
| Synced variable ID | `<vault-name>/<lob-name>/<safe-name>/<account-name>/<property>` | `data/vault/<safe-name>/<account-name>/<property>` |

{Product} reads these secrets:

<!-- AUTHOR: PARTNER FILLS. One row per kind of secret {Product} reads. Example: "Database password | data/vault/<safe-name>/<account-name>/password". -->

| Secret {Product} reads | Variable ID pattern |
|:---|:---|
| {SecretUseCase} | {VariableIDPattern} |

URL-encode every identifier you put in a URL path or in `variable_ids`.

---

## Authentication

<!-- AUTHOR: PARTNER FILLS {SupportedAuthenticators}: the authenticators you certified, recommended first, for example "JWT (recommended), API key". -->

{Product} supports: {SupportedAuthenticators}

Prefer an authenticator that uses the workload's own identity, such as JWT or a client certificate. Use an API key only when no workload-identity authenticator is available.

- **SaaS limits:** client certificate authentication works only through Secrets Manager Edge. Kubernetes (`authn-k8s`) and OIDC (`authn-oidc`) authenticators are not supported; use JWT with Kubernetes service account tokens.
- **Access token:** send `Accept-Encoding: base64` with the authenticate request to get the token Base64-encoded. Send it in every request as `Authorization: Token token="<encoded-token>"`. Tokens expire after 8 minutes. Reuse a token until it expires; do not authenticate before every retrieval.

---

## Configuration

Complete **Configure Idira**, and then **Configure {Product}**.

### Configure Idira

<!-- AUTHOR: PRE-WRITTEN. Keep only the Step 1 blocks for authenticators you certified, and fill only the {Placeholders}. -->

**Self-Hosted:** use the Secrets Manager CLI. Load policy and set secrets on the Leader; Followers are read-only.
**SaaS:** use the Secrets Manager UI or CLI, as each step shows.

#### Step 1: Create the workload and its authenticator

**API key**

1. Save this policy as `{WorkloadName}.yml`:

   ```yaml
   - !host
     id: {WorkloadName}
     annotations:
       authn/api-key: true
   ```

2. Load it and get the API key:
   - **Self-Hosted:** `conjur policy load -b <policy-branch> -f {WorkloadName}.yml`, then `conjur host rotate-api-key -i <policy-branch>/{WorkloadName}`.
   - **SaaS:** `conjur policy load -b data -f {WorkloadName}.yml`. The command returns the API key. Or, on the **Workloads** page, click **Create workloads**, select **Other**, enter `{WorkloadName}`, select **API key**, and select the Safes it can access.
3. Store the API key securely, for example as an account in Idira Privileged Access Manager.

**JWT**

- **Self-Hosted:**
  1. Save this authenticator policy as `authn-jwt.yml`, with `<service-id>` set to a name such as `{WorkloadName}-jwt`, and load it with `conjur policy load -b root -f authn-jwt.yml`:

     ```yaml
     - !policy
       id: conjur/authn-jwt/<service-id>
       body:
         - !webservice
         - !variable jwks-uri
         - !variable issuer
         - !variable audience
         - !variable token-app-property
         - !variable identity-path
         - !group apps
         - !permit
           role: !group apps
           privilege: [ read, authenticate ]
           resource: !webservice
         - !webservice status
         - !group operators
         - !permit
           role: !group operators
           privilege: [ read ]
           resource: !webservice status
     ```

  2. Set the authenticator values. Set `identity-path` without the `host/` prefix.

     ```bash
     conjur variable set -i conjur/authn-jwt/<service-id>/jwks-uri -v {JWKSURI}
     conjur variable set -i conjur/authn-jwt/<service-id>/issuer -v {JWTIssuer}
     conjur variable set -i conjur/authn-jwt/<service-id>/audience -v {JWTAudience}
     conjur variable set -i conjur/authn-jwt/<service-id>/token-app-property -v {TokenAppProperty}
     conjur variable set -i conjur/authn-jwt/<service-id>/identity-path -v <policy-branch>
     ```

  3. Save this workload policy as `{WorkloadName}-jwt-host.yml`, with the claim annotations {Product} tokens carry, and load it with `conjur policy load -b root -f {WorkloadName}-jwt-host.yml`: {JWTClaimAnnotations}

     ```yaml
     - !policy
       id: <policy-branch>
       body:
         - !group
         - &hosts
           - !host
             id: {WorkloadName}
             annotations:
               authn-jwt/<service-id>/<claim>: <claim-value>
         - !grant
           role: !group
           members: *hosts

     - !grant
       role: !group conjur/authn-jwt/<service-id>/apps
       member: !group <policy-branch>
     ```

     Each annotation adds a claim the token must match. Add as many as you need to stop workloads from impersonating each other. For a nested claim, use `<claim_root>/<claim_name>`.

  4. Allowlist the authenticator. On the Secrets Manager host, open `conjur.yml` (in `/opt/cyberark/conjur/config` by default, or `/etc/conjur/config/conjur.yml` inside the container), add `authn-jwt/<service-id>` under `authenticators`, keep `authn`, and run `docker exec <conjur> evoke configuration apply`, where `<conjur>` is the Secrets Manager container.
- **SaaS**, as a member of `Authn_Admins`:
  1. On the **Authenticators** page, click **Create authenticator** > **JSON Web Token (JWKS)**, and enter a unique name.
  2. Enter **JWKS URI** {JWKSURI}, **Issuer** {JWTIssuer}, **Audience** {JWTAudience}, **Token app property** {TokenAppProperty}, and **Identity path**, for example `data/<branch>`.
  3. On the **Workloads** page, click **Create workload**, enter `{WorkloadName}`, and select the branch from the identity path. The name must match the {TokenAppProperty} claim.
  4. On the **Authentication** page, select the JWT authenticator you created. On the **Workload definition** page, add the claim annotations: {JWTClaimAnnotations}

**Client certificate**

- **Self-Hosted:**
  1. Save this authenticator policy as `cert-auth.yml`, with your `<service-id>`:

     ```yaml
     - !policy
       id: <service-id>
       body:
         - !webservice
         - !variable ca-cert
         - !group apps
         - !permit
           role: !group apps
           privilege: [ read, authenticate ]
           resource: !webservice
         - !group operators
         - !permit
           role: !group operators
           privilege: [ read, update ]
           resource: !webservice
     ```

  2. Load it, set the CA bundle (PEM, exactly one root CA plus any intermediates), and enable the authenticator:

     ```bash
     conjur policy load -b conjur/authn-cert -f cert-auth.yml
     conjur variable set -i conjur/authn-cert/<service-id>/ca-cert -f <ca-bundle.pem>
     conjur authenticator enable --id authn-cert/<service-id>
     ```

  3. Save this workload policy as `{WorkloadName}-cert-host.yml`, with an annotation for the certificate field {Product} presents, {CertificateIdentityField} (`san-uri`, `san-dns`, `san-ip`, or `cn`), and load it with `conjur policy load -b root -f {WorkloadName}-cert-host.yml`:

     ```yaml
     - !policy
       id: <policy-branch>
       body:
         - !group
         - !host
           id: {WorkloadName}
           annotations:
             authn-cert/<service-id>/san-uri: <san-uri>
         - !grant
           role: !group
           member: !host {WorkloadName}
     ```

  4. Add the workload group to the authenticator's `apps` group. Save this as `authn-cert-grant.yml` and load it with `conjur policy load -b root -f authn-cert-grant.yml`:

     ```yaml
     - !grant
       role: !group conjur/authn-cert/<service-id>/apps
       member: !group <policy-branch>
     ```

- **SaaS** (Secrets Manager Edge only):
  1. On the **Authenticators** page, click **Create authenticator** > **Client certificate**, and add the CA certificate that signed the {Product} client certificate.
  2. On the **Workloads** page, create `{WorkloadName}`, select this authenticator, and add an annotation for the certificate field {Product} presents: {CertificateIdentityField}
  3. Send {Product} requests to `https://<edge-domain>/api`.

#### Step 2: Give the workload access to secrets

- **Synced secrets:** add the workload to the Safe's consumers group, which has `read` and `execute` on all the Safe's secrets.
  - **Self-Hosted:** save this as `grant.yml` and run `conjur policy load -b <vault-name>/<lob-name>/<safe-name> -f grant.yml`:

    ```yaml
    - !grant
      role: !group delegation/consumers
      member: !host /<policy-branch>/{WorkloadName}
    ```

  - **SaaS:** select the Safes on the workload's **Access to Safes** page. Or load the same policy, with `member: !host /data/{WorkloadName}`, with `conjur policy load -b data/vault/<safe-name> -f grant.yml`. A Safe can take a few minutes to sync.
- **Native variables:** declare each variable and permit the workload to read it, in the branch that holds the variables:

  ```yaml
  - !variable <variable-name>
  - !permit
    role: !host /<policy-branch>/{WorkloadName}
    privileges: [ read, execute ]
    resource: !variable <variable-name>
  ```

#### Step 3: Set native secret values

For native variables, run `conjur variable set -i <variable-id> -v <value>`. On Self-Hosted, run it on the Leader.

### Configure {Product}

#### Step 1: Install the {Product} integration

<!-- AUTHOR: PARTNER FILLS. Mandatory. Where the customer gets the integration package and how to install it, in numbered steps. If the integration is built in to {Product}, write "The integration is built in to {Product}. Nothing to install." -->

{ProductInstallSteps}

#### Step 2: Connect {Product} to Secrets Manager

<!-- AUTHOR: PARTNER FILLS. Choose ONE option, delete the other and its label.
     Option A: link to your published configuration guide. It must use the connection values from this guide.
     Option B: write the steps here, keep the mapping table, and add one screenshot per slot. Delete mapping rows for authenticators you did not certify. -->

**Option A**

Follow the [{Product} configuration guide]({ProductConfigDocsURL}). Use the workload ID and variable IDs from **Connection values**.

**Option B**

As a {Product} user with the {ProductAdminRole} role:

1. Go to **{IntegrationMenuPath}**, enter these values, and save:

   | Secrets Manager value | Where you get it | {Product} field |
   |:---|:---|:---|
   | Base URL | **Connection values** | {BaseURLField} |
   | Account | **Connection values** | {AccountField} |
   | Workload ID | `{WorkloadName}` with its branch, from Configure Idira, Step 1 | {WorkloadIDField} |
   | Authenticator | `authn`, `authn-jwt/<service-id>`, or `authn-cert/<service-id>` | {AuthenticatorField} |
   | API key, JWT source, or client certificate and key | Configure Idira, Step 1 | {CredentialField} |
   | CA certificate | The CA that signed the Follower load balancer, tenant, or Edge certificate | {CACertificateField} |

   ![{Product} connection settings for Idira Secrets Manager]({ScreenshotConnection})

2. Go to **{SecretMenuPath}**. For each object, enter the variable ID of its secret, and save: {VariableField}

   ![{Product} secret settings]({ScreenshotSecret})

---

## Validate the integration

<!-- AUTHOR: PARTNER FILLS the {Product} checks. The API check is PRE-WRITTEN. -->

1. **API check:** from a {Product} machine, authenticate with the API key and retrieve one secret:

   ```bash
   # Self-Hosted
   token=$(curl --cacert <ca.pem> --header "Accept-Encoding: base64" --data <api-key> \
     https://<follower-lb>/authn/<account>/<url-encoded-login>/authenticate)
   curl --cacert <ca.pem> --header "Authorization: Token token=\"$token\"" \
     https://<follower-lb>/secrets/<account>/variable/<url-encoded-variable-id>

   # SaaS
   token=$(curl --header "Accept-Encoding: base64" --data <api-key> \
     https://<subdomain>.secretsmgr.cyberark.cloud/api/authn/conjur/<url-encoded-login>/authenticate)
   curl --header "Authorization: Token token=\"$token\"" \
     https://<subdomain>.secretsmgr.cyberark.cloud/api/secrets/conjur/variable/<url-encoded-variable-id>
   ```

2. **Connection and retrieval in {Product}:** {ProductRetrievalTest}
3. **Secret change:** change the secret (for a synced secret, change the password in Idira Privileged Access Manager and wait for the sync), and confirm {Product} uses the new value: {RotationBehavior}
4. **Audit:**
   - **Self-Hosted:** the audit log shows **Authenticate** and **Fetch secret value** events for `host/<policy-branch>/{WorkloadName}`.
   - **SaaS:** the Audit space shows `authn-authenticate` and `fetch-fetch` events for the workload. Requests through Edge are audited on the Edge machine, not in the Audit space.

---

## Troubleshooting

<!-- AUTHOR: The Idira rows are PRE-WRITTEN. Delete rows for authenticators or models you did not certify. PARTNER FILLS the last row with the most common {Product}-side failure. Add rows if needed. -->

| Symptom | Applies to | Cause | Fix |
|:---|:---|:---|:---|
| 401 on authenticate | Both | The login is missing `host/` or is not URL-encoded, or the API key is wrong. | Use `host/<workload-id>`, URL-encoded. Rotate the API key if needed. |
| 401 on authenticate with JWT or a client certificate | Both | The workload is not in the authenticator's `apps` group, its annotations do not match, or the authenticator is not enabled. | Check the `apps` group and annotations from Configure Idira, Step 1. On Self-Hosted, check that the authenticator is allowlisted or enabled. |
| 401 on retrieve | Both | The token expired, is not Base64-encoded, or contains newlines. | Authenticate again with `Accept-Encoding: base64`. |
| 403 on retrieve | Both | The workload lacks `execute` on the variable. | Complete Configure Idira, Step 2. |
| 404 on retrieve | Both | The variable does not exist, has no value, or its ID is not URL-encoded. | Check and URL-encode the ID. Check that the Safe finished syncing. |
| 422 on retrieve | Both | A request parameter is missing or invalid. | Check the request URL and parameters. |
| Request fails on SaaS but works on Self-Hosted | SaaS | The path is missing `/api`. | Use `https://<subdomain>.secretsmgr.cyberark.cloud/api/...`. |
| Policy load or secret update fails | Self-Hosted | The request went to a read-only Follower. | Send it to the Leader. |
| Client certificate authentication fails | SaaS | The request went to the tenant, not Edge. | Send it to `https://<edge-domain>/api`. |
| {PartnerSymptom} | Both | {PartnerCause} | {PartnerFix} |

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
| Secrets Manager, authenticators, workloads, and synced Safes | Idira Technical Support | Your usual Technical Support channel |
