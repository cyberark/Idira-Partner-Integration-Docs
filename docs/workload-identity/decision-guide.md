# Workload Identity Workflow — Is This the Right Workflow?

**Workflow:** Workload Identity  
**Type:** Decision Guide  
**Author:** Idira Technical Alliances  
**Version:** 1.0  
**Last Updated:** 2026-10-05

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this guide.
Read this block first before answering any questions about Workload Identity integrations.

DOCUMENT TYPE: Workflow decision guide — a ROUTER, not a build guide. No auth procedure, no request
  bodies, no field schemas. Do not answer a build question from this file.
WORKFLOW: Workload Identity
CONTACT: cybr-bizdevtech@paloaltonetworks.com

THIS GUIDE ANSWERS A DIFFERENT QUESTION FROM THE OTHER WORKFLOW DECISION GUIDES, AND THAT IS
DELIBERATE. The ../discovery/, ../epm/ and ../secrets-management/ guides pick which kit WITHIN their
workflow. This workflow has one kit, so there is no within-workflow choice to make. Its job is the
INBOUND boundary: confirming the integration belongs in this workflow at all rather than in Secrets
Management or Discovery, which is where it is most often misfiled. If the boundary is already
settled, skip straight to swa-federation/development-guide.md.

THE ONE QUESTION THAT SETTLES IT: does the integration ESTABLISH an identity, or does it USE one to
get something?
  Establishes identity (the partner platform attests what a workload is)  -> this workflow
  Uses an identity to retrieve a secret value from Idira                  -> ../secrets-management/
  Reports identities it found, as inventory records                        -> ../discovery/
An integration can legitimately do more than one. It then builds against each kit and is certified
once per kit — not once overall. Do not merge two kits into one submission.

SWA IS AN ACRONYM COLLISION AND THIS IS THE FILE THAT CATCHES IT:
  Secure Workload Access                      -> swa-federation/ (this workflow)
  Secure Web Application Connectors Framework -> ../psm-connectors/web-connection-component/
The second is PSM browser automation for self-hosted deployments and is unrelated on every axis —
different API, different deployment scope, different certification path. If a partner says "SWA"
without expanding it, resolve which one before matching a kit.

SWA IS NOT A STANDALONE PRODUCT. It is delivered as part of Secrets Manager SaaS and documented in
that space. `workload-identity/` is a use-case label like `discovery/` and `identity-response/`, not
a product name or a license line. Write "Secure Workload Access", "SWA" on second reference.

THE SINGLE KIT AND ITS TELEMETRY IDENTIFIER:
- swa-federation/   Secure Workload Access federation   it=WorkloadIdentity
PascalCase, matching the ../secrets-management/ and ../credential-rotation/ convention rather than
the Title-Hyphen used by ../discovery/. The values are assigned, not derivable — see
../telemetry-reference.md §3 and do not normalise the casing. `SWA` was deliberately NOT used as the
value, because the acronym collision above makes it ambiguous in the one registry where a wrong
value misattributes a partner's traffic.

THE KIT IS PREVIEW. Not a certifiable path yet, and its development guide has one deliberate gap —
the step-level federation exchange, which is confirmed per build rather than published. Do not
promise a Marketplace listing on it, and do not let an agent reconstruct the exchange from SPIFFE or
SPIRE material.

NO CERTIFICATION CHECKLIST PAIRS WITH THIS FILE, BY DESIGN. Nothing here is graded directly; the
checks live in the kit. Keep this file to routing.

FILES IN THIS DIRECTORY:
- decision-guide.md — this file — whether this is the right workflow
- swa-federation/ — the kit: a development-guide + certification-checklist pair
- ../journey.md — the stage above this one: which workflow, before which kit
- ../telemetry-reference.md — the telemetry transform, the it registry, and test vectors

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> Use this guide before opening the development guide. Unlike the other workflow decision guides,
> this one does not pick between kits — this workflow has one. It confirms that your integration
> belongs here rather than in Secrets Management or Discovery, which is the error this file exists to
> prevent.

---

## 1. Solution Overview

**Secure Workload Access (SWA)** is Idira's SPIFFE-based workload identity capability, delivered as
part of Secrets Manager SaaS. A workload proves what it is with a short-lived, cryptographically
attested **SPIFFE SVID** rather than a pre-shared secret.

This workflow holds one kit.

| Dev Kit | What the integration establishes | Status | Telemetry `it` |
|:---|:---|:---|:---|
| **[SWA Federation](swa-federation/)** | Workloads your platform runs, routes, or hosts attest to SWA and authenticate to Idira without a distributed secret | Preview | `WorkloadIdentity` |

> **This kit is Preview** — not a certifiable path yet, and one section of its development guide is
> deliberately incomplete. See [the kit's own notice](swa-federation/development-guide.md#6-the-federation-exchange)
> and talk to your Idira Technical Alliances contact before committing engineering time.

---

## 2. The Decision

One question settles it. Does your integration **establish** an identity, or **use** one to get
something?

```
Does your platform attest what a workload IS —
supplying platform evidence Idira can verify?
│
├─ Yes, my platform runs, routes, hosts, or already
│  issues identities for other people's workloads ──────► Workload Identity (this workflow)
│                                                          → swa-federation/
│
└─ No — my platform is the one being identified
    │
    └─ What does it do once identified?
        │
        ├─ Retrieves a secret VALUE from the
        │  Idira vault at runtime ──────────────────────► Secrets Management
        │                                                 → ../secrets-management/decision-guide.md
        │
        └─ Reports identities it FOUND, as
           inventory records ──────────────────────────► Discovery
                                                         → ../discovery/decision-guide.md
```

**The test in one line:** if the answer to *"who vouches for this workload?"* is **your platform**,
you are in this workflow. If the answer is *"something else vouches, and then we fetch a secret,"*
you are in Secrets Management.

> **These are additive, not exclusive.** A platform that attests its workloads *and* retrieves
> secrets for them builds against both kits and is certified **twice** — each kit carries its own
> checklist. Do not merge two kits into one submission.

---

## 3. Use Cases for This Workflow

Use the SWA Federation kit when:

- Your platform is a **runtime that hosts workloads or agents** — a compute platform, container
  platform, or agent runtime — and those workloads need to reach Idira-managed resources without a
  distributed credential
- Your platform is a **gateway or proxy** brokering traffic on a workload's behalf, and the customer
  wants attested workload identity end to end rather than one shared gateway credential
- Your platform **already issues SPIFFE identities**, and federating with SWA avoids the customer
  maintaining two workload identity systems
- The customer's requirement is that non-human identities are **attested rather than pre-trusted** —
  a property a bearer secret cannot demonstrate regardless of how well it is stored

**Strongest signal for this workflow:** your product is in a position to know what a workload is
because it is the thing running or routing it. That position is what makes attestation possible, and
it is what no secrets-retrieval client has.

**Not this workflow:** your product needs a credential to do its job. That is Secrets Management,
even if the credential is fetched using an SVID your platform did not issue.

---

## 4. The "SWA" Acronym Collision

Resolve this before a technical call, because the two meanings route to different kits with different
APIs, deployment scopes, and certification paths.

| If "SWA" means… | It is… | Kit |
|:---|:---|:---|
| **Secure Workload Access** | SPIFFE-based workload identity, part of Secrets Manager SaaS | [SWA Federation](swa-federation/development-guide.md) — this workflow |
| **Secure Web Application Connectors Framework** | A PSM browser-automation component for brokering sessions into web applications | [PSM Connectors / Web Connection Component](../psm-connectors/web-connection-component/development-guide.md) |

If a partner uses the bare acronym, ask which one they mean rather than inferring from context. The
request forms do not disambiguate it either.

---

## 5. Shared Technical Requirements

These apply to any integration in this workflow:

- **Attestation is platform-driven, not preference-driven.** The method follows from where the
  workload runs — AWS EC2 Instance Identity Document, Google Cloud, or Kubernetes `k8s_jwt`. Check
  the platform before concluding a workload has no path; a workload holding no SVID today may still
  attest on one of the three.
- **Fallback order, only when no attestation path exists:** client certificate, then JWT, then API
  key as a last resort. An embedded static key is not a fallback — it is the anti-pattern the kit
  grades against.
- **SVIDs are short-lived.** Build renewal in from the start; never cache one past its validity or
  treat it as a long-term credential.
- **Fail closed.** A rejected attestation must not silently fall back to a static credential.
- **Telemetry header:** all requests include `x-cybr-telemetry` Base64 URL-encoded, with
  `it=WorkloadIdentity`. The `in`, `iv` and `vn` values are agreed with your Idira Technical Alliances
  contact before certification rather than chosen at build time.
- **Node time synchronisation** on anything running SWA Agent — attested, time-bound credentials are
  sensitive to clock drift, and skew presents as a permission failure if you do not separate them.

---

## 6. Development Guide

| Dev Kit | Development Guide | Certification Checklist |
|:---|:---|:---|
| [SWA Federation](swa-federation/) | [Development Guide](swa-federation/development-guide.md) | [Checklist](swa-federation/certification-checklist.md) |

---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.0 | 2026-10-05 | **[Added]** First publication, alongside the SWA Federation kit and the new `workload-identity/` workflow. This guide answers a different question from the other three workflow decision guides and says so up front: with one kit in the workflow there is no within-workflow choice, so its job is the inbound boundary rather than kit selection. It carries the one question that settles that boundary — does the integration *establish* an identity or *use* one to get something — routing establishment here, secret retrieval to Secrets Management, and inventory reporting to Discovery, with the note that these are additive and a platform doing two of them is certified twice rather than once. §4 exists for the `SWA` acronym collision between Secure Workload Access and the Secure Web Application Connectors Framework, which route to different workflows and are unrelated on every axis; the bare acronym is not disambiguated by the request forms either. §5 carries the graded shared requirements for generated code, with emphasis on attestation being platform-driven rather than chosen, on fail-closed behaviour, and on clock skew presenting as a permission failure when the two are not separated. The kit's Preview status and its one deliberate documentation gap are stated here as well as in the kit, so a reader routed by this file learns them before opening the guide. — Idira Technical Alliances |
