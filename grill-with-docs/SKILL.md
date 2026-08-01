---
name: grill-with-docs
description: A relentless, self-contained interview that sharpens a plan or design and captures the results as docs (a glossary + decision register in CONTEXT.md and ADRs in docs/adr/). No external skill dependencies.
disable-model-invocation: true
---

# Grill with docs

A relentless product-owner interview that turns a rough idea (or a set of draft
plans) into **shared language + explicit, recorded decisions**. It is
**self-contained** — it does not require any other skill. (If `/grilling` or
`/domain-modeling` happen to be installed you may delegate to them, but this
skill inlines the full method and needs neither.)

## Two modes

This skill is used at two different points and behaves differently:

- **Mode 1 — Initial grilling + domain modeling.** Sharpen a raw idea into a
  glossary, a decision register, and ADRs. Run this first, before any PRD or
  shaping.
- **Mode 2 — Consolidation / extract-ADRs + consistency check.** After downstream
  planning docs exist (PRD, shaping outputs), review them, reconcile against the
  decisions of record, extract any missing ADRs, and surface inconsistencies.

Detect which mode you're in: if only the raw idea (`REQS.md`) exists → Mode 1; if
`FRAME.md`/`SHAPING.md`/`BREADBOARD.md`/`SLICES.md` also exist → Mode 2.

## Fresh-context / source awareness

This skill is usually invoked in a **fresh chat with no prior conversation** —
do **not** stall waiting for context. Read the source docs and work from them:
`REQS.md` (the raw idea) plus any existing `CONTEXT.md`, `PRD.md`,
`docs/adr/*.md`, `QUESTIONS.md`, and shaping docs.

## Doc locations (path-flexible)

Default to the project's convention — `REQS.md`, `CONTEXT.md`, and `QUESTIONS.md`
may live at the **repo root or under `docs/`**; detect which and match it. ADRs
always go in **`docs/adr/NNNN-title.md`**. Never hardcode repo-root paths.

---

## Mode 1 — Initial grilling + domain modeling

### The interview

Be relentless and specific. Interrogate the idea like a skeptical product owner:
surface hidden assumptions, forks in the design, scope boundaries, and anything
that would change the architecture. Prefer questions about **mechanics and
consequences** over vague ones.

**Log all questions in `QUESTIONS.md` up front, then add more as you go.** Dumping
the whole question set first lets the user answer several per turn, which is much
faster than one-at-a-time. Group by topic and tag each with a priority:

- **P0** — blocks the architecture (must resolve before the PRD)
- **P1** — shapes a stage / important
- **P2** — nice to pin down; can take a sensible default (mark `ASSUMED` and
  state the default so the user can correct it)

Track a status per question: `OPEN` · `ANSWERED` · `DEFERRED` · `ASSUMED`.

### Answer convention (avoid drift)

The user answers **inline in `QUESTIONS.md`**, directly beneath each question,
flipping its status `OPEN → ANSWERED`. **Do not create a parallel hand-copied
`ANSWERS.md`** — a duplicated question list drifts from the canonical one. If a
separate answer sheet is genuinely wanted, generate it from `QUESTIONS.md`; never
maintain both by hand.

### Domain-model outputs

As answers land, distill them into two kinds of durable doc:

1. **`CONTEXT.md`** — the shared source of truth:
   - a **glossary** fixing what each key term means (use these terms
     consistently everywhere downstream), and
   - a **decision register** table: `id | decision | status | ADR`
     (e.g. `D1 | single in-process pipeline | Accepted | ADR-0001`).
2. **`docs/adr/NNNN-title.md`** — one ADR per architectural decision, sections:
   **Status · Date · Deciders · Context · Decision · Consequences.** Number
   sequentially. Capture the *why*, alternatives considered, and the trade-off —
   not just the choice.

### Final consistency pass (A2)

Before handing off, re-read `CONTEXT.md` + `docs/adr/*.md` and grill the user on
any remaining inconsistencies or contradictions between decisions. Fold the
resolutions back into the register and ADRs.

---

## Mode 2 — Consolidation / extract-ADRs + consistency check

Run after shaping/PRD docs exist, to keep every level of the plan consistent and
to capture decisions that were made downstream but never recorded.

1. **Review** the downstream docs: `FRAME.md`, `SHAPING.md`, `BREADBOARD.md`,
   `SLICES.md`, and any `SPIKE-*.md`.
2. **Cross-check** them against the decisions of record — `CONTEXT.md`,
   `PRD.md`, `docs/adr/*.md`. Look for: contradictions between a doc and an ADR,
   scope drift, and **load-bearing decisions that lack an ADR**.
3. **Extract missing ADRs.** Any architectural decision that the plan now depends
   on but that has no ADR gets one (and a row in the CONTEXT register).
4. **Log inconsistencies + open questions** in `QUESTIONS.md` (same convention as
   Mode 1). Make edits where you're confident; **confirm with the user** where a
   fix is a real decision, not just a typo.
5. Ripple every change through all affected levels so the docs stay in sync
   (a change to an ADR must reach CONTEXT, the PRD, and the shaping docs).

This pass is not a rubber stamp — it routinely surfaces genuine conflicts (e.g. a
requirement that contradicts an accepted ADR, or an entity/behavior the model
never pinned down). Treat it as real work.
