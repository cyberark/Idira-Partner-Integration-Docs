# Idira Partner Integration Development Kits

Development kits for building and certifying technology integrations with the **Idira Identity Security Platform** by Palo Alto Networks.

Each kit gives a technology partner everything needed to build an integration: the use case, the environment prerequisites, authentication, verified API operations with working request examples, integration patterns, error handling, and a certification checklist that defines what Idira reviews before listing the integration on the Idira Marketplace.

## Start here

- **[The Partner Integration Journey](docs/journey.md)** — read this first. The whole path in five stages, what you do, what we do, and what each gate expects. It tells you that the certification checklist is graded and that a working demonstration is mandatory while you can still act on both.
- **[Which Integration Do I Select?](docs/decision-guide.md)** — maps what you are building to the right option on the integration request form and the right kit
- **[Development Kits Index](docs/index.md)** — the catalog, once you know which kit you need
- **[Telemetry reference](docs/telemetry-reference.md)** — the one requirement every kit shares, with working code and test vectors
- **[Marketplace listing standards](docs/marketplace-standards.md)** — what certification requires

**Building with an AI coding agent?** Point it at **[AGENTS.md](AGENTS.md)** first. You are welcome to feed these kits into your own tooling — see [Using these kits with AI tooling](#using-these-kits-with-ai-tooling).

## Workflows

| Workflow | What you build |
|:---|:---|
| [Discovery](docs/discovery/) | Push discovered privileged accounts, AI agents, machine identities, or secrets into Idira |
| [Credential Rotation](docs/credential-rotation/) | A CPM plugin that rotates credentials for a target application |
| [Audit Service](docs/audit-service/) | Stream Idira identity and privileged-access audit events into your platform |
| [EPM](docs/epm/) | Endpoint audit events, JIT admin elevation via ticketing, or XDR/SOAR endpoint containment |
| [Identity Response](docs/identity-response/) | Trigger identity, session, credential, and access-policy response actions from an XDR/SIEM/SOAR platform — **Preview** |
| [Secrets Management](docs/secrets-management/) | Retrieve secrets from Idira instead of storing them locally |
| [PSM Connectors](docs/psm-connectors/) | A connection component so Idira Privileged Session Manager can broker and record a privileged session into your web application. Idira PAM Self-Hosted only |
| [Workload Identity](docs/workload-identity/) | SPIFFE identity for workloads your platform runs, routes, or hosts, so they authenticate to Idira with an attested SVID instead of a distributed secret — **Preview** |
| [Identity Access Management](docs/identity-access-management/identity-governance/certification-checklist.md) | Provision, reconcile, and certify identities and entitlements in Idira from your IGA platform — **Preview**, certification checklist only; the development guide is not yet published |

**Preview** means the kit is published for early review and is not yet a certifiable path: you can build against it, but its checklist is not a settled gate and we cannot promise a Marketplace listing on it. Talk to us before committing engineering time. Per-kit status is in the [Development Kits Index](docs/index.md).

## How to use these kits

1. Read [the journey](docs/journey.md) once, so you know what the five stages are and what is graded.
2. Use [Which Integration Do I Select?](docs/decision-guide.md) to pick the right form option and kit. If the workflow has its own Decision Guide, that narrows it further.
3. Follow the Development Guide. Every API call lists its method, URL, authentication, and request fields.
4. Implement the telemetry header from [the telemetry reference](docs/telemetry-reference.md), not from a summary table — the `IntegrationType` value is assigned per kit.
5. Work through the Certification Checklist **during** the build, not at submission. It is the document your integration is graded against.
6. Submit your integration request ([journey, Stage 1](docs/journey.md#32-submit-the-integration-request)). Your build environment is provisioned once the request is approved. Questions: `cybr-bizdevtech@paloaltonetworks.com`.

## Using these kits with AI tooling

You may read, copy, quote, summarise, embed, index, and feed the contents of this repository into your own tooling — coding agents, retrieval indexes, internal documentation, code generators, and developer assistants — to build, test, document, or certify an Idira integration. No permission request is needed. Attribution to *Palo Alto Networks, Inc.* satisfies the CC BY 4.0 licence.

Two things to know, both about correctness rather than permission:

- **Nothing generated from this repository is pre-approved.** Certification is a human review.
- **These guides are build guides, not API specifications.** No kit currently ships an OpenAPI document, GraphQL SDL, or XSD, and the worked examples do not fully determine every schema. Where a field's type or permitted values are not stated, an agent should ask rather than infer — [AGENTS.md](AGENTS.md) §5 lists the specific cases.

Found a contradiction between a guide and its checklist, or an undefined field? That is a defect worth reporting — open an issue.

## Sandbox and support

- **Build environment:** provisioned after your integration request is approved, and it depends on the kit — see [Stage 2 of the journey](docs/journey.md#4-stage-2--get-access-to-idira). Some kits use the C3 Integrations Platform — https://c3.cyberark.cloud
- **Contact:** `cybr-bizdevtech@paloaltonetworks.com`

## Contributing

These kits are maintained by the Idira Technical Alliances team. Partners: please open an issue or email the contact above rather than a pull request — every requirement here is a certification gate, so changes are reviewed on our side. Found a contradiction, a broken link, or an undefined field? That is a defect worth reporting. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Documentation in this repository is licensed under [CC BY 4.0](LICENSE). See the LICENSE file for details.
