# Idira Marketplace Integration Contribution Standards

**Type:** Reference Guide  
**Version:** 1.10  
**Author:** Idira Technical Alliances  
**Last Updated:** 2026-10-14  
**Source:** Idira_Marketplace_Standards_Guide.pdf

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this file.
Read this block first before answering any questions about Marketplace listings.

DOCUMENT TYPE: Listing standards reference. It governs the LISTING, not the integration — there is no
  endpoint, no auth and no code here, and nothing in this file changes how an integration is built.
POSITION: the LAST node in the routing chain. It applies after the integration is built and certified.
  Do not front-load it; a partner still choosing a kit does not need it yet.
ANSWERS: "What must the Marketplace listing say, and how is it submitted?"
CONTACT / SUBMISSION: cybr-bizdevtech@paloaltonetworks.com

SUBMISSION IS EMAIL, AND THERE IS NO PARTNER-FACING UPLOAD PORTAL. Send the listing content to
cybr-bizdevtech@paloaltonetworks.com with the tracking reference in the subject line; the Idira Technical Alliances contact
publishes it. Do NOT invent a portal, a form, or a self-service contribution flow, and do NOT tell a
partner to wait for a new process — the header note is explicit that nothing here is provisional and
that a route change would affect how content reaches Idira, never what it must say. The end-to-end
sequence lives in journey.md §7, not in this file.

THREE DESTINATIONS, ONE UNCHANGED SET OF STANDARDS. A certified integration is listed on the Idira
Marketplace (the in-product catalog inside the Identity Security Platform), the legacy CyberArk
Marketplace which remains active in parallel, and the public Palo Alto Networks technology partner
directory. NAME THE DESTINATION rather than saying "the Marketplace" — they are distinct surfaces with
different lifespans. The standards in this document apply to all three identically.

THE §3 USE CASES ARE MARKETPLACE BUCKETS, NOT DEV KITS, AND THE TWO SETS DO NOT MAP ONE-TO-ONE. This is
the most common mistake made from this file. There are ten listing buckets and seventeen kits:
- Some buckets have NO dev kit at all — "Enable SSO or MFA for Users" is a listing category with no
  corresponding kit in this repository. "Sync Identities Between Systems (Identity Governance)" is
  the bucket for `identity-access-management/identity-governance`, but that kit is Preview, so
  listing is not open on it yet.
- Some buckets cover FOUR kits each — all four Secrets Management kits list under "Manage Secrets for
  Apps or Services"; all four Discovery kits list under "Discover Assets or Accounts".
- AND THE INVERSE: one KIT has no bucket. `workload-identity/swa-federation` has no §3 use case —
  establishing workload identity is not any of the ten. Do NOT file it under "Other / Not Sure" and do
  NOT map it to "Manage Secrets for Apps or Services", which describes the opposite operation. Route
  the bucket question to the Idira Technical Alliances contact. The kit is Preview, so listing is not
  open on it yet and this is not blocking a partner today.
Pick the bucket by the CUSTOMER-FACING use case, not by the kit directory path. And note the gap: this
file does not publish a kit-to-bucket mapping, so genuinely ambiguous cases — `epm/audit-events`, which
reads as either "Security Analytics" or "Manage Endpoint Privileges" — must be confirmed with the Idira Technical Alliances contact
rather than guessed. Do not assert a mapping this file does not state.

TITLE FORMAT IS EXACT AND ENFORCED AT REVIEW: `<Vendor name> <Vendor product> <Use Case/solution>`.
Manually checked today, to be automated later. The tooltip must match the same format.

SHORT DESCRIPTIONS ARE SUPPLIED, NOT AUTHORED. If §3 gives an example for the use case, use that string
and substitute the bracketed placeholder — `[company name]`, `[partner name]`, `[Company Name]` — with
the partner's name. Do not write a fresh description when an example exists, and never ship a listing
with the bracket still in it. Only where no example exists is a new description written, and then in no
more than 10 words.

`Idira Solution` AND `Idira Products` ARE FIXED VALUES, NOT FREE TEXT. Take them verbatim from the §3
entry for the chosen use case. §6 is the full allowed product vocabulary — a product not on that list
cannot be named on a listing.

CAUTION ON §6 AS A NAMING AUTHORITY: it is the Marketplace picker list, and it carries entries whose
phrasing the kits' own prose rules would not use. For product naming in prose, defer to
naming-crosswalk.md, which also explains why documented API names, role and persona names, and
hostnames are deliberately NOT rebranded.

THE DOCUMENTATION ASSET NAME IS ONE EXACT STRING (§5, decided 2026-08-11): `Configuration guide` —
sentence case, no per-integration variation, no alternatives. It replaces both "Technical Documentation"
and the earlier default "Integration Guide" label, and it applies to every new integration and every
change to an existing one. The asset TYPE is an HTML LINK — a URL to the guide, NOT an uploaded file.
R&D has been asked to hardcode the name so it cannot be typed freehand; until that ships it is entered
by hand, exactly as written. "Solution Brief" is UNCHANGED — this rename covers the documentation asset
only, so do not apply it to the brief. Joint Solution Brief standards are in jsb-standards.md.

THE LISTING OVERVIEW IS THREE HEADINGS, SOLUTION HIGHLIGHTS ONLY (§4): Business Problem, Solution, Key
Features. Do not add sections, and do not paste development-guide material into it — the listing is
marketing copy for a customer browsing a catalog, not technical documentation.

KNOWN GAP — DO NOT FILL IT IN FROM MEMORY: §5 states that a documentation template is "ongoing for each
development kit" and names what it must include (configuration steps, diagrams, prerequisites,
validation tests), but the template itself is not in this file or elsewhere in this repository. If asked
for it, say it is not published and route the request to the Idira Technical Alliances contact.

SIBLING TOP-LEVEL FILES:
- AGENTS.md — the machine entry point: read order, file graph, and hard limits
- journey.md — the five stages; §7 owns the submission sequence this file only summarises
- index.md — the catalogue of all 17 kits
- jsb-standards.md — Joint Solution Brief standards, a separate asset from the Configuration guide
- naming-crosswalk.md — authoritative product naming, including what is deliberately not rebranded

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> This document defines the standards for contributing an integration listing to the Idira Marketplace. It covers title format, short description guidelines, per-use-case standards, and the overview structure partners must follow.

> **Where your listing appears.** A certified integration is listed on the Idira Marketplace, the in-product catalog customers browse inside the Idira Identity Security Platform. The legacy CyberArk Marketplace remains active in parallel, and your integration is also listed in the public Palo Alto Networks technology partner directory. **The listing standards in this document apply to all of them and are unchanged.**
>
> **How to submit, today.** Do not wait for a new process and do not submit through a portal. Send your listing content to **cybr-bizdevtech@paloaltonetworks.com** with your tracking reference in the subject line, and your Idira Technical Alliances contact publishes it. This is the current path for both destinations and it is the same path described in [The Partner Integration Journey](journey.md) §7 — that document, not this one, is where the end-to-end sequence lives.
>
> **Nothing below is provisional.** If the submission route ever changes, it changes *how* content reaches us, not *what* the content must say. Your Idira Technical Alliances contact will tell you before your listing goes live; there is nothing here for you to track.

---

## 1. Title Format

```
<Vendor name> <Vendor product> <Use Case/solution>
```

**Example:** `Palo Alto Networks Idira® Single-Sign On`

**Guideline:** Initially enforce manually during review; automate later. Include tooltip matching format.

---

## 2. Short Description Guidelines

Use the provided example for each use case (see Section 3). If no example is available, use no more than 10 words.

---

## 3. Standards Per Use Case

### Enable SSO or MFA for Users (SSO and MFA)

**Short Description:**
- SSO: `Provide secure access with Single Sign-On and MFA for [company name]`
- MFA: `Provide secure access with MFA using [company name]`

**Idira Solution:** Identity Governance  
**Idira Products:** Palo Alto Networks Idira® Privileged Access Manager Self-Hosted, Idira Privileged Access Manager SaaS, Idira Identity, Idira Identity Flows, Idira Identity Security Platform

---

### Sync Identities Between Systems (Identity Governance)

**Short Description:** `Ensure consistent identity governance across platforms, integrated by [partner name].`

**Idira Solution:** Identity Access Management  
**Idira Products:** Idira Identity

---

### Rotate Credentials in a Vault or Cloud (CPM or SRS)

**Short Description:** `Manage [partner name] privileged accounts`

**Idira Solution:** Credential Rotation  
**Idira Products:** Central Policy Manager (CPM), Secrets Rotation Service (SRS)

---

### Manage Secrets for Apps or Services (Secrets Manager)

**Short Description:** `Securely retrieve privileged credential required by [partner name]`

**Idira Solution:** Secrets Management  
**Idira Products:** Idira Secrets Manager SaaS, Idira Secrets Manager Self-Hosted, Credential Provider (CP), Central Credential Provider (CCP)

---

### Security Analytics (SIEM Integration)

**Short Description:** `Feed Idira Audit logs into [partner name] for security analytics.`

**Idira Solution:** Security Information & Event Management Integration  
**Idira Products:** Idira Identity Security Platform, Audit Service

---

### Discover Assets or Accounts (Discovery user/cert/machine)

**Short Description:** `Discover identities with [partner name].`

**Idira Solution:** Discovery & Inventory  
**Idira Products:** Idira Identity, Idira Privileged Access Manager SaaS

---

### Manage Endpoint Privileges

**Short Description:** `Enforce least privilege on endpoints with [partner name].`

**Idira Solution:** Endpoint Privilege Management  
**Idira Products:** Idira Endpoint Privilege Manager

---

### Broker a Privileged Session into a Web Application (PSM Connection Component)

**Short Description:** `Broker and record privileged sessions into [partner name].`

**Idira Solution:** Privileged Session Management  
**Idira Products:** Privileged Session Manager (PSM), Idira Privileged Access Manager Self-Hosted

---

### Trigger Identity Response Actions (XDR / SIEM / SOAR)

**Short Description:** `Automate identity response in Idira from [partner name].`

**Idira Solution:** Threat Detection & Response  
**Idira Products:** Idira Identity Security Platform, Idira Privileged Access Manager SaaS, Idira Identity, Idira Secure Infrastructure Access, Idira Endpoint Privilege Manager

---

### Other / Not Sure

**Short Description:** `Explore additional Idira security solutions with [Company Name] to meet unique needs.`

**Idira Solution:** Found on Idira Marketplace  
**Idira Products:** See full product list below

---

## 4. Overview Structure

Solution highlights only. Use this structure for the Marketplace listing overview:

**Business Problem:**
[Describe the business challenge addressed by the integration]

**Solution:**
[Explain how the integration solves the problem]

**Key Features:**
[List main features and benefits]

---

## 5. Documentation Template

Ongoing for each development kit. Include configuration steps, diagrams, prerequisites, and validation tests.

> **Asset naming — decided 2026-08-11.** Every documentation asset on a listing is named **`Configuration guide`**. Exact string, sentence case, no per-integration variation. Reviewed with the technical writers and agreed in preference to "Technical Documentation"; it also replaces the default "Integration Guide" label proposed 2026-08-10. Applies to every new integration and every change to an existing one.
>
> The asset type is an **HTML link** — a URL to the guide, not an uploaded file. R&D has been asked to hardcode the name in the contribution flow so it cannot be typed freehand (`Marketplace/2026-08-11_configuration-guide-asset-type-requirement.md`); until that ships, enter it by hand exactly as written.
>
> **"Solution Brief" is unchanged** — this renames the documentation asset only.

---

## 6. List of All Available Products

- Central Credential Provider
- Central Policy Manager (CPM)
- Conjur Open Source
- Credential Provider (CP)
- Discovery
- Idira Endpoint Privilege Manager
- Password Vault Web Access (PVWA)
- Privileged Session Manager (PSM)
- Privileged Session Manager for Unix (PSMP)
- Privileged Threat Analytics (PTA)
- Idira Vendor Privileged Access Manager
- Idira Secrets Manager, Self-Hosted
- Idira Identity
- Application Server Credential Provider (ASCP)
- Idira Secrets Manager, SaaS
- Idira Secure Infrastructure Access
- Idira Secrets Hub
- Idira Secure Web Sessions
- Idira Secure Cloud Access
- Secure Browser — **discontinued 2026-09-30, not available for new listings.** Service
  access is disabled. Do not name this product on a new or updated listing; if an existing
  listing names it, raise it with your Idira Technical Alliances contact rather than editing it yourself.
- Idira Workload Identity Manager
- Idira Code Sign Manager
- Idira SSH Manager for Machines
- Idira Workforce Password Management
- Idira Privileged Access Manager Self-Hosted
- Idira Privileged Access Manager SaaS
- Idira Identity Flows
- Audit Service
- Idira Identity Security Platform
- Threat Detection & Response (TDR)
- Secrets Rotation Service (SRS)

---

## Change Log

| Date | Change | Author |
|:---|:---|:---|
| 2026-10-14 | **[Updated]** v1.10 — The AI context block said "Sync Identities Between Systems" has no dev kit. The new `identity-access-management/identity-governance` kit is that bucket's integration, so the block now names it and notes it is Preview, leaving "Enable SSO or MFA for Users" as the one bucket with no kit. Kit counts moved from sixteen to seventeen. No standard, bucket or short description changed. | Idira Technical Alliances |
| 2026-10-05 | **[Fixed]** v1.9 — The AI context block stated the corpus as fifteen kits and `index.md` as "the catalogue of all 15 kits". Both went stale when `workload-identity/swa-federation` was added in `3a6469c`, so this file — the last node in the routing chain and the one an agent reads at listing time — was contradicting the six files above it. Counts corrected to sixteen. Also added the case the §3 bucket-mapping note never covered: it enumerated buckets with no kit, but not the inverse, and there is now one — workload identity is not any of the ten use cases. The note says to route the bucket question to the Idira Technical Alliances contact rather than file under *Other / Not Sure* or map it to "Manage Secrets for Apps or Services", which describes the opposite operation, and records that the kit is Preview so listing is not open on it and no partner is blocked today. This mirrors what that kit's own certification checklist already tells the partner, which until now this file did not corroborate. No standard, string, bucket, product entry or submission route changed | Idira Technical Alliances |
| 2026-10-02 | **[Fixed]** v1.8 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. | Idira Technical Alliances |
| 2026-10-02 | **[Updated]** v1.7 — Marked **Secure Browser** as discontinued in the §6 allowed-product vocabulary, following its permanent discontinuation on 2026-09-30 (service access disabled; migration to alternative secure access solutions). §6 is the enforced vocabulary for the `Idira Products` listing field — the AI context block states that a product not on that list cannot be named on a listing — so an unannotated entry authorised a partner to list against a product that no longer exists. The line is annotated rather than deleted on purpose: §6 is described as the Marketplace picker list, and whether the live picker has dropped the entry is unverified, so annotation is correct whether it has or not. No other product entry, standard, string or submission route was changed, and no listing already naming Secure Browser was edited — those route to the Idira Technical Alliances contact. Surfaced by the `/review-dev-kits` weekly run | Idira Technical Alliances |
| 2026-09-30 | **[Added]** v1.6 — AI context block, completing the agent-readable layer across the dev-kit corpus. It places this file as the last node in the routing chain, applying after certification rather than during a build, and leads with the two facts an agent most often gets wrong from it. First, submission is email to `cybr-bizdevtech@paloaltonetworks.com` with a tracking reference and there is no partner-facing upload portal — an agent must not invent one or tell a partner to wait for a self-service flow. Second, the §3 use cases are Marketplace buckets rather than dev kits and the two sets do not map one-to-one: ten buckets against fifteen kits, two buckets with no kit at all, and two buckets each covering four kits. Where a kit does not map cleanly to a bucket, `epm/audit-events` is the genuinely ambiguous case — route it to your Idira Technical Alliances contact rather than guess. The block also carries the three named destinations and the instruction to name the destination rather than saying "the Marketplace", the exact title format, the rule that short descriptions are supplied and substituted rather than authored, that `Idira Solution` and `Idira Products` are fixed values with §6 as the allowed vocabulary but not a prose-naming authority, the exact `Configuration guide` asset name as an HTML link with "Solution Brief" explicitly out of scope of that rename, and the three-heading overview structure. §5 describes a per-kit documentation template that is not published in this repository — ask your Idira Technical Alliances contact for it. No standard, string or submission route was changed | Idira Technical Alliances |
| 2026-09-28 | **[Fixed]** v1.5 — The header notes are rewritten around what is settled rather than what is in flight, the same change made in [`journey.md`](journey.md) §9 at v1.3. The in-product catalog is described as the live surface it is, and an in-product navigation path that is not the partner's surface is removed. The two parallel destinations, the email submission route, and the "nothing below is provisional" assurance are unchanged | Idira Technical Alliances |
| 2026-09-24 | **[Fixed]** v1.4 — Added Credential Provider (CP) and Central Credential Provider (CCP) to the Secrets Manager use-case product list. They previously appeared only in the §6 catch-all, so a certified CP or CCP integration had no listing bucket to map to | Idira Technical Alliances |
| 2026-09-17 | **[Fixed]** v1.3 — Renamed Privilege Cloud to Idira Privileged Access Manager SaaS in prose, per the current product naming. Documented API names, role and persona names, and hostnames are deliberately unchanged and are explained in [`naming-crosswalk.md`](naming-crosswalk.md) §3 | Idira Technical Alliances |
| 2026-08-14 | **[Fixed]** v1.1 → v1.2 — the header note previously said the submission process "will be documented in this file" and told readers to check back here, which meant the one question a partner has at listing time had no answer anywhere. Replaced with the current route (email `cybr-bizdevtech@paloaltonetworks.com`; there is no partner-facing upload portal), both listing destinations named, and the in-flight product work scoped to *how* content reaches us rather than *what* it must contain. The end-to-end sequence now points to [The Partner Integration Journey](journey.md) §7 | Idira Technical Alliances |
| 2026-08-12 | **[Updated]** v1.1 — environment contradictions corrected during a kit-wide QA pass | Idira Technical Alliances |
| 2026-08-11 | **[Added]** §5 asset-naming standard — every documentation asset on a listing is named `Configuration guide`, supplied as an HTML link. Reviewed with the technical writers | Idira Technical Alliances |
