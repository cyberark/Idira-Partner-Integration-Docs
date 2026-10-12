# Discovery Workflow — Which Dev Kit to Build Against

**Workflow:** Discovery  
**Type:** Decision Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.3  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about Discovery integrations.

DOCUMENT TYPE: Workflow decision guide — a ROUTER, not a build guide. No auth procedure, no request
  bodies, no field schemas. Its job is to pick which of four kits a partner builds against.
WORKFLOW: Discovery
ANSWERS: "Which Discovery dev kit matches what this tool scans?"
DOES NOT ANSWER: how to authenticate, shape a mutation, or map a field. That is the selected kit's
  development-guide.md. Do not answer a build question from this file.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

DIRECTION IS THE DEFINING PROPERTY OF THIS ENTIRE WORKFLOW, AND IT IS THE OPPOSITE OF SECRETS
MANAGEMENT. Discovery kits PUSH INVENTORY INTO IDIRA: the partner tool scans an environment and reports
what it found. A Discovery integration reports WHERE a secret lives and WHAT it is — it does NOT
transmit the secret value, and the ../secrets-management/ kits, which retrieve secret values FROM
Idira, are a different workflow with different checklists. "Our platform finds secrets" is Discovery.
"Our platform needs a secret" is Secrets Management. Getting this backwards produces an integration
that fails on its first check.

THE KITS ARE ADDITIVE, NOT MUTUALLY EXCLUSIVE (Section 2's note). This is the one place a decision
guide in this corpus does NOT narrow to a single answer. A cloud scanner routinely pushes machine
identities (EC2 instances, EKS service accounts) AND secrets (AWS access keys, Kubernetes secrets) in
one sync cycle. Build against each kit that matches the tool's scanning surface — and note that each
kit carries its OWN certification checklist, so a two-object integration is certified twice, not once.
Do not merge two kits into one submission.

ONE API FAMILY, BUT PRIVILEGED ACCOUNTS IS THE EXCEPTION ON EVERY AXIS. Three kits share the Discovery
Context GraphQL endpoint `/api/discovery/graphql`; Privileged Accounts uses the separate Privilege Cloud
REST API at `/api/discovered-accounts`. Auth differs too — see below. Never assume a fact from one of
the three transfers to Privileged Accounts.

THE FOUR KITS, THEIR MUTATIONS, AND THEIR TELEMETRY IDENTIFIERS:
- privileged-accounts/    Privilege Cloud REST `/api/discovered-accounts`  it=Privileged-Account-Discovery
- secrets/                addReplaceExternalSecrets                        it=Secrets-Discovery
- machine-identities/     addReplaceExternalWorkloads                      it=Machine-Identity-Discovery
- ai-agents/              addReplaceExternalAiAgents                       it=AI-Agent-Discovery
NOTE THE CASING: the Discovery kits are the only ones in the corpus using Title-Hyphen `it` values.
Everywhere else is CamelCase (`SecretsManager`, `CredentialRotation`). The values are assigned, not
derivable — see ../telemetry-reference.md §3 and do not normalise the casing.

THE DECISION IS TWO QUESTIONS, AND THE FIRST ONE IS ABOUT INTENT RATHER THAN OBJECT TYPE (Section 2).
Question 1: does the tool onboard privileged credentials into PAM vault safes for ACTIVE MANAGEMENT —
storage, rotation, governance by Idira? Yes -> Privileged Accounts, and stop. No, the tool scans and
surfaces findings -> question 2 picks the object type: credentials at rest -> Secrets; compute and
workload identities -> Machine Identities; autonomous AI agents -> AI Agents. A tool that finds an SSH
key and reports it is Secrets; a tool that finds one and vaults it is Privileged Accounts. Inventory
versus active management is the whole distinction, and object type does not settle it.

MACHINE IDENTITIES VERSUS AI AGENTS IS A REAL BOUNDARY, NOT A SPECTRUM (Sections 3's "strongest
signal" lines). Machine Identities is non-human, NON-AGENT compute — things that run code and carry
credentials. AI Agents is explicitly AI agent frameworks, cloud AI services and agentic pipelines
(Bedrock Agents, Azure AI Agents, Vertex AI, LangChain, CrewAI, AutoGen). A Lambda function is a
machine identity; a Bedrock Agent is an AI agent. Do not route a general compute workload to the AI
Agents kit because it happens to call a model API.

KUBERNETES SECRETS APPEARS UNDER TWO KITS IN SECTION 4 AND THAT IS DELIBERATE, NOT AN ERROR. It is the
one row with two checkmarks — the secret material is a Secrets push, the service account that consumes
it is a Machine Identities push. Report both if the tool sees both.

SHARED REQUIREMENTS THAT ARE GRADED IN ALL FOUR CHECKLISTS (Section 5) — carry these into generated
code by default:
- Auth: OAuth 2.0 client credentials against `https://<tenant>.id.cyberark.cloud/oauth2/platformtoken`.
  NOTE THE PATH: `platformtoken`, NOT the `/oauth2/token/<APP_NAME>` shape used by the ../epm/ and
  ../audit-service/ kits. Privileged Accounts is the exception and uses its own flow — see that guide.
- Token handling: cache and reuse, refresh proactively before expiry, NEVER persist to disk.
- `originId` MUST be a stable cloud-native resource identifier — an ARN, a full vault path, a
  Kubernetes resource path. NOT a display name, NOT an IP address, NOT anything that can change
  between scans. This is the single most consequential field in the workflow: an unstable `originId`
  turns every scan into a duplicate insert rather than an update.
- Keep each mutation request within the documented 64 KB request-size limit, and check the
  `totalProcessed*` field to confirm completeness rather than trusting a 200 response.
- Stale-record deletion after a full-replace scan: diff the current scan against your own record of the
  `originId`s pushed last run, and delete what is absent — the Machines External Data Contributor role
  can write but cannot read inventory. An integration that only ever adds will fail this.
- OAuth credentials in a secrets manager — not an environment variable, not a config file.

TELEMETRY VALUES ARE AGREED WITH THE Idira Technical Alliances contact BEFORE CERTIFICATION (Section 5). The `it` values above are
the assigned registry entries, but `in`, `iv` and `vn` are the partner's and are confirmed with the
Idira Technical Alliances contact rather than chosen unilaterally at build time.

NO CERTIFICATION CHECKLIST PAIRS WITH THIS FILE, BY DESIGN. Nothing here is graded directly; the checks
live in the four kits. This file is also not read by the corpus checker, which only inspects
directories holding a development-guide/certification-checklist pair — so a claim made here is not
cross-validated against anything. Keep it to routing.

FILES IN THIS DIRECTORY:
- decision-guide.md — this file — which Discovery kit to build against
- privileged-accounts/ · secrets/ · machine-identities/ · ai-agents/ — the four kits, each a
  development-guide + certification-checklist pair
- ../journey.md — the stage above this one: which workflow, before which kit
- ../telemetry-reference.md — the telemetry transform, the it registry, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> Use this guide before opening any development guide. It maps your partner tool's scanning surface to the correct Discovery dev kit and directs you to the right guide and certification checklist.

---

## 1. Solution Overview

Idira's Discovery workflow uses a single shared API — the **Discovery Context API** (GraphQL, OAuth 2.0) — but exposes four distinct object types. Each dev kit targets one object type. Your choice depends on what your tool scans and what data it can surface.

| Dev Kit | What you push | Where it lands in Idira | API mutation |
|:--------|:-------------|:------------------------|:-------------|
| **Privileged Accounts** | Discovered privileged accounts for onboarding into Idira Privileged Access Manager SaaS safes | `Inventory > Privileged Accounts` | Privilege Cloud REST API (`/api/discovered-accounts`) |
| **Secrets** | API keys, database credentials, certificates, tokens, cloud access keys | `Inventory > Secrets` | `addReplaceExternalSecrets` |
| **Machine Identities** | Compute instances, containers, Kubernetes service accounts, serverless functions, CI/CD pipelines | `Inventory > Machine Identities` | `addReplaceExternalWorkloads` |
| **AI Agents** | LLM-powered agents, automation bots, agentic pipelines | `Inventory > AI Agents` | `addReplaceExternalAiAgents` |

> **Note:** The Secrets, Machine Identities, and AI Agents dev kits all use the same GraphQL endpoint (`/api/discovery/graphql`). The Privileged Accounts dev kit uses the separate Privilege Cloud REST API. Authentication flows differ — see the relevant guide.

---

## 2. Decision Tree

Answer these two questions in order:

```
1. Does your tool discover and onboard privileged credentials
   (passwords, SSH keys) into PAM vault safes for active management?
   │
   ├─ Yes ──────────────────────────────────────────────────► Privileged Accounts
   │
   └─ No — my tool scans environments and surfaces findings
       │
       └─ What does your tool primarily identify?
           │
           ├─ Credentials at rest: API keys, database passwords,
           │  certificates, tokens, cloud access keys ────────► Secrets
           │
           ├─ Compute and workload identities: VMs, containers,
           │  Kubernetes service accounts, Lambda functions,
           │  CI/CD pipelines ─────────────────────────────► Machine Identities
           │
           └─ Autonomous AI agents: LLM-powered services,
              automation bots, agentic pipelines ────────────► AI Agents
```

**Note:** Many tools will push to more than one dev kit in the same integration. A cloud scanner may push both machine identities (EC2 instances, EKS service accounts) and secrets (AWS access keys, Kubernetes secrets) in a single sync cycle. The dev kits are additive — build against each one that matches your tool's scanning surface.

---

## 3. Use Cases by Dev Kit

### Privileged Accounts

Use this dev kit when:

- Your tool scans an environment and surfaces privileged credentials (local admin accounts, service accounts, SSH keys) that need to be onboarded into the Idira Privileged Access Manager SaaS vault
- Your use case is **active credential management** — accounts that will be stored, rotated, and governed by Idira Privileged Access Manager SaaS
- You are building a scanner that feeds the Idira onboarding pipeline (discover → check existence → onboard to safe)
- The customer wants discovered accounts placed into Idira Privileged Access Manager SaaS safes with assigned platforms and rotation policies

> **Scope:** This dev kit uses the Privilege Cloud REST API, not the Discovery Context GraphQL API. Adding accounts requires **Idira Privilege Cloud Discovery Source**; checking, reading and onboarding also require a Privilege Cloud administrator role (Lite, Basic or full).

### Secrets

Use this dev kit when:

- Your tool scans source code repositories, cloud secrets managers, CI/CD pipelines, container images, or infrastructure-as-code for credentials at rest
- You surface API keys, database passwords, TLS/SSL certificates, SSH private keys, OAuth tokens, or cloud access keys
- Your goal is **secrets inventory** — enumeration, expiry tracking, and compliance reporting — not active rotation by Idira
- You integrate with AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, HashiCorp Vault, GitHub/GitLab secret scanning, or Kubernetes Secrets
- The customer needs to identify orphaned secrets, near-expiry certificates, or static credentials that should be rotated to dynamic

**Strongest signal for this kit:** Your tool's output is a list of where secrets live and what they are — not the secrets themselves. Push `permanence` and `validityTo` wherever available; those two fields drive the most actionable customer workflows.

### Machine Identities

Use this dev kit when:

- Your tool is a CIEM, CNAPP, cloud security posture, or Kubernetes security scanner
- You discover compute instances (EC2, Azure VMs, GCP instances), containers, Kubernetes pods and service accounts, serverless functions, or CI/CD pipeline runners
- Your goal is **workload inventory** — giving the customer visibility into which machine identities exist and what credentials they carry
- You need to correlate workload identities with secrets or privileged accounts discovered from the same environment
- The customer is building Zero Trust architecture and needs a machine identity inventory as the policy foundation

**Strongest signal for this kit:** Your tool enumerates non-human, non-agent compute identities — things that run code and carry credentials.

### AI Agents

Use this dev kit when:

- Your tool discovers or manages LLM-powered agents, automation bots, or agentic pipelines (AWS Bedrock Agents, Azure AI Agents, LangChain, CrewAI, AutoGen, Vertex AI)
- You surface autonomous services that assume IAM roles, call external APIs, or operate with scoped credentials across cloud boundaries
- Your goal is **AI agent inventory** — bringing autonomous agent identities under the same PAM visibility applied to human and machine accounts
- The customer needs to satisfy AI governance requirements (NIST AI RMF, OWASP LLMSVS) or CIEM/CNAPP frameworks that now include AI workload identity

**Strongest signal for this kit:** Your tool's scanning surface is explicitly AI agent frameworks, cloud AI services, or agentic pipelines — not general compute workloads.

---

## 4. Use-Case Quick Reference

| Use case | Privileged Accounts | Secrets | Machine Identities | AI Agents |
|:---------|:-------------------:|:-------:|:-----------------:|:---------:|
| Onboard discovered accounts into Idira Privileged Access Manager SaaS safes | ✓ | | | |
| Enumerate credentials at rest (API keys, passwords, certs) | | ✓ | | |
| Track certificate expiry and near-expiry alerts | | ✓ | | |
| Classify static vs dynamic credentials | | ✓ | | |
| Cloud secrets manager inventory (AWS/Azure/GCP/HashiCorp) | | ✓ | | |
| GitHub/GitLab secret scanning integration | | ✓ | | |
| Kubernetes Secrets enumeration | | ✓ | ✓ | |
| Discover EC2, Azure VM, GCP compute instances | | | ✓ | |
| Discover Lambda / Cloud Run / serverless functions | | | ✓ | |
| Kubernetes service account / pod discovery | | | ✓ | |
| CI/CD runner inventory (Jenkins, GitHub Actions, GitLab) | | | ✓ | |
| Cloud IAM / managed identity discovery | | | ✓ | |
| AWS Bedrock / Azure AI / Vertex AI agent discovery | | | | ✓ |
| LangChain / CrewAI / AutoGen agent inventory | | | | ✓ |
| AI governance and agent privilege scoping | | | | ✓ |

---

## 5. Shared Technical Requirements (All Dev Kits)

These apply regardless of which dev kit you build against:

- **Authentication:** OAuth 2.0 client credentials flow against `https://<tenant>.id.cyberark.cloud/oauth2/platformtoken` (except Privileged Accounts — see that guide)
- **Token handling:** Cache and reuse the access token; refresh proactively before expiry; never persist to disk
- **Telemetry header:** All requests must include `x-cybr-telemetry` Base64 URL-encoded — values must be agreed with your Idira Technical Alliances contact before certification
- **`originId` stability:** Must be a stable, cloud-native resource identifier (ARN, full vault path, Kubernetes resource path) — not a display name or IP address that may change between scans
- **Batch size:** each mutation request at most 64 KB; track the `totalProcessed*` field to verify completeness
- **Stale record deletion:** After full-replace scans, diff against your own record of pushed `originId`s and delete records not present in the latest scan (querying by `providerId` requires Machines Admin)
- **No secrets in code or config:** OAuth credentials must be stored in a secrets manager, not environment variables or config files

---

## 6. Development Guides

| Dev Kit | Development Guide | Certification Checklist |
|:--------|:-----------------|:------------------------|
| [Privileged Accounts](privileged-accounts/) | [Development Guide](privileged-accounts/development-guide.md) | [Checklist](privileged-accounts/certification-checklist.md) |
| [Secrets](secrets/) | [Development Guide](secrets/development-guide.md) | [Checklist](secrets/certification-checklist.md) |
| [Machine Identities](machine-identities/) | [Development Guide](machine-identities/development-guide.md) | [Checklist](machine-identities/certification-checklist.md) |
| [AI Agents](ai-agents/) | [Development Guide](ai-agents/development-guide.md) | [Checklist](ai-agents/certification-checklist.md) |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-08 | **[Updated]** Batch sizing follows the documented 64 KB request-size limit rather than a 100-record count. Stale-record deletion reconciles against the integration's own push record, since the required write-only role cannot read inventory. The Privileged Accounts persona names both roles it needs | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, extending the agent-readable layer from the fifteen kits to the workflow decision guides. It leads with direction, which defines the whole workflow and is the inverse of Secrets Management: Discovery kits push inventory **into** Idira and report where a secret lives without ever transmitting its value. It records the property unique to this decision guide — the four kits are **additive**, so a cloud scanner pushing both machine identities and secrets builds against two kits and is certified twice rather than merging them into one submission — and that Privileged Accounts is the exception on every axis, using the Privilege Cloud REST API and its own auth flow while the other three share the Discovery Context GraphQL endpoint. It carries the four mutation names alongside the assigned `it` values, flagging that the Discovery kits are the only ones in the corpus using Title-Hyphen casing and that it must not be normalised. It states that the first decision question turns on intent rather than object type — inventory versus active management, so a tool that reports an SSH key is Secrets while one that vaults it is Privileged Accounts — that the Machine Identities/AI Agents split is a real boundary rather than a spectrum, and that Kubernetes Secrets carrying two checkmarks in Section 4 is deliberate. The shared graded requirements are spelled out for generated code, with emphasis on the `platformtoken` path that differs from the EPM and Audit Service kits and on `originId` stability, since an unstable identifier turns every scan into a duplicate insert. Finally it notes that no checklist pairs with this file and the corpus checker never reads it, so nothing here is cross-validated and it should stay limited to routing. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No routing guidance was changed. — Idira Technical Alliances |
