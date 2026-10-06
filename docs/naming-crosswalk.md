# Idira Product Names — Crosswalk

**Type:** Reference
**Version:** 1.0
**Author:** Idira Technical Alliances
**Last Updated:** 2026-09-17

---

<!--
## AI CONTEXT BLOCK
This is the NAME RESOLVER for the partner integration dev-kit repository. It is a reference file,
not a stage in the journey.

PURPOSE: Idira products were renamed from their CyberArk names, and several carry a third, older
name from before that. Partner engineering teams are building against documentation written under
the earlier names, and rewriting their own docs to the current names unassisted. This file is the
mapping, stated once, so nobody has to rediscover it.

WHEN TO USE: any time a name in a partner's source material, a public docs page, or an API response
does not match the name used in this repository. Resolve here first before assuming two names are
two products.

DO NOT use this file to answer "which kit do I open?" — that is decision-guide.md. This file only
resolves names.

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md → development-guide.md
→ certification-checklist.md → marketplace-standards.md. This file is consulted from any of them.
-->

---

> **What this is.** Idira products were renamed from their CyberArk names, and several have an older name before that. Public documentation, API responses, and your own existing material will use all three. This table maps them.
>
> **Use the current Idira name** in your integration documentation, your certification submission, and your Marketplace listing content. Use the other columns to recognise what an older document is talking about.

---

## 1. The crosswalk

| Current name (use this) | CyberArk name | Older / legacy names |
|:---|:---|:---|
| Idira Identity Security Platform | Identity Security Platform / Shared Services (ISPSS) | — |
| Idira Endpoint Privilege Manager (EPM) | Endpoint Privilege Manager | — |
| Idira Privileged Access Manager SaaS | Privilege Cloud | PAM SaaS |
| Idira Privileged Access Manager Self-Hosted | Privileged Access Manager Self-Hosted | Core PAS, PAS, the Vault, Digital Vault |
| Idira Secrets Manager, SaaS | Secrets Manager – SaaS | Conjur Cloud |
| Idira Secrets Manager, Self-Hosted | Secrets Manager – Self-Hosted | Conjur Enterprise, DAP |
| Idira Secrets Hub | Secrets Hub | — |
| Idira Credential Provider (CP) | Credential Provider | AIM, Application Identity Manager |
| Idira Central Credential Provider (CCP) | Central Credential Provider | AAM, Application Access Manager |
| Idira Identity | Identity / Identity Administration | Idaptive |
| Idira Conjur | Conjur (open source) | — |

**Endpoint Privilege Manager, one caveat:** EPM now runs on the Idira Identity Security Platform. The standalone EPM console is on a published sunset path — if your integration or its documentation assumes the standalone console, check the current deprecation dates before you build against it.

---

## 2. Three rules that catch people out

**Name the PAM deployment, always.** There are two Privileged Access Manager products and they are not interchangeable — **SaaS** and **Self-Hosted**. Never write "Idira Privileged Access Manager" on its own in documentation, a certification submission, or listing content: a customer reading it cannot tell which product your integration supports. "PAM" as an informal umbrella in prose is fine ("the three PAM flows"); as a product name it is not.

**Watch the comma.** Secrets Manager takes a comma before the deployment — *Idira Secrets Manager, SaaS* and *Idira Secrets Manager, Self-Hosted*. Privileged Access Manager does not — *Idira Privileged Access Manager Self-Hosted*. The two products follow different rules; this is not a typo in one of them.

**CP and CCP are different products with a shared history.** Both sat under the AAM / AIM family, which is why older documents blur them:

| | Idira Credential Provider (CP) | Idira Central Credential Provider (CCP) |
|:---|:---|:---|
| Former name | AIM, Application Identity Manager | AAM, Application Access Manager |
| How it works | Local agent installed alongside your application | Agentless REST web service |
| You are building for it if | Your application can host an agent on the same machine | Your application retrieves secrets over HTTP |

If your source material says "CyberArk AAM" or "CyberArk CCP", it means CCP — the agentless one. See [`secrets-management/decision-guide.md`](secrets-management/decision-guide.md) to confirm which path your integration needs.

---

## 3. Where you will still see CyberArk names — correctly

Some CyberArk-era names are not renamed and are not errors. Do not "correct" these:

| You will see | Where | Why |
|:---|:---|:---|
| `docs.cyberark.com` | Product documentation links throughout this repository | The documentation portal has not moved |
| `x-cybr-telemetry` | The required telemetry header on every API transaction | It is a wire-protocol header name; renaming it would break existing integrations |
| `cyberark.cloud` hostnames | Environment URLs, e.g. `https://c3.cyberark.cloud` | Live service hostnames |
| `conjur` | Secrets Manager API paths, CLI, and open-source project | The API surface and the open-source project keep the name |
| `CyberArk` in an API response or error string | Any API | Response payloads were not renamed with the products |
| `Privilege Cloud REST API` | The Discovery Privileged Accounts kit | The API's own documented name |
| `Privilege Cloud Discovery Source`, `Privilege Cloud Administrator` | Role and persona names you assign to your integration user | These are the role names as they appear in the product — assign them exactly as written or the assignment fails |

The rule: **product names changed; hostnames, header keys, API paths, response payloads, and role names did not.** If you are writing prose, use the current name. If you are assigning a role or calling an endpoint, use exactly what the product and the API reference say.

So you will see both names in this repository, deliberately: *Idira Privileged Access Manager SaaS* when we mean the product, and *Privilege Cloud* when we mean a specific API or role you have to type correctly.

---

## 4. Names on your agreement

The names above are the product names used in documentation, certification, and Marketplace listing content. The names on a signed agreement may differ. If your agreement and this table disagree, ask your Business Development representative rather than reconciling it yourself.

---

## 5. Where to ask

If you hit a name that is not in this table and you cannot tell which product it refers to, email **cybr-bizdevtech@paloaltonetworks.com** with your tracking reference and the document you found it in. A name we have not mapped is a gap in this file, and we would rather fix it once than answer it repeatedly.

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-09-17 | **[Added]** Initial version. Consolidates the current / CyberArk / legacy name mapping into one partner-facing reference, replacing the shorter table previously carried at the end of `decision-guide.md`. Adds the PAM deployment-naming rule, the asymmetric comma rule, the CP-vs-CCP disambiguation, and §3 — the CyberArk-era hostnames, header keys, and API paths that are deliberately unchanged and should not be "corrected" | Idira Technical Alliances |

---

*Maintained by Idira Technical Alliances — cybr-bizdevtech@paloaltonetworks.com*
