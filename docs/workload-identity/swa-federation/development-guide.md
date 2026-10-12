# Idira Secure Workload Access Partner Development Guide

**Workflow:** Workload Identity  
**Dev Kit:** SWA Federation  
**Type:** Self-Service Guide  
**Status:** Preview — not a certifiable path yet  
**Author:** Idira Technical Alliances  
**Version:** 1.1  
**Last Updated:** 2026-10-08

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about this integration.

PRODUCT: Secure Workload Access (SWA) — Idira's SPIFFE-based workload identity capability.
WORKFLOW: Workload Identity
USE CASE: SWA Federation — a partner platform that runs, routes, or hosts workloads establishes
  SPIFFE identity for those workloads so they authenticate to Idira with a short-lived attested
  SVID instead of a pre-shared secret.
TELEMETRY: Required on every request — x-cybr-telemetry header, Base64url-encoded. it=WorkloadIdentity
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS KIT IS PREVIEW. The federation exchange (Section 6) and the SWA management APIs (Section 6.3)
are documented in the public Secrets Manager SaaS documentation and summarised here. Build from
those pages — not from the SPIFFE specification or a SPIRE tutorial, which do not match Idira's setup
step for step. One point remains unconfirmed and must be checked with an Idira Technical Alliances
contact before you rely on it: whether X.509-SVIDs (rather than JWT-SVIDs) are accepted for
authenticating to Secrets Manager.

SWA IS NOT A STANDALONE PRODUCT AND NOT A SEPARATE DOC SPACE. It is delivered as part of Secrets
Manager SaaS and documented inside that space. Write "Secure Workload Access" in full, "SWA" on
second reference, and never present it as its own SKU or license line. The workflow directory name
`workload-identity/` is a USE CASE label, in the same way `discovery/` and `identity-response/` are
— it is not a product name.

DIRECTION — WHAT SEPARATES THIS KIT FROM SECRETS MANAGEMENT. This kit is about ESTABLISHING
IDENTITY: the partner platform gives a workload a verifiable identity, and Idira consumes it. The
../../secrets-management/ kits are about RETRIEVING A SECRET VALUE from Idira once a client is
already authenticated. "Our platform needs a secret" is Secrets Management. "Our platform gives
workloads an identity Idira should trust" is this kit. An integration can legitimately do both, and
then it builds against both kits and is certified twice.

THE CLOSEST THING TO AN OVERLAP, AND WHY IT IS NOT ONE:
  ../../secrets-management/secrets-manager-saas/ Section 4a describes SWA federation as the fourth
  AUTH OPTION for a retrieval client. That is SWA used as a means to an end. This kit covers the
  federation itself as the integration's deliverable. If the partner's product is a secrets client
  that happens to hold an SVID, use that kit. If the partner's product is what issues, carries, or
  brokers the workload identity, use this one.

NOT THIS KIT, EASILY CONFUSED:
- ../../discovery/ai-agents/ — INVENTORIES agents that already exist. Cataloguing an identity and
  issuing one are different operations; that kit pushes records, this one establishes trust.
- ../../discovery/machine-identities/ — same point for non-agent compute.
- ../../psm-connectors/web-connection-component/ — "SWA" in some CyberArk-era material means
  Secure Web Application Connectors Framework, a PSM browser-automation component. UNRELATED to
  Secure Workload Access. If a partner says "SWA" and means a web connector, route there instead.

ATTESTATION IS THE REAL DECISION IN THIS KIT (Section 5), AND IT IS PLATFORM-DRIVEN. The SWA Agent
attests its node with one of:
  aws_iid      AWS EC2 Instance Identity Document — no certificate pre-provisioned
  k8s_jwt      Kubernetes projected service-account token, verified cryptographically — SWA Server
               needs no route to the cluster API server, so hub-and-spoke is supported
  k8s_psat     Kubernetes projected service-account token validated against the cluster API server
               (SWA Server in the same cluster)
  x509pop      X.509 proof-of-possession: a machine certificate signed by a CA configured on the
               server group; the certificate's Subject CN names the node group (Unix/Linux)
Gemini Enterprise agents on Google Cloud get SPIFFE identities through Google Cloud service-account
attestation. Check the platform BEFORE concluding a workload has no SWA path.

FEDERATION — WHAT AN SWA IDENTITY IS EXCHANGED FOR (Section 6). A workload fetches a JWT-SVID from SWA
and exchanges it: with Secrets Manager through the JWT authenticator, or for temporary AWS, Azure,
Google Cloud, Claude or OpenAI credentials. SPIFFE changes how workloads reach downstream services;
it does not replace how a workload authenticates to Secrets Manager at bootstrap.

THE SECRETS MANAGER EXCHANGE, EXACTLY (Section 6.1): JWT authenticator with `jwks-uri`, `issuer`,
`audience`, `token-app-property` = `sub` and `identity-path`; the trust domain must sign JWT-SVIDs
with RSA — not elliptic-curve — for this path; SWA creates each workload host under
`data/swa/trust-domains/<trust-domain>/workloads/` with NO secret access by default, so the admin
must create the workloads group, annotate the host with its SPIFFE ID, add it to the group and grant
secret permissions.

FALLBACK ORDER WHEN NO ATTESTATION PATH EXISTS: a cloud IAM authenticator or JWT, then API key as a
last resort — documented in ../../secrets-management/secrets-manager-saas/ Section 4. Client
certificate authentication works only through Secrets Manager Edge. An embedded static key in
workload or agent code is an anti-pattern this corpus grades against, not a shortcut.

FILES IN THIS DIRECTORY:
- development-guide.md — this file — how to build the integration
- certification-checklist.md — what the integration is graded on; read it during the build
- ../decision-guide.md — whether this is the right workflow at all
- ../../telemetry-reference.md — the telemetry transform, this kit's it value, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> **This kit is Preview.** The guidance below is usable and the certification checklist is published,
> but this is **not a certifiable path yet** and Section 6 is deliberately incomplete — see the notice
> there. Talk to your Idira Technical Alliances contact before committing engineering time, so you
> know which parts are settled.

---

## 1. Why Workload Identity Federation Matters

A workload that authenticates with a pre-shared secret carries that secret everywhere it goes. The
secret is copied into images, baked into manifests, inherited by clones, and captured in snapshots.
For long-lived infrastructure that was a manageable risk. For workloads that are created and
destroyed continuously — containers, serverless functions, and especially AI agents — it is not: the
population of credential holders changes faster than any rotation schedule can track, and an
embedded key leaks with the first snapshot.

**Secure Workload Access (SWA)** is Idira's SPIFFE-based answer. A workload proves what it is with a
short-lived, cryptographically attested **SPIFFE SVID** rather than something it was told in advance.
Idira describes the capability as authenticating *"workloads to external platforms with SWA
federation and SPIFFE."* The identity is derived from the platform the workload actually runs on, so
it cannot be copied out of that context and reused.

For a technology partner, the opportunity is specific: if your platform runs, routes, or hosts other
people's workloads, you are already in the position to attest what those workloads are. Federating
that attestation with Idira means your customers' workloads reach Idira-managed resources without
either side distributing static credentials.

**Why customers are asking now:**

- Agentic deployments multiply short-lived identities, and static-credential models do not survive
  the volume.
- SPIFFE has become the common vocabulary for workload identity across service meshes, AI gateways,
  and agent runtimes — so federation is increasingly a configuration exercise rather than a custom
  build.
- Platform teams are being asked to show that non-human identities are attested rather than
  pre-trusted, which a bearer secret cannot demonstrate.

---

## 2. Use Cases at a Glance

This kit covers integrations where **workload identity itself is the integration**. Build the row
that matches your platform.

| # | Your platform is… | What the integration establishes | Guide section |
|:--|:---|:---|:--:|
| 1 | A runtime that hosts workloads or agents (compute platform, container platform, agent runtime) | Workloads you host attest to SWA and receive an SVID, so they authenticate to Idira without a distributed secret | [5](#5-choosing-an-attestation-method) |
| 2 | A gateway or proxy that brokers traffic on a workload's behalf | Requests carry an attested workload identity end to end rather than a shared gateway credential | [5](#5-choosing-an-attestation-method), [6](#6-the-federation-exchange) |
| 3 | A platform that already issues SPIFFE identities | Your existing SVIDs federate with SWA instead of your customers maintaining two identity systems | [6](#6-the-federation-exchange) |

If what you are actually building is a client that *fetches a secret* from Idira, this is the wrong
kit even if that client holds an SVID — go to
[`secrets-management/decision-guide.md`](../../secrets-management/decision-guide.md). The
[workflow decision guide](../decision-guide.md) settles the boundary in one question.

---

## 3. What This Kit Covers — and What It Does Not

Being explicit here, because this kit sits next to three others that look similar and are not.

**In scope:** establishing and federating workload identity. Your platform attests what a workload
is; Idira consumes that attestation as the basis for trusting it.

**Out of scope, with the kit that owns it:**

| If the integration… | Build against |
|:---|:---|
| Retrieves a secret value from Idira at runtime | [Secrets Management](../../secrets-management/decision-guide.md) — four paths, including SWA federation as an auth option |
| Pushes a catalogue of AI agents it found into Idira inventory | [Discovery / AI Agents](../../discovery/ai-agents/development-guide.md) |
| Pushes non-agent compute identities into Idira inventory | [Discovery / Machine Identities](../../discovery/machine-identities/development-guide.md) |
| Brokers a recorded privileged session into a web application | [PSM Connectors / Web Connection Component](../../psm-connectors/web-connection-component/development-guide.md) |

> **Terminology collision, worth settling before a technical call.** In some CyberArk-era material
> "SWA" abbreviates **Secure Web Application Connectors Framework**, a PSM browser-automation
> component with no relationship to Secure Workload Access. If a partner uses "SWA" without
> expanding it, confirm which one they mean before matching a kit. The two have different APIs,
> different deployment scopes, and different certification paths.

**On naming:** write **Secure Workload Access**, with **SWA** on second reference. It is delivered as
part of Secrets Manager SaaS and documented in that space — it is not a standalone product, a
separate documentation space, or its own license line. The `workload-identity/` directory name is a
use-case label, exactly as `discovery/` and `identity-response/` are.

---

## 4. Architecture

Three participants, and the partner's platform is usually responsible for the third.

| Component | What it is | Typically owned by |
|:---|:---|:---|
| **SWA Server** | The control-plane component that evaluates attestation evidence and issues SVIDs | The customer's Idira deployment |
| **SWA Agent** | The node-local component that gathers platform evidence and presents it to SWA Server | The customer, deployed onto nodes the partner's platform runs on |
| **The attested workload** | The process, container, function, or agent that ends up holding an SVID | The partner's platform runs or hosts it |

The flow in outline: the workload asks the local SWA Agent for an identity, the agent gathers
platform-supplied evidence of what that workload is, SWA Server evaluates the evidence against the
configured attestation method, and an SVID is issued if it holds. **The step-level sequence is not
stated here — see Section 6.**

What matters for integration design is where the evidence comes from. It is supplied by the platform,
not by the workload, which is precisely why the resulting identity cannot be copied: a cloned
container does not carry its origin node's attestation evidence with it.

### 4.1 Topology

Since the Kubernetes attestation method was added (2026-09-10), **SWA Server does not require network
access to the cluster's API server**. SWA Server outside the cluster with SWA Agents inside it — a
hub-and-spoke arrangement — is supported.

This is worth re-checking against any earlier assessment. If a customer or an internal feasibility
note previously ruled SWA out because SWA Server could not reach a cluster API endpoint, that
objection no longer applies, and the conclusion should be re-tested rather than carried forward.

---

## 5. Choosing an Attestation Method

This is the real decision in the kit, and it is driven by where the workload runs — not by
preference. Three methods are confirmed. Each **removes** a provisioning step rather than adding one,
which is the point: there is no bootstrap credential to distribute, so there is nothing to leak.

| Method | Where it applies | What it proves | What you do *not* need |
|:---|:---|:---|:---|
| **`aws_iid`** | AWS EC2 | The EC2 Instance Identity Document, supplied to the instance automatically | No X.509 certificate pre-provisioned on the instance |
| **`k8s_jwt`** | Kubernetes, SWA Server inside or outside the cluster | A projected service-account token, verified cryptographically | No bootstrap secret, and no SWA Server route to the cluster API server — hub-and-spoke is supported |
| **`k8s_psat`** | Kubernetes, SWA Server in the same cluster | A projected service-account token validated against the cluster API server | No bootstrap secret |
| **`x509pop`** | Unix/Linux machines | A machine certificate signed by a CA configured on the server group; its Subject CN names the node group | No shared secret — the private key never leaves the machine |
| **Google Cloud service-account attestation** | Gemini Enterprise AI agents | The agent's Google Cloud service account | No static credential issued to the agent |

The node group decides which workloads on an attested node receive an identity: its `workload_type` (`kubernetes` or `unix`), the SPIFFE ID template (it must begin `spiffe://{{ .trustdomain }}/{{ .nodegroup }}/`), and optional CEL registration policies. **If you omit the registration policies, SWA issues an SVID to every workload on an attested node** — set them to issue identities only to the workloads that need one. See [Configure node attestation](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-node-attestation-x509pop.htm), [Design node groups](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-node-groups-design.htm) and [Configure SPIFFE templates, attestors, and policies](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-node-groups-templates-policies.htm).

### 5.1 Check the platform before concluding there is no path

A workload that holds no SPIFFE SVID *today* may still have a usable SWA path through one of the
methods above. The sequence:

1. Identify where the workload actually runs — EC2, Kubernetes, a Unix/Linux machine with a CA-issued certificate, Gemini Enterprise, or something else.
2. If one of the methods above applies, use it.
3. Only if none applies, fall back to Section 5.2.

Skipping step 1 and going straight to a fallback is the failure this section exists to prevent.

### 5.2 When no attestation path exists

Fall back to the Workload API authentication methods in
[`secrets-management/secrets-manager-saas/development-guide.md`](../../secrets-management/secrets-manager-saas/development-guide.md)
Section 4, in this order: **a cloud IAM authenticator or JWT, then API key as a last resort.** Client certificate authentication works only through Secrets Manager Edge, a customer-hosted component.

> **An embedded static key is not a fallback.** Never ship a workload or an agent with a key in its
> code or configuration. Agents are cloned and redeployed constantly, so an embedded key leaks with
> the first snapshot. Retrieve against a workload identity on each run instead. The certification
> checklist grades this.

---

## 6. The Federation Exchange

A workload fetches a **JWT-SVID** from SWA and exchanges it for access. SPIFFE changes how a workload reaches downstream services; it does not replace how a workload authenticates to Secrets Manager at bootstrap. See [Understand SPIFFE workload identities](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-overview.htm).

### 6.1 Exchanging a JWT-SVID with Secrets Manager

Secrets Manager accepts SWA identities through its **JWT authenticator**. Full procedure: [Integrate Secure Workload Access with Secrets Manager JWT authentication](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/operations/services/cjr-authn-jwt-swa.htm).

1. **Signing.** The trust domain must sign JWT-SVIDs with **RSA** (`RS*` with an `RSA_*` key). SWA can also sign with elliptic-curve keys, but the JWT authenticator path needs RSA. Confirm the OIDC issuer and audience values for your trust domain.
2. **Authenticator.** Load a JWT authenticator policy in the `conjur/authn-jwt` branch and set its variables: `jwks-uri` (SWA's JWKS endpoint), `issuer`, `audience`, `token-app-property` = `sub`, and `identity-path`.
3. **Workload hosts.** When SWA attests a workload it creates a host under `data/swa/trust-domains/<trust-domain>/workloads/`. **New workload identities have no secret access by default.** The customer's administrator must:
   - create the workloads group (SWA does not create it),
   - annotate each workload host with its SPIFFE ID so the authenticator can map the `sub` claim,
   - add the host to the group, and
   - grant the group permissions on the secrets it needs.
4. **At runtime** the workload fetches a JWT-SVID from the SWA agent (`/opt/swa/bin/swa-agent` on a machine), presents it to the JWT authenticator, receives a Secrets Manager access token, and retrieves its authorized secrets.

> **Still to confirm.** The documented path uses JWT-SVIDs. Whether X.509-SVIDs are accepted for authenticating to Secrets Manager is not stated in the public documentation — confirm with your Idira Technical Alliances contact before you depend on it.

### 6.2 Exchanging a JWT-SVID with external platforms

SWA-issued JWTs can be exchanged for temporary credentials on other platforms, so the workload holds no long-term credential there either:

| Target | Reference |
|:---|:---|
| AWS | [Authenticate SWA workloads with AWS](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-aws.htm) |
| Microsoft Azure | [Authenticate SWA workloads with Azure](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-azure.htm) |
| Google Cloud | [Authenticate SWA workloads with Google Cloud](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-gcp.htm) |
| Gemini Enterprise agents | [Authenticate Gemini Enterprise agents with SWA](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-gemini-enterprise.htm) |
| Claude | [Authenticate SWA workloads with Claude](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-claude.htm) |
| OpenAI | [Authenticate SWA workloads with OpenAI](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-openai.htm) |

### 6.3 SWA management APIs

A partner product that issues, carries or brokers workload identity manages SWA through its REST API, under `https://<subdomain>.secretsmgr.cyberark.cloud/api/swa/`, with `Authorization: Token token="<token>"` (a Secrets Manager admin token) and the v2 media type `application/x.secretsmgr.v2+json`:

| Resource | Operations |
|:---|:---|
| Trust domains — `/api/swa/trust-domains` | register, list, get, update, delete; JWT signing key type |
| Server groups — `/api/swa/trust-domains/{name}/server-groups` | create, list, get, update, delete; node attestation configuration |
| Node groups — `…/server-groups/{name}/node-groups` | create, list, get, update, delete; `workload_type`, SPIFFE ID template, registration policies |
| Servers | register, list, get, update, delete |
| Discovery | OpenID configuration, JWKS, CA bundles |

Reference: [Secure Workload Access APIs overview](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/apis/ccl-api-swa-lp.htm). A Terraform provider is also available: [Install the Secrets Manager provider for SWA](https://docs.cyberark.com/secrets-manager-saas/latest/en/content/conjurcloud/ccl-swa-terraform-provider.htm).

### 6.4 Design rules that do not change

- The workload presents an attested identity rather than a bearer secret. Your platform's job is to make sure a real identity is available at the point of the call.
- SVIDs are **short-lived**. Build renewal in from the start and do not cache an SVID past its validity, or treat one as a long-term credential.
- The identity is bound to the platform context the workload runs in, so it will not survive being moved out of that context. That is the security property, not a defect — do not design around it by extracting and forwarding an SVID.

---

## 7. Telemetry Header (Required)

Every API request must include `x-cybr-telemetry` — a Base64 URL-encoded string of
ampersand-delimited key=value pairs:

```
in=<IntegrationName>&it=WorkloadIdentity&iv=<version>&vn=<VendorName>
```

Example (before encoding):
```
in=AcmeCorp Agent Gateway&it=WorkloadIdentity&iv=1.0&vn=Acme Corporation
```

The `it` value for this kit is **`WorkloadIdentity`**. Take it exactly as written — the registry
values are assigned per kit, not derived, and adapting another kit's value attributes your traffic to
someone else's integration. The transform, reference code in five languages, and test vectors are in
[`telemetry-reference.md`](../../telemetry-reference.md); build the header from that file rather than
from this example. Your `in`, `iv`, and `vn` values are agreed with your Idira Technical Alliances
contact before certification rather than chosen at build time.

---

## 8. Failure Modes to Handle

For HTTP status codes, see the reference pages linked in Section 6. This section covers the
architectural failures, which are the ones that actually bite in deployment. Handle all four.

| Failure | Why it happens | What your integration should do |
|:---|:---|:---|
| **Attestation rejected** | The evidence does not match the configured method — wrong platform, wrong namespace or service account, or an attestation method configured for a platform the workload is not on | Fail closed and surface which method was attempted. Do not fall back to a static credential automatically |
| **SVID expired mid-operation** | SVIDs are short-lived and the operation outlived the validity window | Renew and retry once. Do not extend the cached lifetime to avoid the renewal |
| **Clock skew** | Attested, time-bound credentials are sensitive to node clock drift | Require time sync on nodes running SWA Agent, and treat a validity-window failure as a skew signal rather than a permission problem |
| **No attestation path on the platform** | The workload runs somewhere none of the three methods covers | Route to the Section 5.2 fallback explicitly, log the decision, and never silently embed a key |

Log the attestation method attempted and its outcome for every identity issued. Without that, an
attestation failure and an authorization failure look identical in the logs.

---

## 9. Pre-Development Checklist

- [ ] Confirmed this is the right kit — the integration establishes workload identity rather than
      retrieving a secret value ([workflow decision guide](../decision-guide.md))
- [ ] Confirmed which "SWA" is in play — Secure Workload Access, not the Secure Web Application
      Connectors Framework
- [ ] Platform identified for every workload in scope, and the attestation method determined from it
      (Section 5) rather than chosen by preference
- [ ] Federation exchange confirmed with an Idira Technical Alliances contact (Section 6) — this is a
      gate, not a formality, and nothing in this guide substitutes for it
- [ ] SVID renewal implemented, with no code path that caches an SVID past its validity
- [ ] No static key in any workload or agent image, manifest, or configuration
- [ ] Node time synchronisation confirmed on anything running SWA Agent
- [ ] Attestation method and outcome logged per identity issued
- [ ] Telemetry header values agreed with your Idira Technical Alliances contact (IntegrationName,
      VendorName, version)
- [ ] Preview status understood — read [`certification-checklist.md`](certification-checklist.md)
      during the build, and confirm the current gate with your Idira Technical Alliances contact
      before submission

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.1 | 2026-10-08 | **[Added]** The documented federation exchange with Secrets Manager — JWT-SVIDs through the JWT authenticator, RSA signing, the authenticator variables, and the host, group and permission steps without which an attested workload has no secret access; exchange with AWS, Azure, Google Cloud, Gemini Enterprise, Claude and OpenAI; the SWA management APIs and Terraform provider; the `k8s_psat` and `x509pop` node attestation methods; node-group design, SPIFFE ID templates and registration policies. **[Updated]** Google Cloud is listed as service-account attestation for Gemini Enterprise agents and as a federation target. The fallback order no longer starts with client certificate, which works only through Secrets Manager Edge. One point remains to confirm: whether X.509-SVIDs are accepted by Secrets Manager | Idira Technical Alliances |
| 1.0 | 2026-10-05 | **[Added]** First publication, as the single kit in the new `workload-identity/` workflow. It exists because workload identity federation had no kit of its own: SWA appeared only as the fourth authentication option inside the Secrets Manager SaaS guide (Section 4a), which serves a retrieval client that happens to hold an SVID and does not serve a partner whose platform *is* the identity surface — gateways, agent runtimes, and platforms that already issue SPIFFE identities had nothing to build against and nothing to be graded on. Published as **Preview**: Section 5's three attestation methods, the Section 4 component model, and the 4.1 topology change are confirmed, but Section 6's step-level federation exchange is documented only in the authenticated Secrets Manager SaaS space and is therefore stated as a gap with an explicit instruction not to reconstruct it from SPIFFE or SPIRE material. Carries the direction rule that separates this kit from Secrets Management (establishing identity versus retrieving a secret value, and an integration doing both is certified twice), the boundary against both Discovery kits (inventorying an identity is not issuing one), and the `SWA` acronym collision with the Secure Web Application Connectors Framework, which routes to a different kit entirely. Telemetry `it` value `WorkloadIdentity` assigned in the same change — `SWA` was deliberately not used, because the acronym collision makes it ambiguous in exactly the registry where a wrong value misattributes traffic. — Idira Technical Alliances |
