# Templates

Read this in phase 3, when writing. These are skeletons rather than fixed forms,
so drop any section that has nothing to say instead of filling it with a
restatement of its heading.

---

## PLAN.md

```markdown
# <Project>: Plan

Status: <draft | agreed> · Milestone: <MVP | vN>

## Problem

What is broken or missing, from the user's point of view. Two paragraphs at most.

## Solution

What we are building, from the user's point of view. What it feels like to use.
Not the architecture.

## Users and actors

Who this serves, primary first. Include non-human actors (agents, CI, cron) where
they are real. State who wins when two actors want different things.

## Scope

**In this milestone.** <bulleted, specific, testable>

**Out.** <bulleted. As load-bearing as the in-list. Say why for anything a reader
would expect to be in.>

## Requirements

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | <the core goal, one line> | Core goal |
| R1 | <…> | Must-have |
| R2 | <…> | Nice-to-have |

Nine top-level maximum. Beyond that, group into R3.1, R3.2 and keep the top level
scannable. Requirements state what is needed, never how.

## Shape

The mechanisms being built. Each part is something you build or change, not an
intention. Cite ADRs where a part rests on a decision.

| Part | Mechanism | ADR |
|------|-----------|-----|
| S1 | <concrete mechanism, e.g. "single write path: HTTP PATCH → validate → persist → broadcast"> | ADR-0003 |
| S2 | <…> | |

Co-locate data with the feature that needs it. No horizontal "data model" part.

## Affordances

**UI.** What the user sees and can act on.

| Affordance | Place | Wires to |
|------------|-------|----------|
| <…> | <screen or view> | <what it calls> |

**Non-UI.** Stores, handlers, commands, jobs, services.

| Affordance | Kind | Wires to |
|------------|------|----------|
| <…> | <store / handler / CLI command> | <…> |

## Implementation decisions

Prose or bullets. Modules and their boundaries, contracts, schemas, the shape of
each interface. Cite ADRs rather than repeating their reasoning. No file paths and
no code, except where a type or schema states a decision more precisely than
prose can.

## Testing approach

The seams being tested, preferring the fewest and highest. What makes a good test
here (external behaviour, not internals). Per-slice test plans live in SLICES.md.

## Assumed defaults

Decisions taken on the user's behalf that a reader should know are defaults, not
conclusions. One line each, pointing at the QUESTIONS.md row.

| ID | Assumed | Cost if wrong |
|----|---------|---------------|
| Q7 | <…> | <…> |

## Open risks

What could still sink this, and the earliest slice that would reveal it.
```

---

## docs/adr/NNNN-<kebab-title>.md

```markdown
# ADR-NNNN: <decision, stated as a choice made>

- Status: Accepted
- Date: <YYYY-MM-DD>
- Deciders: <who>

## Context

The forces in play: constraints, the requirement driving this, what was unknown.
Enough that a reader six months out does not need the conversation.

## Decision

What we are doing, in the active voice. Specific enough to be checkable.

## Alternatives considered

| Option | Why not |
|--------|---------|
| <…> | <…> |

## Consequences

What this buys, what it costs, what it forecloses, and what now has to be true.
Include the bad consequences, since a list of only benefits means the trade-off
was never examined.
```

Number sequentially from the highest existing ADR. One decision per file.

---

## SLICES.md

```markdown
# <Project>: Slices

Vertical increments. Each ends in something you can demonstrate. Slice 1
confronts the riskiest unknown.

## V1: <name>

**Delivers:** R0, R2 (partial)

**Build plan**

1. <ordered, concrete step>
2. <…>

**Demo:** <what you do, and what you see, to know it works>

**Rests on assumptions:** Q7 (<one-line restatement>), and if wrong <impact>

### Test plan

#### End-to-end

- <one line per test. These are the acceptance criteria.>

#### Integration

- <one line per test>

#### Unit

- <one line per test>

## V2: <name>

<same structure>
```

Every slice ends in visible output, and no slice depends on a later one. The
end-to-end lines are the acceptance criteria, so they have to be checkable by a
person or a test rather than by judgement.

---

## QUESTIONS.md

The decision register. Every question, whoever answered it, and where the answer
landed. This is the audit trail, so it stays accurate even after the plan is
written.

```markdown
# Questions

Statuses: `DECIDED` (user answered) · `ASSUMED` (default taken, correct it if
wrong) · `FORK` (waiting on the user) · `DEFERRED` (not needed this milestone).

## Open forks

<empty when the round is closed>

| ID | Question | Recommendation | What changes |
|----|----------|----------------|--------------|
| F1 | <…> | <…> | <…> |

## Register

| ID | Question | Status | Answer or default | Landed |
|----|----------|--------|-------------------|--------|
| Q1 | <…> | DECIDED | <…> | ADR-0002 |
| Q2 | <…> | ASSUMED | <…> | PLAN §Shape |
| Q3 | <…> | DEFERRED | <why it can wait> | n/a |

## Coverage

One row per checklist category, so a skipped category is visible.

| Category | Covered by |
|----------|-----------|
| Primary user and actors | Q1, Q18 |
| Scope boundary | Q5, Q7 |
| Data model and identity | Q25 |
| State and storage | Q19, Q22 |
| Concurrency and conflict | Q21 |
| Interfaces and contracts | Q23, Q24 |
| Failure behaviour | Q28 |
| External dependencies | Q11, Q12 |
| Runtime and deployment | Q2 |
| Measurable success | Q17 |
| Security and secrets | <…> |
| Versioning and migration | <…> |
```

When resuming a project, keep the original question IDs. Continuity of numbering
matters more than tidiness, because other documents already cite them.
