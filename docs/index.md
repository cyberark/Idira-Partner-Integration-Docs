# Idira Partner Integration Development Kits — Index

**Maintained by:** Idira Technical Alliances  
**Contact:** `cybr-bizdevtech@paloaltonetworks.com`  
**Last Updated:** 2026-10-05  
**Version:** 1.4

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this file.

IF YOU ARE AN AGENT, THIS IS PROBABLY THE WRONG FILE. AGENTS.md IS THE MACHINE ENTRY POINT.
This index is the HUMAN front door — a catalogue of what exists, with links. AGENTS.md carries the
normative read order, the file graph, and the stop rule about what the guides do and do not specify.
Read AGENTS.md first; come back here only for the inventory below. Do not reconstruct a read order
from this file's link order — it is a catalogue, and catalogue order is not precedence.

DOCUMENT TYPE: Index / catalogue. No endpoints, no auth, no schemas, no procedure.
ANSWERS: "What kits exist, and where does each one live?"
DOES NOT ANSWER: anything about how to build. Every build fact is in a kit.
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THE INVENTORY IS 16 KITS ACROSS 8 WORKFLOWS: Discovery (4), Secrets Management (4), EPM (3),
Credential Rotation (1), Audit Service (1), Identity Response (1), PSM Connectors (1), Workload
Identity (1). Every kit is a development-guide.md + certification-checklist.md pair in its own
directory. If a partner names a product that is not in the table below, there is NO kit for it — say
so rather than adapting the nearest one, and route the request to the Idira Technical Alliances contact.

THE STATUS COLUMN IS LOAD-BEARING, NOT DECORATION. TWO kits carry a status other than Available —
`identity-response/response-actions` and `workload-identity/swa-federation` — and neither is a
certifiable path yet: a partner can build against them, but do not present their checklists as settled
gates or promise a Marketplace listing on them. The Workload Identity kit additionally has one
deliberate documentation gap, the step-level federation exchange, which is confirmed per build rather
than published — do not let an agent reconstruct it. Every other kit is Available. Read the status cell
itself and check it before telling a partner they can certify.

THREE ROWS ARE NOT KITS. The "All workflows" row points at the top-level decision-guide.md, and the
Secrets Management and Workload Identity rows with "—" in the Integration column point at those
workflows' decision guides. All three are routers. None has a checklist, and none is something a
partner builds against. NOTE that Workload Identity holds a single kit, so its decision guide routes
the INBOUND boundary — whether an integration belongs in that workflow at all — rather than choosing
between kits the way the Discovery, EPM and Secrets Management guides do.

DEPLOYMENT SCOPE CONSTRAINTS STATED HERE — AND IN SOME CASES ONLY HERE (Section "Workflow
Descriptions"). These bound whether an integration is possible at all, so check them before designing:
- PSM Connectors / Web Connection Component: **Idira PAM Self-Hosted only.** Browser automation via the
  PSM Plugin Generator Utility, not a REST integration.
- Identity Response / Response Actions: **Idira SaaS only.** Idira acts as a stateless execution
  engine — the partner playbook resolves the target, runs the action, and reads back per-action status.
- Discovery / Privileged Accounts: the one Discovery kit on the Privilege Cloud REST API rather than the
  Discovery Context GraphQL API, with a different auth flow.

THE DEMONSTRATION REQUIREMENT APPLIES TO EVERY KIT AND IS GRADED IN EVERY CHECKLIST. Either a recorded
2–5 minute end-to-end demo video OR a live walkthrough call with the Idira Technical Alliances contact. The FORMAT is the
partner's choice — recording restrictions, customer-data sensitivity and approval delays are all valid
reasons to book the call instead — but the demonstration itself is not optional. Do not describe it as
a nice-to-have, and do not tell a partner a video is mandatory.

DO NOT IMPLEMENT TELEMETRY FROM THIS FILE'S TABLE. The table here is a field summary; it does not carry
the transform, and its `it=SIEM` cell is an example drawn from one kit rather than a default. The
`IntegrationType` value is ASSIGNED PER KIT and is not free text — look it up in
telemetry-reference.md §3, which is authoritative and also carries the Base64url transform, reference
code in five languages, and test vectors. Adapting another kit's `it` value is a certification failure.
PSM Web Connection Components are the single exception in the corpus and carry no telemetry
requirement at all, being browser automation rather than REST.

CERTIFICATION IS NOT A ONE-TIME EVENT. Listing requires passing the relevant checklist, and the partner
then owns YEARLY RECERTIFICATION plus ongoing support for the integration. Mention the recurring
obligation when a partner asks what certification commits them to.

SIBLING TOP-LEVEL FILES:
- AGENTS.md — the machine entry point: read order, file graph, and hard limits. START THERE.
- journey.md — the five-stage path from integration request to a certified, listed integration
- decision-guide.md — top-level router: which kit, and which option on the integration request form
- telemetry-reference.md — authoritative telemetry transform, per-kit it registry, test vectors
- security-baseline-reference.md — the `Source` column vocabulary and the OWASP ASVS 5.0.0 control
  behind each security requirement. Read it before filling a Source cell or defending a security
  finding. It also lists the checks that LOOK security-shaped and are not (telemetry, demonstration,
  token-expiry handling) — do not source those to ASVS.
- naming-crosswalk.md — resolve a product name that differs between partner material and these kits
- marketplace-standards.md — what a Marketplace listing must contain
- jsb-standards.md — Joint Solution Brief standards

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **New here? Start with [The Partner Integration Journey](journey.md)** — the whole path from integration request to a certified, listed integration, in five stages. Read it once before you start; it tells you what each gate expects while you can still act on it.
>
> **Already know you are building and just need the right kit? [Which Integration Do I Select?](decision-guide.md)** — maps what you are building to the right option on the integration request form and the right kit below. Read it before opening any guide.
>
> This index lists all available workflows and their Development Kits. Each kit contains a Development Guide and a Certification Checklist. The Development Guide gives a technology partner everything needed to understand the use case, navigate their provisioned environment, and develop the integration. The Certification Checklist defines what Idira reviews before listing the integration on the Marketplace.
>
> For Marketplace listing standards, see [`marketplace-standards.md`](marketplace-standards.md). For Joint Solution Brief standards, see [`jsb-standards.md`](jsb-standards.md). If a product name in your own material or in public documentation does not match the name used here, resolve it in [`naming-crosswalk.md`](naming-crosswalk.md) before assuming they are two different products.
>
> For the mandatory telemetry header — the transform, the `IntegrationType` value for your kit, reference code, and test vectors — see [`telemetry-reference.md`](telemetry-reference.md). Build against that file rather than re-deriving the header from your kit's prose.
>
> **Wondering why a requirement applies to you?** Each graded row in a certification checklist carries a `Source` naming the authority behind it — an Idira doc, an OWASP ASVS control, or an Idira house rule. [`security-baseline-reference.md`](security-baseline-reference.md) explains the three and maps every security requirement to its ASVS control. A requirement sourced to a doc or a control is not ours to waive; one sourced to a house rule is, so raise it with your Idira Technical Alliances contact if you think it is wrong.
>
> **Pointing an AI coding agent at these kits?** Start it on [`AGENTS.md`](AGENTS.md) — the read order, the file graph, and the limits on what the guides do and do not specify.

---

## Workflows & Development Kits

| Workflow                                    | Integration                                  | Development Guide                                                                        | Checklist                                                                              | Status    |
| :------------------------------------------ | :------------------------------------------- | :--------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- | :-------- |
| **All workflows**                           | **Which integration do I select?**           | [**Top-Level Decision Guide**](decision-guide.md)                                        | —                                                                                      | Available |
| [Discovery](discovery/)                     | Privileged Accounts                          | [Development Guide](discovery/privileged-accounts/development-guide.md)                  | [Checklist](discovery/privileged-accounts/certification-checklist.md)                  | Available |
| [Discovery](discovery/)                     | AI Agents                                    | [Development Guide](discovery/ai-agents/development-guide.md)                            | [Checklist](discovery/ai-agents/certification-checklist.md)                            | Available |
| [Discovery](discovery/)                     | Machine Identities                           | [Development Guide](discovery/machine-identities/development-guide.md)                   | [Checklist](discovery/machine-identities/certification-checklist.md)                   | Available |
| [Discovery](discovery/)                     | Secrets                                      | [Development Guide](discovery/secrets/development-guide.md)                              | [Checklist](discovery/secrets/certification-checklist.md)                              | Available |
| [Credential Rotation](credential-rotation/) | CPM REST API Plugin                          | [Development Guide](credential-rotation/cpm-rest-api/development-guide.md)               | [Checklist](credential-rotation/cpm-rest-api/certification-checklist.md)               | Available |
| [Audit Service](audit-service/)             | SIEM Integration                             | [Development Guide](audit-service/siem-integration/development-guide.md)                 | [Checklist](audit-service/siem-integration/certification-checklist.md)                 | Available |
| [EPM](epm/)                                 | Audit Events                                 | [Development Guide](epm/audit-events/development-guide.md)                               | [Checklist](epm/audit-events/certification-checklist.md)                               | Available |
| [EPM](epm/)                                 | Ticketing — JIT Admin Elevation              | [Development Guide](epm/ticketing-jit/development-guide.md)                              | [Checklist](epm/ticketing-jit/certification-checklist.md)                              | Available |
| [EPM](epm/)                                 | SOC Response — XDR/SOAR Endpoint Containment | [Development Guide](epm/soc-response/development-guide.md)                               | [Checklist](epm/soc-response/certification-checklist.md)                               | Available |
| [Identity Response](identity-response/)     | Identity Response Actions (XDR/SIEM/SOAR)    | [Development Guide](identity-response/response-actions/development-guide.md)             | [Checklist](identity-response/response-actions/certification-checklist.md)             | Preview |
| [Secrets Management](secrets-management/)   | —                                            | [Decision Guide](secrets-management/decision-guide.md)                                   | —                                                                                      | —         |
| [Secrets Management](secrets-management/)   | Secrets Manager SaaS                         | [Development Guide](secrets-management/secrets-manager-saas/development-guide.md)        | [Checklist](secrets-management/secrets-manager-saas/certification-checklist.md)        | Available |
| [Secrets Management](secrets-management/)   | Credential Provider (CP)                     | [Development Guide](secrets-management/credential-provider/development-guide.md)         | [Checklist](secrets-management/credential-provider/certification-checklist.md)         | Available |
| [Secrets Management](secrets-management/)   | Central Credential Provider (CCP)            | [Development Guide](secrets-management/central-credential-provider/development-guide.md) | [Checklist](secrets-management/central-credential-provider/certification-checklist.md) | Available |
| [Secrets Management](secrets-management/)   | Secrets Manager Self-Hosted                  | [Development Guide](secrets-management/secrets-manager-self-hosted/development-guide.md) | [Checklist](secrets-management/secrets-manager-self-hosted/certification-checklist.md) | Available |
| [PSM Connectors](psm-connectors/)           | Web Connection Component                     | [Development Guide](psm-connectors/web-connection-component/development-guide.md)        | [Checklist](psm-connectors/web-connection-component/certification-checklist.md)        | Available |
| [Workload Identity](workload-identity/)     | —                                            | [Decision Guide](workload-identity/decision-guide.md)                                    | —                                                                                      | —         |
| [Workload Identity](workload-identity/)     | SWA Federation                               | [Development Guide](workload-identity/swa-federation/development-guide.md)               | [Checklist](workload-identity/swa-federation/certification-checklist.md)               | Preview   |

> **Status key:** *Available* — the kit is complete and open for development and certification.
> *Preview* — the kit is published for early review and is not yet a certifiable path: you can build
> against it, but do not treat its checklist as a settled gate. A Preview kit also marks what is
> genuinely unsettled, in one of two ways: an unsettled API field name is marked `[TBD]` in the guide,
> and an unsettled procedure is stated as a visible gap telling you to confirm it. Both mean ask
> rather than guess past it. *—* — the row is a supporting document, not a development kit.

---

## Workflow Descriptions

### Discovery
Push discovered identities into Idira Privileged Access Manager SaaS. Covers four asset categories: Privileged Accounts, AI Agents, Machine Identities (workloads), and Secrets. The AI Agents, Machine Identities, and Secrets kits use the Idira Discovery Context GraphQL API; the Privileged Accounts kit uses the separate Privilege Cloud REST API, and its authentication flow differs. Start with the [Discovery Decision Guide](discovery/decision-guide.md).

### Credential Rotation
Develop a CPM plugin using the Idira REST API framework to automate credential verification, change, and reconciliation for a target application.

### Audit Service
Stream identity and privileged access audit events from Idira into a partner security platform (SIEM, analytics, observability).

### EPM
Three use cases: stream EPM audit events into a partner security platform (SIEM, observability); integrate EPM's Just-in-Time (JIT) admin elevation with a partner ticketing system to gate elevation requests through an approval workflow; or trigger real-time endpoint privilege containment from an XDR detection or SOAR playbook. Start with the [EPM Decision Guide](epm/decision-guide.md) to choose the right path.

### Secrets Management
Enable a partner application, service, or tool to securely retrieve secrets from Idira instead of storing them locally. Covers four integration paths — Secrets Manager SaaS, CP (agent-based), CCP (agentless REST), and Secrets Manager Self-Hosted. Start with the [Decision Guide](secrets-management/decision-guide.md) to choose the right path.

### PSM Connectors
Package a connection component that lets Idira Privileged Session Manager (PSM) broker a privileged session to a partner web application: PSM launches a controlled browser on the customer's PSM server, injects vaulted credentials into the application's login web form, and records the session. This is a browser-automation integration built with the PSM Plugin Generator Utility, not a REST/API integration, so the telemetry-header requirement below does not apply to it. Idira PAM Self-Hosted only.

### Workload Identity
Let a partner platform that runs, routes, or hosts workloads establish SPIFFE identity for them, so those workloads authenticate to Idira with a short-lived attested SVID instead of a distributed secret. Covers **Secure Workload Access (SWA)**, which is delivered as part of Secrets Manager SaaS rather than as a standalone product — `workload-identity/` is a use-case label, not a product name. One kit, so the [Decision Guide](workload-identity/decision-guide.md) confirms the integration belongs in this workflow rather than in Secrets Management or Discovery, which is where it is most often misfiled: establishing an identity and using one to fetch a secret are different integrations. Note that "SWA" also abbreviates the unrelated Secure Web Application Connectors Framework — see the decision guide before matching a kit. **Preview.**

### Identity Response
Let any partner XDR, SIEM, or SOAR platform trigger deterministic identity and privilege response actions in Idira in real time — lock or disable a user, force logout, expire a password, remove a privileged role, list/terminate/suspend privileged sessions, rotate or verify a credential, vault a flagged account, and disable a Secure Infrastructure Access policy. Idira acts as a stateless execution engine: the playbook resolves the target entity, runs the action, and reads back per-action status. Idira SaaS only. Applies to platforms such as Palo Alto Cortex (XSIAM / XSOAR), Google Security Operations, and Splunk.

---

## Certification

All partner-led integrations must pass Idira certification before being listed on the Idira Marketplace. Certification is a review process where Idira validates the integration against the checklist for the relevant integration type. Once certified, the partner is responsible for yearly recertification and ongoing support.

### Demonstration Requirement (All Integrations)

Every certification submission must include a demonstration of the integration working end to end. Either format satisfies the requirement:

- A **recorded demo video** (2–5 minutes) showing the end-to-end flow, **or**
- A **live demonstration call** with the Idira Technical Alliances contact, walking the same flow.

Partners who cannot publish a video — for recording restrictions, customer-data sensitivity, or approval delays — should book the live call instead. What is not optional is the demonstration itself.

---

## Telemetry Requirement (All Integrations)

All certified integrations must include the `x-cybr-telemetry` HTTP header on every API transaction, Base64 URL-encoded:

| Field | Header Key | Required | Example |
|:------|:-----------|:---------|:--------|
| IntegrationName | `in` | Yes | `in=Azure Sentinel Audit` |
| IntegrationType | `it` | Yes | `it=SIEM` |
| IntegrationVersion | `iv` | Yes | `iv=1.0` |
| VendorName | `vn` | Yes | `vn=Microsoft` |
| VendorVersion | `vv` | No | `vv=10.0` |

**Do not implement from this table alone.** [`telemetry-reference.md`](telemetry-reference.md) is the authoritative reference: it carries the full transform, the assigned `IntegrationType` value for every kit, working code in five languages, and test vectors. The `IntegrationType` value is assigned per kit and is not free text — look yours up rather than adapting another kit's.

PSM Web Connection Components are the one exception and carry no telemetry requirement, since they are browser automation rather than REST.

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.4 | 2026-10-05 | **[Added]** The **Workload Identity** workflow and its single kit, **SWA Federation**, taking the inventory to 16 kits across 8 workflows. It fills a gap this catalogue made visible: workload identity federation appeared only as the fourth authentication option inside the Secrets Manager SaaS guide, which serves a retrieval client that happens to hold an SVID and gave nothing to a partner whose platform *is* the identity surface — so gateways, agent runtimes and platforms that already issue SPIFFE identities had no kit to build against and no checklist to be graded on. Listed as **Preview**, which makes it the second non-Available kit, so the AI context block's status warning now names two rather than one. Two rows were added, not one: the kit plus a workflow decision guide, which takes the router count in this table from two to three. That decision guide is deliberately unlike the Discovery, EPM and Secrets Management ones — with a single kit there is no within-workflow choice, so it routes the inbound boundary instead, which is where this integration is most often misfiled. The Status key was also generalised: it described an unsettled API field name marked `[TBD]` as the only form a Preview gap takes, and the new kit's gap is an unsettled *procedure* stated as visible prose instead, so both forms are now described. No existing listing, status or requirement was changed. — Idira Technical Alliances |
| 1.3 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.2 | 2026-10-01 | **[Added]** `security-baseline-reference.md` to the sibling-file list in the AI context block and to the reader-facing pointers, including why it matters to a partner: a requirement sourced to an Idira doc or an OWASP ASVS control is not ours to waive, and one sourced to a house rule is. No listing, status or requirement was changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. Because this file is the human catalogue and `AGENTS.md` is the machine entry point, the block leads by routing agents away from it: it states that the read order is normative in `AGENTS.md` and that this file's link order is catalogue order rather than precedence. It records the inventory as 15 kits across 7 workflows and instructs that a product absent from the table has no kit, rather than inviting the nearest one to be adapted. It flags the Status column as load-bearing — `identity-response/response-actions` carries a status other than Available and is not yet a certifiable path — and that two table rows are routers rather than kits. It carries the deployment-scope constraints this file states and in some cases states alone: PSM Connectors is PAM Self-Hosted only, Identity Response is SaaS only, and Discovery/Privileged Accounts is the one Discovery kit on the Privilege Cloud REST API. It records that the demonstration requirement is graded in every checklist with the format being the partner's choice but the demonstration itself not optional, that telemetry must not be implemented from this file's summary table — whose `it=SIEM` cell is one kit's example and not a default — and that certification carries a recurring yearly recertification and support obligation. Also added the `**Version:**` header field and this change log; the file carried `**Last Updated:**` but no version and no revision history, so no change before this one is recorded. No listing, status or requirement was changed. — Idira Technical Alliances |
