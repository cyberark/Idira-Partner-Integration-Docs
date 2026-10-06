# Idira Secrets Manager Self-Hosted — Development Guide

**Workflow:** Secrets Management  
**Integration:** Secrets Manager Self-Hosted  
**Type:** Development Guide  
**Author:** Idira Technical Alliances  
**Reference:** [Idira Docs — Secrets Manager Self-Hosted Developer](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/hometileslps/lp-tile5.htm)  
**Version:** 1.3  
**Last Updated:** 2026-10-02

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Secrets Manager Self-Hosted (Conjur Enterprise) — customer-operated secrets platform.
WORKFLOW: Secrets Management
USE CASE: Secrets Manager Self-Hosted — a workload authenticates to the customer's own Conjur cluster
  and retrieves secrets over the Conjur REST API. Policy and secret writes are also in scope.
INTEGRATION PATTERN: REST against a customer-hosted cluster. No fixed hostname and no SaaS endpoint.
AUTH METHOD: Workload authenticators — Cloud IAM (AWS/Azure/GCP), JWT, Kubernetes, or API key as a
  last resort (Section 5, graded by check 2.4)
AUTH HEADER FORMAT: Authorization: Token token="<BASE64_ENCODED_JSON_TOKEN>"   — NOT `Bearer`.
BASE URL: https://<conjur-follower>/   for reads and authentication
          https://<conjur-leader>/     for policy loads and secret writes
TOKEN ENDPOINT: POST https://<conjur-follower>/authn/<account>/<workload-id>/authenticate
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs.
  it=SecretsManagerSH — see ../../telemetry-reference.md
CONTACT: your Idira Technical Alliances contact (Skytap access); cybr-bizdevtech@paloaltonetworks.com

THERE IS NO `/api` SEGMENT IN THIS KIT'S URLs. Paths are `/authn/…`, `/secrets/…`, `/policies/…`
directly off the cluster host. The `/api` suffix is a SECRETS MANAGER SAAS requirement, not a Conjur
one — check 3.4 grades it only for an integration built for BOTH products, and then only on the SaaS
side. Do not add it here and do not report its absence as a defect.

BASE64-ENCODE THE TOKEN, DO NOT DECODE IT (Section 5). The authenticate response is a JSON access
token; the `Authorization` header expects that JSON Base64-encoded with the line wrapping stripped:
`| base64 | tr -d '\n'`. A token that was decoded, or that still contains newlines, returns 401 on
retrieval. This guide is the one place in the corpus that documents the requirement outright — the
../secrets-manager-saas/ guide links here for it.

READS GO TO A FOLLOWER, WRITES GO TO THE LEADER (check 3.3, Section 4). Followers are read-only
replicas behind a load balancer; the Leader is the only read/write node. Targeting the wrong one is
the most common 403 in this kit, and Section 7 names the trap explicitly: a write needs BOTH the
Leader AND the `update` privilege, and missing either returns a 403 that looks identical.

THE PRIVILEGE SET IS GRADED AGAINST WHAT THE INTEGRATION ACTUALLY DOES (Section 7). The policy
example grants `privilege: [ read, execute ]`, which authenticates and retrieves but cannot set a
value. A writing integration needs `[ read, execute, update ]`. A read-only integration must NOT
request `update` — certification checks the granted privileges match the real behaviour, so widening
the example "just in case" fails the check rather than passing it.

`<account>` IS A DEPLOYMENT-TIME VALUE HERE AND THIS GUIDE DOES NOT STATE IT. On a Secrets Manager
SaaS tenant it is the literal `conjur`; on a self-hosted cluster the customer sets it when the cluster
is initialised. Do not carry `conjur` across from ../secrets-manager-saas/ and do not hardcode any
value — take it from configuration.

TOKEN LIFETIME IS NOT PUBLISHED. Request a new token only when the existing one has expired, never
per retrieval (check 3.9, Section 9). Do not generate a fixed-duration refresh timer.

BATCH RETRIEVAL IS BY FULLY-QUALIFIED ID HERE, NOT A BARE PATH (Section 6, check 3.10). Up to 50 per
request, and each id is `<account>:variable:<path>`:
`/secrets?variable_ids=<account>:variable:<path1>,<account>:variable:<path2>`. The SaaS kit's
`?variable_ids=<id1>,<id2>` shape is not the same string. Do not copy one into the other.

ENVIRONMENT — SKYTAP, NOT C3 (Section 4). Partners integrating with this product get a Skytap
environment from their Idira Technical Alliances contact, gated on a signed Partner Agreement. The C3 shared ISP
environment is for ../credential-provider/ and ../central-credential-provider/ only. The guide states
this inversion itself because partners building more than one kit reliably assume one environment.

TERMINOLOGY: `Secrets Manager Self-Hosted` or `Conjur Enterprise`. NEVER `DAP` (check 4.1) — that is
the retired name.

TWO KNOWN GAPS — DO NOT FILL THEM IN FROM MEMORY:
- Checks 2.3 and 3.5 grade rotation tolerance and rotation handling, and this guide does not document
  a rotation procedure. Section 9 says only to fetch live rather than cache. The corpus-wide pattern
  (wait 5 seconds, re-retrieve, retry once, then surface a clear error) is documented in
  ../secrets-manager-saas/development-guide.md Section 6 and in both Credential Provider guides — cite
  it from there rather than presenting it as this guide's own guidance.
- This guide's own Section 11 key-items list includes "Dual accounts supported (where applicable)",
  but the certification checklist has NO dual-accounts check for this kit. The checklist governs.

SIBLING KITS — four Secrets Management kits, easily confused:
- ../secrets-manager-saas/: the Idira-managed cloud counterpart. it=SecretsManager. Requires `/api`.
- ../central-credential-provider/: agentless REST against the Idira Vault, customer-hosted IIS. it=CCP
- ../credential-provider/: agent-based SDK against the Idira Vault, no REST at all. it=CP
- Start at ../decision-guide.md if the choice is not already settled; check 2.1 grades that it was.
NOTE ON DIRECTION: these four kits RETRIEVE secrets from Idira. ../../discovery/secrets/ does the
opposite — it reports secrets that exist elsewhere into an inventory, and never transmits a secret
value at all. Do not conflate them.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — which Secrets Management dev kit to build against
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **Not sure this is the right guide?** See the [Decision Guide](../decision-guide.md) first.  
> Use this guide if the customer runs Secrets Manager Self-Hosted and your tool needs to integrate directly with the Conjur REST API — cloud-native apps, containers, CI/CD pipelines, or microservice architectures.

---

## 1. Overview

Idira Secrets Manager Self-Hosted is a self-hosted secrets management platform that exposes a full REST API and supports a broad set of workload authenticators (Kubernetes, AWS IAM, Azure AD, JWT, and others).

Partners building integrations against Secrets Manager Self-Hosted interact directly with the Conjur REST API to authenticate workloads, retrieve secrets, and manage policy.

**Integration pattern:**  
Workload authenticates to Conjur → receives short-lived access token → retrieves secret(s) via REST → uses secret at runtime → token expires; re-authenticate on next use.

---

## 2. Use Cases at a Glance

Your integration authenticates a workload to Conjur, then performs one or more of the operations below. Most integrations only need to read secrets — build the operations your use case requires.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Authenticate a workload | Exchange a workload identity for a short-lived access token | [5](#5-authentication) |
| 2 | Retrieve a secret | Read a single secret or a batch (up to 50) at runtime | [6](#6-retrieve-secrets) |
| 3 | Manage policy | Define a workload identity and its access grants | [7](#7-policy-management) |
| 4 | Write a secret | Create or update a secret value (Leader node only) | [8](#8-write-a-secret-if-applicable) |

Read-only integrations implement authenticate + retrieve. Policy and write operations are for integrations that provision workloads or push secrets into the vault. Document which operations your integration implements in the certification checklist.

---

## 3. When to Use This Guide

Use this guide if:
- The customer's Idira deployment is fully on-premises or private cloud
- Your tool runs in an elastic environment (containers, Kubernetes, cloud VMs) that needs secrets from a customer-controlled Conjur cluster
- Your tool is part of a CI/CD pipeline that integrates directly with Secrets Manager Self-Hosted
- The use case requires write operations (creating or updating secrets) — only the Leader node supports writes

For SaaS-based workloads against the Idira-managed cloud, use [Secrets Manager SaaS](../secrets-manager-saas/development-guide.md) instead.

---

## 4. Environment

Idira provisions a **Skytap environment** for partners integrating with Secrets Manager Self-Hosted. Access details and a Skytap Instructions document are provided by your Business Development representative.

> **Building CP or CCP instead?** Those do **not** use Skytap. Credential Provider and Central Credential Provider are provisioned on the Idira shared ISP environment (`https://c3.cyberark.cloud`) — see the Prerequisites section of the [CP](../credential-provider/development-guide.md) or [CCP](../central-credential-provider/development-guide.md) guide.

A Partner Agreement must be signed before environment access is granted.

Secrets Manager Self-Hosted cluster components in a typical deployment:

| Component | Role |
|:----------|:-----|
| **Leader** | Read/write node — use for policy updates and secret writes |
| **Standby** | Inactive replica — promoted to Leader if the original Leader fails |
| **Follower** | Read-only replicas behind a load balancer — use for all secret reads and authentication |

All production secret retrieval should target Followers, not the Leader directly.

---

## 5. Authentication

Secrets Manager Self-Hosted supports several workload authenticators. Use the strongest method available in your deployment context:

| Authenticator | When to use |
|:--------------|:-----------|
| **Cloud IAM (AWS, Azure, GCP)** | Workloads running on cloud infrastructure — authenticate using the workload's cloud IAM identity |
| **JWT** | Workloads in Kubernetes, Jenkins, GitLab, or any environment that issues JWTs to workloads |
| **Kubernetes** | Native Kubernetes service account authentication |
| **API key** | Use only when no other authenticator is available |

API key authentication should be a last resort — it does not leverage native workload identity and requires managing a static credential.

### Authenticate and Get a Token

```bash
# API key authentication (last resort)
curl -X POST \
  https://<conjur-follower>/authn/<account>/<workload-id>/authenticate \
  -H "Content-Type: text/plain" \
  -d "<api-key>"
```

The response is a **JSON access token**. Base64-encode it — do not decode it — and send the encoded value in the `Authorization` header as `Token token="<encoded>"`:

```bash
TOKEN=$(curl -s -X POST \
  https://<conjur-follower>/authn/<account>/<workload-id>/authenticate \
  -H "Content-Type: text/plain" \
  -d "<api-key>" | base64 | tr -d '\n')
```

The `| base64 | tr -d '\n'` pipeline is intentional: it encodes the JSON token and strips the line wrapping `base64` adds. A token that is decoded, or that still contains newlines, returns 401 on retrieval.

Access tokens expire — request a new token only when the existing one has expired, not per-retrieval.

---

## 6. Retrieve Secrets

### Single Secret

```bash
curl -H "Authorization: Token token=\"$TOKEN\"" \
  https://<conjur-follower>/secrets/<account>/variable/<policy-path>/<variable-name>
```

### Batch Retrieval (up to 50 secrets per request)

Batch retrieval is required for any integration that retrieves more than one secret. It reduces round trips and is checked during certification.

```bash
curl -H "Authorization: Token token=\"$TOKEN\"" \
  "https://<conjur-follower>/secrets?variable_ids=<account>:variable:<path1>,<account>:variable:<path2>"
```

---

## 7. Policy Management

Conjur uses a YAML-based policy language to define identities, permissions, and secrets. Policy is loaded to the **Leader** node.

### Define a Workload Identity

```yaml
- !policy
  id: integrations/<partner-name>
  body:
    - !host
      id: <workload-id>
      annotations:
        description: Partner integration workload

    - !variable
      id: <secret-name>

    - !permit
      role: !host <workload-id>
      privilege: [ read, execute ]
      resource: !variable <secret-name>
```

Load policy:

```bash
curl -X POST \
  https://<conjur-leader>/policies/<account>/policy/<policy-path> \
  -H "Authorization: Token token=\"$ADMIN_TOKEN\"" \
  -H "Content-Type: application/x-yaml" \
  --data-binary @policy.yml
```

**Important:** If your integration requires write operations, two things must both be true, and missing either returns a 403 that looks identical:

1. **Target the Leader.** Followers are read-only. Do not attempt to load policy or write secrets to a Follower.
2. **Grant the `update` privilege.** The `!permit` example above grants `[ read, execute ]`, which is retrieval-only — enough to *read* a secret and authenticate, but not to set its value. An integration that writes secrets needs `privilege: [ read, execute, update ]` on each variable it writes.

If you only retrieve secrets — the common case for a partner integration — leave the example as `[ read, execute ]`. Do not request `update` you do not use; certification checks that the granted privileges match what the integration actually does.

---

## 8. Write a Secret (if applicable)

Most integrations only read secrets. If your integration writes secrets (e.g. a rotation plugin or a secrets injection tool):

```bash
curl -X POST \
  https://<conjur-leader>/secrets/<account>/variable/<policy-path>/<variable-name> \
  -H "Authorization: Token token=\"$TOKEN\"" \
  -H "Content-Type: text/plain" \
  -d "<new-secret-value>"
```

Only write to the Leader. Followers will reject write requests.

---

## 9. Best Practices

- Define one workload identity per integration client — do not share workload IDs
- Always target Followers for reads; use the Leader only for writes and policy updates
- Refresh the access token only on expiry — do not request a new token for every secret retrieval
- Use batch retrieval when fetching multiple secrets in one call (max 50 per batch)
- Cache secrets only for very short periods when the same secret is retrieved repeatedly in a tight loop; otherwise fetch live to avoid stale values
- Never log or print secrets, tokens, or API keys
- Provide clear user-facing error messages — customers need to diagnose configuration issues without Idira support

---

## 10. Engine-Specific Notes

- Conjur stores secrets as **variables** within a policy tree
- Groups and Layers are the permission containers — assign workload identities to layers, then grant layer permissions on variable sets
- The Vault Synchronizer can push secrets from Idira Privileged Access Manager SaaS / Self-Hosted into Conjur variables — useful if the customer already manages secrets in the Vault and wants to expose them via Conjur

---

## 11. Certification

See [Certification Checklist](certification-checklist.md) for full requirements. Key items:

- [ ] Appropriate solution confirmed via [Decision Guide](../decision-guide.md)
- [ ] Workload identity defined per client — no shared IDs
- [ ] JWT or cloud IAM authentication used (API key only as last resort)
- [ ] All reads target Followers; writes target Leader
- [ ] Token expiry handled — no per-retrieval token requests
- [ ] Batch retrieval implemented where multiple secrets are needed
- [ ] Secrets not logged or printed
- [ ] Dual accounts supported (where applicable)
- [ ] `x-cybr-telemetry` header included on all API requests
- [ ] Demonstration provided — **either** a demo video (2–5 min) showing end-to-end secret retrieval, **or** a live demonstration call with the Idira Technical Alliances contact walking the same flow

---

## 12. Telemetry Header

Include the `x-cybr-telemetry` HTTP header on all Conjur REST requests, Base64 URL-encoded:

| Field | Header Key | Required | Example |
|:------|:-----------|:---------|:--------|
| IntegrationName | `in` | Yes | `in=Acme Pipeline Secrets` |
| IntegrationType | `it` | Yes | `it=SecretsManagerSH` |
| IntegrationVersion | `iv` | Yes | `iv=1.0` |
| VendorName | `vn` | Yes | `vn=Acme` |
| VendorVersion | `vv` | No | `vv=2.0` |

---

## 13. Resources

- [Secrets Manager Self-Hosted Developer Docs | Idira Docs](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/hometileslps/lp-tile5.htm)
- [Secrets Manager, Self-Hosted REST API Reference | Idira Docs](https://docs.cyberark.com/secrets-manager-sh/latest/en/content/developer/lp_rest_api.htm)
- Contact your Idira Technical Alliances contact for Skytap environment access

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.2 | 2026-10-01 | **[Fixed]** All four "Use Cases at a Glance" section links were off by one, landing a partner on the section above the one named. The table was added in `2e49fc87` (2026-07-20), the same commit that inserted a new Section 2 and renumbered every heading +1 — the new table was written against the pre-renumber numbering and never caught up. Authentication is Section 5 (not 4), Retrieve Secrets 6 (not 5), Policy Management 7 (not 6), Write a Secret 8 (not 7); both the link labels and the anchors are corrected. The seven sibling guides renumbered by the same commit were checked and are correct. No guidance changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the cross-kit traps against the SaaS sibling, in both directions: there is **no `/api` segment** in this kit's URLs (that is a Secrets Manager SaaS requirement, graded here only by the dual-build check 3.4), `<account>` is a deployment-time customer value rather than the literal `conjur`, and batch retrieval takes fully-qualified `<account>:variable:<path>` ids rather than the SaaS kit's bare ids. It also records that reads target a Follower while policy loads and writes target the Leader, and Section 7's identical-403 trap — a write needs both the Leader **and** the `update` privilege, while a read-only integration must not request `update` because certification grades the privilege set against actual behaviour. Environment is Skytap, not the C3 platform the CP/CCP kits use. Two gaps are recorded rather than filled: checks 2.3 and 3.5 grade rotation handling that this guide never documents (the pattern is cited from the sibling guides instead of presented as this guide's own), and this guide's Section 11 key-items list claims a dual-accounts requirement the certification checklist does not carry. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
