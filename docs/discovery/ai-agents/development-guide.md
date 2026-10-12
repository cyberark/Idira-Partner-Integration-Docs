# Idira Discovery Service Partner Development Guide

**Workflow:** Discovery  
**Dev Kit:** AI Agents  
**Type:** Self-Service Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.3  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Discovery & Context — the inventory service on the Identity Security Platform that holds the customer's machine identities, AI agents, and secrets.
WORKFLOW: Discovery
USE CASE: AI Agents — a partner scanner pushes the AI agents it discovers (autonomous LLM services, automation bots, agentic pipelines) into the customer's Idira inventory and keeps that inventory current.
INTEGRATION PATTERN: GraphQL. One endpoint, one HTTP verb. Every operation — push, query, delete — is a POST to the same URL with a different GraphQL document in the body. Do not look for per-operation REST paths; there are none.
AUTH METHOD: OAuth 2.0 against ISPSS (Identity Security Platform SaaS) — see Section 5
AUTH HEADER FORMAT: Authorization: Bearer <access_token>
TOKEN ENDPOINT: POST https://<tenant>.id.cyberark.cloud/oauth2/platformtoken
API ENDPOINT: POST https://<tenant>.app.cyberark.cloud/api/discovery/graphql
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs. it=AI-Agent-Discovery
CONTACT: cybr-bizdevtech@paloaltonetworks.com

OPERATION NAME vs. SERVER FIELD — THE MOST COMMON ERROR READING THIS GUIDE. In GraphQL these
are two different things and this guide shows both. The operation name is a client-side label you
may rename freely; the server field is the API and is fixed:
  operation `AddReplaceAiAgents`  ->  server field `addReplaceExternalAiAgents`
  operation `ListAiAgents`        ->  server field `aiAgents`
  operation `DeleteAiAgents`      ->  server field `deleteExternalAiAgents`
Calling `addReplaceAiAgents` (without `External`) fails. The write and delete fields carry
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
  same `originId` twice and the record is updated in place, not duplicated. Getting `originId`
  wrong (for example, using a value that changes between scans) creates duplicate inventory.
- `providerId` identifies the partner source. RECONCILE ON YOUR SIDE: the Machines External Data
  Contributor role can write but CANNOT READ inventory. Persist the set of `originId`s you pushed on
  the previous run, diff it against the current scan, and call `deleteExternalAiAgents` filtered by `originId`
  for what is gone. Querying by `providerId` and diffing in Idira is possible only with Machines Admin.
- Size batches by PAYLOAD, not count: each mutation request may be at most 64 KB. Track
  `totalProcessedAiAgents` on the response — if it is lower than the number you sent, the batch landed only
  partly, which is otherwise silent.
- Delete returns `totalDeleted`.
- A push is an upsert, not a sync. Stale records are NOT removed by pushing a smaller set; they
  must be deleted explicitly.

SIBLING KITS — the other three Discovery kits, easily confused:
- ../machine-identities/: workloads and compute identities. Same endpoint, fields named
  `...Workloads`. it=Machine-Identity-Discovery
- ../secrets/: the credentials those identities use. Same endpoint, fields named `...Secrets`.
  it=Secrets-Discovery. NOTE: that kit discovers secrets that exist elsewhere; the
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

## 1. Why AI Agent Discovery Matters

AI agents — autonomous LLM-powered services, automation bots, agentic pipelines — are proliferating faster than traditional identity governance programs can track them. Each agent carries credentials, assumes roles, calls APIs, and may operate across cloud boundaries with no human in the loop. Left unmanaged, these identities represent an expanding blind spot for security teams.

Integrating AI agent discovery into Idira brings these identities under the same visibility, context enrichment, and policy enforcement applied to human and machine accounts. The Idira Discovery Context API is the authoritative ingestion path: your integration pushes what it sees; Idira provides the inventory, deduplication, lifecycle tracking, and risk posture.

**Current industry signals driving customer demand:**
- AI governance frameworks (NIST AI RMF, OWASP LLMSVS) require organizations to enumerate autonomous agents and their privilege scope.
- CIEM and CNAPP vendors are adding AI workload identity to their scanning surfaces — customers expect PAM to be a correlation point.
- Agentic frameworks (LangChain, CrewAI, AutoGen) and cloud-native AI services (AWS Bedrock Agents, Azure AI Agents, Vertex AI) provision service identities that are rarely reviewed post-deployment.

---

## 2. Use Cases at a Glance

This integration pushes AI agent identities into the Idira AI Agents inventory and keeps them current. It exposes three operations against the Discovery Context API — build the ones your use case needs.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Push (upsert) AI agents | Send discovered agents into the Idira inventory; re-sending updates the existing record | [7.1](#71-push-upsert-ai-agents) |
| 2 | Query AI agents | Read back what your integration has pushed — requires Machines Admin; not needed for reconciliation | [7.2](#72-query-ai-agents) |
| 3 | Delete AI agents | Remove agents that no longer exist in the source, to keep the inventory clean | [7.3](#73-delete-ai-agents) |

A complete discovery integration pushes on each scan and deletes stale records, reconciling against its own record of what it pushed (Section 8). Query is optional and needs the Machines Admin role. Document which operations your integration implements in the certification checklist.

---

## 3. What the Customer Sees in Inventory

Once your integration pushes AI agent records, they appear in the Idira **AI Agents inventory** (`Inventory > AI Agents`). Each entry surfaces:

| Column | Source field |
|:---|:---|
| Agent name | `name` |
| Provider | `providerType` / `providerId` |
| Type / Subtype | `type` / `subType` |
| Location | `location` |
| Tags | `tags[]` |
| Last seen | Managed by Idira (timestamp of last upsert) |
| Additional context | `additionalData` (arbitrary JSON) |

Customers use this inventory to identify unmanaged agents, correlate them with secrets or workloads discovered from the same environment, and feed them into access review workflows. The richer the context your integration provides, the more actionable the inventory becomes.

---

## 4. API User Persona

> **Updated 2026-09-08:** Discovery & Context replaced its role model on 2026-08-06. Three roles now govern the machine identities, AI agents, and secrets inventories: **Machines Admin** (full access), **Machines External Data Contributor** (write-only via API), and **Machines Internal Data Contributor** (internal service access). **Any integration user provisioned under the previous model requires reassignment** — an existing integration will start returning `403` until it is moved.

To call the Discovery Context API, the integration user must sign in to **ISPSS (Identity Security Platform SaaS)** and hold the **Machines External Data Contributor** role. This is the least-privilege role for a partner integration that pushes inventory data in over the API — it grants write access only, which is exactly this integration's access pattern. Do not request **Machines Admin** unless the integration also needs to read or manage inventory beyond its own upserts.

> **Note for administrators:** Provisioning **Machines External Data Contributor** membership in ISPSS is the required step. If this integration user previously held the Secrets Hub role for this API, that assignment must be replaced, not supplemented. Consult your Idira tenant administrator or the Idira Docs portal for the current role assignment procedure.

---

> **What the Contributor role cannot do.** Machines External Data Contributor grants write access through the external API — push and delete — *without the ability to read inventory data*. Queries need **Machines Admin**, which grants full access including queries, mutations and onboarding operations. Build reconciliation from your own record of what you pushed (Section 8), so the integration needs only the Contributor role. Role definitions: Idira Docs what's new, "Simplified roles for the machine identities, AI agents, and secrets inventories" (August 6, 2026).

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

Cache and reuse the returned `access_token` (typically valid 30 minutes). Never store the token persistently — request a fresh one on startup and refresh proactively before expiry.

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
in=<IntegrationName>&it=AI-Agent-Discovery&iv=<version>&vn=<VendorName>
```

Example (before encoding):
```
in=AcmeCorp AI Scanner&it=AI-Agent-Discovery&iv=1.0&vn=Acme Corporation
```

Encode and set the header:
```
x-cybr-telemetry: aW49QWNtZUNvcnAgQUkgU2Nhbm5lciZpdD1BSS1BZ2VudC1EaXNjb3ZlcnkmaXY9MS4wJnZuPUFjbWUgQ29ycG9yYXRpb24=
```

---

## 7. Core API Operations

### 7.1 Push (Upsert) AI Agents

Use `addReplaceExternalAiAgents` to insert new agents or update existing ones. Idira deduplicates on `originId` — if a record with that ID already exists, it is updated in place.

```graphql
mutation AddReplaceAiAgents($aiAgents: [AiAgentInput!]!) {
  addReplaceExternalAiAgents(aiAgents: $aiAgents) {
    aiAgents {
      id
      originId
      name
    }
    totalProcessedAiAgents
  }
}
```

**Variables — full field reference:**

```json
{
  "aiAgents": [
    {
      "originId": "arn:aws:bedrock:us-east-1:123456789:agent/AGNT01",
      "providerId": "aws-prod-123456789",
      "providerType": "AWS",
      "name": "InvoiceProcessingAgent",
      "type": "LLM_AGENT",
      "subType": "BEDROCK_AGENT",
      "description": "Processes invoice PDFs and routes to ERP via tool calls",
      "location": "us-east-1",
      "tags": [
        { "key": "env", "value": "production" },
        { "key": "team", "value": "finance-automation" },
        { "key": "framework", "value": "bedrock" }
      ],
      "additionalData": "{\"modelId\":\"anthropic.claude-3-5-sonnet\",\"toolsAttached\":[\"InvoiceParser\",\"ERPSubmitter\"],\"iamRoleArn\":\"arn:aws:iam::123456789:role/BedrockAgentRole\",\"lastDeployed\":\"2026-05-14T09:00:00Z\"}"
    }
  ]
}
```

**Field notes:**

| Field | Required | Description |
|:---|:---:|:---|
| `originId` | Yes | Stable unique ID from the source system — used for upsert deduplication |
| `providerId` | Yes | Account/tenant/subscription ID in the source cloud or platform |
| `providerType` | Yes | Cloud or platform identifier (e.g. `AWS`, `AZURE`, `GCP`, `GITHUB`, `CUSTOM`) |
| `name` | Yes | Human-readable agent name |
| `type` | Yes | Broad classification (e.g. `LLM_AGENT`, `RPA_BOT`, `AUTOMATION_AGENT`) |
| `subType` | No | Framework or service subtype (e.g. `BEDROCK_AGENT`, `AZURE_AI_AGENT`, `LANGCHAIN`) |
| `description` | No | Plain-text description of what the agent does |
| `location` | No | Region, namespace, or deployment location |
| `tags` | No | Tag entries (`type` `TAG`, `ANNOTATION` or `LABEL`, plus key and value) — use for env, team, risk tier, framework |
| `additionalData` | No | A JSON object **serialized as a string** (escaped quotes, not a nested object) — include IAM role ARN, model ID, tools, last deploy timestamp |
| `instructions` | No | The agent's instruction text or configuration notes |
| `model` | No | The model identifier the agent runs (for example `gpt-4o`) |
| `owners` | No | The agent's owners. Send it whenever you have it — the inventory raises a **missing-owner** risk for agents without one |
| `accountEnabled` | No | Whether the agent is enabled in its origin |
| `originCreatedAt`, `originUpdatedAt` | No | When the agent was created and last updated in its origin |

Full field list: [Add or replace external AI agents](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-ai-agents.htm).

> **Best practice:** Populate `additionalData` generously. Customers use it to answer: *what model does this agent run? what tools can it call? what IAM role does it assume?* These fields materially improve security review quality.

---

### 7.2 Query AI Agents

> Requires the **Machines Admin** role. An integration holding only Machines External Data Contributor cannot query — reconcile from your own push record instead (Section 8).

Use queries to verify what has been pushed and to support reconciliation.

```graphql
query ListAiAgents($filter: AiAgentsFilterInput, $pageInput: PageInput) {
  aiAgents(filter: $filter, pageInput: $pageInput) {
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

**Filter by provider:**
```json
{
  "filter": {
    "providerType": { "eq": "AWS" }
  },
  "pageInput": { "limit": 50, "offset": 0 }
}
```

**Filter by name substring:**
```json
{
  "filter": {
    "name": { "contains": "Invoice" }
  }
}
```

---

### 7.3 Delete AI Agents

Delete operations are **irreversible**. Use filter criteria — never delete without scoping to a specific provider or originId set.

```graphql
mutation DeleteAiAgents($filter: AiAgentsFilterInput!) {
  deleteExternalAiAgents(filter: $filter) {
    totalDeleted
  }
}
```

**Recommended pattern — delete by providerId before a full resync:**
```json
{
  "filter": {
    "providerId": { "eq": "aws-prod-123456789" }
  }
}
```

---

## 8. Sync Strategy

| Pattern | When to use |
|:---|:---|
| **Full replace** | Scheduled scans (hourly/daily) — query all agents from source, call `addReplaceExternalAiAgents` with the full set. Agents no longer present in source should be deleted using the delete mutation. |
| **Delta push** | Event-driven sources — push only on create/update events from source. Avoid delete unless you have a reliable tombstone event. |
| **Reconciliation** | Keep the set of `originId`s you pushed on the last run. After each full scan, diff it against the current `originId`s and call `deleteExternalAiAgents` filtered by `originId` for the ones that are gone. This needs only the Machines External Data Contributor role. (Querying Idira by `providerId` and diffing there requires Machines Admin.) |

Batch size: each mutation request may be at most **64 KB** — there is no record-count limit. Size batches by payload, and compare `totalProcessedAiAgents` with the number you sent to detect a partial batch. See [the add/replace mutation reference](https://docs.cyberark.com/manage/latest/en/content/disco/disco-apis/api-add-replace-ai-agents.htm).

---

## 9. Identity Types and Recommended Mappings

| Source agent type | Recommended `type` | Recommended `subType` |
|:---|:---|:---|
| AWS Bedrock Agent | `LLM_AGENT` | `BEDROCK_AGENT` |
| Azure AI Agent (Assistants API) | `LLM_AGENT` | `AZURE_AI_AGENT` |
| Google Vertex AI Agent | `LLM_AGENT` | `VERTEX_AI_AGENT` |
| LangChain / LangGraph agent | `LLM_AGENT` | `LANGCHAIN` |
| CrewAI agent | `LLM_AGENT` | `CREWAI` |
| AutoGen agent | `LLM_AGENT` | `AUTOGEN` |
| GitHub Actions bot | `AUTOMATION_AGENT` | `GITHUB_ACTIONS` |
| UiPath / Automation Anywhere RPA | `RPA_BOT` | `UIPATH` |
| Custom service identity | `AUTOMATION_AGENT` | `CUSTOM` |

---

## 10. Error Handling

| HTTP status | Meaning | Action |
|:---|:---|:---|
| `200` | Success | Log `totalProcessedAiAgents` for audit trail |
| `400` | Validation error | Parse GraphQL `errors[]` — fix required field or type mismatch |
| `401` | Token expired or invalid | Re-authenticate and retry once |
| `403` | Insufficient permissions | Verify the **Machines External Data Contributor** role is assigned (replaced the previous Discovery & Context role model on 2026-08-06) |
| `429` | Rate limited | Implement exponential backoff — do not retry in tight loop |
| `500` | Server error | Log full response, retry after backoff, alert if persistent |

Always log the `originId` of each agent alongside the API response status. If Idira returns a partial success (some agents processed, some failed), surface per-item errors.

---

## 11. Pre-Development Checklist

- [ ] OAuth credentials provisioned and stored in a secrets manager (not in code or config files)
- [ ] **Machines External Data Contributor** role confirmed on integration user (not the retired Discovery Source / Secrets Hub role)
- [ ] Source system API access verified (can enumerate agents in target environment)
- [ ] `originId` strategy defined — must be stable across rescans (use native cloud resource ID, not display name)
- [ ] Telemetry header values agreed with your Idira Technical Alliances contact (IntegrationName, VendorName, version)
- [ ] Batch size and sync frequency defined
- [ ] Logging captures `originId`, mutation result, and `totalProcessedAiAgents` per run

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-08 | **[Fixed]** Reconciliation is done against the integration's own record of what it pushed, then `deleteExternalAiAgents` by `originId` — the Machines External Data Contributor role this kit requires cannot read inventory, so the query-and-diff method did not work with it. Batches are limited by request size (64 KB per mutation), not by a count of 100. `type` is a required field. **[Added]** `instructions`, `model`, `owners` (an agent without one raises a missing-owner risk), `accountEnabled`, `originCreatedAt` and `originUpdatedAt`; the tag types; that `additionalData` is a serialized JSON string; that queries need Machines Admin | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It states the GraphQL single-endpoint pattern, the operation-name vs. server-field distinction (`addReplaceExternalAiAgents` is the field; `AddReplaceAiAgents` is only a client-side label), the post-2026-08-06 role requirement, and the `originId` / `providerId` reconciliation contract. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
