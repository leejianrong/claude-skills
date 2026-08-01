# The implementation specification planning process

Start from a detailed product description and turn it into implementation
specifications, using `/grill-with-docs` + `/shaping` + the Simple Kanban skills.

Install the shaping/grilling skills if missing:

```shell
npx skills add -g mattpocock/skills --skill grill-with-docs
npx skills add -g rjs/shaping-skills --skill shaping
```

## Documents

### Exist prior to this session

- REQS.md - initial idea, handwritten capture of thoughts
- QUESTIONS.md - scratch file primarily used by `/grill-with-docs`
- CONTEXT.md - shared glossary + decision register, created via `/grill-with-docs`
- docs/adr/*.md - architectural decision records
- docs/PRD.md - problem, solution, user stories, decisions, out-of-scope
- FRAME.md - succinct product definition, created via `/shaping`
- SHAPING.md - requirements, shapes, RxS fit matrix, selected shape
- SPIKE-*.md - ideation on requirement/shape changes to improve RxS fit
- BREADBOARD.md - affordances and how they connect

### Produced during this session

- SLICES.md - breadboard split into vertical implementation increments
- SLICE-V*.md - one detailed slice each (build plan + test plan)
- ARCHITECTURE.md - technical architecture / committed stack
- TESTING.md - audit of the slice test plans, with suggested fixes
- A **Simple Kanban board** - one epic per slice, one card per build-plan item
  (replaces file-based issue tickets)

## The grill cycle

Every grill is the same loop. It is where conflicting information gets resolved, and
it is the part of this process worth protecting. Define it once here; the steps below
point at it.

1. `/grill-with-docs` on {target}, reading {context}. Add all questions up front and
   as you go to QUESTIONS.md (continue the numbering). Grill me; change nothing else yet.
2. — you answer one or more questions —
3. Apply: create/update ADRs in docs/adr/*; ripple the resolutions into CONTEXT.md +
   docs/PRD.md + any other affected docs (and TESTING.md + the SLICE-V*.md test plans
   when the grill covers tests); mark each question resolved in QUESTIONS.md with a
   pointer to where it landed; add any new questions.
4. Repeat 2-3 until no open questions remain.

## Guidance

- Use a **fresh chat for each lettered step**; the previous step's outputs are on disk.
- Keep track of which step (and sub-prompt) you are on.
- Model selection: Low -> Haiku / GPT5.4-low; Medium -> Sonnet-medium / GPT5.4-medium;
  High -> Opus-max / GPT5.5-xhigh.

## Steps

### A - Slice  (High, fresh)

Break the breadboard into vertical, demo-able increments, then detail each with a
build plan and a tiered test plan.

```text
/shaping
status: completed through breadboarding
context: FRAME.md + CONTEXT.md + docs/PRD.md + docs/adr/*.md
shaping outputs: SHAPING.md + BREADBOARD.md
task: slice — produce SLICES.md (candidate vertical slices, each ending in demo-able UI)
```

After a quick sanity check of the candidates:

```text
create one SLICE-Vn.md per slice (SLICE-V1.md, …). Each contains:
- Affordances, Build Plan (ordered steps), Demo
- a "## Test Plan" with "### End-to-End Tests" (the acceptance criteria),
  "### Integration Tests", and "### Unit Tests" — one-line descriptions only
```

### B - Architecture first pass  (Medium, fresh)

Commit to a stack. Generate the architecture doc from the template; its first-pass
defaults are the targets of the grill in step C.

```text
create ARCHITECTURE.md based on CONTEXT.md + docs/PRD.md + BREADBOARD.md + SLICES.md +
docs/adr/*.md using the template at
https://raw.githubusercontent.com/timajwilliams/architecture/refs/heads/main/architecture.md
```

### C - Grill the stack and the tests  (High, reuse B's window)

One grill cycle (see above) covering architecture decisions, unmade technology
choices, and the slice test plans together.

```text
/grill-with-docs
- read FRAME.md + CONTEXT.md + ARCHITECTURE.md; read other *.md on demand
- read the "## Test Plan" section in each SLICE-V*.md
- grill me on:
  (1) architectural decisions whose first-pass defaults may be wrong;
  (2) technology choices not yet made — languages / libraries / frameworks /
      environments / deployments / persistence / APIs / 3rd-party services;
  (3) the test plans — missing, duplicate/overlapping, miscategorised, or
      out-of-slice tests, and any test that reveals a planning/architecture problem
- add all questions up front and as you go to QUESTIONS.md
- write the test-plan findings to TESTING.md
- do nothing else yet
```

Then run the grill cycle's apply half on your answers, adding:

```text
- update the "## Test Plan" section in each SLICE-V*.md to match the resolutions
```

Notes:

- **Escape hatch:** if a project's test plans are large, split C into two grill cycles
  (stack first, then tests) so neither pass is overloaded. The default stays combined.
- Optional, out of band: for one specific library/framework pick, ask a search engine
  directly — "help me choose X for Y; suggest 3 with tradeoffs; context: …".

### D - Publish to board  (Medium, fresh)

Turn the slices into a working backlog on Simple Kanban instead of files.

```text
/project-manager-kanban
- create a new Simple Kanban board named for this product
- from SLICES.md + SLICE-V*.md: one epic per slice; one card per "## Build Plan"
  item, linked to its epic; group tightly-coupled items only when >= 80% sure
- put each slice's Demo + Test Plan acceptance criteria on its epic
- (optional) add a short manual-test line to each epic: one happy-path and one
  failure-path scenario the user can run by hand to confirm the slice works
```

Uses `/simple-kanban` under the hood for the board operations.
