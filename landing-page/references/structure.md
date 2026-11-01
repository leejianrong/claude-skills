# Landing page structure

Build the page as one sequenced argument: problem, stakes, mechanism, proof, action.
Features sit inside that argument, not in a standalone grid. If sections can be shuffled
without hurting comprehension, there is no argument yet.

## Table of contents
- Hero
- Section order and length
- CTA placement
- Proof placement
- Forms
- Layout devices
- Output

## Hero

The first screen contains exactly:
- One benefit-focused headline and one subhead.
- One primary CTA.
- One trust cue: a specific number, one named review, or one recognizable customer.
- A real product shot, short muted loop or live demo, not stock art.

The hero is the most characteristic thing in the subject's world (see `frontend-design`),
not the template of big number, small label and gradient. Treat the fold as a trust test:
does the first screen establish relevance and message match immediately.

## Section order and length

- Start from this spine and adapt it to the argument: hero, the problem in the customer's
  words, how it works, proof, objections, pricing or offer detail, final CTA. Do not ship
  the spine unexamined.
- Length follows purchase risk: about 5 to 7 sections for a simple or low-cost offer, about
  10 to 12 for high-ticket B2B that needs objection handling and a staged CTA (for example
  "See a demo", then "Talk to sales").
- For each section, write down its job in one sentence. A section with no job is cut.
- **Reorder test:** if you can reorder the sections and nothing breaks, redo the structure.

## CTA placement

- One primary action, repeated roughly every 400 to 600px of scroll and once at the bottom.
  At most one lower-friction secondary action, such as a product tour.
- No co-equal buttons side by side.
- On mobile, a sticky CTA. Do not stack it on top of an above-the-fold CTA.

## Proof placement

Next to the claim, the CTA, the form and the pricing it supports. Proof rules are in
`copy.md`.

## Forms

- Defaults: about 3 fields for consumer offers, 4 to 5 for B2B. Every extra field needs a
  reason in the brief.
- One step under about 5 fields. Multi-step at 5 or more fields or when answers branch.
- Ask for email first so an abandoned form still yields a lead.
- Cold traffic gets minimal fields; warm, high-intent traffic can take more.
- Label every field, show validation errors beside the field, and say what happens after
  submit.
- If the form has no backend, say so (see SKILL.md).

## Layout devices

- A bento grid fits multi-feature products in the features or proof section: 5 to 9 cells
  with one anchor cell about twice the size of the next, reprioritized for mobile. For one
  dominant offer, use a linear sequence instead.
- Do not add numbering, eyebrows or decorative dividers unless they carry information;
  `frontend-design` explains why.

## Output

Before building, write down: the ordered section list with each job, the hero layout, CTA
and proof placements, form decisions, and the result of the reorder test.
