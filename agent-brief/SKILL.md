---
name: agent-brief
description: Write, trim, or audit the CLAUDE.md/AGENTS.md file an agent harness loads automatically at a repo's root. Covers the discoverability filter for what belongs in it, size discipline, WHAT/WHY/HOW structure, progressive disclosure, and when to add a rule versus let it go. Use when creating a repo's first agent-brief file, an existing one has grown bloated or stale, an agent keeps missing a convention, or after the second time an agent makes the same mistake.
---

# Agent brief

CLAUDE.md and AGENTS.md are the same idea under different names: a file an agent harness
loads into every session, unconditionally, before it sees the task. That makes it the
highest-leverage file in the repo — and the easiest one to ruin by treating it as a dumping
ground.

This skill is the deep dive on writing and maintaining that file well. For the broader case
for having one at all — alongside permission allowlists, worktree isolation for parallel
agents, and orchestrating multiple agents — see `dev-playbook`'s
`references/agent-enablement.md`; this skill doesn't repeat that ground.

## The filter: could the agent find this itself?

Before adding anything, ask whether an agent reading the repo would already know it.

**Leave out** — the agent gets these for free:
- A codebase overview or file-by-file description — it explores the tree as needed
- Framework conventions (how Express routing works, how React hooks work) — training data
- A dependency list — `package.json`/`go.mod`/`requirements.txt` already say this
- Anything the README already says — the agent reads the README too

**Put in** — this is genuinely unrecoverable without being told:
- Non-standard build/test/run commands (`uv pip install -e ".[dev]"`, not plain `pip install`)
- Tool substitutions ("use `podman`, not `docker`")
- Constraints that aren't visible in any one file ("the UID in the Dockerfile must match
  `runAsUser` in the Go service — they drift silently otherwise")
- Files that must never be committed, beyond what `.gitignore` already blocks
- Review/merge standards (CODEOWNERS approval required, DCO sign-off, squash-only)
- Where the deep docs live, so the agent can go find them

A file that only ever holds this second category stays short by construction — the filter
does the pruning for you.

## Structure: WHAT / WHY / HOW

Three sections cover nearly everything worth keeping:

- **WHAT** — stack and repo layout, at the level of "here's the map," not a tour of every
  directory.
- **WHY** — what the project is for, briefly, when it isn't obvious from the name.
- **HOW** — the exact commands to install, run, test, and check; the workflow conventions
  (branch-per-slice, PR-only, how migrations land); a short "trust the code over the docs
  where they disagree, and fix the docs" line, so a stale sentence elsewhere in the repo
  doesn't get treated as authoritative.

Put the highest-priority material first — a long file degrades gracefully at the top and
badly at the bottom; don't bury the one rule that actually matters under a wall of
less-important context.

## Size discipline

Target well under 150 lines; treat 300 as a hard ceiling, not a goal. Every line in this
file taxes every single session whether or not it's relevant to the task at hand, and a
bloated file doesn't just waste tokens — past a point, agents start ignoring instructions
wholesale rather than selectively filtering the noise. A CLAUDE.md that tries to cover every
edge case is worse than one that covers the five that actually recur.

When the file grows past budget, don't trim by deleting — restructure with progressive
disclosure:

```
agent_docs/
├── building.md
├── testing.md
└── conventions.md
```

Then point to them from the root file: "Read `agent_docs/testing.md` before writing tests."
The root file stays a table of contents; depth lives one level down, loaded only when
relevant.

Reference code by pointer, not by copy: `see auth/middleware.go:42`, not a pasted snippet
that will drift out of sync with the code it was copied from.

## When to add a rule

Add a rule on the **second** occurrence of the same mistake, not the first. A rule earned
from one incident is often actually specific to that incident; a rule earned from two is a
real pattern. Committing a line to this file every time something goes wrong once turns it
into a graveyard of one-off incident reports that dilutes the handful of rules that actually
matter every session.

## One file, not several

Keep a single canonical file (`AGENTS.md` is the vendor-neutral name) rather than
maintaining near-duplicate copies for `CLAUDE.md`, `.cursorrules`, and whatever the next
harness calls it. Where a harness needs its own filename, import rather than duplicate —
e.g. a one-line `CLAUDE.md` containing `@AGENTS.md` — so there's exactly one place to keep
accurate.

## Maintenance

Review the file when the architecture changes, not only when onboarding a new project — a
convention that was true six months ago and never got removed is actively misleading, not
neutral. Update the brief in the same PR that changes the convention it describes, the same
discipline as keeping a README from going stale.

See `references/audit-checklist.md` for a pass over an existing file.
