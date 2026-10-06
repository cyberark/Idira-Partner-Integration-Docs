# Idira Joint Solution Brief (JSB) Standards

**Type:** Reference Guide
**Version:** 1.5
**Author:** Idira Technical Alliances
**Last Updated:** 2026-09-30
**Source:** Palo Alto Networks Tech Partnerships JSB template; Idira Naming Guidelines — Partners

---

<!--
## AI CONTEXT BLOCK
This block is for AI coding assistants (Claude, Copilot, Cursor, etc.) importing this file.
Read this block first before drafting, editing or reviewing any Joint Solution Brief.

DOCUMENT TYPE: Content standards for co-branded marketing collateral. No endpoints, no code.
THIS FILE GOVERNS A WRITING TASK, NOT A BUILD TASK, WHICH MAKES IT DIFFERENT FROM EVERY OTHER FILE IN
THIS CORPUS. Elsewhere an agent generates an integration; here an agent generates PROSE THAT CARRIES THE
IDIRA NAME, and several rules below bar things a language model emits by default. Treat §5 and §7 as
hard constraints on your own output, not as background for a human writer.
WHAT IT PRODUCES: the **Solution Brief** resource on an Idira Marketplace listing.
CONTACT: cybr-bizdevtech@paloaltonetworks.com, quoting the tracking reference.

THE FOUR RULES A MODEL BREAKS WITHOUT BEING TOLD. Check your draft against these before anything else:
1. NO EM DASHES ANYWHERE (§7.4). Use a colon, a comma, a period, or rewrite the sentence. This is the
   single most reliably violated rule in the document, because the character is a default habit rather
   than a decision. NOTE: this context block uses em dashes for consistency with the rest of the
   corpus. The BRIEF must not. Do not take this block's punctuation as a licence.
2. NO CLICHÉS OR UNGROUNDED SUPERLATIVES (§7.5), and the barred list is explicit: seamless,
   best-in-class, game-changing, end-to-end, next-generation, best-of-breed, synergy. That list is close
   to a model's default register for marketing copy. Write the specific outcome instead.
3. NO ABBREVIATIONS OF IDIRA PRODUCT NAMES, EVER, INCLUDING IN PARENTHESES AFTER THE FULL NAME (§5,
   §9). No "Idira EPM", and no "(PAM)" appended to a first mention. Expanding-then-abbreviating is
   standard practice in technical writing and is a rejection here. Generic industry terms used as
   categories (IAM, PAM, SIEM, MFA) are fine; the ban is on shortening a PRODUCT name.
4. NO INACCURATE IDIRA CAPABILITY CLAIMS (§7.8), described in the file itself as the single most common
   accuracy rejection. If it is not certain that Idira does something, ASK — do not assert, and do not
   infer a capability from a plausible adjacency. An agent generating fluent marketing copy will invent
   capability claims unless it is holding this line deliberately.

ESTABLISH THE TRACK BEFORE DRAFTING A SINGLE LINE. You cannot infer it (§1).
- TRACK A, the PANW template: the default. §2 mandatory section order and §3 character limits are
  ENFORCED.
- TRACK B, the partner's own template and copyright: EXEMPT from §2 structure and §3 length only.
TRACK B IS NOT A LIGHTER STANDARD. Every content rule binds both tracks without exception: naming,
product-claim accuracy, competitive positioning, prohibited content, and the whole of §7. If the track
is unknown, ask rather than assuming Track A and producing a structure the partner's format rejects.

COMPETITIVE POSITIONING IS THE HARD STOP (§7.3), AND IT IS NOT A STYLE NOTE. No section may present the
partner product as superior to Idira or Palo Alto Networks, or present ours as inferior to, incomplete
without, or DEPENDENT ON theirs. The file quotes the barred pattern verbatim: *"Idira secures the
privileged accounts it knows about, but can't protect what it can't see."* That construction triggers a
mandatory internal review and WILL NOT be silently reworded for the partner. The trap is that
gap-framing is the natural way to write a joint value proposition, so a model will produce it while
trying to be helpful. Frame joint value as complementary coverage, never as a deficiency Idira has.

WRITE ONLY WHAT THE PARTNER OWNS (§4). IF ASKED TO "WRITE THE WHOLE BRIEF", TWO SECTIONS ARE STILL NOT
YOURS TO WRITE:
- The IDIRA PRODUCT SPOTLIGHT is written by IDIRA. Leave it blank or as a placeholder. Filling it in is
  a returned brief even if the content is accurate.
- ABOUT PALO ALTO NETWORKS is written by NEITHER party. On Track A it is FIXED BOILERPLATE, reproduced
  VERBATIM from §5, and a paraphrase is a rejection. DO NOT REGENERATE IT FROM MEMORY OR TRAINING DATA
  — copy the paragraph from §5 of this file, and retain the ® on Unit 42®. On Track B, substitute an
  "About Idira" block that is accurate and current, carries ® on first use of the Idira brand, and links
  to paloaltonetworks.com/idira.
- The INTEGRATION DIAGRAM on Track A is built by PANW partner marketing. Do not produce one; leave a
  placeholder plus a one-line figure description, and supply icons separately.

NAMING SPECIFICS THAT GET BRIEFS RETURNED (§5, §9):
- The self-hosted product is "Idira Privileged Access Manager Self-Hosted". NEVER "Idira Privilege
  Access Manager" bare — note "Privileged", and note that the deployment suffix is part of the name.
- "Privileged Access Management" is the lowercase CATEGORY, not the product noun. Check which one the
  sentence needs.
- No legacy CyberArk-era names: not "CyberArk PAM", "PAS", or "CyberArk Privilege Cloud". CyberArk is
  now a Palo Alto Networks company and the brand is Idira.
- ® goes on the FIRST body-copy use of the Idira brand or product name only. Never in a heading, never
  in the cover title, never on subsequent uses.
- First use: "Palo Alto Networks Idira®" or "Idira® [Product] by Palo Alto Networks". After: "Idira" or
  "Idira [Product]".
- Legitimate survivals that are NOT defects: verbatim analyst quotes, published case studies, and named
  certification or community programs.

STATE THE DEPLOYMENT MODEL AT FIRST MENTION (§7.10). Where an integration supports only Self-Hosted or
only SaaS, say so inline rather than in a footnote: an unqualified Idira product name reads as "all
deployments" and is treated as a CAPABILITY MISSTATEMENT, not an omission. This connects directly to the
kits — psm-connectors/web-connection-component is Idira PAM Self-Hosted only, and
identity-response/response-actions is Idira SaaS only.

TWO MORE STRUCTURAL RULES THAT LOOK LIKE STYLE AND ARE NOT (Track A):
- THE CHALLENGE NAMES NO PRODUCT OR BRAND AT ALL (§7.1). Market problem and business impact only.
- THE SOLUTION'S OPENING NAMES NO PRODUCT OR BRAND (§7.2). Capabilities generically; branded detail
  belongs in the two spotlights beneath it.
Also: KEY BENEFITS ARE 5 TO 7 BULLETS, customer outcomes, NO product names, and not prose paragraphs
(§3, §7.6).

CHARACTER LIMITS ARE COUNTED WITH SPACES AND ENFORCED, AND OVERRUNS COME BACK WITH THE ACTUAL COUNT
(§3). The self-check is explicit that they are "counted, not estimated" — so COUNT them, do not
approximate from word counts. The approximate word ranges in the §3 table are orientation only. The
tightest ones are the easiest to miss: Title and Subtitle 100 each, each Key Benefit bullet 128, The
Solution 750, use-case challenge 400, multiple-integrations entry 175, About Partner 400.

FIXED HEADING FORMATS (§2): cover title is `Palo Alto Networks and [Partner Name]`, outcome-led, NO
VERBS and no task framing. Joint Value heading is `Palo Alto Networks and [Partner Name]: [heading]`.

SCOPE — WHAT A JSB IS NOT (§1). Not a whitepaper, press release, or product datasheet, and NOT technical
configuration content. Configuration steps belong in the separate `Configuration guide` asset
(marketplace-standards.md §5). A JSB is strongly preferred but not strictly required: a listing can be
built from the partner's website instead, though it will be materially weaker. Length target is 2 pages
after layout, which is what the §3 limits exist to hold.

TWO ASSET ABSOLUTES (§6): NO PRODUCT SCREENSHOTS anywhere in a JSB, ever — photography of the partner's
own hardware is fine. Customer quotes and case studies are optional but require WRITTEN customer
approval for external use, supplied with the draft; unapproved named customers are removed or
anonymized.

EVIDENCE RULES (§7.5, §7.7): a percentage, time saving or compliance assertion needs a nameable basis,
and standards revisions must be current — FIPS 140-2 is SUPERSEDED BY 140-3, so state which one a
certification is actually against, and do not write "highest security" beside a Level 3 claim when Level
4 exists. Related, §7.9: every challenge raised must be answered somewhere in the brief. Raising
post-quantum risk and never addressing it reads as filler.

TIMELINE AND GATES (§8), FOR SETTING EXPECTATIONS RATHER THAN FOR DRAFTING: submission is through the
PANW partner portal, not by email, and routes to partner marketing who share a Google Doc with the
Idira technical reviewer. Findings return as an ITEMIZED LIST, never as edits to partner-owned sections.
Editorial and technical review runs 2 to 3 business days, 5 to 7 with a revision round. THE PUBLISH GATE
IS SEPARATE from that review: before the brief is attached to a listing, Technical Alliances runs a
final check on naming, accuracy against the listing and its Configuration guide, competitive
positioning, and asset completeness. Track A allows a maximum of 2 design revision rounds. Expect 15 to
25 business days total, 25 to 40 with major revisions, legal review, or customer-quote approvals.

RUN §9 BEFORE SUBMITTING. It is the self-check, split into shared content rules, Track A structure, and
Track B items. Work it as a checklist rather than reading it as prose.

SIBLING TOP-LEVEL FILES:
- marketplace-standards.md — listing metadata, and the separate `Configuration guide` asset. Note that
  the 2026-08-11 rename to `Configuration guide` covers the documentation asset ONLY; the brief's
  resource name on a listing is still "Solution Brief".
- AGENTS.md — the machine entry point for the repository
- journey.md — the five stages; the brief is collateral attached at the listing stage
- naming-crosswalk.md — product naming, including what is deliberately not rebranded

ROUTING PRECEDENCE: journey.md → decision-guide.md → workflow decision-guide.md →
development-guide.md → certification-checklist.md → marketplace-standards.md
-->

---

> This document defines the standards a Joint Solution Brief must meet to be approved as a **Solution Brief** resource on an Idira Marketplace listing. It is the JSB counterpart to [`marketplace-standards.md`](marketplace-standards.md), which governs listing metadata.
>
> **Read this before you draft.** Every requirement below is checked at review. Briefs that miss a mandatory section, exceed a character limit, or use a barred product name are returned rather than fixed for you.

**Destination note.** A JSB may be attached to an **Idira Marketplace** listing (the in-product catalog) and/or to your Solution in the **Palo Alto Networks technology partner directory**. These are distinct destinations with distinct publish gates. The content standards in this document apply to both.

---

## 1. Scope

**A JSB is expected when** your integration is progressing to a Marketplace listing and you want joint, co-branded collateral attached to it. It is strongly preferred but not strictly required: a listing can be built from your website instead, though it will be materially weaker.

**A JSB is not the vehicle for** whitepapers, press releases, product datasheets, or technical configuration content. Configuration steps belong in your **Configuration guide** asset (see [`marketplace-standards.md`](marketplace-standards.md) §5), not in the brief.

**Length target:** 2 pages after layout. The character limits in §3 exist to hold that.

### Two tracks

Which sections apply depends on whose template the brief is built on. **Content rules apply to both tracks without exception.** Structure rules apply only to Track A.

| | **Track A — PANW template** | **Track B — Partner template** |
|:---|:---|:---|
| **When** | Default. Use this unless you already own an established co-branded brief format | You have your own solution-brief template and design system, and are producing the brief under your own copyright |
| §2 Mandatory sections and order | **Enforced** | Exempt — your format governs |
| §3 Character limits | **Enforced** | Exempt — your layout governs length |
| §4 Section ownership | **Enforced** | Applies in spirit: we write Idira product copy, you write yours |
| §5 Naming, branding, ® | **Enforced** | **Enforced** |
| §5 About Palo Alto Networks boilerplate | **Verbatim, enforced** | Substitute an "About Idira" block. Must be accurate and current; ® on first use |
| §6 Assets | **Enforced** | Enforced except the diagram rule: you produce your own diagrams |
| §7 Prohibited content | **Enforced** | **Enforced** — every item |
| §8 Submission and review | **Enforced** | **Enforced** |

**Track B is not a lighter standard.** It exempts you from our layout, not from naming accuracy, product-claim accuracy, or the competitive-positioning bar. Those are the rules that exist because the brief carries the Idira name, and they do not depend on whose template it sits in.

**Choosing Track B.** Say so when you submit. If you have no established brief format, use Track A: it is faster, and PANW partner marketing does the layout for you.

---

## 2. Mandatory Sections and Order

> **Track A only.** On Track B (partner template) your own format governs structure and section naming. Skip to §5.

All sections are required in this order unless marked conditional. A missing or reordered mandatory section is a rejection.

| # | Section | Conditional? |
|:--|:---|:---|
| 1 | Cover — Title + Subtitle | Required |
| 2 | Key Benefits | Required |
| 3 | The Challenge | Required |
| 4 | The Solution | Required |
| 4a | Partner product spotlight | Required |
| 4b | Palo Alto Networks / Idira product spotlight | Required |
| 5 | Joint Value / How It Works | Required |
| 6 | Use Cases (typically 2) | Required — minimum 1 |
| 7 | Integration Diagram | Required as placeholder (see §6) |
| 8 | Multiple Integrations | Only if you have more than one Idira integration |
| 9 | About [Partner] | Required |
| 10 | About Palo Alto Networks | Required — verbatim boilerplate (§5) |

**Cover title format:** `Palo Alto Networks and [Partner Name]`. Outcome-led, no verbs, no task framing.

**Joint Value heading format:** `Palo Alto Networks and [Partner Name]: [heading]`.

---

## 3. Character Limits

> **Track A only.** On Track B your layout governs length. The 2-page target still applies.

Counts include spaces. Every limit is enforced. Overruns are returned with the actual count.

| Section | Limit | Approx. words |
|:---|:---|:---|
| Title | 100 | ~15 |
| Subtitle | 100 | ~15 |
| Each Key Benefit bullet | 128 | ~20 |
| The Challenge | 1000 | 140–210 |
| The Solution | 750 | 110–190 |
| Partner product spotlight | 1000 | 110–210 |
| Idira product spotlight | 1000 | 140–210 |
| Joint Value / How It Works | 1000 | 140–200 |
| Use case title | 128 | ~20 |
| Use case challenge | 400 | 60–100 |
| Use case solution | 700 | 100–120 |
| Multiple integrations (per entry) | 175 | ~25 |
| About Partner | 400 | ~50 |

**Key Benefits** must be 5 to 7 bullets, not prose paragraphs.

---

## 4. Section Ownership

Write only what you own. Editing an Idira-owned section is a returned brief, as is us rewriting yours.

| Section | Written by |
|:---|:---|
| Partner product spotlight | **You** |
| About [Partner] | **You** |
| Cover, Key Benefits, Challenge, Solution, Joint Value, Use Cases | **You** — reviewed and corrected by Idira for product accuracy |
| Idira product spotlight | **Idira** — leave it blank or as a placeholder |
| About Palo Alto Networks | **Neither** — fixed boilerplate, §5 |
| Integration Diagram | **PANW partner marketing** — you supply icons only, §6 |

---

## 5. Naming, Branding, and Boilerplate

**Product names.** Use the approved Idira product names exactly as listed in [`marketplace-standards.md`](marketplace-standards.md) §6. Specifically:

- **No abbreviations of Idira product names in partner-facing copy.** Write "Idira Endpoint Privilege Manager", never "Idira EPM". Industry terms (IAM, PAM, SIEM, MFA) are fine.
- **No legacy CyberArk-era product names** — "CyberArk PAM", "PAS", "CyberArk Privilege Cloud". CyberArk is now a Palo Alto Networks company; the brand is **Idira**.
- **The self-hosted PAM product is "Idira Privileged Access Manager Self-Hosted."** Never "Idira Privilege Access Manager" bare.
- Exceptions where legacy names legitimately survive: verbatim analyst quotes, published case studies, and named certification/community programs. These are not defects.

**Trademark symbol.** **®** on the first use of the Idira brand or product name in body copy. Never in a heading, never in the cover title, never on subsequent uses.

**First vs. subsequent form.** First use: "Palo Alto Networks Idira®" or "Idira® [Product] by Palo Alto Networks". After that: "Idira" or "Idira [Product]".

**Partner branding.** Use your own official product and company names. Supply a high-resolution transparent-background PNG logo.

**About Palo Alto Networks — Track A, verbatim, do not paraphrase:**

> Palo Alto Networks (NASDAQ: PANW), the global AI cybersecurity leader, protects our digital way of life with a comprehensive portfolio of cybersecurity solutions and platforms across Network, Cloud, Security Operations, AI, and Identity. Trusted by more than 70,000 customers and powered by Unit 42® threat intelligence, our AI-driven platforms eliminate complexity, empowering enterprises to modernize with confidence and securing the speed of innovation. Explore the future of security at www.paloaltonetworks.com.

A paraphrased version of this paragraph is a rejection on Track A. Retain the ® on Unit 42.

**Track B — "About Idira" block.** Where your template carries a partner-description sidebar instead, supply an About Idira block. It must be accurate and current, carry ® on the first use of the Idira brand, and link to `paloaltonetworks.com/idira`. Do not describe Idira as anything other than what it is. Send us the text if you want it confirmed before layout.

---

## 6. Assets

| Asset | Requirement |
|:---|:---|
| Partner logo | High-resolution PNG, transparent background |
| Diagram icons | Your product icons, high-resolution, transparent background |
| Integration diagram | **Track A: do not produce one.** PANW partner marketing builds it from your icons; leave a placeholder with a one-line figure description. **Track B:** produce your own, in your design system. Label every component with an approved product name per §5 |
| Product screenshots | **Not accepted** anywhere in a JSB. Product photography of your own hardware is fine |
| Customer quotes / case studies | Optional. Requires written customer approval for external use, supplied with the draft. Unapproved named customers are removed or anonymized |

---

## 7. Prohibited Content

These are the recurring reasons briefs come back.

1. **No product or brand names in The Challenge.** Describe the market problem and its business impact only. *(Track A. On Track B, keep the equivalent problem-framing section product-neutral where your format allows.)*
2. **No product or brand names in The Solution opening.** Describe capabilities generically; branded detail belongs in the two spotlights below it. *(Track A.)*
3. **No competitive positioning against Palo Alto Networks or Idira.** No section may present your product as superior to ours, or ours as inferior to, incomplete without, or dependent on yours. Phrasing of the form *"Idira secures the privileged accounts it knows about, but can't protect what it can't see"* is a hard stop. It triggers a mandatory internal review and will not be silently reworded for you.
4. **No em dashes (—).** Use a colon, a comma, a period, or rewrite the sentence.
5. **No clichés or ungrounded superlatives** — seamless, best-in-class, game-changing, end-to-end, next-generation, best-of-breed, synergy. A superlative your own brief then contradicts is the worst case: do not write "highest security" beside a FIPS 140-2 Level 3 claim when Level 4 exists. Name the certification and let it speak.
6. **No feature dumping.** Key Benefits are customer outcomes, not capability lists, and carry no product names.
7. **No unsubstantiated claims.** A percentage, a time saving, or a compliance assertion needs a basis you can name. Cite current standards revisions: FIPS 140-2 is superseded by 140-3, so state which one the certification is actually against.
8. **No inaccurate Idira capability claims.** If you are unsure whether Idira does something, ask rather than assert. This is the single most common accuracy rejection.
9. **No orphaned challenges.** Every problem you raise must be answered somewhere in the brief. Raising quantum-computing or post-quantum risk and then never addressing it leaves the reader with an unanswered question and reads as filler.
10. **State the deployment model.** Where an integration supports only Self-Hosted or only SaaS, say so at the first mention, not in a footnote. An unqualified Idira product name reads as "all deployments" and is treated as a capability misstatement, not an omission.
11. **Passive voice and future tense** where present tense works. Capabilities are described in the present.

---

## 8. Submission and Review

1. **Draft.** Track A: use the JSB template from the Palo Alto Networks partner portal ("Marketing Resources" → "Joint Solution Brief Template"). Track B: use your own template and say so on submission. Self-check against §9 before submitting.
2. **Submit** your JSB request through the partner portal. It routes to Palo Alto Networks partner marketing, who share it as a Google Doc with your Idira technical reviewer.
3. **Editorial and technical review.** Findings come back as an itemized list, not as edits to your owned sections. Typical turnaround 2 to 3 business days; 5 to 7 if a revision round is needed.
4. **Publish-time approval.** Before the brief is attached to an Idira Marketplace listing, the Idira Technical Alliances team runs a final publish gate covering naming, accuracy against the listing and its Configuration guide, competitive positioning, and asset completeness. This is a separate gate from step 3.
5. **Creative production.** Track A: partner marketing submits the creative request and the Palo Alto Networks Creative Team applies the JSB layout, maximum 2 design revision rounds. Track B: you produce the final PDF; send it back for a naming and accuracy re-check before publish, since layout changes can reintroduce a corrected product name.
6. **Publish.** The finished PDF is attached to the listing as the **Solution Brief** resource.

**Expected total:** 15 to 25 business days from submission. 25 to 40 if major revisions, legal review, or customer-quote approvals are required.

**Where to ask:** cybr-bizdevtech@paloaltonetworks.com, quoting your tracking reference.

---

## 9. Self-Check Before You Submit

**Both tracks — content**

- [ ] Every Idira product name matches §5 exactly. Check the noun: it is **Idira Privileged Access Manager Self-Hosted**, not "Privileged Access Management" (that is the category, lowercase)
- [ ] No abbreviated Idira product name anywhere, including in parentheses after the full name — no "(PAM)", no "Idira EPM"
- [ ] No legacy CyberArk product names
- [ ] ® on first body-copy use of the Idira brand or product name, never in a heading
- [ ] Deployment model stated at first mention where support is Self-Hosted-only or SaaS-only (§7.10)
- [ ] Every Idira capability claim is one you can source
- [ ] No competitive positioning against Idira or Palo Alto Networks
- [ ] Every challenge you raise is answered somewhere in the brief (§7.9)
- [ ] No superlative your own evidence contradicts; standards revisions cited correctly (§7.5, §7.7)
- [ ] No em dashes, no clichés
- [ ] Customer quotes carry written external-use approval
- [ ] No product screenshots
- [ ] Spelling and grammar read cleanly — a co-branded brief carries our name too

**Track A only — structure**

- [ ] All mandatory sections present, in the §2 order
- [ ] Every section within its §3 character limit — counted, not estimated
- [ ] Key Benefits: 5 to 7 bullets, outcome-oriented, no product names
- [ ] The Challenge and The Solution opening name no product or brand
- [ ] About Palo Alto Networks boilerplate is verbatim
- [ ] Idira product spotlight left for Idira to write
- [ ] Diagram left as a placeholder, icons supplied separately, transparent-background PNG

**Track B only**

- [ ] About Idira block is accurate and current, with ® and the `paloaltonetworks.com/idira` link
- [ ] Every component in your own diagrams is labelled with an approved product name
- [ ] Final PDF sent back for a naming re-check after layout

---

## Change Log

| Version | Date | Author | Changes |
|:---|:---|:---|:---|
| 1.5 | 2026-09-30 | Idira Technical Alliances | **[Added]** AI context block, completing the agent-readable layer across the dev-kit corpus. This file is the one place in the corpus where an agent generates prose carrying the Idira name rather than generating an integration, so the block treats §5 and §7 as constraints on the agent's own output. It leads with the four rules a language model breaks by default: em dashes, which §7.4 bars outright and which are a punctuation habit rather than a decision; the §7.5 cliché list, which is close to a model's default register for marketing copy; the ban on abbreviating Idira product names even in parentheses after a first full mention, which inverts standard technical-writing practice; and §7.8's accuracy rule, since fluent generated copy invents capability claims unless the line is held deliberately. It requires the track to be established before drafting because it cannot be inferred, and records that Track B is exempt from structure and length only. It flags §7.3 competitive positioning as the hard stop with the barred gap-framing pattern quoted, noting that gap-framing is the natural way to write a joint value proposition and so will be produced while trying to be helpful. It names the two sections an agent must leave alone even when asked to write the whole brief, and states that the About Palo Alto Networks boilerplate must be copied from §5 rather than regenerated from memory. It also carries the naming specifics that get briefs returned, the §7.10 deployment-model rule tied to the two kits it affects, the product-neutrality rules for The Challenge and The Solution opening, that character limits are counted rather than estimated, the asset absolutes on screenshots and customer quotes, the evidence and standards-revision rules, and the §8 timeline with its separate publish gate. Also bumped the version and `**Last Updated:**`. No standard, limit, or prohibition was changed |
| 1.4 | 2026-09-28 | Idira Technical Alliances | **[Fixed]** The destination note drops an in-product navigation path that is not the partner's surface and was not verified against the shipped UI. Matches the same change in [`journey.md`](journey.md) v1.3 and [`marketplace-standards.md`](marketplace-standards.md) v1.5 |
| 1.3 | 2026-09-17 | Idira Technical Alliances | **[Fixed]** §8 now describes the submission and review path by role rather than by individual, and states the contact address for questions. The destination note names the Palo Alto Networks technology partner directory directly |
| 1.2 | 2026-08-17 | Idira Technical Alliances | **[Updated]** Replaced the §5 Track A "About Palo Alto Networks" boilerplate with the current corporate version — "Palo Alto Networks (NASDAQ: PANW), the global AI cybersecurity leader… 70,000 customers… Unit 42®…". The prior "world's cybersecurity leader" text was stale; several briefs independently flagged the conflict. This version is now canonical |
| 1.1 | 2026-08-13 | Idira Technical Alliances | **[Updated]** Added the §1 two-track scope split, prompted by a brief built on a partner's own template and copyright: v1.0 wrongly implied every JSB uses the Palo Alto Networks template, which would have failed an already-approved brief on structure and substituted boilerplate. Track A (Palo Alto Networks template) enforces §§2–3; Track B (partner template) is exempt on structure and length but bound by every content rule. Scoped §2, §3, §5 boilerplate, §6 diagram/screenshot, §7.1–7.2, and §8 steps 1/5 by track; split §9 into shared-content and per-track checks. **[Added]** §7.9 orphaned challenges, §7.10 deployment-model statement, and evidence-contradicting-superlative and standards-revision guidance in §7.5/§7.7 — each a real defect a review surfaced that v1.0 did not name |
| 1.0 | 2026-08-13 | Idira Technical Alliances | **[Added]** Initial partner-facing JSB standards. Consolidates the Palo Alto Networks JSB template structure and character limits, Idira naming rules, prohibited content, asset requirements, and the submission/approval path into one citable document, mirroring `marketplace-standards.md` for listings |
