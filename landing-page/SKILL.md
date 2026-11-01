---
name: landing-page
description: Build or improve a landing page, marketing site, product homepage, waitlist or signup page with a coding agent - from brief to copy, section structure, art direction, code, browser verification and launch gates (SEO, accessibility, performance). Use when the user asks for a landing page, hero section, pricing or signup page, "marketing site", conversion improvements, or a page audit. Builds on frontend-design for look and tokens; use frontend-design alone for app screens, dashboards and components.
---

# Landing page

A landing page is one argument aimed at one action. The pipeline below keeps the agent from
defaulting to the stock hero, three icon cards and a gradient. It builds on two skills; use
them instead of repeating them here:

- `frontend-design`: art direction, tokens (`references/tokens.md`), browser checks
  (`references/verify.md`), the list of AI-default looks to avoid.
- `natural-writing`: final pass over every line of copy.

## Pipeline

Copy this into your reply and check items off:

1. [ ] **Brief.** Write it down: product, audience, the one action, traffic source, proof you
       actually have, constraints (stack, brand, deadlines). Ask one question if audience or
       action is unclear; otherwise state your assumptions and go.
2. [ ] **Copy.** Customer language first, then headline last. See `references/copy.md`.
3. [ ] **Structure.** One argument, an ordered section list with each section's job, CTA and
       proof placement. See `references/structure.md`.
4. [ ] **Art direction and tokens.** Follow `frontend-design`: plan, review the plan against
       the brief, then tokens. Show the user the copy, structure and plan before building if
       the stakes are high; otherwise continue.
5. [ ] **Build.** Use the project's stack. With none, plain HTML and CSS for one page, or
       Astro for several. Component names and tokens from the plan; no raw hex.
6. [ ] **Verify.** `frontend-design/references/verify.md`, then the launch gates in
       `references/launch-gates.md`. Fix and re-run until they pass.
7. [ ] **Report.** What was built, which checks ran and passed, which could not run, and
       what is still a placeholder.

## Rules that apply throughout

- **Never invent proof.** No made-up testimonials, logos, user counts, statistics, ratings or
  deadlines. If real proof is missing, use an obvious placeholder (`[Quote from customer]`)
  and list it in the report. Urgency only when literally true.
- **Never fake the conversion path.** A form with no endpoint says so in the report and in
  the code. Do not show a success message for a submission that goes nowhere.
- **One primary action** per page. Repeat the same CTA; do not add competing ones.
- **Use real content.** A real product screenshot or demo beats stock art. If none exists,
  say what is missing and design the slot, not a fake.
- **Existing site wins.** On an existing project, match its brand and stack, and change only
  what the request covers. A copy-only request stays copy-only.

## Audit mode

When asked to review or improve an existing page, skip the pipeline. Run the live page
through `verify.md` and `references/launch-gates.md`, then compare it with the checklists in
`references/copy.md` and `references/structure.md`. Report findings tied to what you
observed, ordered by likely impact, and list the checks you could not run. Do not claim a
conversion improvement without real outcome data; a change is a hypothesis until measured.
