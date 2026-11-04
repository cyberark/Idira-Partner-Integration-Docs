# Credential Rotation — Is This the Right Workflow?

**Workflow:** Credential Rotation
**Type:** Decision Guide
**Author:** Idira Technical Alliances
**Version:** 1.0
**Last Updated:** 2026-11-04

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about Credential Rotation integrations.

DOCUMENT TYPE: Workflow decision guide — a ROUTER, not a build guide. No procedures, no configuration
  values. Do not answer a build question from this file.
WORKFLOW: Credential Rotation
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

Use this workflow if you want the CPM to verify, change and reconcile credentials on **your product** through its REST API, by shipping a plugin configuration (XML) built on the REST API Application CPM Plugin Framework. The deliverable is configuration, not partner code.

## 2. Which Deployment?

| Your customers run | You build and test on | Connector server |
|:---|:---|:---|
| Idira Privileged Access Manager Self-Hosted | A Self-Hosted environment, provisioned once your request is approved | Not applicable |
| Idira Privileged Access Manager SaaS | Your own Windows server running the Connector agent, connected to a SaaS tenant | **Required** — [install steps and prerequisites](cpm-rest-api/development-guide.md) |

**SaaS note.** Install the CPM component on your Connector server through Connector Management, as [the install page](https://docs.cyberark.com/setup/latest/en/content/ispss-deployment/privilege%20cloud/privcloud-connectorinstall-cm.htm) describes.

## 3. When NOT to Use This Workflow

- If you need to launch a session into a web application, use [PSM Connectors](../psm-connectors/decision-guide.md).
- If you need to retrieve secrets at runtime, use [Secrets Management](../secrets-management/decision-guide.md).
- If you are building on the retired WSChains framework, do not: new plugins must use the REST API framework.

## 4. Guide

| Dev Kit | Development Guide | Certification Checklist |
|:---|:---|:---|
| [CPM REST API Plugin](cpm-rest-api/) | [Development Guide](cpm-rest-api/development-guide.md) | [Checklist](cpm-rest-api/certification-checklist.md) |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.0 | 2026-11-04 | **[Added]** First publication. The kit and its development guide were already stated as Self-Hosted only in places; this guide states both deployments and that a SaaS partner installs the Connector agent on their own server. — Idira Technical Alliances |
