# Idira Discovery Service Partner Development Guide

**Workflow:** Discovery  
**Dev Kit:** Secrets  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.2  
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Discovery & Context — the inventory service on the Identity Security Platform that holds the customer's machine identities, AI agents, and secrets.
WORKFLOW: Discovery
USE CASE: Secrets — a partner scanner pushes the secrets it finds (API keys, database credentials, TLS certificates, SSH keys, OAuth tokens, cloud access keys) into the customer's Idira inventory and keeps that inventory current.
INTEGRATION PATTERN: GraphQL. One endpoint, one HTTP verb. Every operation — push, query, delete — is a POST to the same URL with a different GraphQL document in the body. Do not look for per-operation REST paths; there are none.
AUTH METHOD: OAuth 2.0 against ISPSS (Identity Security Platform SaaS) — see Section 5
AUTH HEADER FORMAT: Authorization: Bearer <access_token>
TOKEN ENDPOINT: POST https://<tenant>.id.cyberark.cloud/oauth2/platformtoken
API ENDPOINT: POST https://<tenant>.app.cyberark.cloud/api/discovery/graphql
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs. it=Secrets-Discovery
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS KIT DOES THE OPPOSITE OF THE SECRETS-MANAGEMENT KITS. READ THIS BEFORE WRITING ANY CODE.
This kit REPORTS THAT A SECRET EXISTS SOMEWHERE ELSE — in source code, a CI pipeline, a container
image, an IaC repo, a third-party SaaS platform, a cloud secrets manager. It builds an inventory
of exposure. The ../../secrets-management/ kits (Secrets Manager SaaS/Self-Hosted, CP, CCP) do the
reverse: they RETRIEVE a secret's value from Idira at runtime. If the task is "fetch a credential
from Idira", this is the wrong kit entirely.
AND: THE SECRET VALUE IS NEVER PUSHED. This integration sends metadata about a secret — type,
location, source, identifiers — not the secret itself. An integration that transmits secret values
into the inventory is a security defect, not a feature.

OPERATION NAME vs. SERVER FIELD — THE MOST COMMON ERROR READING THIS GUIDE. In GraphQL these
are two different things and this guide shows both. The operation name is a client-side label you
may rename freely; the server field is the API and is fixed:
  operation `AddReplaceSecrets`  ->  server field `addReplaceExternalSecrets`
  operation `ListSecrets`        ->  server field `secrets`
  operation `DeleteSecrets`      ->  server field `deleteExternalSecrets`
Calling `addReplaceSecrets` (without `External`) fails. The write and delete fields carry
`External` because a partner integration is an external data source; the read field does not.
This kit's read field also accepts a `sort: [SecretsSortInput]` argument, which the sibling
workload and AI-agent queries do not.

ROLE MODEL CHANGED 2026-08-06 — AN OLDER INTEGRATION RETURNS 403 UNTIL REASSIGNED:
- Required role: **Machines External Data Contributor** (write-only — the least-privilege fit).
- Do NOT request **Machines Admin** unless the integration also reads or manages inventory beyond
  its own upserts.
- If the integration user previously held the Secrets Hub role for this API, that assignment must
  be REPLACED, not supplemented. This trips this kit most often, because Secrets Hub sounds like
  the right role for a secrets integration and is not.
The same three roles govern all three GraphQL Discovery kits.

KEY CONSTRAINTS:
- Idira deduplicates on `originId` — the stable identifier from the partner's own system. Push the
  same `originId` twice and the record is updated in place, not duplicated. It must be stable
  across rescans; deriving it from a file path or line number that moves creates duplicates.
- `providerId` identifies the partner source. Reconciliation is: push the full set, then query by
  `providerId` and diff `originId` sets, then delete what is no longer present.
- Batch 100 secrets per mutation call. Track `totalProcessedSecrets` on the response to confirm
  each batch landed completely — a partial success is otherwise silent.
- Delete returns `totalDeleted`.
- A push is an upsert, not a sync. Stale records are NOT removed by pushing a smaller set; they
  must be deleted explicitly. A remediated secret that is no longer in the source must be deleted,
  or the inventory will keep reporting an exposure the customer has already fixed.
- Section 9 maps secret types and Section 10 lists supported data sources — map to those, do not
  invent type strings.

SIBLING KITS — the other three Discovery kits, easily confused:
- ../machine-identities/: the workloads that USE these secrets. Same endpoint, fields named
  `...Workloads`. it=Machine-Identity-Discovery
- ../ai-agents/: autonomous LLM services and agentic pipelines. Same endpoint, fields named
  `...AiAgents`. it=AI-Agent-Discovery
- ../privileged-accounts/: NOT on this API. It uses Privilege Cloud REST with different auth and
  different roles. Do not carry an auth pattern or an endpoint across from it.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — which Discovery dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

## 1. Why Secrets Discovery Matters

Secrets — API keys, database credentials, TLS certificates, SSH keys, OAuth tokens, cloud access keys — are the credentials that non-human identities use to authenticate. They are created constantly, often in places never reviewed by security teams: source code, CI/CD pipelines, container images, infrastructure-as-code repositories, third-party SaaS platforms, and cloud secrets managers.

The first step in securing secrets is knowing they exist. Integrating secrets discovery into Idira gives customers a centralized inventory: what secrets exist, where they live, what they expire, whether they are static or dynamic, and which workloads or agents are associated with them. That inventory is the prerequisite for rotation policy, access review, and compliance reporting.

**Current industry drivers:**
- GitLab and GitHub's secret scanning features surface secrets in code repositories, but customers need those findings in a PAM context — correlated against vaulted accounts and rotation policies.
- Cloud provider secrets managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, HashiCorp Vault) are widely deployed but rarely inventoried in aggregate across a customer's estate.
- SLSA and software supply chain security frameworks now require organizations to enumerate secrets used in build pipelines.
- DORA and financial sector regulators are expanding requirements for credentials lifecycle documentation to include non-human and API credentials.

---

## 2. Use Cases at a Glance

This integration pushes discovered secrets into the Idira inventory and keeps them current. It exposes three operations against the Discovery Context API — build the ones your use case needs.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Push (upsert) secrets | Send discovered secrets into the Idira inventory; re-sending updates the existing record | [7.1](#71-push-upsert-secrets) |
| 2 | Query secrets | Read back the secrets your integration has pushed, for reconciliation | [7.2](#72-query-secrets) |
| 3 | Delete secrets | Remove secrets that no longer exist in the source, to keep the inventory clean | [7.3](#73-delete-secrets) |

A complete discovery integration typically implements all three: push on each scan, query to reconcile, and delete stale records. Document which operations your integration implements in the certification checklist.

---

## 3. What the Customer Sees in Inventory

Pushed secret records appear in the Idira **Secrets inventory** (`Inventory > Secrets`). Each entry surfaces:

| Column | Source field |
|:---|:---|
| Secret name | `name` |
| Provider | `providerType` / `providerId` |
| Type / Subtype | `type` / `subType` |
| Location | `location` |
| Username | `username` |
| Permanence | `permanence` (DYNAMIC / STATIC) |
| Validity (from / to) | `validityFrom` / `validityTo` |
| Tags | `tags[]` |
| Last seen | Managed by Idira (timestamp of last upsert) |

Customers use this inventory to identify orphaned secrets (no associated workload), near-expiry certificates, static credentials that should be rotated to dynamic, and secrets stored outside the vault that should be onboarded.

> **Important:** Do not push `secretValue` unless the customer's use case explicitly requires it and the transport channel is verified end-to-end. The field exists in the schema, but it should be treated as a last resort. In most discovery use cases, the goal is enumeration — not value extraction.

---

## 4. API User Persona

> **Updated 2026-09-08:** Discovery & Context replaced its role model on 2026-08-06. Three roles now govern the machine identities, AI agents, and secrets inventories: **Machines Admin** (full access), **Machines External Data Contributor** (write-only via API), and **Machines Internal Data Contributor** (internal service access). **Any integration user provisioned under the previous model requires reassignment** — an existing integration will start returning `403` until it is moved.

To call the Discovery Context API, the integration user must sign in to **ISPSS (Identity Security Platform SaaS)** and hold the **Machines External Data Contributor** role. This is the least-privilege role for a partner integration that pushes inventory data in over the API — it grants write access only, which is exactly this integration's access pattern. Do not request **Machines Admin** unless the integration also needs to read or manage inventory beyond its own upserts.

> **Note for administrators:** Provisioning **Machines External Data Contributor** membership in ISPSS is the required step. If this integration user previously held the Secrets Hub role for this API, that assignment must be replaced, not supplemented. Consult your Idira tenant administrator or the Idira Docs portal for the current role assignment procedure.

---

## 5. Authentication

All Discovery Context API calls use **OAuth 2.0 client credentials flow** against the Idira Identity tenant.

```
POST https://<tenant>.id.cyberark.cloud/oauth2/platformtoken
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=<service-account-id>
&client_secret=<service-account-secret>
```

Cache and reuse the returned `access_token` (typically valid 30 minutes). Refresh proactively before expiry. Never persist tokens to disk.

The Discovery Context API is a **GraphQL** endpoint:

```
POST https://<tenant>.app.cyberark.cloud/api/discovery/graphql
Authorization: Bearer <access_token>
Content-Type: application/json
x-cybr-telemetry: <Base64url-encoded telemetry>
```

---

## 6. Telemetry Header (Required)

Every request must include `x-cybr-telemetry` — a Base64 URL-encoded string of ampersand-delimited key=value pairs:

```
in=<IntegrationName>&it=Secrets-Discovery&iv=<version>&vn=<VendorName>
```

Example (before encoding):
```
in=AcmeCorp Secrets Scanner&it=Secrets-Discovery&iv=1.0&vn=Acme Corporation
```

---

## 7. Core API Operations

### 7.1 Push (Upsert) Secrets

Use `addReplaceExternalSecrets` to insert new secret records or update existing ones. Idira deduplicates on `originId`.

```graphql
mutation AddReplaceSecrets($secrets: [SecretInput!]!) {
  addReplaceExternalSecrets(secrets: $secrets) {
    secrets {
      id
      originId
      name
    }
    totalProcessedSecrets
  }
}
```

**Variables — full field reference:**

```json
{
  "secrets": [
    {
      "originId": "arn:aws:secretsmanager:us-east-1:123456789:secret:prod/payments/db-credentials-xK9a2c",
      "providerId": "aws-prod-123456789",
      "providerType": "AWS",
      "name": "prod/payments/db-credentials",
      "type": "DATABASE_CREDENTIAL",
      "subType": "POSTGRES",
      "description": "PostgreSQL credentials for the payments service production database",
      "location": "us-east-1",
      "username": "payments_svc",
      "permanence": "STATIC",
      "validityFrom": "2026-01-01T00:00:00Z",
      "validityTo": "2026-12-31T23:59:59Z",
      "tags": [
        { "key": "env", "value": "production" },
        { "key": "team", "value": "payments" },
        { "key": "rotation-policy", "value": "90-days" },
        { "key": "compliance", "value": "pci-dss" }
      ]
    }
  ]
}
```

**Field notes:**

| Field | Required | Description |
|:---|:---:|:---|
| `originId` | Yes | Stable unique ID from source system — use the cloud-native resource ARN or path |
| `providerId` | Yes | Account/tenant/subscription ID in the source cloud |
| `providerType` | Yes | Cloud or platform identifier (see Section 9) |
| `name` | Yes | Human-readable secret name or path |
| `type` | No | Broad credential category (see mapping table in Section 9) |
| `subType` | No | Specific service or format |
| `description` | No | Plain-text description of the secret's purpose |
| `location` | No | Region, vault path, or repository location |
| `username` | No | Associated username or service account (highly recommended for database credentials) |
| `permanence` | No | `STATIC` (long-lived, rotation required) or `DYNAMIC` (short-lived, auto-generated) |
| `validityFrom` | No | ISO 8601 / AWSDateTime — when the credential became valid |
| `validityTo` | No | ISO 8601 / AWSDateTime — expiry date — populate for all certificates and time-bounded keys |
| `tags` | No | Key/value pairs — include env, team, rotation policy, compliance scope |
| `secretValue` | No | Raw secret value — **do not populate in discovery use cases unless explicitly required** |

> **Best practice:** Always populate `permanence` and `validityTo` where the data is available. These two fields drive the most actionable customer workflows: identifying static credentials that should be rotated and certificates approaching expiry.

---

### 7.2 Query Secrets

```graphql
query ListSecrets($filter: SecretsFilterInput, $pageInput: PageInput, $sort: [SecretsSortInput]) {
  secrets(filter: $filter, pageInput: $pageInput, sort: $sort) {
    items {
      id
      originId
      name
      type
      subType
      location
      username
      permanence
      validityFrom
      validityTo
      providerId
      providerType
      tags { key value }
      createdAt
      updatedAt
    }
    totalCount
  }
}
```

**Filter for near-expiry secrets (next 30 days):**
```json
{
  "filter": {
    "validityTo": { "lt": "2026-07-18T00:00:00Z" }
  },
  "sort": [{ "validityTo": "ASC" }],
  "pageInput": { "limit": 100, "offset": 0 }
}
```

**Filter for static credentials in a specific provider:**
```json
{
  "filter": {
    "and": [
      { "providerType": { "eq": "AWS" } },
      { "permanence": { "eq": "STATIC" } }
    ]
  }
}
```

---

### 7.3 Delete Secrets

Delete operations are **irreversible**. Always scope to a specific `providerId`, `providerType`, or `originId` set. Never issue an unfiltered delete.

```graphql
mutation DeleteSecrets($filter: SecretsFilterInput!) {
  deleteExternalSecrets(filter: $filter) {
    totalDeleted
  }
}
```

---

## 8. Sync Strategy

| Pattern | When to use |
|:---|:---|
| **Full replace** | Scheduled scans — enumerate all secrets in scope, upsert the full set, delete records whose `originId` is absent from the latest scan |
| **Delta push** | Event-driven sources (CloudTrail, Vault audit log, GitHub webhook) — push on create/rotate/delete events |
| **Expiry-focused** | For certificate and key discovery — push with `validityTo` populated, re-scan and update whenever a rotation occurs |
| **Reconciliation** | After any full replace, query Idira by `providerId`, diff `originId` sets, and delete stale records |

Batch size recommendation: **100 secrets per mutation call**. Track `totalProcessedSecrets` to verify completeness.

---

## 9. Secret Types and Recommended Mappings

| Source secret type | Recommended `type` | Recommended `subType` | `permanence` |
|:---|:---|:---|:---|
| Database password | `DATABASE_CREDENTIAL` | `MYSQL` / `POSTGRES` / `MSSQL` / `ORACLE` | `STATIC` |
| AWS IAM access key | `CLOUD_ACCESS_KEY` | `AWS_IAM` | `STATIC` |
| Azure Service Principal secret | `CLOUD_ACCESS_KEY` | `AZURE_SP` | `STATIC` |
| GCP Service Account key | `CLOUD_ACCESS_KEY` | `GCP_SA_KEY` | `STATIC` |
| AWS STS session token | `CLOUD_ACCESS_KEY` | `AWS_STS` | `DYNAMIC` |
| TLS/SSL certificate | `CERTIFICATE` | `TLS` | `STATIC` |
| SSH private key | `SSH_KEY` | `RSA` / `ED25519` | `STATIC` |
| API key (generic) | `API_KEY` | `CUSTOM` | `STATIC` |
| GitHub PAT | `API_KEY` | `GITHUB_PAT` | `STATIC` |
| HashiCorp Vault dynamic secret | `VAULT_SECRET` | `VAULT_DYNAMIC` | `DYNAMIC` |
| AWS Secrets Manager secret | `VAULT_SECRET` | `AWS_SECRETS_MANAGER` | `STATIC` or `DYNAMIC` |
| Azure Key Vault secret | `VAULT_SECRET` | `AZURE_KEY_VAULT` | `STATIC` |
| GCP Secret Manager secret | `VAULT_SECRET` | `GCP_SECRET_MANAGER` | `STATIC` |
| Kubernetes Secret | `KUBERNETES_SECRET` | `OPAQUE` / `DOCKER_CONFIG` | `STATIC` |
| OAuth 2.0 client secret | `OAUTH_CREDENTIAL` | `CLIENT_SECRET` | `STATIC` |

---

## 10. Data Sources Reference

The `providerType` field must map to a recognized source system. Standard values include:

| Source | `providerType` value |
|:---|:---|
| AWS Secrets Manager, IAM | `AWS` |
| Azure Key Vault, Entra ID | `AZURE` |
| GCP Secret Manager | `GCP` |
| HashiCorp Vault (self-hosted) | `HASHICORP_VAULT` |
| Conjur / Idira Secrets Manager | `CONJUR` |
| Kubernetes Secrets | `KUBERNETES` |
| GitHub (PATs, Actions secrets) | `GITHUB` |
| GitLab | `GITLAB` |
| Other / custom | `CUSTOM` |

Idira also recognizes the following first-party data source types: `SECRETS_HUB`, `CONJUR`, `KUBERNETES_DISCOVERY_AGENT`, `SAI`, `AWS_SCANNER`, `AZURE_SCANNER`, `SECRETS_MANAGER_SAAS`.

---

## 11. Error Handling

| HTTP status | Meaning | Action |
|:---|:---|:---|
| `200` | Success | Log `totalProcessedSecrets` for audit trail |
| `400` | Validation error | Parse GraphQL `errors[]` — fix required field or type mismatch |
| `401` | Token expired or invalid | Re-authenticate and retry once |
| `403` | Insufficient permissions | Verify the **Machines External Data Contributor** role is assigned (replaced the previous Discovery & Context role model on 2026-08-06) |
| `429` | Rate limited | Implement exponential backoff — do not retry in tight loop |
| `500` | Server error | Log full response, retry after backoff, alert if persistent |

Log the `originId` of every record alongside the API response. Surface per-item errors for partial batch failures.

---

## 12. Pre-Development Checklist

- [ ] OAuth credentials provisioned and stored in a secrets manager (not in code or environment variables)
- [ ] **Machines External Data Contributor** role confirmed on integration user (not the retired Discovery Source / Secrets Hub role)
- [ ] Source system API access verified (can enumerate secrets in target environment)
- [ ] `originId` strategy defined — must be stable across rescans (use cloud-native resource ARNs or full vault paths, not display names)
- [ ] Decision made: will `secretValue` be pushed? If yes, confirm customer consent and transport security
- [ ] `permanence` classification logic defined for all secret types in scope
- [ ] `validityTo` population confirmed for all certificate and key types
- [ ] Telemetry header values agreed with your Idira Technical Alliances contact
- [ ] Batch size and scan frequency defined
- [ ] Logging captures `originId`, mutation result, and `totalProcessedSecrets` per batch
- [ ] Stale record deletion logic tested in non-production before go-live

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the two distinctions an agent gets wrong reading this kit cold: that it reports secrets existing *elsewhere* rather than retrieving them from Idira (the `secrets-management/` kits do the reverse), and that the secret *value* is never transmitted — only metadata. Also states the GraphQL single-endpoint pattern, the operation-name vs. server-field distinction (`addReplaceExternalSecrets` is the field), the post-2026-08-06 role requirement including why Secrets Hub is the wrong role despite the name, and the `originId` / `providerId` reconciliation contract. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
