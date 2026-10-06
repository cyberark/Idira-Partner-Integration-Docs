# Contributing

## For technology partners

These development kits are maintained by the Idira Technical Alliances team. If you find an error,
have a question about a kit, or want to propose a new integration:

- **Open an issue** in this repository, or
- **Email** `cybr-bizdevtech@paloaltonetworks.com`

Issues are the preferred route for anything about the content itself — a contradiction between a
guide and its checklist, a field whose type or permitted values are not stated, a broken link, a
requirement you cannot act on. Those are defects, and reporting one helps every partner after you.
Email is better for anything specific to your integration, your tenant, or your certification
timeline.

Please **do not open pull requests.** Every requirement in this repository is a certification gate,
so changing the wording of one changes what partners are graded against — that review happens on our
side and cannot be delegated to a patch. Open an issue describing what is wrong and we will make the
change.

### What to expect

Issues are triaged by the Idira Technical Alliances team. We do not publish a response-time
commitment for this repository. If an issue is blocking your build, email the address above and say
so — that puts it in front of your Idira Technical Alliances contact directly.

## For the Idira Technical Alliances team

**This repository is the source of truth for the dev-kit corpus.** Author and edit the kits here,
directly on `master`. There is no upstream copy to edit first and no sync step — a change merged
here is the published change.

### Before you commit

Two guards run in CI on every push and pull request, and both must pass:

1. **Publish guard** — scans `docs/` for content that must not be published: internal planning and
   roadmap material, internal tooling or repository names, individual employees named as decision
   authorities, references to internal systems. See **What must never appear** below.
2. **Link integrity** — every relative path resolves and every `#anchor` matches a real heading.
   A broken link ships silently, because the page still loads.

Run the link check locally before pushing:

```
python3 .github/scripts/link-check.py --rules R8,R9 .
```

### What must never appear in `docs/`

This repository is public. Everything in `docs/` is read by partners, their legal teams, and their
AI tooling.

- **Internal planning and roadmap.** Unreleased features, rollout phases and dates, internal team
  attribution for in-flight work. State what is settled; say nothing about what is in flight.
- **Individual employees named as decision authorities.** A requirement is sourced to the
  certification programme or to an Idira document, never to a person. Attribute to *Idira Technical
  Alliances*.
- **Internal systems, paths, and tooling names** — internal repository names, internal hostnames,
  internal document paths, internal task keys, the names of internal review or validation tools.
- **Customer names**, in any form, including in examples.
- **Unverified documentation URLs.** A deep link is published only once it has been fetched and
  confirmed to resolve. Where no verified URL exists, name the authority and leave the link out.

**A redaction described in a change log is not a redaction.** When you remove something from this
class, the change-log entry records *what the document now says* — not what was taken out and why.
Writing "no longer describes the unreleased X" republishes X.

### Change-log and versioning convention

Every content change bumps the document's `**Version:**`, updates `**Last Updated:**`, and appends a
change-log row prefixed `**[Added]**`, `**[Updated]**`, `**[Fixed]**`, `**[Removed]**`, or
`**[Restructured]**`, authored as *Idira Technical Alliances*. The change log is partner-facing
documentation in its own right: write it for a partner deciding whether the change affects their
build.
