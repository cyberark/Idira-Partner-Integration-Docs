# Secrets Management — Which Integration to Build

**Workflow:** Secrets Management  
**Type:** Decision Guide  
**Author:** Idira Technical Alliances  
**Source:** Idira Secrets Manager Overview & Best Practices for Tech Partners  
**Version:** 1.1  
**Last Updated:** 2026-09-30

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about Secrets Management integrations.

DOCUMENT TYPE: Workflow decision guide — a ROUTER, not a build guide. It contains no endpoints, no
  auth procedure and no code. Its whole job is to pick which of four kits a partner builds against.
WORKFLOW: Secrets Management
ANSWERS: "Which Idira secrets product should this integration target?"
DOES NOT ANSWER: how to authenticate, retrieve, or write a secret. That is the selected kit's
  development-guide.md. Do not answer a build question from this file.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

READ THIS BEFORE ANY development-guide.md IN THIS WORKFLOW, AND SAY SO. Every one of the four kits
opens with check 2.1 — "appropriate solution confirmed via the Decision Guide" — so skipping this step
is a graded failure, not a shortcut. If a partner arrives already naming a product, confirm the choice
against Section 2 rather than accepting it: picking the wrong kit means building the wrong integration
and failing certification on the first check.

THE FOUR KITS AND THEIR TELEMETRY IDENTIFIERS (the `it` value is per-kit and not interchangeable):
- Secrets Manager SaaS (Conjur Cloud), Idira-managed        -> secrets-manager-saas/        it=SecretsManager
- Credential Provider (CP), agent on the app machine        -> credential-provider/         it=CP
- Central Credential Provider (CCP), agentless REST         -> central-credential-provider/ it=CCP
- Secrets Manager Self-Hosted (Conjur Enterprise)           -> secrets-manager-self-hosted/ it=SecretsManagerSH
See ../telemetry-reference.md for the header transform and test vectors.

THE DECISION TAKES THREE INPUTS, IN ORDER (Section 2), AND THE FIRST ONE DOES NOT DISCRIMINATE
EVERYTHING. 1) the customer's Idira PAM deployment — SaaS or Self-Hosted; 2) is the partner tool
cloud-native or containerized; 3) can an agent run on the application machine. CP AND CCP WORK AGAINST
BOTH PAM BACKENDS, so question 1 does NOT choose between them — question 3 does. Only the two Conjur
products are split by deployment: Secrets Manager SaaS for a SaaS PAM tenant, Secrets Manager
Self-Hosted for on-prem or private cloud.

CP VERSUS CCP IS ONE QUESTION AND ONLY ONE: can you install an agent on the same machine as the
application? Yes -> CP (local SDK calls, no REST surface at all). No -> CCP (agentless REST). Do not
reason about it from tool architecture, cloud posture or vault backend — those inputs are already spent
by the time this question is reached.

AN AI AGENT IS A WORKLOAD, AND THE ANTI-PATTERN IS EXPLICIT (Section 3a). Do NOT generate an
integration that hands an AI agent a long-lived API key in an env var or a config file — agents are
cloned, forked and redeployed constantly, so a static key leaks with the first snapshot. Retrieve at
runtime against a workload identity. Section 3a's table maps agent deployment to kit; use it rather
than inferring.

SECURE WORKLOAD ACCESS (SWA) IS NOT A PRODUCT AND NOT AN API (Section 3b). It is the SPIFFE-based
workload-identity federation layer delivered as part of Secrets Manager SaaS. There is no SWA kit, no
SWA endpoint and no SWA SKU. If a customer asks for SWA, the answer is the Secrets Manager SaaS kit
built against its workload-authentication surface. Write "Secure Workload Access" (SWA on second
reference), never as a standalone product.

DIRECTION TRAP — RETRIEVAL IS NOT DISCOVERY. All four kits here RETRIEVE secrets from Idira for a
workload to use. Two Discovery kits do the opposite and belong to a different workflow with different
checklists: ../discovery/secrets/ reports secrets that exist elsewhere into an inventory and never
transmits a secret value at all, and ../discovery/ai-agents/ catalogues AI agents as identities rather
than giving them credentials. "Our platform finds secrets" is Discovery; "our platform needs a secret"
is this workflow.

ENVIRONMENT SPLIT — TWO DIFFERENT PARTNER ENVIRONMENTS, AND PARTNERS BUILDING MORE THAN ONE KIT GET
THIS WRONG. Secrets Manager Self-Hosted is provisioned on a SKYTAP environment from the partner's
Idira Technical Alliances contact; CP and CCP are provisioned on the Idira shared ISP environment
(`https://c3.cyberark.cloud`). Both are gated on a signed Partner Agreement. This guide does not state
the split — it is in secrets-manager-self-hosted/development-guide.md Section 4 and in the CP/CCP
prerequisites.

SECTION 4'S BEST PRACTICES ARE GRADED IN ALL FOUR CHECKLISTS, NOT ADVISORY: never log or print a
secret, token or API key; tolerate a temporarily wrong value because a request can land mid-rotation;
cache only for a tight repeated-read window and otherwise fetch live; request a new token only on
expiry, never per retrieval. Carry these into generated code by default.

SECTION 6'S TERMINOLOGY TABLE IS A RECOGNITION AID, NOT A VOCABULARY. The right-hand column is retired
names, and using one is a certification failure in the kit that owns it — `DAP` specifically fails
check 4.1 of the Self-Hosted kit. Read a partner's "AIM", "AAM", "Conjur Cloud" or "DAP" as the current
product, then write the current name back.

NO CERTIFICATION CHECKLIST PAIRS WITH THIS FILE, BY DESIGN. Nothing here is graded directly; the
checks live in the four kits. This file is also not read by the corpus checker, which only inspects
directories holding a development-guide/certification-checklist pair — so a claim made here is not
cross-validated against anything. Keep it to routing.

FILES IN THIS DIRECTORY:
- decision-guide.md — this file — which Secrets Management kit to build against
- secrets-manager-saas/ · credential-provider/ · central-credential-provider/ ·
  secrets-manager-self-hosted/ — the four kits, each a development-guide + certification-checklist pair
- ../journey.md — the stage above this one: which workflow, before which kit
- ../telemetry-reference.md — the telemetry transform, per-kit it values, and test vectors
- ../naming-crosswalk.md — current versus retired product names

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> Use this guide before opening any integration guide. It maps your partner's deployment context to the correct Idira solution and points you to the right guide and certification checklist.

---

## 1. Solution Overview

Idira Secrets Management is a suite of products — not a single API. The right integration depends on how your tool is deployed, how the customer's Idira environment is deployed, and whether your tool can run an agent.

| Product | What it is | Deployment |
|:--------|:-----------|:-----------|
| **Secrets Manager SaaS** | SaaS-hosted secret store (Conjur Cloud) with Workload API | Idira-managed cloud |
| **Credential Provider (CP)** | Agent installed on the same machine as your app; uses SDK calls | Customer-owned (SaaS or Self-Hosted vault backend) |
| **Central Credential Provider (CCP)** | Agentless REST service; no agent on the app machine | Customer-owned (SaaS or Self-Hosted vault backend) |
| **Secrets Manager Self-Hosted** | Self-hosted Conjur Enterprise REST API + Vault Synchronizer | Customer-owned on-prem or private cloud |

---

## 2. Decision Tree

Answer these three questions in order:

```
1. What is the customer's Idira PAM deployment?
   │
   ├─ Idira Privileged Access Manager SaaS
   │   │
   │   └─ Is your tool cloud-native or containerized?
   │       ├─ Yes  ──────────────────────────────────► Secrets Manager SaaS (Conjur Cloud)
   │       └─ No
   │           └─ Can you run an agent on the app machine?
   │               ├─ Yes ──────────────────────────► Credential Provider (CP)
   │               └─ No  ──────────────────────────► Central Credential Provider (CCP)
   │
   └─ PAM Self-Hosted (on-prem / private cloud)
       │
       └─ Is your tool cloud-native or containerized?
           ├─ Yes  ──────────────────────────────────► Secrets Manager Self-Hosted (Conjur Enterprise)
           └─ No
               └─ Can you run an agent on the app machine?
                   ├─ Yes ──────────────────────────► Credential Provider (CP)
                   └─ No  ──────────────────────────► Central Credential Provider (CCP)
```

**Note:** CP and CCP work against both Idira Privileged Access Manager SaaS and Idira Privileged Access Manager Self-Hosted vault backends. The integration guide for each covers both backends.

---

## 3. Use Cases by Product

### Use CP or CCP when your tool is:

- A custom application or COTS tool that needs to access databases, web services, or API credentials at runtime
- A scheduled script that requires secrets to access resources during execution
- An automated build or deployment system that needs credentials at build time
- A traditional application running in a static, non-containerized environment

Choose **CP** if an agent running on the same machine as the application is acceptable.  
Choose **CCP** if the application cannot or should not have a local agent (machine-to-machine REST preferred).

### Use Secrets Manager SaaS (Conjur Cloud) when your tool is:

- A SaaS product — you want to avoid any on-premises component in the integration
- A cloud-native application or container-based workload
- Part of a CI/CD pipeline (Jenkins, GitLab, GitHub Actions)
- A microservice architecture where multiple services need access to secrets

### Use Secrets Manager Self-Hosted (Conjur Enterprise) when:

- The customer runs a fully on-premises or private cloud environment
- Your tool needs to integrate with a self-hosted Conjur Enterprise cluster directly
- The use case requires elastic workload authentication (Kubernetes, cloud IAM, JWT)
- The customer requires maximum control over their secrets infrastructure

---

## 3a. AI Agents and Autonomous Workloads

AI agents — LLM-powered services, agentic pipelines, automation bots — are workloads like any other: they hold credentials, call APIs, and act with no human in the loop. The secrets question for an agent is the same as for any workload — *how does this non-human identity prove who it is before it retrieves a secret?* — but the volume, churn, and blast radius are higher, so the identity model matters more.

### Anti-pattern: static keys baked into an agent

Do not build an integration that hands an AI agent a long-lived API key in an env var or config file. Agents are cloned, forked, and redeployed constantly; a static key leaks with the first snapshot. Every agentic integration should retrieve secrets at runtime against a workload identity, never ship them embedded.

### Recommended pattern by deployment

| If the agent runs as… | Build against | Identity |
|:---|:---|:---|
| A cloud-native / containerized service (K8s, serverless, CI/CD) | **Secrets Manager SaaS** | Workload identity — SPIFFE SVID, JWT, or client certificate (see [SaaS guide §3](secrets-manager-saas/development-guide.md)) |
| A traditional app or bot on a static host, agent allowed | **Credential Provider (CP)** | App authentication on the local agent |
| A traditional app or bot on a static host, no local agent | **Central Credential Provider (CCP)** | Client cert / allowed machine (agentless REST) |
| A self-hosted / air-gapped agent platform | **Secrets Manager Self-Hosted** | Conjur authenticators (K8s, cloud IAM, JWT) |

> **Related but distinct:** *discovering and inventorying* AI agents as identities is a **Discovery** flow, not a Secrets Management flow — see the [AI Agents Discovery dev kit](../discovery/ai-agents/development-guide.md). This section is about how an agent *retrieves secrets*, not how it is catalogued.

---

## 3b. Secure Workload Access (SPIFFE)

**Secure Workload Access (SWA)** is Idira's SPIFFE-based workload identity capability, delivered as part of Secrets Manager SaaS — not a standalone product or doc space. Idira frames it as authenticating **"workloads to external platforms with SWA federation and SPIFFE"**: a workload (including an AI agent) proves its identity with a short-lived, cryptographically attested **SPIFFE SVID** instead of a pre-shared secret.

For partner integrations, SWA is not a separate API to code against — it is the **workload-identity federation layer** on top of Secrets Manager SaaS:

- If the customer's workloads already carry SPIFFE identities, SWA federation is the path that lets those identities authenticate to Secrets Manager SaaS — build against the SaaS workload-authentication surface ([SaaS guide §3a](secrets-manager-saas/development-guide.md)), not a static credential.
- No SPIFFE identity available? Fall back to the standard Workload API auth methods (JWT, or API key as last resort).

Lead with SWA when the customer's pitch is *"give our AI agents and workloads a real identity"* — it is the bundled identity story (Identity Broker + Secure Workload Access + Secrets Management), not a point secret-retrieval feature.

> **Naming & verification:** write **Secure Workload Access** (or **SWA** on second reference); it sits under Secrets Manager SaaS / ISP — do not describe it as a standalone product SKU. The step-level federation flow is documented in the Secrets Manager SaaS *"Authenticate workloads using SPIFFE"* section — verify it there before a partner builds. *(Terminology verified against docs.cyberark.com, 2026-07-17; deeper auth-flow pages need authenticated access. See [naming crosswalk](../naming-crosswalk.md).)*

---

## 4. General Best Practices (All Products)

These apply regardless of which product you build against:

- Never print or write secrets, tokens, or API keys to log or debug files
- Make your integration tolerant to temporarily incorrect secret values — customers rotate secrets on a schedule, and a request may land mid-rotation
- Provide clear, user-friendly error messages and log output so customers can self-diagnose configuration issues
- Cache secrets only when fetching the same secret multiple times in a very short window — otherwise, fetch live so secrets don't go stale
- Request a new access token only when the existing one has expired — do not get a fresh token on every secret retrieval

---

## 5. Development Guides

| Product | Development Guide | Certification Checklist |
|:--------|:-----------------|:------------------------|
| [Secrets Manager SaaS](secrets-manager-saas/) | [Development Guide](secrets-manager-saas/development-guide.md) | [Checklist](secrets-manager-saas/certification-checklist.md) |
| [Credential Provider (CP)](credential-provider/) | [Development Guide](credential-provider/development-guide.md) | [Checklist](credential-provider/certification-checklist.md) |
| [Central Credential Provider (CCP)](central-credential-provider/) | [Development Guide](central-credential-provider/development-guide.md) | [Checklist](central-credential-provider/certification-checklist.md) |
| [Secrets Manager Self-Hosted](secrets-manager-self-hosted/) | [Development Guide](secrets-manager-self-hosted/development-guide.md) | [Checklist](secrets-manager-self-hosted/certification-checklist.md) |

---

## 6. Terminology Reference

Idira product naming has changed over time. Use current names in all documentation and certification submissions:

| Current Name | Previous Names |
|:-------------|:---------------|
| Credential Provider (CP) | AIM, Application Identity Manager |
| Central Credential Provider (CCP) | AAM, Application Access Manager |
| Secrets Manager Self-Hosted | Conjur Enterprise, DAP |
| Secrets Manager SaaS | Conjur Cloud |
| PAM Self-Hosted | Core PAS, Vault |
| Idira Privileged Access Manager SaaS | Privilege Cloud, PAM SaaS |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.1 | 2026-09-30 | **[Added]** AI context block, extending the agent-readable layer from the fifteen kits to the workflow decision guides. It states up front that this file is a router with no endpoints or auth procedure, so a build question must be answered from the selected kit rather than from here, and that all four kits grade "solution confirmed via the Decision Guide" as check 2.1 — skipping this step is a graded failure. It records the three decision inputs in order and the trap that the first one does not discriminate everything: CP and CCP work against both PAM backends, so the deployment question does not choose between them and the agent question does. It carries the four kit paths with their per-kit `it` telemetry values, Section 3a's static-key anti-pattern for AI agents, that Secure Workload Access is a federation layer on Secrets Manager SaaS rather than a product or an API, and the direction trap that separates these four retrieval kits from the Discovery secrets and AI-agents kits. It also records the Skytap-versus-C3 environment split that this guide does not state, that Section 4's best practices are graded in all four checklists rather than advisory, and that Section 6's retired-name column is a recognition aid whose use fails certification — `DAP` specifically against check 4.1 of the Self-Hosted kit. Finally it notes that no checklist pairs with this file and the corpus checker never reads it, so nothing here is cross-validated and it should stay limited to routing. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No routing guidance was changed. — Idira Technical Alliances |
