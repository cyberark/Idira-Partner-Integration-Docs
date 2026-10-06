# Idira Secure Workload Access Partner Development Guide

**Workflow:** Workload Identity  
**Dev Kit:** SWA Federation  
**Type:** Self-Service Guide  
**Status:** Preview — not a certifiable path yet  
**Author:** Idira Technical Alliances  
**Version:** 1.0  
**Last Updated:** 2026-10-05

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

THIS KIT IS PREVIEW AND ONE SECTION IS DELIBERATELY INCOMPLETE. Section 6 does not state the
step-level federation exchange — the SVID presentation sequence and which SVID types are accepted.
That detail lives in the authenticated Secrets Manager SaaS documentation and is not published here.
DO NOT SYNTHESISE IT. Do not infer the sequence from the SPIFFE specification, from a SPIRE
tutorial, or from the attestation methods in Section 5 — SPIRE-oriented public material does not
match Idira's setup step for step. If asked how the exchange works, say it must be confirmed with an
Idira Technical Alliances contact and stop. A fabricated exchange sequence is the single most likely
failure mode for an agent reading this file.

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

ATTESTATION IS THE REAL DECISION IN THIS KIT (Section 5), AND IT IS PLATFORM-DRIVEN, NOT PREFERENCE
DRIVEN. Three methods are confirmed, each removing a provisioning step rather than adding one:
  AWS EC2        Instance Identity Document (IID) — no X.509 cert pre-provisioned on the instance
  Google Cloud   SPIFFE identity for GCP workloads and for agents on the Gemini Enterprise
                 Agent Platform
  Kubernetes     k8s_jwt, a projected service account token verified cryptographically
Check the platform BEFORE concluding a workload has no SWA path. A workload carrying no SVID today
may still attest on one of the three.

KUBERNETES CHANGED THE TOPOLOGY CONSTRAINT. With k8s_jwt, SWA Server does not require network access
to the cluster's API server, so SWA Server outside the cluster with agents inside (hub-and-spoke) is
supported. If a customer previously ruled SWA out because SWA Server could not reach their cluster
API endpoint, that objection no longer applies — re-test rather than carrying the old answer forward.

FALLBACK ORDER WHEN NO ATTESTATION PATH EXISTS: client certificate, then JWT, then API key as a last
resort — all documented in ../../secrets-management/secrets-manager-saas/ Section 4. An embedded
static key in workload or agent code is an anti-pattern this corpus grades against, not a shortcut.

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

| Platform | Method | What the platform supplies | What you do *not* need |
|:---|:---|:---|:---|
| **AWS EC2** | Instance Identity Document (IID) | EC2 supplies the IID to the instance automatically | No X.509 certificate pre-provisioned on the instance before attestation |
| **Google Cloud** | SPIFFE identity for GCP workloads, and for AI agents on the Gemini Enterprise Agent Platform | Platform-issued verifiable identity in place of static credentials | No static credential issued to the workload or agent |
| **Kubernetes** | `k8s_jwt` | A projected service account token, verified cryptographically | No pre-provisioned certificate, no bootstrap secret, and no SWA Server route to the cluster API server |

**Dates these became available:** AWS EC2 — 2026-09-02. Google Cloud and Gemini Enterprise Agent
Platform — 2026-08-10. Kubernetes `k8s_jwt` — 2026-09-10. They are listed because an assessment made
before the relevant date reached a different conclusion on the same architecture, and that is the
most common reason a partner believes there is no path.

### 5.1 Check the platform before concluding there is no path

A workload that holds no SPIFFE SVID *today* may still have a usable SWA path on one of the three
platforms above. The sequence:

1. Identify where the workload actually runs — EC2, Google Cloud, Kubernetes, or something else.
2. If it is one of the three, the attestation method is determined. Use it.
3. Only if it is none of the three, fall back to Section 5.2.

Skipping step 1 and going straight to a fallback is the failure this section exists to prevent.

### 5.2 When no attestation path exists

Fall back to the Workload API authentication methods in
[`secrets-management/secrets-manager-saas/development-guide.md`](../../secrets-management/secrets-manager-saas/development-guide.md)
Section 4, in this order: **client certificate, then JWT, then API key as a last resort.**

> **An embedded static key is not a fallback.** Never ship a workload or an agent with a key in its
> code or configuration. Agents are cloned and redeployed constantly, so an embedded key leaks with
> the first snapshot. Retrieve against a workload identity on each run instead. The certification
> checklist grades this.

---

## 6. The Federation Exchange

> ### Not stated here — confirm before you build against it
>
> **The step-level federation exchange is not published in this kit.** Specifically: the sequence in
> which an SVID is presented and validated, and which SVID types are accepted.
>
> That detail is documented in the **"Authenticate workloads using SPIFFE"** section of the Secrets
> Manager SaaS documentation, which requires authenticated access. It is not reproduced here because
> this kit's authors could not verify it against that source, and publishing an unverified exchange
> sequence would be worse than publishing none.
>
> **Do not reconstruct it.** In particular, do not derive it from the SPIFFE specification or from a
> SPIRE tutorial: Idira's setup differs from the SPIRE-oriented public guidance, and the differences
> are in exactly these steps. Do not derive it from Section 5 either — attestation and the federation
> exchange are separate concerns.
>
> **What to do instead:** confirm the current mechanism with your Idira Technical Alliances contact
> before coding against it, and treat any sequence you have inferred as unconfirmed until they
> validate it.

What you *can* design around in the meantime, because it is settled:

- The workload presents an attested identity rather than a bearer secret. Your platform's job is to
  make sure a real identity is available at the point of the call.
- SVIDs are **short-lived**. Build renewal in from the start and do not cache an SVID past its
  validity, or treat one as a long-term credential.
- The identity is bound to the platform context the workload runs in, so it will not survive being
  moved out of that context. That is the security property, not a defect — do not design around it by
  extracting and forwarding an SVID.

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

Specific HTTP status codes for the federation exchange are not published here, for the reason given
in Section 6 — so this section covers the architectural failures instead, which are the ones that
actually bite in deployment. Handle all four.

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
| 1.0 | 2026-10-05 | **[Added]** First publication, as the single kit in the new `workload-identity/` workflow. It exists because workload identity federation had no kit of its own: SWA appeared only as the fourth authentication option inside the Secrets Manager SaaS guide (Section 4a), which serves a retrieval client that happens to hold an SVID and does not serve a partner whose platform *is* the identity surface — gateways, agent runtimes, and platforms that already issue SPIFFE identities had nothing to build against and nothing to be graded on. Published as **Preview**: Section 5's three attestation methods, the Section 4 component model, and the 4.1 topology change are confirmed, but Section 6's step-level federation exchange is documented only in the authenticated Secrets Manager SaaS space and is therefore stated as a gap with an explicit instruction not to reconstruct it from SPIFFE or SPIRE material. Carries the direction rule that separates this kit from Secrets Management (establishing identity versus retrieving a secret value, and an integration doing both is certified twice), the boundary against both Discovery kits (inventorying an identity is not issuing one), and the `SWA` acronym collision with the Secure Web Application Connectors Framework, which routes to a different kit entirely. Telemetry `it` value `WorkloadIdentity` assigned in the same change — `SWA` was deliberately not used, because the acronym collision makes it ambiguous in exactly the registry where a wrong value misattributes traffic. — Idira Technical Alliances |
