# Idira Discovery Service Partner Development Guide

**Workflow:** Discovery  
**Dev Kit:** Machine Identities  
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
USE CASE: Machine Identities — a partner scanner pushes the workloads it discovers (compute instances, containers, Kubernetes pods, serverless functions, CI/CD pipelines) into the customer's Idira inventory and keeps that inventory current.
INTEGRATION PATTERN: GraphQL. One endpoint, one HTTP verb. Every operation — push, query, delete — is a POST to the same URL with a different GraphQL document in the body. Do not look for per-operation REST paths; there are none.
AUTH METHOD: OAuth 2.0 against ISPSS (Identity Security Platform SaaS) — see Section 5
AUTH HEADER FORMAT: Authorization: Bearer <access_token>
TOKEN ENDPOINT: POST https://<tenant>.id.cyberark.cloud/oauth2/platformtoken
API ENDPOINT: POST https://<tenant>.app.cyberark.cloud/api/discovery/graphql
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs. it=Machine-Identity-Discovery
CONTACT: cybr-bizdevtech@paloaltonetworks.com

NOTE ON THE ENTITY NAME: the kit is called "Machine Identities" but the API calls them WORKLOADS.
Every type, field, and filter uses that word — `WorkloadInput`, `WorkloadsFilterInput`,
`totalProcessedWorkloads`. There is no `machineIdentity` type. Use "workload" in code.

OPERATION NAME vs. SERVER FIELD — THE MOST COMMON ERROR READING THIS GUIDE. In GraphQL these
are two different things and this guide shows both. The operation name is a client-side label you
may rename freely; the server field is the API and is fixed:
  operation `AddReplaceWorkloads`  ->  server field `addReplaceExternalWorkloads`
  operation `ListWorkloads`        ->  server field `workloads`
  operation `DeleteWorkloads`      ->  server field `deleteExternalWorkloads`
Calling `addReplaceWorkloads` (without `External`) fails. The write and delete fields carry
`External` because a partner integration is an external data source; the read field does not.

ROLE MODEL CHANGED 2026-08-06 — AN OLDER INTEGRATION RETURNS 403 UNTIL REASSIGNED:
- Required role: **Machines External Data Contributor** (write-only — the least-privilege fit).
- Do NOT request **Machines Admin** unless the integration also reads or manages inventory beyond
  its own upserts.
- If the integration user previously held the Secrets Hub role for this API, that assignment must
  be REPLACED, not supplemented.
The same three roles govern all three GraphQL Discovery kits.

KEY CONSTRAINTS:
- Idira deduplicates on `originId` — the stable identifier from the partner's own system. Push the
  same `originId` twice and the record is updated in place, not duplicated. Use the native cloud
  resource ID, never a display name: an instance rename would otherwise create a second record.
- `providerId` identifies the partner source. Reconciliation is: push the full set, then query by
  `providerId` and diff `originId` sets, then delete what is no longer present.
- Batch 100 workloads per mutation call. Track `totalProcessedWorkloads` on the response to confirm
  each batch landed completely — a partial success is otherwise silent.
- Delete returns `totalDeleted`.
- A push is an upsert, not a sync. Stale records are NOT removed by pushing a smaller set; they
  must be deleted explicitly. This matters most here, where workloads are ephemeral by nature —
  a scanner that only ever pushes will accumulate terminated instances indefinitely.

SIBLING KITS — the other three Discovery kits, easily confused:
- ../ai-agents/: autonomous LLM services and agentic pipelines. Same endpoint, fields named
  `...AiAgents`. it=AI-Agent-Discovery
- ../secrets/: the credentials these workloads use to authenticate. Same endpoint, fields named
  `...Secrets`. it=Secrets-Discovery. NOTE: that kit discovers secrets that exist elsewhere; the
  ../../secrets-management/ kits retrieve secrets from Idira and do the opposite.
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

## 1. Why Machine Identity Discovery Matters

Machine identities — workloads, compute instances, containers, Kubernetes pods, serverless functions, CI/CD pipelines — now outnumber human identities by orders of magnitude in cloud-native environments. Each carries at least one credential (API key, certificate, service account token, IAM role) and often operates with privileges far beyond what its function requires.

The challenge is enumeration: cloud environments provision and destroy machine identities dynamically, at a pace no manual review process can sustain. Without automated discovery feeding a central identity store, security teams lack the foundational inventory needed to enforce least privilege, detect anomalies, or pass compliance audits.

Integrating workload discovery into Idira closes this gap. Your integration pushes the compute and workload context your scanner sees; Idira correlates it with the privileged accounts, secrets, and certificates those workloads access — giving the customer a unified risk picture.

**Current industry drivers:**
- Cloud entitlements reviews (CIEM) increasingly require workload identity as a first-class input alongside human IAM.
- Kubernetes security benchmarks (CIS, NSA/CISA) require enumeration of service accounts and workload identities.
- Zero Trust architecture mandates machine identity verification at every workload — customers need the inventory to build the policy.
- Regulatory frameworks (PCI DSS 4.0, NIS2, SOC 2) are expanding scope to include non-human identities.

---

## 2. Use Cases at a Glance

This integration pushes machine identities (workloads) into the Idira inventory and keeps them current. It exposes three operations against the Discovery Context API — build the ones your use case needs.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Push (upsert) workloads | Send discovered workloads into the Idira inventory; re-sending updates the existing record | [7.1](#71-push-upsert-workloads) |
| 2 | Query workloads | Read back the workloads your integration has pushed, for reconciliation | [7.2](#72-query-workloads) |
| 3 | Delete workloads | Remove workloads that no longer exist in the source, to keep the inventory clean | [7.3](#73-delete-workloads) |

A complete discovery integration typically implements all three: push on each scan, query to reconcile, and delete stale records. Document which operations your integration implements in the certification checklist.

---

## 3. What the Customer Sees in Inventory

Pushed workload records appear in the Idira **Machine Identities inventory** (`Inventory > Machine Identities`). Each entry exposes:

| Column | Source field |
|:---|:---|
| Workload name | `name` |
| Provider | `providerType` / `providerId` |
| Type / Subtype | `type` / `subType` |
| Location | `location` |
| Tags | `tags[]` |
| Last seen | Managed by Idira (timestamp of last upsert) |
| Additional context | `additionalData` (arbitrary JSON) |

Customers correlate these entries against secrets and privileged account records in Idira to identify workloads with standing credentials that should be rotated or vaulted, and workloads with no associated secrets that may be misconfigured.

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

Cache and reuse the returned `access_token` (typically valid 30 minutes). Request a fresh token on startup and refresh proactively before expiry. Never persist tokens to disk.

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
in=<IntegrationName>&it=Machine-Identity-Discovery&iv=<version>&vn=<VendorName>
```

Example (before encoding):
```
in=AcmeCorp Cloud Scanner&it=Machine-Identity-Discovery&iv=1.0&vn=Acme Corporation
```

---

## 7. Core API Operations

### 7.1 Push (Upsert) Workloads

Use `addReplaceExternalWorkloads` to insert new workload records or update existing ones. Idira deduplicates on `originId`.

```graphql
mutation AddReplaceWorkloads($workloads: [WorkloadInput!]!) {
  addReplaceExternalWorkloads(workloads: $workloads) {
    workloads {
      id
      originId
      name
    }
    totalProcessedWorkloads
  }
}
```

**Variables — full field reference:**

```json
{
  "workloads": [
    {
      "originId": "arn:aws:eks:us-east-1:123456789:cluster/prod-cluster/namespace/payments/sa/payments-processor",
      "providerId": "aws-prod-123456789",
      "providerType": "AWS",
      "name": "payments-processor",
      "type": "KUBERNETES_SERVICE_ACCOUNT",
      "subType": "EKS",
      "description": "Kubernetes service account for the payments microservice in the EKS prod cluster",
      "location": "us-east-1/prod-cluster/payments",
      "tags": [
        { "key": "env", "value": "production" },
        { "key": "team", "value": "payments" },
        { "key": "namespace", "value": "payments" },
        { "key": "criticality", "value": "high" }
      ],
      "additionalData": "{\"clusterName\":\"prod-cluster\",\"namespace\":\"payments\",\"iamRoleArn\":\"arn:aws:iam::123456789:role/PaymentsServiceRole\",\"podSelectors\":[\"app=payments-processor\"],\"automountServiceAccountToken\":true}"
    }
  ]
}
```

**Field notes:**

| Field | Required | Description |
|:---|:---:|:---|
| `originId` | Yes | Stable unique ID from source system — cloud resource ARN, full Kubernetes resource path, or equivalent |
| `providerId` | Yes | Account/tenant/subscription/project ID in the source cloud |
| `providerType` | Yes | Cloud or platform identifier (e.g. `AWS`, `AZURE`, `GCP`, `KUBERNETES`, `GITHUB`, `CUSTOM`) |
| `name` | Yes | Human-readable workload name |
| `type` | No | Identity category (see mapping table in Section 9) |
| `subType` | No | Service or runtime subtype |
| `description` | No | Plain-text description of the workload's function |
| `location` | No | Region, cluster, namespace, or deployment zone |
| `tags` | No | Key/value pairs — include env, team, namespace, criticality, owner |
| `additionalData` | No | Arbitrary JSON string — include IAM roles, attached policies, network exposure, last scan time |

> **Best practice:** For Kubernetes workloads, always include `namespace`, `clusterName`, and whether `automountServiceAccountToken` is true. These are the fields customers interrogate first during Kubernetes security reviews.

---

### 7.2 Query Workloads

```graphql
query ListWorkloads($filter: WorkloadsFilterInput, $pageInput: PageInput) {
  workloads(filter: $filter, pageInput: $pageInput) {
    items {
      id
      originId
      name
      type
      subType
      location
      providerId
      providerType
      tags { key value }
      additionalData
      createdAt
      updatedAt
    }
    totalCount
  }
}
```

**Filter by providerType and location:**
```json
{
  "filter": {
    "and": [
      { "providerType": { "eq": "AWS" } },
      { "location": { "contains": "us-east-1" } }
    ]
  },
  "pageInput": { "limit": 100, "offset": 0 }
}
```

---

### 7.3 Delete Workloads

Delete operations are **irreversible**. Always scope to a specific `providerId` or `originId` — never issue an unfiltered delete.

```graphql
mutation DeleteWorkloads($filter: WorkloadsFilterInput!) {
  deleteExternalWorkloads(filter: $filter) {
    totalDeleted
  }
}
```

---

## 8. Sync Strategy

| Pattern | When to use |
|:---|:---|
| **Full replace** | Scheduled scans — enumerate all workloads in scope, upsert the full set, then delete records whose `originId` is absent from the latest scan result |
| **Delta push** | Event-driven sources (CloudTrail, Kubernetes audit log) — push on create/modify events; use tombstone events for deletions |
| **Reconciliation** | Query Idira by `providerId` after each full scan; diff `originId` sets; delete stale records |

Batch size recommendation: **100 workloads per mutation call**. Track `totalProcessedWorkloads` to verify each batch.

---

## 9. Identity Types and Recommended Mappings

| Source workload type | Recommended `type` | Recommended `subType` |
|:---|:---|:---|
| AWS EC2 instance | `COMPUTE_INSTANCE` | `EC2` |
| AWS Lambda function | `SERVERLESS_FUNCTION` | `LAMBDA` |
| AWS ECS task | `CONTAINER` | `ECS` |
| Kubernetes service account | `KUBERNETES_SERVICE_ACCOUNT` | `EKS` / `GKE` / `AKS` / `GENERIC` |
| Kubernetes pod | `CONTAINER` | `KUBERNETES_POD` |
| Azure VM | `COMPUTE_INSTANCE` | `AZURE_VM` |
| Azure Managed Identity | `MANAGED_IDENTITY` | `AZURE_USER_ASSIGNED` / `AZURE_SYSTEM_ASSIGNED` |
| GCP Service Account | `SERVICE_ACCOUNT` | `GCP_SA` |
| GCP Cloud Run service | `SERVERLESS_FUNCTION` | `CLOUD_RUN` |
| GitHub Actions runner | `CI_CD_PIPELINE` | `GITHUB_ACTIONS` |
| GitLab CI runner | `CI_CD_PIPELINE` | `GITLAB_CI` |
| Jenkins agent | `CI_CD_PIPELINE` | `JENKINS` |
| Generic service identity | `SERVICE_ACCOUNT` | `CUSTOM` |

---

## 10. Error Handling

| HTTP status | Meaning | Action |
|:---|:---|:---|
| `200` | Success | Log `totalProcessedWorkloads` for audit trail |
| `400` | Validation error | Parse GraphQL `errors[]` — fix required field or type mismatch |
| `401` | Token expired or invalid | Re-authenticate and retry once |
| `403` | Insufficient permissions | Verify the **Machines External Data Contributor** role is assigned (replaced the previous Discovery & Context role model on 2026-08-06) |
| `429` | Rate limited | Implement exponential backoff — do not retry in tight loop |
| `500` | Server error | Log full response, retry after backoff, alert if persistent |

Log the `originId` of every record alongside the API response. For partial batch failures, surface per-item errors rather than reporting only the aggregate count.

---

## 11. Pre-Development Checklist

- [ ] OAuth credentials provisioned and stored in a secrets manager (not in code or environment variables)
- [ ] **Machines External Data Contributor** role confirmed on integration user (not the retired Discovery Source / Secrets Hub role)
- [ ] Source system API access verified (can enumerate workloads in target environment)
- [ ] `originId` strategy defined — must be stable across rescans (use cloud-native resource identifiers, not display names or IPs)
- [ ] `providerType` values agreed and documented for all source systems in scope
- [ ] Telemetry header values agreed with your Idira Technical Alliances contact
- [ ] Batch size and scan frequency defined and load-tested against the target environment
- [ ] Logging captures `originId`, mutation result, and `totalProcessedWorkloads` per batch
- [ ] Stale record deletion logic tested in non-production before go-live

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It states the GraphQL single-endpoint pattern, the operation-name vs. server-field distinction (`addReplaceExternalWorkloads` is the field; `AddReplaceWorkloads` is only a client-side label), the fact that the API names this entity `Workload` rather than "machine identity", the post-2026-08-06 role requirement, and the `originId` / `providerId` reconciliation contract. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
