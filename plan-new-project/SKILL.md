---
name: plan-new-project
description: Plan a new software project fast. Turn a rough idea into a PRD-grade plan, ADRs and implementation slices in one short interview instead of a multi-step process. The agent answers its own questions and escalates only the decisions that genuinely need the user. Use when starting a greenfield project or feature and you want a plan today, not a document trail over a week. Also resumes a project stalled partway through a longer FRAME/PRD/SHAPING-style planning process.
license: MIT
metadata:
  author: jian
  version: "0.1.0"
---

# Plan a new project

Role: a sceptical product owner who does the homework before asking questions.

Goal: an idea becomes `PLAN.md` + ADRs + `SLICES.md` in **one** interview round,
with the same decision coverage a long process would have reached.

## When to apply

- "Help me plan this project / feature"
- A rough idea exists (in a file, or just in the user's head) and the next thing
  needed is a plan an agent can build from
- A project stalled partway through a longer planning process (partial
  FRAME.md/PRD.md/SHAPING.md/ADRs on disk) and needs finishing quickly (see
  "Resume mode")

## When not to apply

- The plan already exists and the job is implementation
- The project is large enough that competing architectures need a real bake-off,
  with people to convince — that kind of multi-round consensus process is
  outside this skill's scope.

## Inverted grilling

**The agent answers the questions; the user only breaks ties.**

A long planning process is slow because it asks the user to author fifty
decisions from scratch. Coverage is not the problem, authorship is. So derive the
full decision set, answer every item yourself with a stated default, and escalate
only the few where a wrong default is expensive and the idea itself does not
settle it. The coverage stays the same and it costs the user a fraction of the
effort.

Never quietly skip a decision category to save time. Mark it `ASSUMED` and move
on, so a bad default is visible rather than absent.

## Budget

These hold even when a project seems to want more.

- **1 grill round** is the target and **3 is the hard cap.**
- **Max 12 forks** in round 1, fewer after. If more qualify, keep the ones where
  being wrong costs most and demote the rest to `ASSUMED`.
- **4 artifacts**, listed below, and no others.
- Every round must strictly reduce open forks. A round that adds more than it
  closes means the scope is unstable, so say so and ask the user to cut scope.

## Artifacts

There is no cross-document reconciliation step because there are only four files.

| File | Contains |
|---|---|
| `PLAN.md` | Problem, solution, users, scope boundary, requirements, the shape (mechanisms), affordances, implementation decisions, testing approach, out of scope |
| `docs/adr/NNNN-*.md` | One architectural decision each, with the why and what was rejected |
| `SLICES.md` | Vertical demo-able increments, each with a build plan and a tiered test plan |
| `QUESTIONS.md` | The decision register: every question, its status, its answer, and where it landed |

`PLAN.md` deliberately absorbs what a longer process splits across FRAME, PRD,
SHAPING and BREADBOARD. It is one narrative document with sections, so nothing can
drift out of sync with anything else.

Path convention: put `PLAN.md`, `SLICES.md` and `QUESTIONS.md` in `docs/` if that
directory exists, else the repo root. ADRs always go in `docs/adr/`.

Skeletons live in `assets/templates.md`. Read that file in phase 3, not before.

## Phases

### P0: Orient (no user input)

Read what exists and decide the mode:

- **Fresh**: only a rough idea, maybe a `REQS.md`. Start at P1.
- **Resume**: artifacts from the longer process exist. See "Resume mode".
- **Nothing written**: the idea is only in the conversation. Capture it into
  `PLAN.md`'s Problem section as you go, and do not demand a `REQS.md` first.

State the mode in one line, then continue without waiting.

### P1: Derive and self-answer (no user input)

1. Walk the **coverage checklist** below. For each category, write the specific
   questions this project actually raises, concrete about mechanics and
   consequences rather than vague ones like "what about scalability".
2. Answer every one yourself, using the idea, the constraints already stated, and
   what the ecosystem actually offers. Where a checkable fact decides it, search
   or read the code instead of guessing.
3. Score each answer on two axes:
   - **Confidence**: can the idea, the constraints, or a checkable fact settle it?
   - **Cost of being wrong**: rework in days if the default is wrong. Anything
     that changes the data model, the primary user, the scope boundary, or a
     dependency you cannot swap later counts as high.
4. Classify:
   - **FORK** = low confidence **and** high cost. These go to the user.
   - **ASSUMED** = everything else. Record the default and the reasoning.
   - **DEFERRED** = genuinely not needed until after this milestone.

Do not show the user the whole set. Write it to `QUESTIONS.md` and take only the
forks to P2.

### P2: Grill, once (the human round)

Present the forks as one compact numbered list, three lines each and no more:

```
F3. Handwritten charts in scope, or engraved only?
    Recommend: engraved only. Every offline OMR engine is trained on engraved
    scores, and handwriting needs a different model plus probably a research spike.
    Changes: whether the import pipeline needs a second engine, and whether
    "photo of my own manuscript" is a supported story at all.
```

Rules for this round:

- Lead with a recommendation. Without one the fork is homework handed back, which
  is what this skill exists to avoid.
- Say **what changes** depending on the answer, because that is what makes a fork
  answerable in one pass.
- Tell the user they can reply in a single message, mix and match, and answer any
  fork with "your call" to accept the recommendation.
- Ask nothing you have already answered, nothing whose answer you could look up,
  and nothing that is merely interesting.
- Push back once, briefly, if an answer contradicts something already decided or
  the stated scope. Then take the user's decision and move on.

If the answers open genuinely new forks, run at most two more rounds, each smaller
than the last.

### P3: Write (no user input)

Read `assets/templates.md`, then write all four artifacts in one pass.

- One ADR per decision that is architectural, expensive to reverse, or something a
  future agent would otherwise re-litigate. User-answered forks almost always earn
  one, and `ASSUMED` items earn one only if load-bearing.
- `PLAN.md` cites ADRs by number rather than restating their reasoning. This is
  the only place duplication could creep in, so keep it a citation.
- Slices are vertical and each ends in something demonstrable. A slice with no
  visible output is a horizontal layer, so merge or resequence it.
- Slice one should exercise the riskiest mechanism rather than the easiest. If the
  project lives or dies on one unknown, slice one confronts it.
- Test plans are one-line descriptions under `### End-to-end`, `### Integration`
  and `### Unit`. The end-to-end lines are the acceptance criteria.
- Where a slice depends on an `ASSUMED` decision, mark it inline in that slice, so
  it is obvious what rests on a default rather than a decision.

### P4: Adversarial self-review (short user checkpoint)

Re-read the four artifacts as an opponent looking for reasons the build fails:

- A requirement no slice delivers, or a slice serving no requirement
- An `ASSUMED` default that, if wrong, invalidates a slice
- Two decisions that contradict each other
- A dependency whose licence, offline story or platform support was never checked
- A slice whose acceptance criteria are not actually checkable

Fix what you can, report only what you cannot as a short list, and stop. Do not
open a new grill round for tidying.

## Coverage checklist

This is what makes a single round defensible. Every category gets answered or
explicitly deferred, in writing, for every project.

1. **Primary user and actors.** Who is this for first? Humans, agents, both? When
   they conflict, who wins?
2. **Scope boundary.** What is in this milestone and what is explicitly out. The
   out-list is as load-bearing as the in-list.
3. **Core data model and identity.** What are the entities, and how is a thing
   addressed? Stable IDs or positional references? Does identity survive export
   and re-import?
4. **State and storage.** Where does data physically live, and can the user see
   and diff it?
5. **Concurrency and conflict.** Two writers, one of them possibly an agent. Who
   wins, and is the losing write rejected or silently lost?
6. **Interfaces and contracts.** Every surface (UI, CLI, API), and whether they
   share one write path. For agent-facing surfaces: machine-readable output,
   meaningful exit codes, and a cheap read projection to reason over.
7. **Failure behaviour.** What happens on bad input, partial results, or an
   unavailable dependency. A hard error, a partial result with gaps flagged, or
   nothing at all.
8. **External dependencies.** Each one named, with its licence, whether it runs
   offline, and what the fallback is. Do not leave a pick as a shortlist.
9. **Runtime and deployment.** Where it runs, how it is started, what crosses the
   process or container boundary, and what it may assume about the host.
10. **Measurable success.** How you would know it works, stated so a test could
    check it. Replace every "correctly" and "fast" with a number or a procedure.
11. **Security and secrets.** What is trusted, what is validated, and what must
    never be logged or committed. Say "nothing sensitive here" if that is true.
12. **Versioning and migration.** Whether stored data or a public contract will
    need to change shape later, and whether that is planned for or deferred.

Add domain categories when the project needs them, and never drop one silently.

## Resume mode

For a project with partial planning artifacts already on disk from a longer,
document-heavy process. The point is to salvage the work rather than redo it.

1. Inventory what exists: `REQS.md`, `QUESTIONS.md`, `CONTEXT.md`, `docs/adr/*`,
   `docs/PRD.md`, `FRAME.md`, `SHAPING.md`, `SPIKE-*.md`, `BREADBOARD.md`,
   `SLICES.md`, `ARCHITECTURE.md`.
2. **Answered questions and accepted ADRs are authoritative. Never re-ask them.**
   An existing "settled" or "already decided" section is binding.
3. Adopt the existing open questions as the decision set instead of deriving a new
   one, then run P1's self-answer and classification over them. A file with forty
   unanswered questions usually yields under a dozen real forks.
4. Run the coverage checklist over the adopted set and add only what is missing.
5. Fold the old documents into the four artifacts: `CONTEXT.md` glossary and
   decision register into `PLAN.md` plus the ADRs, `FRAME.md` into Problem and
   Outcome, `docs/PRD.md` into Solution, user stories and decisions, `SHAPING.md`
   and `BREADBOARD.md` into the shape and affordance sections.
6. Leave the superseded files on disk and add one line at the top of each pointing
   at `PLAN.md` as the live document. Deleting someone's planning history is not
   this skill's call, so say they can remove them once happy.
7. Keep ADR numbering continuous with what is already there.

## Autonomy

The default is one grill round, as above. The invocation may override it.

- `auto`: no grill. Everything becomes `ASSUMED`, every fork is decided with its
  recommendation, and the report lists what was decided on the user's behalf and
  what it costs if wrong. Use this when the user says "just decide".
- `deep`: allow up to 3 rounds and raise the fork cap. Use this when the stakes
  are high, or when P1 finds many high-cost unknowns.

## Anti-bloat rules

Planning skills fail by producing volume.

- No competing-shapes bake-off or R × S fit matrix unless two architectures are
  genuinely live. One shape of record is normal, so say why it was chosen.
- No exhaustive user-story enumeration. Write enough stories to pin the behaviour
  and stop. Stories are not a coverage mechanism, the checklist is.
- No separate frame, breadboard, context or architecture file. They are sections.
- No status commentary, no restating the process back to the user, and no summary
  of a document you just wrote and they can read.
- If a section would only restate its heading, delete the section.

## Handoff

`SLICES.md` is the build handoff. Both optional next steps come from existing
skills:

- `/pandan-pm` (or the `pandan` CLI directly) to publish the slices to the
  Pandan board, one epic per slice
- `/dev-playbook` for test layering, quality gates and CI on the way in
