# Idira Secrets Manager SaaS — Development Guide

**Workflow:** Secrets Management  
**Integration:** Secrets Manager SaaS (Conjur Cloud)  
**Type:** Development Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.3  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Idira Secrets Manager SaaS — cloud-hosted secrets store built on Conjur Cloud.
WORKFLOW: Secrets Management
USE CASE: Secrets Manager SaaS — a SaaS, cloud-native or containerised workload authenticates its own
  identity and retrieves a secret at runtime, with no on-premises component.
INTEGRATION PATTERN: REST. Authenticate a workload, then GET secrets with the returned token.
AUTH METHOD: Workload authentication — cloud IAM (AWS, Azure, GCP), JWT (including Kubernetes), SWA
  federation (SPIFFE), client certificate (Secrets Manager Edge only), or API Key (last resort). See
  Section 4.
AUTH HEADER FORMAT: Authorization: Token token="<ACCESS_TOKEN>"   — NOT `Bearer`.
BASE URL: https://<tenant>.secretsmgr.cyberark.cloud/api/
TOKEN ENDPOINT: POST https://<tenant>.secretsmgr.cyberark.cloud/api/authn/conjur/<url-encoded host/<workload-id>>/authenticate  (API key)
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded key=value pairs.
  it=SecretsManager — see ../../telemetry-reference.md
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THE FOUR THINGS GENERATED CODE GETS WRONG HERE, ALL IN THE AUTH CALL (Section 4c):
1. THE API KEY GOES IN THE REQUEST BODY, NOT A HEADER. The key is the raw body. There is no
   `Authorization` header on the authenticate call and no JSON wrapper.
2. THE LOGIN IS `host/<workload-id>`, URL-ENCODED. Prefix the Workload ID with `host/`, then encode
   `/` as `%2F` (and `:` as `%3A`): workload `data/myapp` logs in as `host%2Fdata%2Fmyapp`. A missing
   prefix or an unencoded ID fails the call, which reads as a missing workload rather than a
   formatting fault — the single most misdiagnosed failure in this kit.
3. THE RETRIEVAL HEADER IS `Authorization: Token token="<ACCESS_TOKEN>"`. Not `Bearer`. The value
   must be the Base64-encoded token: send `Accept-Encoding: base64` on the authenticate call and the
   response is already encoded; otherwise Base64-encode the raw JSON token and strip newlines
   (`| base64 | tr -d '\r\n'`).
4. `<account>` IS `conjur` ON A SECRETS MANAGER SAAS TENANT — the same value in the authenticate path
   and the secrets path. It is not the tenant name and not the partner name.

TOKENS EXPIRE AFTER 8 MINUTES (Section 4c). Reuse the token until it expires — refresh shortly before
8 minutes, or on a 401 mid-run re-authenticate ONCE and retry. Never loop. Requesting a token per
retrieval fails check 4.11.

THE `/api` SUFFIX IS MANDATORY ON EVERY URL (check 4.6, Section 7). Every Conjur Cloud path in this
kit is `https://<tenant>.secretsmgr.cyberark.cloud/api/...`. Dropping it is a silent 404.

API KEY IS A LAST RESORT AND IS GRADED AS ONE (check 2.4, Section 4). Use it only when no workload
identity authenticator is available. On AWS, Azure or Google Cloud use that platform's IAM
authenticator; in Kubernetes, Jenkins or GitLab use JWT; where workloads carry SPIFFE identities use
SWA. CLIENT CERTIFICATE AUTHENTICATION WORKS ONLY THROUGH SECRETS MANAGER EDGE — a customer-hosted
component — so it is not an option for a workload talking to the SaaS tenant directly. The C3
sandbox ships with API Key configured on all three workloads purely so the flow can be tested — that
is a convenience, not a recommendation.

SWA FEDERATION (SPIFFE) IS A SEPARATE PATH, NOT A RE-LABELLED CERTIFICATE (Section 4a, check 4.5).
Where the customer's workloads carry SPIFFE identities, authentication must use SWA federation rather
than a static credential. Three attestation paths were added during 2026 and each REMOVES a
provisioning step, so check the platform before defaulting to JWT or API Key:
- AWS EC2 — the Instance Identity Document attests the node; NO certificate to pre-provision.
- Google Cloud, and AI agents on the Gemini Enterprise Agent Platform — verifiable SPIFFE identity
  in place of static credentials.
- Kubernetes — `k8s_jwt` with a projected service-account token; no bootstrap secret, and SWA Server
  no longer needs network access to the cluster API server, so hub-and-spoke is supported.

AN AI AGENT IS A WORKLOAD (Section 4b, check 4.4). Authenticate it the same way and NEVER embed a
static key in agent code or config — agents are cloned and redeployed constantly, so an embedded key
leaks with the first snapshot. Retrieve live against a workload identity on each run. Cataloguing
agents as identities is a different kit: ../../discovery/ai-agents/.

BATCH RETRIEVAL, NOT A LOOP (check 4.12, Section 5). `GET /api/secrets?variable_ids=<id1>,<id2>` where
each id is the fully-qualified, URL-encoded resource ID `conjur:variable:<path>`. A per-secret
request loop fails this check. Batch retrieval does not support dynamic secrets. Other graded limits
from Section 7: query size capped at 1000 objects (paginate beyond that, check 4.8), 500
requests/second maximum, user data written to the `data` policy (check 4.7), and one workload
identity per client — never a shared workload ID (check 4.3).

ROTATION IS EXPECTED, NOT AN ERROR (checks 2.3 and 4.11, Section 6). Wait 5 seconds, re-retrieve,
retry once, then surface a clear error. Do not cache a secret beyond the rotation window.

KNOWN GAP — DO NOT FILL IT IN FROM MEMORY: check 4.2 grades dual-account support, and this guide
does not document dual accounts at all. The CP and CCP guides do (`VirtualUsername` in a Vault
account query), but that is Vault query syntax and does not transfer to Conjur variable paths. If a
partner asks how dual accounts work here, say it is not documented in this kit and route to the Idira Technical Alliances contact.

SIBLING KITS — four Secrets Management kits, easily confused:
- ../secrets-manager-self-hosted/: the self-hosted counterpart. it=SecretsManagerSH. Its auth section
  uses the same token encoding and the same `host/` login prefix.
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
> Use this guide if your tool is SaaS-deployed, cloud-native, or containerized — and you want to avoid any on-premises component.

---

## 1. Overview

Idira Secrets Manager SaaS is a cloud-hosted secrets store built on Conjur Cloud. It allows workloads (applications, services, pipelines) to securely retrieve secrets without storing them locally.

Partner integrations use the **C3 Integrations Platform** — an Idira-managed sandbox pre-provisioned with workloads, a safe, and test accounts so you can develop and test your integration before certification.

**Integration pattern:** Your tool authenticates a workload identity, retrieves a secret via REST, and uses it at runtime. Secrets are never stored in your tool's configuration.

---

## 2. Use Cases at a Glance

This integration lets your tool retrieve secrets from Idira Secrets Manager SaaS at runtime instead of storing them locally. The flow is small and linear — most integrations implement all of it.

| # | Capability | What it does | Guide section |
|:--|:---|:---|:--:|
| 1 | Authenticate a workload | Exchange a workload identity for a short-lived token | [4](#4-authentication) |
| 2 | Retrieve a secret | Read a secret via REST at runtime | [5](#5-retrieve-secrets) |
| 3 | Handle secret rotation | Re-fetch transparently when a secret is rotated in the vault | [6](#6-handling-secret-rotation) |

Document the authentication method and retrieval pattern your integration uses in the certification checklist.

---

## 3. Environment Setup

Idira provisions your C3 environment. You will receive an invitation email once your partner account is activated. Contact `cybr-bizdevtech@paloaltonetworks.com` to request access or additional workloads.

The C3 environment includes by default:
- 3 pre-provisioned workloads (Dev, Test, Prod)
- A dedicated safe: `Partner-{Partnername}`
- API Key authentication configured for each workload

### Find Your Workloads

1. Log in to the C3 Integrations Platform.
2. Navigate to **Secrets Manager SaaS** → **Resources** → **Workloads**.
3. Select a workload to retrieve the **Workload ID** and API Key.

### Add Secrets to the Safe

1. In Idira Privileged Access Manager SaaS, click **Add Account** (top right).
2. Select a platform:
   - Key/value secrets: **Application → Generic Application**
   - Workload API Key: **Application → Secrets Manager Host**
3. Select your safe: `Partner-{Partnername}`

---

## 4. Authentication

Use a workload-identity authenticator wherever the platform offers one, so the workload stores no secret:

| Method | When to use |
|:-------|:-----------|
| **Cloud IAM** — AWS IAM, Azure, Google Cloud | The workload runs on that cloud and can present its platform identity. See [AWS IAM](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/operations/authn/authenticate-awsiam-lp.htm), [Azure](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/operations/authn/authenticate-azure-lp.htm), [Google Cloud](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/operations/authn/authenticate-gcp-lp.htm) |
| **JWT** | Kubernetes, Jenkins, GitLab, or any environment that mints JWTs for workloads. See [JWT authenticator](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/conjur_api_jwt_authenticator.htm) |
| **SWA federation (SPIFFE)** | The customer's workloads carry SPIFFE identities — [§4a](#4a-secure-workload-access-spiffe-based-identity) |
| **Client Certificate** | **Only through Secrets Manager Edge**, a customer-hosted component — not for a workload calling the SaaS tenant directly. See [Client certificate authentication](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/api-cert-authn.htm) |
| **API Key** | Last resort, when none of the above is possible. Step-level flow: [§4c](#4c-authenticate-with-an-api-key) |

> **SPIFFE / Secure Workload Access:** if the customer's workloads carry SPIFFE identities, Secrets Manager SaaS can authenticate them via **SWA federation** — see §4a below. That is a separate path from the three methods above, not a re-labelling of the certificate/JWT credential.

### Authentication Flow

1. Retrieve the Workload ID from Secrets Manager UI. Its login is `host/<workload-id>`, URL-encoded.
2. Authenticate the workload using your chosen method.
3. Receive an access token. It expires after 8 minutes.
4. Use the token to retrieve secrets.
5. Re-authenticate only when the token has expired — do not request a new token for every retrieval.

### 4a. Secure Workload Access (SPIFFE-based identity)

**Secure Workload Access (SWA)** is Idira's SPIFFE-based workload identity capability, delivered as part of Secrets Manager SaaS (there is no standalone SWA product or doc space — it lives in the Secrets Manager SaaS documentation). In Idira's own words, it lets you **"authenticate workloads to external platforms with SWA federation and SPIFFE"** — a workload proves its identity with a short-lived, cryptographically attested **SPIFFE SVID** rather than a pre-shared secret.

For a partner integration, the relevance is: if the customer's workloads (including AI agents) already carry SPIFFE SVIDs, SWA is the federation path that lets those identities authenticate — you build against the workload-authentication surface of Secrets Manager SaaS rather than shipping a static credential. If no SPIFFE identity is available, fall back to the standard Workload API auth methods in §4 (JWT, then API Key as last resort).

> **Verify before building:** the step-level SWA-federation flow (how the SVID is exchanged and which SVID types are accepted) is documented in the Secrets Manager SaaS **"Authenticate workloads using SPIFFE"** section — confirm the current mechanism there before a partner codes against it. *(Source terminology verified against docs.cyberark.com Secrets Manager SaaS space, 2026-07-17; deeper auth-flow pages require authenticated access.)*

> **Updated 2026-09-08 / 2026-09-17 — three attestation paths added since this section was written:**
>
> - **AWS EC2 (2026-09-02):** SWA Agent nodes on EC2 instances can attest using the **AWS Instance Identity Document (IID)**. Because EC2 supplies the IID automatically, there is **no X.509 certificate to pre-provision on the instance** before attestation. If the customer's workload runs on EC2, prefer this over any bootstrap-credential scheme — it removes a provisioning step rather than adding one.
> - **Google Cloud and AI agents (2026-08-10):** SPIFFE identity support now extends to workloads on Google Cloud and to AI agents on the Google Gemini Enterprise Agent Platform, which receive a verifiable SPIFFE identity in place of static credentials.
> - **Kubernetes (2026-09-10):** SWA Agent nodes on Kubernetes can attest with the **`k8s_jwt`** method, using a projected service account token that is verified cryptographically. Two consequences for a partner build: the agent needs no pre-provisioned certificate or bootstrap secret, and **SWA Server no longer requires network access to the cluster's API server** — so a hub-and-spoke topology (SWA Server outside the cluster, agents inside) is now supported. If a customer previously ruled SWA out because SWA Server could not reach their cluster API endpoint, that objection no longer applies.
>
> All three narrow the case for the §4 fallback methods: a workload on EC2, Google Cloud, or Kubernetes may have a usable SWA path even if it carries no SPIFFE SVID today. Check the platform before defaulting to JWT or API Key.

### 4b. AI agents and autonomous workloads

An AI agent is a workload: authenticate it the same way, and **never embed a static key in agent code or config** — agents are cloned and redeployed constantly, so an embedded key leaks with the first snapshot. Retrieve secrets live against a workload identity (SVID or JWT preferred) on each run. Cataloguing agents as identities is a separate concern — see the [AI Agents Discovery dev kit](../../discovery/ai-agents/development-guide.md); this guide covers how an agent *retrieves* secrets, not how it is inventoried.

### 4c. Authenticate with an API key

Use this method only when client certificate, JWT, and SWA federation are all unavailable. The certification checklist gates on it: *"API key authentication used only when certificate or JWT authentication is not possible."* If your tool runs in Kubernetes, Jenkins, or GitLab, JWT is available and is the correct choice.

Your C3 environment has API key authentication configured on all three pre-provisioned workloads, so you can test this flow without additional setup.

#### Before you begin

- Retrieve the **Workload ID** and API key from **Secrets Manager SaaS → Resources → Workloads**
- Confirm your tenant subdomain
- The `<account>` segment is **`conjur`** on a Secrets Manager SaaS tenant. It is the same value in both the authenticate path and the secrets path

#### Exchange the API key for an access token

1. Build the login: prefix the Workload ID with `host/`, then URL-encode it (`/` → `%2F`, `:` → `%3A`). Workload `data/myspace/application` becomes `host%2Fdata%2Fmyspace%2Fapplication`.
2. Send the API key as the request body, and ask for a Base64-encoded token:

    ```bash
    curl -s -X POST \
      -H "Accept-Encoding: base64" \
      --data "$IDIRA_API_KEY" \
      "https://<tenant>.secretsmgr.cyberark.cloud/api/authn/conjur/host%2Fdata%2Fmyspace%2Fapplication/authenticate"
    ```

3. The response body is the access token, already Base64-encoded. Store it for its lifetime (8 minutes), and do not log it. Reference: [API key authentication](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/conjur_api_api-key-authn.htm).
4. Retrieve secrets with the token, as described in [§5](#5-retrieve-secrets).
5. Re-authenticate only after the token expires. A 401 mid-run indicates expiry: re-authenticate once and retry the operation. Do not loop.

#### Verification

- The authenticate call returns 200 with a token in the body.
- A follow-up secret retrieval with that token returns 200 and the expected value.
- A second retrieval within the token lifetime succeeds **without** a further authenticate call. If your integration authenticates twice, it fails the checklist item "Access tokens requested only on expiry."

#### Troubleshooting

| Symptom | Cause | Resolution |
|:---|:---|:---|
| 401 or 404 on the authenticate call | Login is missing the `host/` prefix, or is not URL-encoded | Use `host/<workload-id>` and encode `/` as `%2F` and `:` as `%3A` |
| 401 on the authenticate call | Wrong API key, or the key was rotated | Retrieve the current key from the Workloads page |
| 401 on retrieval, immediately after a successful authenticate | Token not Base64-encoded | Send `Accept-Encoding: base64` on authenticate, or Base64-encode the raw token and strip newlines |
| 401 on retrieval, later in a long run | Token expired | Re-authenticate once, then retry |

> **Confirmed:** the `/api/` path prefix and the `<account>` value `conjur` (checked against a live `*.secretsmgr.cyberark.cloud` tenant), the `host/` login prefix, and the 8-minute token lifetime.

---

## 5. Retrieve Secrets

### Single Secret

```bash
curl -H "Authorization: Token token=\"<ACCESS_TOKEN>\"" \
  https://<tenant>.secretsmgr.cyberark.cloud/api/secrets/<account>/variable/<variable-path>
```

### Batch Retrieval

Use batch retrieval whenever your integration needs multiple static secrets. Each ID is the fully-qualified resource ID `conjur:variable:<path>`, URL-encoded. Batch retrieval is not supported for dynamic secrets. Reference: [Batch secret retrieval](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/conjur_api_batch_retrieve.htm).

```bash
curl -H "Authorization: Token token=\"<ACCESS_TOKEN>\"" \
  -H "Content-Type: application/json" \
  -X GET \
  "https://<tenant>.secretsmgr.cyberark.cloud/api/secrets?variable_ids=conjur:variable:data%2Fmyapp%2Fdb-password,conjur:variable:data%2Fmyapp%2Fapi-key"
```

---

## 6. Handling Secret Rotation

Customers rotate secrets on a schedule. Your integration must be tolerant of temporarily incorrect values:

1. Attempt the operation with the retrieved secret.
2. If the operation fails with an authentication error, wait 5 seconds and retrieve the secret again.
3. Retry the operation once. If it fails again, surface a clear error to the user.

Do not cache secrets beyond the rotation window. Fetch live on each use or cache only for a very short period when retrieving the same secret repeatedly in quick succession.

---

## 7. Best Practices

- Define a separate workload identity for each integration client — do not share workload IDs across applications
- Use batch retrieval when your integration needs more than one secret
- The Conjur Cloud API URL must include the `/api` suffix: `https://<tenant>.secretsmgr.cyberark.cloud/api/...`
- Query size is limited to 1000 objects — use pagination for larger queries
- Limit requests to 500 per second maximum
- User data must be written to the `data` policy (exists under the root policy by default in Conjur Cloud)
- Human users are managed in Idira Identity, not via Conjur policy

---

## 8. Certification

See [Certification Checklist](certification-checklist.md) for the full requirements. Key items:

- [ ] Appropriate solution chosen for use case (verify with [Decision Guide](../decision-guide.md))
- [ ] Workload identity defined for each client
- [ ] Certificate or JWT authentication used (API Key only as last resort); SWA federation (SPIFFE) used where the customer's workloads carry SPIFFE identities
- [ ] No static secret embedded in application or AI-agent code/config — retrieved live at runtime
- [ ] Token expiry handled — no per-retrieval token requests
- [ ] Batch retrieval implemented where applicable
- [ ] `/api` URL suffix used on all Conjur Cloud requests
- [ ] Dual accounts supported
- [ ] Secrets not logged or printed
- [ ] `x-cybr-telemetry` header included on all requests
- [ ] Demonstration provided — **either** a demo video (2–5 min) showing end-to-end secret retrieval, **or** a live demonstration call with the Idira Technical Alliances contact walking the same flow

---

## 9. Telemetry Header

All certified integrations must include the `x-cybr-telemetry` HTTP header, Base64 URL-encoded:

| Field | Header Key | Required | Example |
|:------|:-----------|:---------|:--------|
| IntegrationName | `in` | Yes | `in=HashiCorp Vault Sync` |
| IntegrationType | `it` | Yes | `it=SecretsManager` |
| IntegrationVersion | `iv` | Yes | `iv=1.0` |
| VendorName | `vn` | Yes | `vn=HashiCorp` |
| VendorVersion | `vv` | No | `vv=1.15` |

---

## 10. Resources

- [Secrets Manager, SaaS REST API Reference | Idira Docs](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/developer/lp_rest_api.htm)
- [C3 Integrations Platform](https://c3.cyberark.cloud)
- Contact: `cybr-bizdevtech@paloaltonetworks.com`

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.3 | 2026-10-08 | **[Fixed]** The authenticate login is `host/<workload-id>`, URL-encoded — the `host/` prefix was missing from every example. Client certificate authentication works only through Secrets Manager Edge, so it is no longer presented as the strongest option for SaaS workloads. **[Added]** The AWS IAM, Azure and Google Cloud authenticators and the JWT authenticator reference; `Accept-Encoding: base64` for a pre-encoded token; the 8-minute token lifetime; fully-qualified IDs in batch retrieval, and that batch retrieval does not support dynamic secrets. **[Removed]** The unsourced 50-per-batch figure. An integration that authenticates without the `host/` prefix must add it | Idira Technical Alliances |
| 1.2 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances |
| 1.1 | 2026-09-30 | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. It leads with the four things generated code gets wrong in the authenticate call — the API key goes in the request **body** under `Content-Type: text/plain` rather than a header, the Workload ID must be URL-encoded (an unencoded ID 404s and reads as a missing workload), the retrieval header is `Authorization: Token token="…"` and not `Bearer` with the token possibly needing Base64-encoding first, and `<account>` is the literal `conjur` rather than the tenant or partner name. It also records that **token lifetime is not published**, so an agent must not generate a fixed-duration refresh timer and must handle a 401 by re-authenticating once; that SWA federation (SPIFFE) is a separate fourth auth path with three 2026 attestation additions that each remove a provisioning step; that an AI agent is a workload and must never carry an embedded static key; and the graded limits from Section 7 (batch of 50, 1000-object query cap, 500 req/s, `data` policy, one workload identity per client). One gap is recorded rather than filled: check 4.2 grades dual-account support and this guide does not document it, and CP/CCP's `VirtualUsername` Vault query syntax does not transfer to Conjur variable paths. Also added the `**Version:**` and `**Last Updated:**` header fields and this change log — the file previously carried neither, so no revision before this one is recorded. No guidance was changed. — Idira Technical Alliances |
