# The Partner Integration Journey

**Type:** Journey Overview
**Version:** 1.8
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-19

---

<!--
## AI CONTEXT BLOCK
This is the ENTRY POINT for the entire partner integration dev-kit repository — one level above
decision-guide.md.

PURPOSE: decision-guide.md answers "which kit do I open?" and each development guide answers "how
do I build it?" Neither answers "what is the whole path, and where am I on it?" A partner who has
only read a development guide knows how to write code and does not know that a demonstration is
mandatory, that the certification checklist is graded, or that listing has its own content
standards. This file is that path, stated once.

STRUCTURE: five stages, matching the journey model used for internal kit QA. Each stage states what
the partner does, what Idira does, and what "done" looks like. Every stage hands off to a real file
in this repository — no stage ends in a dead end.

ROUTING PRECEDENCE: journey.md (this file) → decision-guide.md → workflow decision-guide.md (where
one exists) → development-guide.md → certification-checklist.md → marketplace-standards.md.

DO NOT answer a partner's "what happens next?" question from a single development guide. Route
through the stage table in §2.
-->

---

> **Start here.** This is the whole path, from first contact to a certified integration listed in the Idira Marketplace — what you do at each stage, what we do, and what has to be true before you move on.
>
> If you already know which integration you are building and just need the next artifact, jump to [Which Integration Do I Select?](decision-guide.md) or the kit catalog in [`index.md`](index.md).

---

## 1. What you are signing up for

Building an Idira integration is five stages. Three of them are ours to unblock, and two are yours to build.

The two places partners most often lose time are the **bookends**, not the middle:

- **At the start** — selecting the wrong Idira product on the request form, which adds a reclassification cycle before your request is even assessed.
- **At the end** — discovering at submission time that certification requires a working demonstration and that the Marketplace listing has its own content standards.

Both are avoidable by reading §2 before you write code. The certification checklist for your integration type is published in this repository from day one, deliberately: it tells you what you will be graded on while you can still act on it.

---

## 2. The journey at a glance

```
   1              2               3              4              5
CHOOSE   →   GET ACCESS   →     BUILD    →   GET CERTIFIED  →  GET LISTED
 the path     to Idira        the integration   reviewed          published
                                                by Idira
 you          us              you               us               both
```

| # | Stage | You do | Idira does | Done when |
|:--|:------|:-------|:-----------|:----------|
| 1 | **[Choose the path](#3-stage-1--choose-the-path)** | Identify what your integration does; select the matching option on the request form and submit it | Review the technical use case, approve or decline, and assign a tracking reference | You have a decision by email and a tracking reference |
| 2 | **[Get access](#4-stage-2--get-access-to-idira)** | Provide the details we ask for; confirm you can log in | Provision an isolated environment matching your integration type and send you the details | You are logged in to a working environment |
| 3 | **[Build](#5-stage-3--build-the-integration)** | Build against the development guide for your kit; apply the required telemetry header | Answer technical questions and fix gaps in the guides | Your integration works end to end and the checklist is satisfied |
| 4 | **[Get certified](#6-stage-4--get-certified)** | Submit the completed checklist, your documentation, and a demonstration | Review against the checklist; pass, or return itemized gaps for remediation | Certification is approved |
| 5 | **[Get listed](#7-stage-5--get-listed)** | Supply listing content to the Marketplace standards | Publish the listing to the Idira Marketplace and the partner directory | Your listing is live and discoverable |

**The stages are sequential and the gates are real.** You cannot get an environment before your request is approved, and you cannot be listed before you are certified. You *can* — and should — read stages 4 and 5 during stage 3.

---

## 3. Stage 1 — Choose the path

**Yours to drive.** Two things happen here, in this order.

### 3.1 Work out which integration you are building

Read **[Which Integration Do I Select?](decision-guide.md)** before you touch the request form. It maps what your integration *does* to the form option you should select and the dev kit you should open — and those do not map one-to-one. One form option covers four distinct integration paths, and two of the options sound interchangeable but are not.

If your workflow has its own decision guide, read that next:

| Workflow | Decision guide | Routes by |
|:---|:---|:---|
| Discovery | [`discovery/decision-guide.md`](discovery/decision-guide.md) | Asset type you discover — accounts, AI agents, machine identities, secrets |
| EPM | [`epm/decision-guide.md`](epm/decision-guide.md) | Use case — audit events, JIT ticketing, SOC response |
| Secrets Management | [`secrets-management/decision-guide.md`](secrets-management/decision-guide.md) | Deployment and retrieval pattern — four paths |
| Workload Identity | [`workload-identity/decision-guide.md`](workload-identity/decision-guide.md) | **Not kit choice — this workflow has one kit.** It tests whether your integration belongs here at all rather than in Secrets Management or Discovery, and resolves the `SWA` acronym collision |

Audit Service, Credential Rotation, PSM Connectors, and Identity Response each have a single use case and no decision guide — go straight to the development guide from [`index.md`](index.md). Workload Identity also has a single kit but *does* carry a decision guide, because establishing a workload identity is routinely misfiled as retrieving a secret — read it rather than skipping on the single-kit pattern.

### 3.2 Submit the integration request

Submit the request form with the option your row in the decision guide gave you.

- **If no option fits**, do not force the closest match. Describe what you are building in the description field and say explicitly that no listed option matches. A clearly-described gap routes correctly on the first pass; a forced selection does not.
- **If your integration already exists and is listed**, you are looking for re-certification, not a new request. Say so in the description so it is not assessed as a new build.

**What Idira does:** reviews the technical use case, approves or declines it, and communicates the outcome by email. An approved request is assigned a tracking reference that follows your integration through every later stage — quote it in any support email.

**Prerequisite worth knowing early:** the integration request is a separate step from becoming an approved Palo Alto Networks technology partner. If your company is not already a technology partner, that application is reviewed in parallel and can gate access at stage 2. Start it early if you are new to the programme.

---

## 4. Stage 2 — Get access to Idira

**Ours to deliver.** Once your request is approved, we provision an isolated environment for you to build against. You do not build against a customer tenant, and you do not get access to Idira source repositories.

The environment you receive depends on what you are building:

| Your integration | What you get |
|:---|:---|
| Discovery | A dedicated Identity Security Platform SaaS tenant |
| Secrets Management (SaaS, CP, CCP) | A shared Identity Security Platform environment |
| Secrets Management (Self-Hosted) | A Skytap environment, provisioned by your Business Development representative with a Skytap Instructions document |
| Credential Rotation | A PAM Self-Hosted environment |
| Audit Service | A dedicated SaaS tenant |
| EPM — Audit Events | A shared integrations-platform environment |
| EPM — Ticketing / JIT | A dedicated tenant |
| PSM Connectors | PAM Self-Hosted on the C3 Integrations Platform — `https://c3.cyberark.cloud` |
| Identity Response | Identity Security Platform SaaS on the C3 Integrations Platform — `https://c3.cyberark.cloud` |
| Workload Identity (SWA Federation) | Confirmed per build with your Business Development representative. Secure Workload Access is delivered as part of Secrets Manager SaaS, but the environment also has to cover the platform your workloads attest from — EC2, Google Cloud, or Kubernetes — so tell us which one at provisioning rather than assuming the Secrets Management row applies |

Environment credentials are never published in these docs. If you need credentials for your environment, email **cybr-bizdevtech@paloaltonetworks.com**.

**Signed before access, not after.** A Partner Agreement must be in place before environment access is granted. It is handled by your Business Development representative in parallel with provisioning, but it is a real gate — if it is unsigned, an approved request still does not produce an environment. Ask where yours stands as soon as your request is approved.

**What you do:** supply the details we request for provisioning, then confirm you can log in and reach the API or component your integration targets. Tell us immediately if you cannot — an unusable environment discovered three weeks in is the most expensive failure in this journey.

**Where to ask:** cybr-bizdevtech@paloaltonetworks.com, quoting your tracking reference.

**Two things to check before you start building:**

1. **Deployment scope.** Some integrations are SaaS-only and some are Self-Hosted-only. Your development guide states which. Confirm it matches the deployment your customers actually run.
2. **API role membership.** Several APIs require your integration user to hold a specific role — for example, pushing inventory over the Discovery Context API requires the **Machines External Data Contributor** role. Role names in this area changed recently, and an assignment made under an earlier name has to be replaced rather than supplemented. Your development guide states the current requirement; verify it on your tenant rather than assuming it was granted at provisioning.

---

## 5. Stage 3 — Build the integration

**Yours to build.** Open the development guide for your kit from [`index.md`](index.md). It covers the use case, the authentication flow, the API operations, error and rotation handling, code examples, and best practices.

Three requirements apply across every integration and are checked at certification, so build them in rather than retrofitting:

| Requirement | What it means |
|:---|:---|
| **Telemetry header** | Every API transaction carries the `x-cybr-telemetry` header, Base64 URL-encoded, with integration name, type, version, and vendor name. Build it from [`telemetry-reference.md`](telemetry-reference.md) — the transform, the `IntegrationType` value assigned to your kit, working code, and test vectors are all there. Do not implement it from a summary table. Does not apply to PSM connection components, which are browser automation rather than REST |
| **No secrets in logs** | Secrets, tokens, and API keys are never written to log or debug output |
| **Rotation tolerance** | Your integration tolerates a temporarily incorrect secret during rotation — retry, or poll for change-in-progress, rather than failing hard |

**If a product name does not match, resolve it before you build around it.** Idira products were renamed from their CyberArk names, and public documentation, older partner material, and API responses use all three generations of name. [Idira Product Names — Crosswalk](naming-crosswalk.md) maps them, and states which CyberArk-era names — hostnames, header keys, API paths — are deliberately unchanged. Partners have lost time both ways: treating one product as two, and "correcting" a header key that was never renamed.

**Read your certification checklist now, not later.** It is published alongside your development guide and it is the exact document your submission is graded against. Working through it as you build costs nothing; discovering it at submission costs a review cycle.

**When you are blocked:** email cybr-bizdevtech@paloaltonetworks.com with your tracking reference. If the answer turns out to be missing from your development guide, we fix the guide — a gap corrected once is better than the same answer given five times.

---

## 6. Stage 4 — Get certified

**Ours to review, yours to submit.** Certification validates the integration for security, quality, and documentation completeness. Every partner-led integration must pass it before it can be listed.

### What you submit

| Item | Notes |
|:---|:---|
| **The completed certification checklist** | The one shipped with your kit, with the attestation section filled in — partner name, integration name, version, date, contact |
| **Your integration documentation** | A technical integration guide matching the provided template, written for the customer who will deploy it |
| **A demonstration** | Expected — see the note below on how it is weighed. Either a recorded 2–5 minute video showing the end-to-end flow, **or** a live demonstration call with your Idira Technical Alliances contact walking the same flow |
| **Test results** | Where your integration type calls for them; your checklist says whether it does |

> **On the demonstration.** The format is your choice — a recording or a live call, whichever you can deliver. If
> recording restrictions, customer-data sensitivity, or internal approval delays mean you cannot publish a video,
> book the live call instead. Partners are surprised by this requirement more than by anything else in the journey
> — plan for it during stage 3.
>
> **How it is weighed.** Your kit's certification checklist grades the demonstration as a required item, but the
> certification programme records it as **highly recommended and non-blocking**: a missing demonstration must never
> be the sole reason an integration is declined. Where a checklist and that policy disagree,
> **[`security-baseline-reference.md`](security-baseline-reference.md) § 3 is authoritative** — the checklists are
> being brought into line with it. Deliver a demonstration: it is expected, it is the fastest way to close review,
> and it is a listing asset you will want anyway. But if it is the only item you cannot produce, submit without it
> and say so, rather than delaying your submission.

### How to submit

| Question | Answer |
|:---|:---|
| **Where does it go?** | Email **cybr-bizdevtech@paloaltonetworks.com** with your tracking reference in the subject line. There is no upload portal — the submission is an email to the Technical Alliances team |
| **How do I deliver the demo?** | For a video: a shareable link (your own hosting, or a link we can access) rather than an attachment — recordings routinely exceed mail size limits. For a live call: say so in the submission email and your Idira Technical Alliances contact schedules it |
| **What do I attach?** | The completed checklist with the attestation section filled in, your integration documentation, and test results where your checklist asks for them |
| **How long does review take?** | Your Idira Technical Alliances contact confirms the review window when they acknowledge your submission. Ask for it at submission time if you are working to a launch date |

### What happens next

- **Pass** — certification is approved and your integration advances to stage 5.
- **Gaps found** — you receive an itemized list, the status moves to remediation, and you resubmit. The review restarts on resubmission; it does not resume mid-way. Whether an integration passed on first attempt is recorded.

There is no certification badge to display. Approved technology partners use the Palo Alto Networks corporate logo.

---

## 7. Stage 5 — Get listed

**Shared.** A certified integration is published so customers can find it. Two destinations, and they are distinct:

| Destination | What it is |
|:---|:---|
| **Idira Marketplace** | The in-product catalog customers browse inside the Idira Identity Security Platform |
| **Partner directory** | The public Palo Alto Networks technology partner directory listing for your solution |

**What you supply:** listing content that meets the standards in **[`marketplace-standards.md`](marketplace-standards.md)** — title format, short description, per-use-case requirements, and overview structure. Read it before writing the content, not after it is rejected. A working demo video is expected as a listing asset wherever you can provide one.

**How you supply it:** email your listing content to **cybr-bizdevtech@paloaltonetworks.com** with your tracking reference in the subject line — the same address you submitted certification to. There is no partner-facing upload portal for listing content today; your Idira Technical Alliances contact publishes it to both destinations. Documentation assets are named exactly `Configuration guide` and supplied as a URL rather than a file (see `marketplace-standards.md` §5).

**What Idira does:** publishes the listing, and — for joint go-to-market — works with you on a solution brief covering the joint value and deployment topology, plus announcement and enablement activity.

---

## 8. After you are live

The journey does not end at listing. Two standing obligations transfer to you once your integration is published:

| Obligation | What it means |
|:---|:---|
| **Yearly recertification** | Re-test against the current Idira release, review and adopt new functionality, address security scan findings, and refresh your documentation. Your certification checklist has a recertification section listing exactly what is re-reviewed |
| **Ongoing support** | You support your own integration for customers running it. Report a defect or enhancement request in the Idira product side of the integration to cybr-bizdevtech@paloaltonetworks.com |

Adoption of your listing — views, downloads, and active customer usage — is tracked and reviewed. A listing with no customer usage for 90 days is flagged for review, so the go-to-market activity in stage 5 is worth taking seriously rather than treating listing as the finish line.

---

## 9. Where this path is still being defined

Two parts of the journey are genuinely in flight. Stated here rather than papered over, so you are not caught out.

**The Marketplace submission mechanics may change.** The listing *standards* in [`marketplace-standards.md`](marketplace-standards.md) are settled, and the submission route is the one stated in §7 above — email your listing content to cybr-bizdevtech@paloaltonetworks.com and your Idira Technical Alliances contact publishes it. If that route changes, your Idira Technical Alliances contact will tell you before your listing goes live. Nothing about what your listing must contain depends on it, so there is nothing here for you to track.

**PSM connection components have no matching form option.** If you are packaging a connection component so Idira Privileged Session Manager can broker a session into your web application, no request-form option describes it. Select the option closest to your product's category and state clearly in the description that this is a PSM web connection component. Do not select an Audit Service option — a connection component is browser automation, not an audit integration, and the mismatch causes a reclassification cycle. See [`decision-guide.md`](decision-guide.md) §4.

---

## 10. Every file in this repository, and when you need it

| Stage | File | Read it when |
|:--|:---|:---|
| 1 | [`decision-guide.md`](decision-guide.md) | Before you fill in the request form — always |
| 1 | Workflow decision guide (Discovery, EPM, Secrets Management, Workload Identity) | After the top-level guide routes you to a multi-path workflow — or, for Workload Identity, to confirm the single-kit workflow is the right one |
| 1–3 | [`index.md`](index.md) | To find your kit, and for the telemetry and demonstration requirements that apply to everything |
| 3 | `{workflow}/{integration}/development-guide.md` | Throughout the build |
| 3 | [`telemetry-reference.md`](telemetry-reference.md) | Once, when you implement the telemetry header — it carries the `IntegrationType` value for your kit, reference code, and test vectors |
| 1–5 | [`naming-crosswalk.md`](naming-crosswalk.md) | Any time a product name in your source material does not match the one used here |
| 3–4 | `{workflow}/{integration}/certification-checklist.md` | **During** the build, and again at submission |
| 5 | [`marketplace-standards.md`](marketplace-standards.md) | Before you write listing content |
| 1–5 | [`AGENTS.md`](AGENTS.md) | If you are driving this build with an AI coding agent — point the agent at it first |

Questions at any stage: **cybr-bizdevtech@paloaltonetworks.com**

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-19 | **[Added]** v1.8 — Stage 2 states that environment credentials are never published in these docs; if you need them, email cybr-bizdevtech@paloaltonetworks.com | Idira Technical Alliances |
| 2026-10-05 | **[Added]** v1.7 — Three rows for the new Workload Identity workflow, whose kit establishes a workload's identity rather than consuming one. §3.1 gains a decision-guide row, and the note beneath it is amended: that workflow has a single kit and still has a decision guide, which breaks the pattern every other row sets, so the note now says why — with one kit there is nothing to choose between, and the guide instead tests whether the integration belongs in the workflow at all rather than in Secrets Management or Discovery. §4's environment row records provisioning as confirmed per build with the partner's Business Development representative, because Secure Workload Access ships as part of Secrets Manager SaaS and the tenant a partner needs is not the same for every attestation platform. §10's read-order row for workflow decision guides now lists Workload Identity alongside the three multi-path workflows, with the same qualification. No stage, gate or graded requirement changed | Idira Technical Alliances |
| 2026-10-05 | **[Fixed]** v1.6 — The stage-4 demonstration row read "Mandatory" with no qualification, which contradicted [`security-baseline-reference.md`](security-baseline-reference.md) § 3 and [`AGENTS.md`](../AGENTS.md) § 6 — both of which record the demonstration as highly recommended and non-blocking, and both of which name this disagreement. Because this file is read first and is normative, a partner or agent starting here met the stricter claim and never reached the policy. The row now points to an expanded note stating how the demonstration is weighed, which authority governs, and what to do when it is the one deliverable a partner cannot produce. The guidance to deliver one is unchanged and strengthened — the demonstration is still expected and still the fastest route through review. **No checklist was changed:** the checklists continue to grade it as required, and reconciling them with the policy is a certification-programme decision, not an authoring one | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v1.5 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-09-30 | **[Updated]** v1.4 — §5's telemetry row now routes to the new [`telemetry-reference.md`](telemetry-reference.md) instead of a summary table in [`index.md`](index.md). The header is a graded, fully deterministic requirement that no kit demonstrated with a worked example, so partners were implementing it from a paragraph; the reference carries the transform, the `IntegrationType` value assigned to each kit, working code, and test vectors. §10 adds rows for that file and for the new root [`AGENTS.md`](AGENTS.md) manifest | Idira Technical Alliances |
| 2026-09-28 | **[Fixed]** v1.3 — §9's Marketplace note is rewritten around what is settled rather than what is in flight. What the partner needs is unchanged and unconditional: the listing standards are settled, the submission route is email via their Idira Technical Alliances contact, and that contact tells them if the route changes. §7's destination table drops an in-product navigation path that is not the partner's surface and was not verified against the shipped UI. Matches the same change in [`marketplace-standards.md`](marketplace-standards.md) v1.5 | Idira Technical Alliances |
| 2026-09-17 | **[Fixed]** v1.2 — §4's API-role example named a role that has since been retired, so a partner following it would provision the wrong role and hit `403`; it now names the current **Machines External Data Contributor** role and warns that an assignment made under an earlier name must be replaced, not supplemented. §5 and §10 now route to the new [`naming-crosswalk.md`](naming-crosswalk.md), which resolves the current / CyberArk / legacy product names in one place — partner engineering teams were rediscovering that mapping mid-build and rewriting their own documentation unassisted | Idira Technical Alliances |
| 2026-08-14 | **[Fixed]** v1.1 — §7 now states *how* listing content is submitted, not only what it must contain; previously the stage named no destination. §9's Marketplace-mechanics note no longer routes the reader to `marketplace-standards.md` for an answer that file did not carry (fixed in v1.2 of that file), and the in-flight work is scoped to the in-product contribution flow. Both certification checklists this document's stage 4 depends on — Audit Service SIEM and EPM Ticketing / JIT — are now published, so every kit path referenced here has graded criteria available from day one as §1 promises | Idira Technical Alliances |
| 2026-08-11 | **[Added]** Initial version — the five-stage partner journey as one document, above the per-kit guides. Consolidates the path that was previously only inferable from the decision guide, the kit index, and each kit's own checklist: request and approval, environment per integration type, the three cross-cutting build requirements, the mandatory demonstration and remediation loop, both listing destinations, and post-listing recertification and support obligations. Records the two in-flight parts of the path (native Marketplace submission mechanics, PSM form-option gap) rather than omitting them | Idira Technical Alliances |
