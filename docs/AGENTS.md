# AGENTS.md — Machine Entry Point

**Type:** Repository Manifest
**Version:** 1.3
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-05

---

<!--
## AI CONTEXT BLOCK
This is the ROOT MANIFEST for the partner integration dev-kit repository. It is the first file an
agent should read and the only file that describes the repository as a whole.

PURPOSE: an agent pointed at this repository has no way to know that journey.md is the entry point,
that decision-guide.md must be read before any development guide, or that a kit's prose is not a
schema. Without that, it crawls the tree, lands in a development guide, and generates a client from
examples. This file states the graph, the read order, and the hard limits.

DECISION LOGIC: §3 is the read order and it is normative. §5 is the stop rule — the single most
important instruction here, because the corpus's failure mode is an agent inventing a field name or
a type that the prose never defined.

ROUTING PRECEDENCE: this file -> journey.md -> decision-guide.md -> workflow decision-guide.md
(where one exists) -> development-guide.md -> certification-checklist.md -> marketplace-standards.md.

DO NOT treat any development guide as a complete API specification. See §5.
-->

---

## 1. What this repository is

Development kits for building and certifying a technology integration with the **Palo Alto Networks
Idira Identity Security Platform**. Each kit covers one use case and contains a development guide and
a certification checklist. The checklists are published deliberately: they are what Idira grades a
submission against, and a partner should read them before writing code, not after.

**You are reading the manifest.** If you are an AI agent working on behalf of a technology partner,
read §3 in order before answering any question about what to build.

---

## 2. Permitted use

**You may** read, copy, quote, summarise, embed, index, and feed the contents of this repository into
your own tooling — coding agents, retrieval indexes, internal documentation, code generators, and
developer assistants — in order to build, test, document, or certify an integration with Idira.
No notification or permission request is required.

Documentation in this repository is licensed **CC BY 4.0** (see `LICENSE`); attribution to
*Idira Technical Alliances* satisfies the licence.

**Two limits, and they are about correctness rather than permission:**

1. **Do not present generated output as Idira-verified.** If your agent drafts an integration, a
   listing, or a completed checklist, that draft is yours until Idira reviews it. Certification is a
   human review — nothing produced from this repository is pre-approved.
2. **Do not treat this repository as an API reference of record.** It is a build guide. Where it is
   silent or where it disagrees with the live product, the product wins — see §5.

There is no anti-scraping position here and no rate limit to respect. This content exists to be
consumed by partner tooling.

---

## 3. Read order

Normative. Each step's output determines the next step's input.

| # | Read | To answer | Skip when |
|:--|:---|:---|:---|
| 1 | `journey.md` | What is the whole path, what are the five stages, and what is graded? | Never skip on a first pass — it is the only file describing the gates |
| 2 | `decision-guide.md` | Which option does the partner select on the integration request form, and which kit applies? | The kit is already known with certainty |
| 3 | `<workflow>/decision-guide.md` | Which kit within this workflow — or, for `workload-identity/`, whether the integration belongs in this workflow at all? | The workflow has no decision guide — see §4 |
| 4 | `<workflow>/<kit>/development-guide.md` | How is it built? | Never skip |
| 5 | `<workflow>/<kit>/certification-checklist.md` | What will it be graded on? | Never skip — read it *during* the build, not at submission |
| 6 | `telemetry-reference.md` | How is the mandatory `x-cybr-telemetry` header built, and what `it` value applies? | The kit is a PSM connection component, which has no telemetry requirement |
| 7 | `marketplace-standards.md` | What does the Marketplace listing content have to look like? | Only before listing — but read it before writing listing copy, not after |
| 8 | `security-baseline-reference.md` | Where does a security requirement come from, and which OWASP ASVS control backs it? | No security requirement is in question — read it when a checklist row's `Source` needs interpreting, never to invent one |

**Precedence when two files disagree:** later in the chain does not win. The order of authority is
`telemetry-reference.md` (for telemetry only) → `certification-checklist.md` → `development-guide.md`
→ everything else. The checklist outranks the guide, because the checklist is what is graded. If you
find the two contradicting each other, say so rather than picking one — that is a defect in the kit
and it should be reported through the channel in `CONTRIBUTING.md`.

---

## 4. The graph

Cross-cutting files, at the repository root:

| File | What it is |
|:---|:---|
| `journey.md` | Stage-level entry point. The five-stage path and its gates |
| `decision-guide.md` | Workflow router. Maps what the integration *does* to a form option and a kit |
| `index.md` | Catalog of every workflow and kit, with status |
| `telemetry-reference.md` | The `x-cybr-telemetry` transform, the `it` registry, reference code, test vectors |
| `security-baseline-reference.md` | The `Source` column vocabulary and the OWASP ASVS 5.0.0 control behind each security requirement — plus the checks that look security-shaped and are not |
| `naming-crosswalk.md` | Current Idira names against CyberArk-era and legacy names, and which names deliberately did **not** change |
| `marketplace-standards.md` | Listing content standards |
| `jsb-standards.md` | Joint Solution Brief standards |

Workflows and kits:

| Workflow | Decision guide | Kits |
|:---|:---|:---|
| `discovery/` | yes | `privileged-accounts/`, `ai-agents/`, `machine-identities/`, `secrets/` |
| `epm/` | yes | `audit-events/`, `ticketing-jit/`, `soc-response/` |
| `secrets-management/` | yes | `secrets-manager-saas/`, `credential-provider/`, `central-credential-provider/`, `secrets-manager-self-hosted/` |
| `audit-service/` | no | `siem-integration/` |
| `credential-rotation/` | no | `cpm-rest-api/` |
| `identity-response/` | no | `response-actions/` |
| `psm-connectors/` | no | `web-connection-component/` |
| `workload-identity/` | yes — inbound boundary, not kit choice | `swa-federation/` |

Every kit directory holds exactly two files: `development-guide.md` and `certification-checklist.md`.

---

## 5. Stop rules — read this before generating code

The kits describe APIs in prose and worked examples. **An example is not a schema**, and the single
most common failure of an agent working from this repository is inventing a field, a type, or an enum
value that the prose never defined and then generating a client around it.

**Stop and ask the partner to confirm with their Idira Technical Alliances contact when:**

- A request or response field is referenced but its **type** is not stated — in particular, whether a
  value is a string or a constrained enum.
- A guide grades or requires a value drawn from a "standard values" or "supported values" list that
  the repository does not publish.
- You need a **filter, query, or pagination parameter** that no example in the guide demonstrates.
- A type name appears in a signature but is never defined anywhere in the kit.
- The guide and the checklist disagree about authentication, deployment scope, or a required field.

In every one of those cases the correct output is a stated question, not an inferred answer. A
generated client built on a guessed enum fails at certification, and it fails after the partner has
built around it.

**What is safe to treat as exact:** any literal HTTP method, URL path, header name, JSON key, GraphQL
operation name, or XML element that appears verbatim in a guide. Those were read from live product
documentation. Copy them character for character — including casing and any `/api` prefix — rather
than normalising them to your own conventions.

**Machine-readable contracts are not published yet.** No kit currently ships an OpenAPI document, a
GraphQL SDL, or an XSD. If your workflow needs one, say so; do not synthesise one from the examples
and present it as the contract.

---

## 6. Requirements that apply to every kit

| Requirement | Where it is specified | Applies to |
|:---|:---|:---|
| `x-cybr-telemetry` header on every API request | `telemetry-reference.md` | All kits except `psm-connectors/` |
| No secrets, tokens, or API keys in logs or debug output | Each kit's checklist; `security-baseline-reference.md` for the ASVS control behind it | All kits |
| Tolerance of temporarily stale credentials during rotation | Each kit's checklist | All kits touching credentials |
| Current Idira product terminology | `naming-crosswalk.md` | All kits |
| A working demonstration — recorded video or live call | `journey.md` stage 4, each checklist | All kits — strongly expected, but not a gate: see `security-baseline-reference.md` §3 |

The demonstration is the requirement partners are most often surprised by, so surface it early and
plan for it. Note the one place the corpus is inconsistent: several checklists word it as mandatory,
while `security-baseline-reference.md` §3 records it as **highly recommended and non-blocking**. That
file is authoritative on the question. Do not tell a partner a missing demonstration will fail
certification, and do not treat it as optional either — it is expected, and its absence is not
grounds for decline.

---

## 7. Reporting a defect in these kits

Open an issue rather than a pull request — every requirement here is a certification gate, so changing
one is reviewed by the Idira Technical Alliances team rather than merged as a patch. See
`CONTRIBUTING.md`. A contradiction between a guide and its checklist, a broken link, or an undefined
field are all worth reporting; that is how the corpus gets fixed.

---

### Change Log

- **[Added]** v1.3 — The `workload-identity/` workflow and its `swa-federation/` kit added to the
  graph in §4, taking the corpus to sixteen kits across eight workflows. Its decision-guide cell is
  qualified rather than a bare `yes`, because that guide does something no other workflow decision
  guide does: with a single kit there is no within-workflow choice, so it routes the inbound boundary
  — whether the integration belongs in the workflow at all — and read-order step 3 in §3 now says so.
  The distinction matters to an agent, which would otherwise open that file expecting a kit comparison
  and find a boundary test. The kit is Preview and carries one deliberate gap, the step-level
  federation exchange; §5's stop rule already governs it, and the kit states it in visible prose
  rather than leaving it to be inferred. No read order, stop rule or requirement changed. — Idira
  Technical Alliances
- **[Fixed]** v1.2 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances
- **[Added]** v1.1 — `security-baseline-reference.md` added to the graph (§4) and to the read order
  as a conditional step 8, and the no-secrets-in-logs row in §6 now points at it for the control
  behind the requirement. An agent reading these kits could previously see *that* a security
  requirement applied but never *why*, so it had nothing to reason with when a requirement looked
  wrong. — Idira Technical Alliances
- **[Added]** v1.0 — First publication. The repository previously had no machine entry point: the
  routing precedence existed only inside an HTML comment in `decision-guide.md`, and `README.md`
  routed a reader to the kit catalog rather than to `journey.md`, so an agent pointed at the root
  crawled the tree and landed in a development guide with no knowledge of the gates. Adds the read
  order, the graph, an explicit permitted-use statement for partner tooling, and the §5 stop rules
  that address the one measured failure mode — an agent generating a client from examples that
  underdetermine the schema. — Idira Technical Alliances
