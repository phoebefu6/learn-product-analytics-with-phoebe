# Agent brief - shared by every fan-out page of learn-product-analytics-with-phoebe

You are writing ONE static HTML session page. No servers, no npm. **If your target file already
exists on disk, do not write it; report that and stop.** Write the file, return its path and one
line of coverage. No HTML in your reply.

## Read first, in this order

1. The template page for YOUR track. Copy its structure, classes, SVG grammar and quiz markup
   EXACTLY, including how many options each question has:
   - Leader track (a1-a6, no code): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe/courses/a1-events-are-the-diary.html`
   - Analyst track (b1-b8, Python): `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe/courses/b1-tracking-plan-as-code.html (the bench page /Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe/courses/b8-the-activation-bench.html is also a model for tables of canon numbers)`
2. The source map: every verified number, its evidence tier, per-session coverage, the seams. Use
   ONLY its numbers; never invent a statistic; if a fact is missing, teach the uncertainty.
   `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe/materials/official-course-map.md`
3. The stylesheet `:root` block for the palette tokens: `/Users/phoebe.fu/Documents/Claude_Work/github_repo/learn-product-analytics-with-phoebe/assets/style.css`
<!-- Slimming these reads (map block only, no stylesheet) is plan step 6: adopt only after an A/B
     page passes the same gate. docs/plans/2026-09-25-course-builder-token-diet.md -->

## Page skeleton (keep every component)

toolbar (crumb EXACTLY "learn-product-analytics-with-phoebe / Leader session N of 6  (or: / Analyst session N of 8)", #toggle-all, #zoom-toggle) · masthead (eyebrow
"Learn Product Analytics with Phoebe · Leader track · Session N of 6  (or: · Analyst track · Session N of 8)", h1 with one `<span class="accent">`, .sub, .chip-row with the level chip
🟡 Core (sessions 1-4) or 🟠 Hands-on (leader 5-6, analyst 5-7), as each page's outline says, .agenda a1-a4) · main.wrap · section#intro (Part 0: kicker, .lede, .legend pills,
.callout.win "★ What you walk out with tonight") · 3 Parts, each `section.section#part-N` with
section-kicker (klabel "Part N · covers ...", h2, `.tag.concept "N min live"`), a `.lede`, ONE
figure, `details.card` accordions (summary: `.mode.live` or `.mode.self`, title, `.mini`,
`.caret ▶`), at least one `.callout.example` with `span.ex-pill` "Real world" on the page ·
section#demo-1 Build-along (kicker `.tag.demo "★ 22 min · everyone builds"`, .lede, ONE figure,
`.steps > .step`, each with a `.prompt-box.good` carrying a `span.label`; Leader pages: a no-code artifact the leader builds (a table, a one-page definition, a review checklist), prompt-boxes hold the written artifact, like a1. Analyst pages: real Python code from the named script in materials/, with the printed outputs as # comments, copied EXACTLY from that script's real output recorded in the course map)
· section#exercise Homework (ol, 4 items) · section#quiz (3 x `.quiz-q data-answer="0-based"`,
`p.qtext`, `button.qopt` "A · ..." as in your template, `p.qwhy`; one `p.quiz-score` after the
last) · section#official, h2 EXACTLY "What this session teaches, and where it came from",
`.covered > .covered-row` (pill solid ✓ / light ◐ + name + note), then the `.mono` line EXACTLY
"Every fact on this page, and its verification tier, is recorded in the course's source map." ·
section.cheat#cheatsheet (h3 "Leader session N cheat sheet (or Analyst session N cheat sheet) <span>· pin this</span>", .grid-2 of six
.cheat-item) · `.callout.next` with `.nx-pill` "Next session" · footer.pagefoot · 
`<script src="../assets/app.js?v=1">`.

Head: the template's social meta block with this page's own title/description/url;
`<title>Leader session N · <Title> - learn product analytics with phoebe  (or Analyst session N · ...)</title>`; `<link rel="stylesheet" href="../assets/style.css?v=1">`.
Nothing else external.

First `details.card` in the FIRST Part is `open`; no other. Sentence case headings. Warm
practitioner voice, concrete, never dry. Inside prompt-boxes escape `&` `<` `>`. 450 to 650 lines
is guidance about depth, never a target: never collapse whitespace, dissolve a list into a
paragraph, or drop a component to fit.

## Hard rules (a violation is rework)

- NEVER an em dash or en dash, anywhere (prose, code, aria-labels, comments). Hyphen only.
- No meta text: never "this course", "in this course", "the course teaches", "banned here". State
  the professional norm directly with its reason. The two exact estate phrases above are the only
  self-references; "session 5" cross-references are fine.
- Attribution "by Phoebe Fu". Never "built with" a tool.
- Every number comes from the map or is labelled constructed. For constructed data print "your
  numbers will differ", never invented outputs as if run.
- Contested or missing evidence: teach the disagreement; never resolve what the literature has not.
- Citations in the exact form of the map's appendix; anything marked secondary is "reported".
- NEVER "lottery" or "lotteries"; say the mechanism ("decided by row order", "arbitrary", "a
  random draw"). A verbatim quoted title in curly quotes is the only exception.
- Default to the English word. A Chinese term that is genuinely a name carries its English in
  brackets right after it, every occurrence: `店播 (brand rooms)`.
- Titles, widget ids and class names must not collide with siblings: "Power user: subagents, MCP, and the platform", "The adoption playbook", "Leading change & adoption", "Brand activation"; widget ids must start with pa- ; never reuse the id pa-activation-bench.
- Every number must appear in the course map (canon tables) or be printed by a materials/ script listed there; if you need a number that is not in the map, do not write it: teach it qualitatively instead. Facebook "7 friends in 10 days" is REPORTED (transcript of a 2012 talk) and taught as contested folklore; Slack "2,000 messages" is read at source (First Round Review 2015) and taught with its survivorship problem (teams that reach 2,000 already stayed long enough). The Power User Curve post is by Li Jin and Andrew Chen (a16z, 2018), never Andrew Chen alone. The code-assistant stream is CONSTRUCTED: say so in the lede, the figure note and the build-along label. Seams: link out in one line, never teach (retention curves/cohorts/CLV, north star/driver trees, ecommerce funnels, A/B tests, dashboard building, exec metric literacy; URLs below). Engagement curves are SAMPLED (5 percent of accounts, two hours a day): never present them as GitHub's true stickiness. Analyst pages name GH Archive files by URL. Leader pages carry no code blocks except written artifacts. Never use gold #F7B928 as a TEXT colour; it is a fill only, with ink or #614300 text on it. Quiz: 4 options each, as the templates.

## Figure grammar (hand-drawn, every figure)

Palette, ONLY these hexes (no invented greys): ink #0F1535 · muted #4B5372 · primary #1D4AFF · deep #1030B0 · mid #3558F0 · soft #BFCBFF · 50-tint #EEF1FF · faint #C8CFEA · hairline #E0E4F5 · gold fill #F7B928 · deep gold ink #614300 · gold tint #FFF4D6 · `#FFFFFF` · universal reds
`#991B1B` `#FEF2F2` `#FCA5A5` only for a wrong-way panel.

- `<figure class="zoomable">` > `<svg viewBox="0 0 880 H" role="img" aria-label="the data, not the
  shape">` > `<defs>` + `<style>` + content, then `<figcaption>🔍 Click to zoom - takeaway</figcaption>`.
  Grow H, never W.
- Prefix unique per figure, used for every class and id: <page id><letter>, e.g. a2a, a2b, a2c, a2d on a2; b5a ... on b5 (ids like a2aSk, a2aHc, a2aAr; classes a2aH, a2aL ...).
- `<defs>` holds three things with the figure prefix P: a wobble filter `id="PSk"`
(`feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="<int>"` +
`feDisplacementMap scale="2.4" xChannelSelector="R" yChannelSelector="G"`, `x="-3%" y="-3%"
width="106%" height="106%"`), a hachure pattern `id="PHc"` (7x7 userSpaceOnUse, rotate(-38), one
accent line, opacity .5), an open arrowhead `id="PAr"` (path `M1 1 L9 5 L1 9`, fill none, ink stroke
1.6). ALL shapes sit inside ONE `<g filter="url(#PSk)" fill="none" stroke="<ink>" stroke-width="2"
stroke-linecap="round" stroke-linejoin="round">`; rects carry a tiny rotation (-4 to 4 degrees for
hand-placed items, under 1 for panels). Fills: white, accent-50, the hachure for "the pile" or "the
data", and the contrast colour ONLY for the one thing the figure is about. One doodle anchor per
figure, simple strokes, never a mascot. Text classes: `.PH` 800 12px ink heading · `.PL` 600 12px
ink label · `.PS` 400 11px muted · `.PB` 800 11px contrast-ink · `.PV` 800 16-20px accent-deep
value · `.PW` 800 12px white on a fill · `.PA` 700 11px accent axis caption · `.PN` 400 12px muted
note. Hand-stacked items must not overlap as painted rects (the gate flags a pile).
- ALL `<text>` outside any filtered group, sans stack, never below 10.5px.
- Fit (owner: `diagram-kit.md`, change it there first): max chars ≈ (box width - 20) / 7 at 12px,
  6.4px/char at 11px; full-width note under 110 chars; 40px between neighbouring point labels; bottom
  note 22px below the last row, H clears it by 8px. When in doubt, shorten.
- Floor: one figure per Part plus one in the build-along. Draw the MECHANISM (the cohort flowing into activated vs not and the two return rates; an L28 histogram built from day-marks; a feature funnel saw -> tried -> used again; the suggestion shown -> accepted -> kept / edited / deleted chain; the three definitions of active as nested sets),
  never a metaphor literally, never decoration.

## Voice and honesty

Every Part gets a real-world story from the map's cases. Constructed cases say "constructed" on the
page: the code-assistant stream (copilot-constructed.py, seed 2022), any example product row like "Workspace Created", any Real world story not in the map (label it as a common pattern, never with invented numbers). No invented statistics, company names with numbers, or quotes. A lift is a correlation; never write that a behaviour "causes" return. Small groups (under 300) are flagged as small.

## Cross-links (absolute URLs)

- Customer retention (retention curves, cohorts, CLV): https://phoebefu6.github.io/learn-customer-retention-with-phoebe/
- Metric decomposition (north star, driver trees): https://phoebefu6.github.io/learn-metric-decomposition-with-phoebe/
- User journey analytics (ecommerce funnels, paths): https://phoebefu6.github.io/learn-user-journey-analytics-with-phoebe/
- Experimentation (A/B tests, causal proof): https://phoebefu6.github.io/learn-experimentation-with-phoebe/
- Business intelligence (building dashboards): https://phoebefu6.github.io/learn-business-intelligence-with-phoebe/
- Data literacy (reading metrics as an exec): https://phoebefu6.github.io/learn-data-literacy-with-phoebe/
- Hub: https://phoebefu6.github.io/learn-with-phoebe/

## Footer chain(s) and session titles

Leader: a1-events-are-the-diary.html "Events are the product's diary" -> a2-the-moment-that-predicts-staying.html "The moment that predicts staying" -> a3-engagement-you-can-defend.html "Engagement you can defend" -> a4-adopted-is-not-valued.html "Adopted is not valued" -> a5-measuring-an-ai-feature.html "Measuring an AI feature" -> a6-the-product-review.html "The product review" (a6 next = Course home ../index.html).
Analyst: b1-tracking-plan-as-code.html "The tracking plan as code" -> b2-meet-the-event-stream.html "Meet the event stream" -> b3-defining-active.html "Defining \"active\"" -> b4-hunting-the-activation-moment.html "Hunting the activation moment" -> b5-the-power-user-curve.html "The power-user curve from real rows" -> b6-adoption-funnels.html "Adoption funnels and time to adopt" -> b7-ai-feature-metrics.html "AI feature metrics" -> b8-the-activation-bench.html "The activation bench".
First page of a track: left link "← Course home". The .callout.next of a6 points to analyst session 1 or to the bench; of b7 to b8.
Footer left: "learn-product-analytics-with-phoebe / Leader session N of 6  (or: / Analyst session N of 8) · learn-product-analytics-with-phoebe · by Phoebe Fu &nbsp;·&nbsp; 📚 <a href="https://phoebefu6.github.io/learn-with-phoebe/">Learn with Phoebe ↗</a>"
Footer right: "← Prev: <title>" and "Next: <title> →" (last page: "← Prev" and "Course home").

Session titles (exact, sentence case, one accent span in h1): as in the footer chains above; h1 wraps one key phrase in <span class="accent">
