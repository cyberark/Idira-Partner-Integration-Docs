#!/usr/bin/env python3
"""Guide-to-checklist consistency check over the partner dev-kit corpus.

Every certification checklist grades a partner on requirements that are supposed to be
documented in its paired development guide. Where they are not, a partner (or a partner's
AI agent) is graded on something it cannot read. This script finds that class of defect
mechanically -- no model call, no network, no credentials.

Rules, in the order they appear in the report:

  R1  pairing            -- a kit directory must hold both a guide and a checklist
  R2  ungrounded gate    -- an identifier a checklist item grades on, absent from the guide
  R3  ungradeable gate   -- a checklist section that states a requirement but has nothing to tick
  R4  telemetry gap      -- checklist grades the telemetry header, guide never mentions telemetry
  R5  deployment scope   -- checklist certifies SaaS, guide's procedure is Self-Hosted-only
  R6  dead authority     -- a reference link that resolves to a bare docs portal, no path
  R7  level vocabulary   -- a requirement level outside Required / Recommended (note only)
  R8  broken cross-ref   -- an internal link pointing at a path the corpus does not hold
  R9  broken anchor      -- a link whose file resolves but whose #fragment matches no heading
  R10 unsourced gate     -- a gating item with an empty Source cell, once its table has the column

R2 is the core rule; R3-R6 are the specific classes the 2026-09-25 agent-consumability
walks found by hand, generalised to the whole corpus. R8 and R9 are the link rules and
run corpus-wide rather than per-kit -- see check_links() for why that distinction is the
whole point of R9 existing.

R10 is the authority rule, added 2026-10-01. R2 asks "can the partner find this
requirement in the guide?"; R10 asks "where did this requirement come from at all?" --
an API contract, a security framework control, or an internal decision. Those are
different questions: a requirement can be fully documented in the guide and still have no
basis anywhere outside this corpus, which is how 11 checklists came to read "A
demonstration is mandatory" three months after the certification programme settled that it
must never block certification. R10 is deliberately advisory and deliberately silent until a
checklist's table actually carries the column -- see the rule's own comment in check_kit().

Output is deterministic for a given corpus state -- no wall-clock time in the body -- so
two runs on the same tree diff clean.

Usage:
    python3 check.py [CORPUS]              # markdown report to stdout
    python3 check.py --json [CORPUS]       # machine-readable findings
    python3 check.py --quiet [CORPUS]      # summary table only

CORPUS defaults to ~/Projects/idira-partner-integration-docs. Exits 1 if any blocking
finding is present, 0 otherwise, so a future CI or pre-publish gate can branch on it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

DEFAULT_CORPUS = Path.home() / "Projects" / "idira-partner-integration-docs"

GUIDE_NAME = "development-guide.md"
CHECKLIST_NAME = "certification-checklist.md"

# Sections that talk about requirements without themselves being gradeable. R3 skips these.
META_SECTION = re.compile(
    r"overview|introduction|scope|submitting|resources|supporting documentation|"
    r"references|attestation instructions|change log|version history|revision",
    re.I,
)

# Identifiers too generic to be worth grading as "absent from the guide". They are still
# counted and reported separately, never silently dropped.
GENERIC_IDENTIFIERS = {
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS",
    "JSON", "XML", "CSV", "YAML", "HTML", "TLS", "SSL", "HTTP", "HTTPS",
    "Base64", "base64", "UTF-8", "URL", "URI", "API", "REST", "GraphQL",
    "Yes", "No", "N/A", "true", "false", "null",
    "Required", "Recommended", "Optional",
}

TELEMETRY_HEADER = "x-cybr-telemetry"
TELEMETRY_MENTION = re.compile(r"telemetry", re.I)

# A guide's own revision history is not guidance, and the grounding rules (R2, R4, R5) must not
# read it. Deliberately much narrower than META_SECTION: that list is tuned for R3 on
# checklists and includes "overview" and "references", either of which can legitimately hold a
# guide's endpoint or field reference -- blanking those would manufacture R2 findings. History
# is the one class that is unambiguously never an implementation path. Found the hard way:
# discovery/privileged-accounts' change-log row records that the guide does *not* document
# telemetry, and the word "telemetry" in that sentence was enough to clear its R4.
HISTORY_SECTION = re.compile(r"change ?log|version history|revision history", re.I)

# R5: procedure steps that only exist on a customer-operated CPM/PSM box.
SELF_HOSTED_MARKERS = [
    r"C:\\Program Files",
    r"services\.msc",
    r"Password Manager\\bin",
    r"remote desktop",
    r"log in to the (CPM|PSM) server",
]
SAAS_MARKERS = re.compile(r"Privilege Cloud|SaaS|Idira-operated|Idira-managed", re.I)

GATE_LANGUAGE = re.compile(r"\bmust\b|\brequired\b|\bmandator|\bshall\b", re.I)

MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BARE_PORTAL = re.compile(r"^https?://(?P<host>[^/]+)/?$")
# R6 is about a link that promises a specific document and delivers a front page. A bare
# link to a tool's homepage (jsonpath.com) promises nothing and is not a finding.
NAMES_A_DOCUMENT = re.compile(
    r"\bguide\b|\bdocs?\b|\bdocumentation\b|\breference\b|\barchitecture\b|\bmanual\b|"
    r"\bspecification\b|\bAPI\b",
    re.I,
)

BACKTICKED = re.compile(r"`([^`\n]+)`")
BOLDED = re.compile(r"\*\*([^*\n]+)\*\*")

# A bold span is an identifier only when it reads like a name (a role, a product concept),
# not an emphasised sentence. Prose punctuation or a lowercase significant word disqualifies
# it -- otherwise "**Demonstration provided -- one of the following is mandatory:**" is
# graded as though it were a typed identifier.
PROSE_PUNCT = re.compile(r"[.;:?!—–,()]")
LOWERCASE_WORD = re.compile(r"^[a-z]")

# An attributed element is documented with its own attribute set, in any order, so match its
# structure rather than the checklist's exact spelling of it.
ATTRIBUTED_ELEMENT = re.compile(r"^<\s*(?P<tag>[\w.:-]+)(?P<attrs>\s[^>]*)?/?>$")
ATTR_PAIR = re.compile(r"([\w.:-]+)\s*=\s*\"([^\"]*)\"")

# A checklist routinely abbreviates what a guide spells out in full. Neither difference is
# a defect, so both are grounded structurally rather than by exact string:
#   verb + path  -- checklist `PUT /api/discovered-accounts/`, guide the whole URL
#   key + value  -- checklist `KillRunningApps: true`, guide `"KillRunningApps": "true"`
VERB_PATH = re.compile(r"^(?:GET|POST|PUT|DELETE|PATCH|HEAD)\s+(?P<path>/\S*)$")
KEY_VALUE = re.compile(r"^(?P<key>[\w.:-]+)\s*[:=]\s*\"?(?P<value>[^\"]+)\"?$")

# Spans removed before identifier extraction -- see identifiers_in().
EXAMPLE_SPAN = re.compile(
    r"\((?:e\.g\.|i\.e\.|for example)[^)]*\)|(?:such as|for example)[^.;|]*",
    re.I,
)
MD_LINK_ANY = re.compile(r"\[[^\]]*\]\([^)]*\)")
# A prohibited value is the one identifier a guide is right not to contain: "uses
# `Idira Endpoint Privilege Manager`, not `CyberArk EPM`" grades the absence, not the
# presence, so the negated span is dropped before extraction.
NEGATED_IDENTIFIER = re.compile(
    r"(?:not|never|rather than|instead of|avoid|no longer)\s+(?:use\s+|using\s+)?"
    r"(?:`[^`]+`|\*\*[^*]+\*\*)",
    re.I,
)
MD_LINK_RELATIVE = re.compile(r"\[([^\]]*)\]\((?!https?://|mailto:|#)([^)\s]+)\)")

# The level cell is captured as free text rather than an enum on purpose. The corpus has a
# third level in the wild -- "One of 10.2 / 10.3" -- and an enum here silently dropped two
# rows per Discovery checklist, which is how a checker quietly under-reports.
STRUCTURED_ROW = re.compile(
    r"^\|\s*(?P<id>\d+(?:\.\d+)*)\s*\|\s*(?P<text>.+?)\s*\|\s*(?P<level>[^|]+?)\s*\|\s*$"
)
# Graded rows are now split on cells rather than matched by STRUCTURED_ROW alone, because
# the 2026-10-01 Source column makes a graded row 3 OR 4 cells wide and the regex above
# cannot tell those apart safely. Its `text` group is `.+?`, which happily matches a pipe,
# so a 4-cell row still matches -- with `level` capturing the Source cell and `text`
# absorbing the real level. Every Recommended row would have silently become a gate
# (is_gate is `level != "Recommended"`) and R7 would have fired on all 606 rows at once.
# Counting cells makes the shape explicit and a wrong count loud instead of absorbed.
#
# Verified against the real corpus before changing this: 606 of 608 id-leading rows are
# exactly 3 cells and none contains an escaped pipe. The 2 four-cell rows are change-log
# rows in `## Change Log`, which META_SECTION already skips -- so nothing is misparsed
# today, and this change is prevention rather than a fix.
CELL_SPLIT = re.compile(r"(?<!\\)\|")
GRADED_ID = re.compile(r"^\d+(?:\.\d+)*$")
KNOWN_LEVELS = {"Required", "Recommended"}
# The third level, stated as a pattern rather than added to the enum above. "One of 5.1 / 5.2"
# is a deliberate corpus construct -- two alternatives, either one satisfies the requirement --
# and it gates (see Item.is_gate). Recognising the shape keeps R7 pointed at levels nobody
# intended while still flagging a malformed one. This does NOT narrow STRUCTURED_ROW's level
# capture, which stays free text on purpose; see the comment there.
CONDITIONAL_LEVEL = re.compile(r"^One of\s+\d+(?:\.\d+)*\s*/\s*\d+(?:\.\d+)*$")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
BARE_ROW = re.compile(r"^\s*[-*]\s*\[[ xX]\]\s*(?P<text>.+?)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(?P<title>.+?)\s*$")

# Any markdown link with its target split into path and fragment, for R8/R9. Unlike
# MD_LINK_RELATIVE this keeps the fragment, which is the whole point of R9 -- R8 threw it
# away and that is exactly how the off-by-one anchors in the Conjur guide survived 73 days.
MD_LINK_TARGET = re.compile(r"\[([^\]]*)\]\(\s*([^)\s]+?)\s*\)")
CODE_FENCE = re.compile(r"^\s*(?:```|~~~)")
# Inline markup a heading carries but its anchor does not.
HEADING_MARKUP = re.compile(r"[`*_~]")
MD_LINK_INLINE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slugify(title: str) -> str:
    """Slug a heading the way GitHub (and Docusaurus) does.

    One rule here is load-bearing and counter-intuitive: **each space becomes its own
    hyphen**, so punctuation that is dropped from between two spaces leaves a DOUBLE
    hyphen. `## 3. Stage 1 - Choose the path` written with an em dash anchors as
    `#3-stage-1--choose-the-path`, not `#3-stage-1-choose-the-path`.

    Collapsing whitespace runs instead produces a false positive on every em-dash heading
    in the corpus -- which is most of them. The first draft of this check did exactly that
    and reported 8 phantom breaks in `journey.md` and `identity-response`, all of which
    render correctly on GitHub today. A link checker that cries wolf gets switched off, so
    do not "simplify" this to `re.sub(r"\\s+", "-", ...)`.
    """
    text = MD_LINK_INLINE.sub(r"\1", title)       # a linked heading anchors on its label
    text = HEADING_MARKUP.sub("", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return text.replace(" ", "-")


def anchors_of(text: str) -> set[str]:
    """Every in-page anchor `text` offers, including GitHub's duplicate suffixes.

    Two identical headings anchor as `#foo` and `#foo-1`, so both are valid targets.
    """
    seen: dict[str, int] = {}
    out: set[str] = set()
    for line in _outside_fences(text):
        m = HEADING.match(line)
        if not m:
            continue
        slug = slugify(m.group("title"))
        if not slug:
            continue
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.add(slug if n == 0 else f"{slug}-{n}")
    return out


def _outside_fences(text: str):
    """Yield the lines of `text` that are not inside a fenced code block.

    A `# comment` in a bash example is not a heading and a bracketed path in a code
    sample is not a link; neither existing rule needed this distinction, R8/R9 do.
    """
    in_fence = False
    for line in text.splitlines():
        if CODE_FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield line


INLINE_CODE = re.compile(r"`[^`\n]*`")


def in_code_span(line: str, pos: int) -> bool:
    """Is `pos` inside an inline `code span` on this line?

    A fenced block is already skipped (see _outside_fences), but an inline span was not, so
    a documented link TEMPLATE written as `[docs: <label>](url)` was extracted as a real
    link and reported by R8 as pointing at a nonexistent path `url`. That is a false
    positive on correct markdown -- a backticked span renders as literal text, so no reader
    can follow it -- and this checker gates a publish, so a false positive blocks a real
    push. Found 2026-10-01 by R8 firing on security-baseline-reference.md, the file that
    documents the Source-cell formats.

    Tests the link's START position rather than blanking the span's text, because the corpus
    idiom `[`telemetry-reference.md`](telemetry-reference.md)` puts a code span inside a real
    link's LABEL. Blanking spans wholesale left that link intact but erased its label from
    every finding message ('cross-reference "    " points at ...'). Here its `[` sits outside
    the span, so the link is still checked and its label still prints, while a link written
    entirely inside a span is skipped.

    Deliberately not applied to the text R2 grounds against: backticked spans are exactly
    what identifiers_in() reads, so skipping them there would disable the core rule.
    """
    return any(m.start() < pos < m.end() for m in INLINE_CODE.finditer(line))


def links_of(text: str):
    """Yield (label, path, fragment, line_number) for every link outside a code fence."""
    in_fence = False
    for n, line in enumerate(text.splitlines(), start=1):
        if CODE_FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for m in MD_LINK_TARGET.finditer(line):
            if in_code_span(line, m.start()):
                continue
            target = m.group(2)
            path, _, frag = target.partition("#")
            yield m.group(1), path, frag, n


def blank_comments(text: str) -> str:
    """Return `text` with every HTML comment emptied but no line moved.

    Both corpus files are read through this before any rule looks at them, so every rule
    grades exactly what a partner can see in the rendered page. Two reasons, and they arrived
    in that order:

    1. An AI context block is an HTML comment carrying its own "## " headings. Left in a
       checklist it reads as a section that states requirements and grades nothing -- a
       self-inflicted R3 on every migrated kit.
    2. Left in a GUIDE it silently satisfies grounding. This reverses the note that used to
       sit here, written 2026-09-29 when no guide had a block yet and the case was
       hypothetical: "a guide's context block legitimately states API paths and field names,
       and dropping it would make R2 report identifiers as undocumented when the guide does
       document them." Once real blocks landed 2026-09-30 the effect was measurable and
       backwards -- corpus blocking fell 19 -> 17 the moment four Discovery guides gained a
       block, and discovery/privileged-accounts went 3 -> 1 while its guide gained no
       guidance whatsoever. A context block restates an identifier *precisely because* it
       matters, so leaving it in makes every important identifier self-grounding. It renders
       as nothing, so the partner still cannot find the requirement, and the whole point of
       R2 is the partner's ability to find it.

    Blanked rather than deleted: the comment is replaced by the newlines it contained, so
    every reported line number stays a real line in the real file. Deleting it would shift
    everything below a block -- about 80 lines in the migrated checklists -- and send a
    reader to the wrong row.
    """
    return HTML_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def row_cells(line: str) -> list[str] | None:
    """Return a markdown table row's cells, or None if the line isn't one.

    Splits on unescaped pipes only, so a cell written `a \\| b` stays one cell instead of
    shifting every column to its right.
    """
    s = line.strip()
    if not s.startswith("|") or not s.endswith("|") or len(s) < 2:
        return None
    return [c.strip() for c in CELL_SPLIT.split(s)[1:-1]]


def graded_row(line: str) -> list[str] | None:
    """Cells of a row whose first cell is a bare item id, else None.

    Shape is not validated here -- a wrong cell count still comes back, so the caller can
    report it rather than silently dropping the row. An item that parses as nothing is never
    graded, and an ungraded requirement reads as a pass.
    """
    cells = row_cells(line)
    if cells and cells[0] and GRADED_ID.match(cells[0]):
        return cells
    return None


@dataclass
class Item:
    """One graded line in a checklist."""

    ident: str  # "2.5" for structured rows, "#7" positional for bare ones
    text: str
    level: str  # Required | Recommended | Unlevelled | any conditional level in the corpus
    section: str
    line: int
    # Where the requirement comes from: an Idira doc link, a framework control
    # ("OWASP ASVS 5.0.0 V13.3.1"), or "House rule -- <decision>". Empty when the table has
    # no Source column yet, which is every checklist as of 2026-10-01. R10 grades this.
    source: str = ""

    @property
    def is_gate(self) -> bool:
        # Bare checklists carry no levels; their own overviews grade every box, so an
        # unlevelled item is treated as a gate rather than quietly downgraded. A
        # conditional level ("One of 10.2 / 10.3") gates too -- failing every alternative
        # blocks certification -- so only an explicit Recommended is non-gating.
        return self.level != "Recommended"


@dataclass
class Finding:
    rule: str
    severity: str  # blocking | advisory | note
    kit: str
    location: str
    detail: str


@dataclass
class KitReport:
    kit: str
    guide: str | None
    checklist: str | None
    fmt: str = "unknown"  # structured | bare | none
    items: int = 0
    gates: int = 0
    assessable_gates: int = 0
    sourced_gates: int = 0  # gates carrying a non-empty Source cell -- R10
    findings: list[Finding] = field(default_factory=list)

    @property
    def unassessable_gates(self) -> int:
        return self.gates - self.assessable_gates


def sections_of(text: str) -> list[tuple[str, int, list[str]]]:
    """Split a markdown file into (heading, start_line, body_lines) at ## level."""
    out: list[tuple[str, int, list[str]]] = []
    current = ("(preamble)", 1, [])
    for n, line in enumerate(text.splitlines(), start=1):
        m = HEADING.match(line)
        if m and len(m.group(1)) == 2:
            out.append(current)
            current = (m.group("title"), n, [])
        else:
            current[2].append(line)
    out.append(current)
    return [s for s in out if s[2] or s[0] != "(preamble)"]


def blank_history(text: str) -> str:
    """Return `text` with every revision-history section emptied but no line moved.

    Same line-preserving trick as blank_comments(), for the same reason.
    """
    lines = text.splitlines()
    for title, start, body in sections_of(text):
        if not HISTORY_SECTION.search(title):
            continue
        for n in range(start - 1, min(start - 1 + len(body) + 1, len(lines))):
            lines[n] = ""
    return "\n".join(lines)


def parse_checklist(text: str) -> tuple[str, list[Item], list[tuple[int, int]]]:
    """Extract graded items, the corpus format in use, and any malformed graded rows.

    The third element is `(line, cell_count)` for every row that leads with an item id but
    is neither 3 nor 4 cells wide. Those are returned rather than skipped so check_kit can
    report them -- see graded_row().
    """
    items: list[Item] = []
    malformed: list[tuple[int, int]] = []
    structured = 0
    bare = 0
    for title, start, body in sections_of(text):
        # A change log's version column ("| 2.0 | 2026-09-30 | ... |") is shaped exactly like
        # a graded row, and was being counted as one -- inflating the item count and reporting
        # the changelog prose as a requirement level. Meta sections state no requirements, so
        # nothing gradeable is lost by skipping them here. R3 already skips the same set.
        if META_SECTION.search(title):
            continue
        for offset, line in enumerate(body, start=1):
            lineno = start + offset
            cells = graded_row(line)
            if cells is not None:
                if len(cells) not in (3, 4):
                    malformed.append((lineno, len(cells)))
                    continue
                structured += 1
                level = cells[2].strip("*").strip()
                source = cells[3] if len(cells) == 4 else ""
                items.append(Item(cells[0], cells[1], level, title, lineno, source))
                continue
            m = BARE_ROW.match(line)
            if m:
                bare += 1
                items.append(
                    Item(f"#{bare}", m.group("text"), "Unlevelled", title, lineno)
                )
    fmt = "structured" if structured > bare else "bare" if bare else "none"
    return fmt, items, malformed


def identifiers_in(text: str) -> tuple[list[str], list[str]]:
    """Pull gradeable identifiers out of one item's text.

    Returns (distinctive, generic). Backticked spans are code identifiers; bolded
    multi-word spans are named roles and product concepts, which the naming crosswalk
    treats as identifiers too. Requirement-level words are never identifiers.

    Two spans are removed before extraction, because neither is a requirement the guide
    owes the reader: an illustrative example ("e.g. `Wiz`, `ServiceNow`" names other
    vendors' products, not ours), and a markdown link construct (its label is a
    cross-reference target, checked by R8 instead).
    """
    text = EXAMPLE_SPAN.sub(" ", text)
    text = NEGATED_IDENTIFIER.sub(" ", text)
    text = MD_LINK_ANY.sub(" ", text)
    raw: list[str] = [m.group(1).strip() for m in BACKTICKED.finditer(text)]
    for m in BOLDED.finditer(text):
        span = m.group(1).strip()
        words = span.split()
        if not 2 <= len(words) <= 6:
            continue
        if span in GENERIC_IDENTIFIERS or PROSE_PUNCT.search(span):
            continue
        if any(LOWERCASE_WORD.match(w) for w in words):
            continue
        raw.append(span)

    distinctive: list[str] = []
    generic: list[str] = []
    for ident in raw:
        if not ident or len(ident) < 3 or ident.isdigit():
            generic.append(ident)
        elif ident in GENERIC_IDENTIFIERS:
            generic.append(ident)
        else:
            distinctive.append(ident)
    return distinctive, generic


def grounded(ident: str, guide: str) -> bool:
    """Is this identifier documented somewhere in the guide?

    Exact substring first. An attributed element gets matched structurally instead: the
    guide documents `<Response type="error">` as
    `<Response name="..." type="error" statusCode="500">`, which is the same contract
    written with its full attribute set, not a different one.
    """
    if ident in guide:
        return True

    # An elided path ("POST .../Sets/<SetId>/Endpoints/search") is grounded when every
    # literal run around the ellipsis appears in the guide -- the checklist abbreviated
    # the base URL, it did not name a different endpoint.
    if "..." in ident or "…" in ident:
        runs = [r.strip() for r in re.split(r"\.{3}|…", ident) if len(r.strip()) >= 4]
        if runs and all(r in guide for r in runs):
            return True

    m = VERB_PATH.match(ident)
    if m:
        return m.group("path") in guide

    m = KEY_VALUE.match(ident)
    if m and not ident.startswith("<"):
        return m.group("key") in guide and m.group("value") in guide

    m = ATTRIBUTED_ELEMENT.match(ident)
    if not m:
        return False
    attrs = ATTR_PAIR.findall(m.group("attrs") or "")
    if not attrs:
        return False
    if f"<{m.group('tag')}" not in guide:
        return False
    return all(f'{k}="{v}"' in guide for k, v in attrs)


def check_kit(kit_dir: Path, corpus: Path) -> KitReport:
    kit = str(kit_dir.relative_to(corpus / "docs"))
    guide_path = kit_dir / GUIDE_NAME
    checklist_path = kit_dir / CHECKLIST_NAME
    rep = KitReport(
        kit=kit,
        guide=GUIDE_NAME if guide_path.exists() else None,
        checklist=CHECKLIST_NAME if checklist_path.exists() else None,
    )

    # R1 -- pairing
    if not guide_path.exists() or not checklist_path.exists():
        missing = GUIDE_NAME if not guide_path.exists() else CHECKLIST_NAME
        rep.findings.append(
            Finding("R1", "blocking", kit, kit, f"kit has no `{missing}`")
        )
        return rep

    # Both files are read as what a partner can actually see -- see blank_comments().
    guide = blank_comments(guide_path.read_text(encoding="utf-8"))
    checklist = blank_comments(checklist_path.read_text(encoding="utf-8"))
    # What the guide actually offers as implementation guidance. R2, R4 and R5 ground against
    # this; the link rules (R6, R8) stay on `guide`, since a broken link in a change log is
    # still a broken link a reader can follow.
    guidance = blank_history(guide)
    rep.fmt, items, malformed = parse_checklist(checklist)
    rep.items = len(items)

    # A graded row of an unexpected width is reported, never absorbed. Dropping it silently
    # would leave a real requirement ungraded, which reads as a pass rather than a bug.
    for lineno, count in malformed:
        rep.findings.append(
            Finding(
                "R10",
                "blocking",
                kit,
                f"{CHECKLIST_NAME}:{lineno}",
                f"graded row is {count} cells wide; expected 3, or 4 with a Source column "
                "— the row was not graded at all (see Rule 3, table integrity)",
            )
        )

    # Report the requirement-level vocabulary rather than assuming it. Anything outside
    # Required/Recommended/Unlevelled is a conditional gate a reader has to interpret.
    exotic = sorted(
        lvl
        for lvl in {i.level for i in items} - KNOWN_LEVELS - {"Unlevelled"}
        if not CONDITIONAL_LEVEL.match(lvl)
    )
    for level in exotic:
        rows = [i.ident for i in items if i.level == level]
        rep.findings.append(
            Finding(
                "R7",
                "note",
                kit,
                CHECKLIST_NAME,
                f'requirement level "{level}" is outside the corpus vocabulary '
                f"(Required / Recommended), on {len(rows)} item(s): {', '.join(rows)}",
            )
        )

    # R2 -- an identifier the checklist grades on, absent from the guide
    for item in items:
        distinctive, _generic = identifiers_in(item.text)
        if item.is_gate:
            rep.gates += 1
            if distinctive:
                rep.assessable_gates += 1
        if not distinctive:
            continue
        for ident in distinctive:
            if grounded(ident, guidance):
                continue
            severity = "blocking" if item.is_gate else "advisory"
            hint = ""
            if ident.lower() in guidance.lower():
                hint = " (present in the guide under different capitalisation)"
            rep.findings.append(
                Finding(
                    "R2",
                    severity,
                    kit,
                    f"{CHECKLIST_NAME}:{item.line} item {item.ident}",
                    f"grades `{ident}`, which the guide never states{hint}"
                    f" — \u00a7 {item.section}",
                )
            )

    # R10 -- a gate with no recorded authority.
    #
    # Scoped deliberately, because the README's own warning applies to this rule more than
    # any other: "a gate that fails every build on day one gets muted rather than fixed."
    # Almost no checklist carries a Source column yet, so grading every gate against it would
    # emit 540 findings on the first run. Instead:
    #
    #   * a SECTION with no sourced rows -> counted into one note per kit. Nothing to drift from.
    #   * a SECTION with some sourced rows -> one advisory per unsourced gate IN THAT SECTION.
    #     The column exists there, so an empty cell beside a filled one is a real omission in a
    #     table someone is actively maintaining -- and a half-sourced table is worse than an
    #     unsourced one, because a reader takes the blank cell to mean "nothing backs this".
    #
    # The scope is the section, not the kit, because each section is its own markdown table and
    # the backfill lands section by section (the security sections first). Scoping it per kit
    # instead -- as this rule did when first written -- made sourcing the SIEM kit's two security
    # sections emit 42 advisories against sections nobody had touched, each one asserting the
    # table's "other rows are sourced" when that table had no sources at all. The finding text
    # was right and the condition was wrong.
    #
    # Advisory, not blocking, in both shapes: an unsourced requirement is a defensibility
    # problem when a partner pushes back, not a reason to fail a docs publish.
    gates = [i for i in items if i.is_gate]
    rep.sourced_gates = sum(1 for i in gates if i.source)
    sourced_sections = {i.section for i in items if i.source}
    unsourced_gates = [i for i in gates if not i.source]
    rollup = [i for i in unsourced_gates if i.section not in sourced_sections]
    for item in unsourced_gates:
        if item.section in sourced_sections:
            rep.findings.append(
                Finding(
                    "R10",
                    "advisory",
                    kit,
                    f"{CHECKLIST_NAME}:{item.line} item {item.ident}",
                    "gates certification with an empty Source, in a table whose other rows "
                    f"are sourced — § {item.section}",
                )
            )
    if rollup:
        sections = len({i.section for i in rollup})
        rep.findings.append(
            Finding(
                "R10",
                "note",
                kit,
                CHECKLIST_NAME,
                f"{len(rollup)} gate(s) across {sections} section(s) carry no Source — they "
                "assert an authority the kit never records, so partner-facing defensibility "
                "is unverifiable there",
            )
        )

    # R3 -- a section that states a requirement with nothing to tick
    for title, start, body in sections_of(checklist):
        if META_SECTION.search(title) or title == "(preamble)":
            continue
        joined = "\n".join(body)
        has_gradeable = any(
            STRUCTURED_ROW.match(line) or BARE_ROW.match(line) for line in body
        )
        if GATE_LANGUAGE.search(joined) and not has_gradeable:
            rep.findings.append(
                Finding(
                    "R3",
                    "blocking",
                    kit,
                    f"{CHECKLIST_NAME}:{start} \u00a7 {title}",
                    "states a requirement but has no checkbox or graded row — an agent "
                    "self-scoring the checklist mechanically never scores it",
                )
            )

    # R4 -- telemetry graded but undocumented
    if TELEMETRY_HEADER in checklist and not TELEMETRY_MENTION.search(guidance):
        rep.findings.append(
            Finding(
                "R4",
                "blocking",
                kit,
                CHECKLIST_NAME,
                f"grades `{TELEMETRY_HEADER}`; the guide never mentions telemetry, so the "
                "kit gives no implementation path for a requirement it gates on",
            )
        )

    # R5 -- checklist certifies both deployments, guide documents one (heuristic)
    checklist_saas = SAAS_MARKERS.search(checklist)
    guide_saas = SAAS_MARKERS.search(guidance)
    hits = [m for m in SELF_HOSTED_MARKERS if re.search(m, guidance, re.I)]
    if checklist_saas and not guide_saas and hits:
        rep.findings.append(
            Finding(
                "R5",
                "advisory",
                kit,
                GUIDE_NAME,
                "checklist certifies a SaaS/Privilege Cloud deployment; the guide's "
                f"procedure is Self-Hosted-only ({len(hits)} on-box marker(s), first: "
                f"\"{hits[0].replace(chr(92) + chr(92), chr(92))}\") and never names the "
                "SaaS case — heuristic, confirm by hand",
            )
        )

    # R8/R9 are not here. Both link rules run corpus-wide in check_links() instead -- see
    # the note there for why restricting them to a kit's own two files was the gap.

    # R6 -- a reference link that points at a portal front page.
    # Scanned line by line, skipping matches inside an inline code span, for the same reason
    # links_of() does: a backticked link template is literal text, not a link a reader can
    # follow. MD_LINK's label class can cross a newline, so a link whose `[` and `](url)` sit
    # on different lines is no longer matched -- the corpus has none, verified before the
    # change, and a reported line number was already wrong for such a match anyway.
    for name, raw in ((GUIDE_NAME, guide), (CHECKLIST_NAME, checklist)):
        for line_no, line in enumerate(raw.splitlines(), start=1):
            for m in MD_LINK.finditer(line):
                if in_code_span(line, m.start()):
                    continue
                portal = BARE_PORTAL.match(m.group(2))
                if not portal:
                    continue
                host = portal.group("host")
                if not (host.startswith("docs.") or NAMES_A_DOCUMENT.search(m.group(1))):
                    continue
                rep.findings.append(
                    Finding(
                        "R6",
                        "advisory",
                        kit,
                        f"{name}:{line_no}",
                        f'"{m.group(1)}" resolves to {m.group(2)} — a portal front page, '
                        "not the referenced page",
                    )
                )

    return rep


KNOWN_RULES = {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "R9", "R10"}
SHARED_KIT_LABEL = "(shared docs)"


def check_links(corpus: Path) -> list[Finding]:
    """R8 and R9 over every markdown file in the corpus, not just the kits' own two.

    Scope is the whole of `docs/` deliberately. R8 used to run inside check_kit() against
    only `development-guide.md` and `certification-checklist.md`, which left the files that
    route a partner INTO a kit -- `index.md`, `journey.md`, the workflow decision guides,
    `naming-crosswalk.md` -- unchecked. Both of the dead links reported on 2026-10-01 lived
    in exactly those unchecked files: `index.md` pointed at a checklist that did not exist
    yet, and the Secrets Management decision guide pointed at a `_reference/` path outside
    this repository that was never going to resolve for a reader. A link check that skips
    the entry points misses the links a partner hits first.

    R9 is the fragment half R8 discarded: a link whose file resolves but whose `#anchor`
    matches no heading in it. Silent on GitHub -- the page loads, the reader just lands in
    the wrong place -- so nothing surfaces it short of checking.
    """
    docs = corpus / "docs"
    findings: list[Finding] = []
    anchors_cache: dict[Path, set[str]] = {}

    def anchors_for(path: Path) -> set[str]:
        if path not in anchors_cache:
            anchors_cache[path] = anchors_of(
                blank_comments(path.read_text(encoding="utf-8"))
            )
        return anchors_cache[path]

    for src in sorted(docs.rglob("*.md")):
        rel = src.relative_to(docs)
        kit = str(rel.parent) if rel.parent != Path(".") else SHARED_KIT_LABEL
        loc_name = rel.name if kit != SHARED_KIT_LABEL else str(rel)
        text = blank_comments(src.read_text(encoding="utf-8"))

        for label, path, frag, line in links_of(text):
            if re.match(r"^(?:https?:|mailto:)", path):
                continue
            # A template's link slot, e.g. `({DiagramFile})`, is a placeholder the partner
            # fills, not a path. Only a whole-target {PascalCase} word is skipped, so a real
            # path with a typo still fails.
            if re.fullmatch(r"\{[A-Z][A-Za-z0-9]+\}", path):
                continue

            # R8 -- the path half. An empty path means a same-file anchor.
            if path:
                target = (src.parent / path).resolve()
                if not target.exists():
                    findings.append(
                        Finding(
                            "R8",
                            "blocking",
                            kit,
                            f"{loc_name}:{line}",
                            f'cross-reference "{label}" points at `{path}`, which does '
                            "not exist in the corpus",
                        )
                    )
                    continue
            else:
                target = src

            # R9 -- the fragment half. Only meaningful once the file resolves, and only
            # for markdown (a directory link carries no headings).
            if not frag or target.is_dir() or target.suffix != ".md":
                continue
            available = anchors_for(target)
            if frag in available:
                continue
            where = "this file" if target == src else f"`{path}`"
            findings.append(
                Finding(
                    "R9",
                    "blocking",
                    kit,
                    f"{loc_name}:{line}",
                    f'anchor "{label}" points at `#{frag}`, which no heading in {where} '
                    "produces — the link resolves but lands the reader somewhere else",
                )
            )

    return findings


def corpus_commit(corpus: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(corpus), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def render(reports: list[KitReport], corpus: Path, quiet: bool) -> str:
    sha = corpus_commit(corpus)
    lines: list[str] = [
        "# Dev-Kit Guide\u2194Checklist Consistency Report",
        "",
        f"Corpus: `{corpus}` at commit `{sha}` \u2014 {len(reports)} kits.",
        "",
        "## Summary",
        "",
        "| Kit | Format | Items | Gates | Blocking | Advisory | Gates not mechanically "
        "assessable | Gates sourced |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(reports, key=lambda r: r.kit):
        blocking = sum(1 for f in r.findings if f.severity == "blocking")
        advisory = sum(1 for f in r.findings if f.severity == "advisory")
        lines.append(
            f"| `{r.kit}` | {r.fmt} | {r.items} | {r.gates} | {blocking} | {advisory} "
            f"| {r.unassessable_gates} | {r.sourced_gates}/{r.gates} |"
        )

    totals = {
        "kits": len(reports),
        "items": sum(r.items for r in reports),
        "gates": sum(r.gates for r in reports),
        "blocking": sum(1 for r in reports for f in r.findings if f.severity == "blocking"),
        "advisory": sum(1 for r in reports for f in r.findings if f.severity == "advisory"),
        "unassessable": sum(r.unassessable_gates for r in reports),
        "sourced": sum(r.sourced_gates for r in reports),
    }
    by_rule: dict[str, int] = {}
    for r in reports:
        for f in r.findings:
            by_rule[f.rule] = by_rule.get(f.rule, 0) + 1
    lines += [
        f"| **total** | | **{totals['items']}** | **{totals['gates']}** | "
        f"**{totals['blocking']}** | **{totals['advisory']}** | "
        f"**{totals['unassessable']}** | **{totals['sourced']}/{totals['gates']}** |",
        "",
        "By rule: " + (", ".join(f"{k} {v}" for k, v in sorted(by_rule.items())) or "none"),
        "",
    ]

    if not quiet:
        lines += ["## Findings", ""]
        for r in sorted(reports, key=lambda r: r.kit):
            if not r.findings:
                continue
            lines += [f"### `{r.kit}`", ""]
            order = {"blocking": 0, "advisory": 1, "note": 2}
            for f in sorted(r.findings, key=lambda f: (order[f.severity], f.rule)):
                lines.append(f"- **{f.rule} {f.severity}** \u2014 `{f.location}`: {f.detail}")
            lines.append("")

    lines += [
        "## What this check does not cover",
        "",
        "- **Prose-level topic mapping.** R2 grounds identifiers, not ideas. A gate item"
        " carrying no code identifier and no named role is counted in the last column and"
        " never judged \u2014 it needs a human or a model.",
        "- **Whether the guide's own statement is correct.** An identifier present in the"
        " guide passes R2 even if the guide documents it wrongly. Nothing here reviews a"
        " guide against the product it documents \u2014 that needs a human or a model.",
        "- **Undeclared enums and missing schemas.** A guide whose examples are its only"
        " specification is an absence rather than a guide\u2194checklist disagreement, so"
        " nothing here detects it.",
        "- **Whether a Source is true.** R10 checks that a gate records an authority, not"
        " that the authority says what the gate claims. A cell reading"
        " `OWASP ASVS 5.0.0 V13.3.1` passes R10 whether or not that control exists or is"
        " relevant — verifying the citation is a human or model job.",
        "- **R5 is a heuristic** and is reported as advisory for that reason.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    ap.add_argument("--json", action="store_true", help="machine-readable findings")
    ap.add_argument("--quiet", action="store_true", help="summary table only")
    ap.add_argument(
        "--rules",
        metavar="R8,R9",
        help="only report and exit on these rules (default: all)",
    )
    args = ap.parse_args(argv)

    corpus = Path(os.path.expanduser(args.corpus)).resolve()
    docs = corpus / "docs"
    if not docs.is_dir():
        print(f"error: no docs/ directory under {corpus}", file=sys.stderr)
        return 2

    kit_dirs = sorted(
        {p.parent for p in docs.rglob("*.md") if p.name in (GUIDE_NAME, CHECKLIST_NAME)}
    )
    if not kit_dirs:
        print(f"error: found no kit directories under {docs}", file=sys.stderr)
        return 2

    reports = [check_kit(d, corpus) for d in kit_dirs]

    # R8/R9 run over the whole corpus, so their findings are distributed back onto the kit
    # they belong to; anything in a top-level shared file lands in a synthetic report.
    by_kit = {r.kit: r for r in reports}
    for f in check_links(corpus):
        if f.kit not in by_kit:
            by_kit[f.kit] = KitReport(kit=f.kit, guide=None, checklist=None, fmt="n/a")
            reports.append(by_kit[f.kit])
        by_kit[f.kit].findings.append(f)

    # --rules narrows what is reported AND what the exit code reflects, so a gate can block
    # on one class without inheriting the corpus's whole open finding count. The link rules
    # are gateable today because the corpus is clean of them; R2's 15 are a real but
    # untriaged backlog, and wiring CI to those would land red on arrival and get muted.
    if args.rules:
        wanted = {r.strip().upper() for r in args.rules.split(",") if r.strip()}
        unknown = wanted - KNOWN_RULES
        if unknown:
            print(
                f"error: unknown rule(s): {', '.join(sorted(unknown))} "
                f"(known: {', '.join(sorted(KNOWN_RULES))})",
                file=sys.stderr,
            )
            return 2
        for r in reports:
            r.findings = [f for f in r.findings if f.rule in wanted]

    if args.json:
        payload = {
            "corpus": str(corpus),
            "commit": corpus_commit(corpus),
            "kits": [
                {
                    **{k: v for k, v in asdict(r).items() if k != "findings"},
                    "unassessable_gates": r.unassessable_gates,
                    "findings": [asdict(f) for f in r.findings],
                }
                for r in reports
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render(reports, corpus, args.quiet), end="")

    blocking = sum(1 for r in reports for f in r.findings if f.severity == "blocking")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
