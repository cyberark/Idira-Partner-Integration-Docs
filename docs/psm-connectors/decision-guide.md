# PSM Connectors — Is This the Right Workflow?

**Workflow:** PSM Connectors
**Type:** Decision Guide
**Author:** Idira Technical Alliances
**Version:** 1.0
**Last Updated:** 2026-11-04

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about PSM Connectors integrations.

DOCUMENT TYPE: Workflow decision guide — a ROUTER, not a build guide. No procedures, no configuration
  values. Do not answer a build question from this file.
WORKFLOW: PSM Connectors
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS WORKFLOW HAS ONE KIT, so there is no within-workflow choice. The guide settles two things before
engineering time is spent: whether the integration belongs here, and which deployment it will be built
and tested on.

DEPLOYMENT: the kit supports Idira Privileged Access Manager Self-Hosted AND Idira Privileged Access
Manager SaaS. On SaaS the partner installs the Connector agent on their own Windows server; there is no
hosted environment to build against. See the Connector server subsection of the development guide.
Never state or imply this kit is Self-Hosted only.
-->

---

## 1. Is This the Right Workflow?

Use this workflow if you want Idira Privileged Session Manager (PSM) to broker and record a privileged session into **your web application**, by packaging a connection component that automates the login in a browser on the PSM server. It is browser automation built with the PSM Plugin Generator Utility, not a REST API integration.

## 2. Which Deployment?

| Your customers run | You build and test on | Connector server |
|:---|:---|:---|
| Idira Privileged Access Manager Self-Hosted | A Self-Hosted environment, provisioned once your request is approved | Not applicable |
| Idira Privileged Access Manager SaaS | Your own Windows server running the Connector agent, connected to a SaaS tenant | **Required** — [install steps and prerequisites](web-connection-component/development-guide.md) |

The Connector agent is the same one Credential Rotation uses. If you build both, install it once and add the CPM and PSM components through Connector Management.

## 3. When NOT to Use This Workflow

- If your integration calls Idira REST APIs, it belongs in another workflow — start from the [journey](../journey.md) or the [index](../index.md).
- If "SWA" in your material means **Secure Workload Access**, you want [Workload Identity](../workload-identity/decision-guide.md). The Secure Web Application Connectors Framework used here is a different thing.
- If you need to rotate a credential on a target system rather than sign in to a web application, use [Credential Rotation](../credential-rotation/decision-guide.md).

## 4. Guide

| Dev Kit | Development Guide | Certification Checklist |
|:---|:---|:---|
| [Web Connection Component](web-connection-component/) | [Development Guide](web-connection-component/development-guide.md) | [Checklist](web-connection-component/certification-checklist.md) |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.0 | 2026-11-04 | **[Added]** First publication. The kit and its development guide were already stated as Self-Hosted only in places; this guide states both deployments and that a SaaS partner installs the Connector agent on their own server. — Idira Technical Alliances |
