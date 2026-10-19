# Which Integration Do I Select?

**Type:** Top-Level Decision Guide
**Version:** 1.8
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-14

---

<!--
## AI CONTEXT BLOCK
This is the WORKFLOW router for the partner integration dev-kit repository — it answers "which kit?"
Read it before any workflow decision guide or development guide.

The stage-level entry point is journey.md (the five-stage path: choose → access → build → certify →
list). This file IS stage 1 of that journey. A partner asking "which kit?" starts here; a partner
asking "what happens next?" or "what will I be graded on?" goes to journey.md.

PURPOSE: A technology partner filling out the Idira integration request form must select
which Idira product their integration targets. The form options are product/SKU names, not
use-case names, so partners routinely select the wrong one. This guide maps what the partner
is BUILDING to (a) the correct form option and (b) the correct dev kit.

DECISION LOGIC: Section 2 is a single question — "what does your integration DO?" — with one
row per answer. Each row gives the form option to select and the dev kit to open. Section 3
disambiguates the most common error (retrieve vs rotate). Do not answer a partner's "which
product do I pick?" question from the form option names alone; route through Section 2.

ROUTING PRECEDENCE: journey.md → this file → workflow decision-guide.md (where one exists) →
development-guide.md → certification-checklist.md → marketplace-standards.md.

WORKFLOWS AND THEIR DECISION GUIDES:
  - discovery/decision-guide.md (4 use cases)
  - epm/decision-guide.md (3 use cases)
  - secrets-management/decision-guide.md (4 products)
  - workload-identity/decision-guide.md (1 use case) — HAS a decision guide despite the single kit,
    and it is not a kit chooser: it tests the INBOUND boundary, because an integration that
    establishes workload identity is routinely misfiled as Secrets Management or Discovery. Send a
    partner there when they describe attesting workloads, SPIFFE, or agent identity.
  - audit-service/, credential-rotation/, psm-connectors/, identity-response/, identity-access-management/ — single use case each, no decision guide

"SWA" IS AMBIGUOUS AND THE FORM DOES NOT DISAMBIGUATE IT. Secure Workload Access routes to
workload-identity/; the Secure Web Application Connectors Framework routes to psm-connectors/. They
share nothing. Resolve which one a partner means before mapping a row in Section 2.
-->

---

> **Start here.** This guide answers one question: *given what you are building, which option do you select on the integration request form, and which development kit do you open?*
>
> Read this before opening any workflow guide. Every workflow guide assumes you have already landed in the right workflow — this is the file that gets you there.

---

## 1. Why this guide exists

The integration request form asks which Idira product your integration targets. The options are product names, and you know your integration by what it **does**, not by which Idira product name covers it. Those two things do not map one-to-one:

- One form option, **Idira Secrets Management**, covers four distinct integration paths.
- Two form options — Secrets Management and Credential Rotation — sound interchangeable and are not. This is the single most common selection error.
- The form option labels and the workflow folder names in this repository are not spelled identically, so even a partner who reads the right guide cannot always map it back to a form checkbox.

Selecting the wrong option does not block you permanently, but it does add a review cycle: the submission is reclassified before it can be assessed. Two minutes here saves that.

---

## 2. Route by what your integration does

Find the row that describes your integration. Read the linked guide before you submit the form.

| Your integration… | Select this form option | Open this dev kit |
|:---|:---|:---|
| **Retrieves secrets** from the Idira vault so your application doesn't store credentials locally | Idira Secrets Management | [Secrets Management decision guide](secrets-management/decision-guide.md) — routes you to one of four paths |
| Lets Idira **rotate a credential on a target system** your product manages, via a CPM plugin | Idira Privileged Access Management - Credential Rotation | [Credential Rotation kit](credential-rotation/cpm-rest-api/development-guide.md) |
| **Streams Idira audit events** into your SIEM, analytics, or observability platform | Idira Privileged Access Management - Audit Service | [Audit Service kit](audit-service/siem-integration/development-guide.md) |
| **Pushes accounts, identities, secrets, or AI agents you discover** into Idira so they can be managed | Idira Privileged Access Management - Discovery | [Discovery decision guide](discovery/decision-guide.md) — routes by asset type |
| **Streams endpoint privilege events** from Idira Endpoint Privilege Manager into your platform | Idira Endpoint Privilege Manager | [EPM decision guide](epm/decision-guide.md) → Audit Events |
| **Gates admin elevation** on approval in your ticketing system | Idira Endpoint Privilege Manager | [EPM decision guide](epm/decision-guide.md) → Ticketing / JIT |
| **Contains an endpoint** — removes local admin rights in real time from an XDR detection or SOAR playbook | Idira Endpoint Privilege Manager | [EPM decision guide](epm/decision-guide.md) → SOC Response |
| **Triggers identity or privilege response actions** in Idira from your XDR, SIEM, or SOAR — lock a user, force logout, terminate a privileged session, expire a password | Idira Identity Security Platform | [Identity Response kit](identity-response/response-actions/development-guide.md) — **Draft**, see §4 |
| **Establishes workload identity** — your platform runs, routes, hosts, or already issues identities for workloads, and attests what they are so they reach Idira without a distributed secret | Idira Secrets Management — *but see §4* | [Workload Identity decision guide](workload-identity/decision-guide.md) → SWA Federation — **Preview**, see §4 |
| **Provisions, reconciles, or certifies identities and entitlements** held in Idira from your IGA platform — joiner/mover/leaver via SCIM, entitlement reads for access reviews, role membership | Idira Identity Access Management | [Identity Governance & Provisioning checklist](identity-access-management/identity-governance/certification-checklist.md) — **Preview**, no development guide yet, see §4 |
| Lets **Idira broker and record a privileged session** into your web application, injecting vaulted credentials into its login form | *No exact form option — see §4* | [PSM Connectors kit](psm-connectors/web-connection-component/development-guide.md) |

**Two or more rows fit?** That is normal and usually means two integrations, not one ambiguous integration. Submit the primary one and note the second in the description — they are assessed together but tracked separately.

**No row fits?** Do not force the closest match. Describe what you are building in the form's description field and say explicitly that no listed option matches. A clearly-described gap is routed correctly on the first pass; a forced selection is not.

---

## 3. Secrets Management vs Credential Rotation

This is the most frequent selection error, so it is worth stating plainly. The distinction is **which system acts**:

| | Secrets Management | Credential Rotation |
|:---|:---|:---|
| **Who acts** | Your application | Idira |
| **What happens** | Your app **retrieves** a secret from the vault at runtime | Idira **changes** a credential on a target system |
| **You build** | A client that authenticates and fetches | A CPM plugin that verifies, changes, and reconciles |
| **Select** | Idira Secrets Management | Idira Privileged Access Management - Credential Rotation |

> **The test: does your code *read* a secret, or does Idira *change* one?** Reading is Secrets Management. Idira changing it is Credential Rotation.

**Worked example.** Your discovery appliance needs a database credential to scan a customer's estate. It fetches that credential from the Idira vault at scan time → **Secrets Management** (via the Central Credential Provider path). Idira might *separately* rotate that same database credential on a schedule — but that rotation is a Credential Rotation integration *with the database platform*, not with you. The two coexist and belong to different form options.

Both can be true of one product. If your integration genuinely does both — your app retrieves secrets *and* you ship a CPM plugin so Idira rotates your product's own credentials — those are two integrations. Submit the primary one first.

---

## 4. Known gaps in the form options

Three cases cannot be selected accurately today. All are being addressed; until then, follow the guidance here.

**PSM connection components have no form option.** If you are packaging a connection component so Idira Privileged Session Manager can broker a session into your web application, no form option describes it. Select the option closest to your product's category and **state clearly in the description that this is a PSM web connection component**. Do not select an Audit Service option — a connection component is browser automation, not an audit or SIEM integration, and the mismatch causes a reclassification cycle. Note that this workflow is Idira PAM - Self-Hosted only.

**"Idira Identity Access Management" has one kit, and it covers identity governance only.** If your platform provisions, reconciles, or certifies identities and entitlements in Idira, open the [Identity Governance & Provisioning checklist](identity-access-management/identity-governance/certification-checklist.md) (§2). Otherwise check §2 first — most integrations that sound like Identity Access Management are actually one of these:

- Triggering response actions against identities → **Idira Identity Security Platform** ([Identity Response kit](identity-response/response-actions/development-guide.md))
- Discovering identities and pushing them into Idira → **Discovery**
- Retrieving secrets on behalf of an identity → **Secrets Management**

If none of those fits, your integration is most likely **SSO** or **WPM (Workforce Password Management)** — neither has a dev kit today. Select Idira Identity Access Management and describe which (or something else) you are building in detail; that description is what routes it while these kits are being scoped.

**Workload identity has no form option of its own.** Secure Workload Access is delivered as part of Secrets Manager SaaS, so **Idira Secrets Management** is the closest accurate selection — but it describes *retrieving a secret*, which is not what this integration does. Select it and **state in the description that the integration establishes workload identity via SWA federation**, naming the platform your workloads run on. Two selections to avoid: **Idira Identity Security Platform**, the platform umbrella, is not a product selection and routes nowhere; and an Identity Access Management option will route to the identity governance kit (above), which is a different integration. The [Workload Identity decision guide](workload-identity/decision-guide.md) settles whether this is even your workflow — the boundary against Secrets Management catches most of these — and resolves the `SWA` acronym collision with the unrelated Secure Web Application Connectors Framework.

**The SWA Federation kit is still Preview.** Its development guide is usable and its certification checklist is published, but the kit is marked **Preview** in [`index.md`](index.md) — not a certifiable path yet — and one section is deliberately incomplete: the step-level federation exchange is confirmed per build rather than published, so do not reconstruct it from the SPIFFE specification or SPIRE material. Talk to your Idira Technical Alliances contact before committing engineering time.

**The Identity Governance & Provisioning kit is Preview, and has no development guide yet.** Its certification checklist is published so you can build against the intended gate, but the kit is marked **Preview** in [`index.md`](index.md) — not a certifiable path yet. Until the guide is published, build from the Idira documentation named in each checklist row's `Source` cell, and talk to your Idira Technical Alliances contact before committing engineering time.

**The Identity Response kit is still Preview.** Its development guide is usable and its certification checklist is published, but the kit is marked **Preview** in [`index.md`](index.md) — not yet a certifiable path — and several API field names in the guide are still marked `[TBD]`. Talk to your Idira Technical Alliances contact before committing engineering time to it, so you know which parts are settled.

---

## 5. Already have a certified integration?

The request form is for **new** integrations. If your integration already exists and is listed, you are looking for **re-certification**, not a new request — say so explicitly in the form description so it is not assessed as a new build. Re-certification is required yearly; see [`index.md`](index.md) for what certification covers.

---

## 6. Then what?

1. **Read the dev kit** your row points to — the development guide, and the certification checklist that goes with it. The checklist tells you what is reviewed before your integration can be listed, so read it before you start building, not after.
2. **Submit the request form** with the option from §2.
3. **Every integration needs a demonstration** — a 2–5 minute recorded demo or a live walkthrough call. Plan for it early; see [`index.md`](index.md).
4. **Every REST integration needs the telemetry header** (`x-cybr-telemetry`). PSM connection components are the one exception. See [`index.md`](index.md) for the field spec.

Full workflow and kit inventory: [`index.md`](index.md).

**For the stages after this one** — environment provisioning, what certification actually reviews, the remediation loop, listing, and your post-listing recertification and support obligations — see [The Partner Integration Journey](journey.md). This guide is stage 1 of five.

---

## 7. Terminology

Idira products were renamed from their CyberArk names, and several have an older name before that. If a name in your source material does not match the name used here, resolve it in **[Idira Product Names — Crosswalk](naming-crosswalk.md)** before assuming they are two different products.

That file also covers the three rules that most often cause a mis-selection on the form: naming the PAM deployment (SaaS vs Self-Hosted), the CP-vs-CCP distinction, and which CyberArk-era names — hostnames, header keys, API paths — are deliberately unchanged and should not be "corrected."

Use current names in all documentation and certification submissions.


---

## Change Log

| Version | Date | Change |
|:---|:---|:---|
| 1.8 | 2026-10-14 | **[Added]** A §2 row and a §4 Preview note for the new Identity Access Management kit, Identity Governance & Provisioning. The §4 note that said Identity Access Management has no dev kit now names the one it has and narrows the no-kit list to SSO and WPM — SCIM provisioning is what the new kit covers. The Workload Identity note no longer says an Identity Access Management selection routes to a kit that does not exist; it now routes to the governance kit, which is still the wrong integration for workload identity. The §2 row links the checklist because the kit has no development guide yet. — Idira Technical Alliances |
| 1.7 | 2026-10-05 | **[Added]** A §2 row and two §4 notes for the new Workload Identity workflow, whose kit establishes workload identity rather than consuming one. The §2 row is qualified rather than clean, because the form cannot express this integration: Secure Workload Access ships as part of Secrets Manager SaaS, so **Idira Secrets Management** is the closest accurate option while describing the opposite operation — retrieving a secret. §4 therefore gains a third known gap, taking it from two to three, telling a partner to select that option and say in the description that the integration establishes workload identity via SWA federation, and naming the two selections that waste a cycle: the platform umbrella, which routes nowhere, and an Identity Access Management option, which routes to a kit that does not exist. A second §4 note records the kit's Preview status and its one deliberate documentation gap. The AI context block now also carries the `SWA` acronym collision, since the form does not disambiguate Secure Workload Access from the Secure Web Application Connectors Framework and the two share no API, scope or certification path. No existing row, form option or kit mapping changed | Idira Technical Alliances |
| 1.6 | 2026-10-05 | **[Fixed]** The Identity Response note said the kit is marked `Draft` in [`index.md`](index.md). That status value does not exist: the kit is marked **Preview**, and `index.md`'s status key defines only *Available* and *Preview*. A partner or agent following this file — read-order step 2 — was sent to look for a value it would never find, in the one place that tells it whether the kit is buildable. The note now says `Preview` and states what Preview means: not yet a certifiable path. The advice to talk to an Idira Technical Alliances contact before committing engineering time is unchanged | Idira Technical Alliances |
| 1.5 | 2026-10-02 | **[Fixed]** Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. Also added this change log — the file previously carried none, so no revision before this one is recorded. — Idira Technical Alliances |

---

*Maintained by Idira Technical Alliances — cybr-bizdevtech@paloaltonetworks.com*
