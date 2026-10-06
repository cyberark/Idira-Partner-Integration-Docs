# EPM — Which Integration to Build

**Workflow:** EPM
**Type:** Decision Guide
**Version:** 1.2
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This decision guide helps AI assistants and human partners choose the correct EPM integration path.
Read this before any development guide in the epm/ directory.

WORKFLOW: EPM
IDIRA PRODUCTS COVERED: Idira Endpoint Privilege Manager (EPM)
USE CASES IN THIS WORKFLOW:
  1. Audit Events — stream EPM audit and privilege events to a SIEM or analytics platform
  2. Ticketing — JIT Admin Elevation — gate admin elevation on a ticketing system approval workflow
  3. SOC Response — XDR/SOAR triggers real-time endpoint privilege containment via EPM group membership

DECISION LOGIC: Answer the two questions in Section 2 in order — they map to a specific development guide.
FILES IN THIS DIRECTORY:
  - decision-guide.md — this file
  - audit-events/development-guide.md — stream EPM audit events to a SIEM or analytics platform
  - audit-events/certification-checklist.md
  - ticketing-jit/development-guide.md — JIT admin elevation gated on ticketing system approval
  - soc-response/development-guide.md — XDR/SOAR-triggered endpoint privilege containment
  - soc-response/certification-checklist.md
-->

---

> Use this guide before opening any development guide in the EPM workflow.
> It maps your platform type and integration intent to the correct guide and certification checklist.

---

## 1. Use Case Overview

| Use Case | What it enables | Best for |
|:---------|:----------------|:---------|
| [Audit Events](audit-events/development-guide.md) | Stream EPM privilege and application control audit events into a partner security platform | SIEM, observability, and analytics platforms ingesting endpoint security telemetry |
| [Ticketing — JIT Admin Elevation](ticketing-jit/development-guide.md) | Gate Just-in-Time local admin elevation on an approval workflow in a partner ticketing system | ITSM and ticketing platforms (ServiceNow, Jira, BMC Remedy, Freshservice) |
| [SOC Response — XDR/SOAR Endpoint Containment](soc-response/development-guide.md) | Trigger real-time privilege restriction on a suspicious endpoint from an XDR detection or SOAR playbook | XDR, SOAR, and SIEM platforms with response playbook or automation capability |

---

## 2. Decision Tree

**Q1: What does your platform primarily do?**

- Collects, aggregates, or analyses security events → **Audit Events** — [Development Guide](audit-events/development-guide.md)
- Manages IT service requests, approvals, and change workflows → go to Q2
- Detects threats and executes automated response actions → **SOC Response** — [Development Guide](soc-response/development-guide.md)

**Q2: What endpoint action do you want to automate?**

- An end user requests temporary local admin access and needs approval → **Ticketing — JIT Admin Elevation** — [Development Guide](ticketing-jit/development-guide.md)
- A SOC analyst (or playbook) needs to restrict privileges on a suspicious endpoint during an active investigation → **SOC Response** — [Development Guide](soc-response/development-guide.md)

---

## 3. When NOT to Use This Workflow

- If your platform needs to retrieve or rotate privileged account credentials (passwords, SSH keys): use [Secrets Management](../secrets-management/decision-guide.md) instead.
- If your platform discovers privileged accounts, machine identities, or AI agents across cloud or SaaS environments: use [Discovery](../discovery/) instead.
- If your platform needs to consume identity and access audit events from PAM (not EPM): use [Audit Service](../audit-service/) instead.
- If your use case involves macOS or Linux endpoints: the EPM workflow covers Windows and Windows Server only. Contact `cybr-bizdevtech@paloaltonetworks.com` — this may be a gap.

---

## 4. General Best Practices (All EPM Use Cases)

- Use OAuth 2.0 `client_credentials` flow with a dedicated service account — never use an interactive user account for programmatic access.
- Re-request Bearer tokens on expiry only — do not request a new token on every API call.
- Never print or log Bearer tokens, Client IDs, or Client Secrets.
- Store all credentials in a secrets manager — not in environment variables or source code.
- Log the EPM-internal identifiers (`ComputerId`, `GroupId`, `PolicyId`) alongside your platform's native alert or ticket IDs to ensure a complete audit trail.
- All API requests must include the `x-cybr-telemetry` header — see the relevant development guide for field values.

---

## 5. Terminology Reference

Use current Idira product names in all documentation and certification submissions:

| Current Name | Previous Names |
|:-------------|:---------------|
| Idira Endpoint Privilege Manager (EPM) | CyberArk EPM, CyberArk Endpoint Privilege Manager |
| Idira Privileged Access Manager SaaS | CyberArk Privilege Cloud, Privilege Cloud, PAM SaaS |
| PAM Self-Hosted | Core PAS, Vault |

---

## 6. All Guides in This Workflow

| Use Case | Development Guide | Certification Checklist |
|:---------|:-----------------|:------------------------|
| [Audit Events](audit-events/) | [Guide](audit-events/development-guide.md) | [Checklist](audit-events/certification-checklist.md) |
| [Ticketing — JIT Admin Elevation](ticketing-jit/) | [Guide](ticketing-jit/development-guide.md) | — *(in development — ask your Idira Technical Alliances contact for the criteria)* |
| [SOC Response — XDR/SOAR Endpoint Containment](soc-response/) | [Guide](soc-response/development-guide.md) | [Checklist](soc-response/certification-checklist.md) |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. Also added this change log — the file previously carried none, so no revision before this one is recorded. — Idira Technical Alliances |
