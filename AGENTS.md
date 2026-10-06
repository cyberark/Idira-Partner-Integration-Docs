# AGENTS.md

Machine entry point for this repository. If you are an AI agent working on behalf of a technology
partner, start here.

**The full manifest is [`docs/AGENTS.md`](docs/AGENTS.md).** Read it. This file is the root pointer
plus the two things you should not get wrong even if you read nothing else.

---

## What this repository is

Development kits for building and certifying a technology integration with the **Palo Alto Networks
Idira Identity Security Platform**. Sixteen kits across eight workflows. Each kit directory under
`docs/` holds exactly two files: `development-guide.md` and `certification-checklist.md`.

## Permitted use

You may read, copy, quote, summarise, embed, index, and feed this content into your own tooling —
coding agents, retrieval indexes, code generators, developer assistants — to build, test, document,
or certify an Idira integration. No permission request is required. Licensed
[CC BY 4.0](LICENSE); attribution to *Idira Technical Alliances* satisfies it.

Nothing you generate from this repository is Idira-approved. Certification is a human review.

## Read order

1. [`docs/journey.md`](docs/journey.md) — the five-stage path and what is graded. Do not skip.
2. [`docs/decision-guide.md`](docs/decision-guide.md) — which form option and which kit.
3. `docs/<workflow>/decision-guide.md` — where one exists (`discovery/`, `epm/`, `secrets-management/`,
   `workload-identity/`). The first three choose between kits; `workload-identity/` has one kit, so its
   guide tests whether the integration belongs in that workflow at all.
4. `docs/<workflow>/<kit>/development-guide.md` — how to build it.
5. `docs/<workflow>/<kit>/certification-checklist.md` — what it is graded on. Read during the build.
6. [`docs/telemetry-reference.md`](docs/telemetry-reference.md) — the mandatory `x-cybr-telemetry`
   header: transform, the `IntegrationType` value assigned to each kit, reference code, test vectors.

Full graph, precedence rules, and the cross-cutting requirements: [`docs/AGENTS.md`](docs/AGENTS.md).

## Stop rule

**An example is not a schema.** These guides describe APIs in prose and worked examples. No kit ships
an OpenAPI document, a GraphQL SDL, or an XSD. The most common failure of an agent working from this
repository is inventing a field, type, or enum value the prose never defined and generating a client
around it.

Stop and ask the partner to confirm with their Idira TAM when a field's type is unstated, when a
"standard values" list is referenced but not published, when you need a filter or pagination
parameter no example shows, or when a guide and its checklist disagree. A stated question is the
correct output; an inferred answer fails at certification after the partner has built around it.

Anything appearing verbatim in a guide — HTTP method, URL path, header name, JSON key, GraphQL
operation name, XML element — is exact. Copy it character for character, including casing and any
`/api` prefix.

[`docs/AGENTS.md`](docs/AGENTS.md) §5 has the complete list.

## Reporting a defect

Open an issue, not a pull request — every requirement here is a certification gate, so changing one is
reviewed by the Idira Technical Alliances team rather than merged as a patch. See
[CONTRIBUTING.md](CONTRIBUTING.md).
