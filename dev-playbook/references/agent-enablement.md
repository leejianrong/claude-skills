# Agent enablement

Coding agents are now first-class contributors. The same gates that keep humans honest keep
agents honest, but agents need one thing more: the conventions written down where they'll read
them every session. That artifact is the highest-leverage thing in the repo.

## The agent brief (CLAUDE.md / AGENTS.md)

A markdown file at the repo root that every agent session loads. What makes it work:

- **Build status, honestly, up front.** A short table of what's built and what isn't, with a
  standing instruction: **trust the code over the docs where they disagree, and update the
  docs.** This stops an agent from confidently acting on stale prose.
- **Exact commands.** The real invocations to install, run, test, and check — copy-pasteable,
  with the actual ports and paths. Not "run the tests" but the literal command per package.
- **Workflow conventions, spelled out.** Branch-per-slice, PR-only, the merge-vs-squash choice,
  the pre-push expectation, how migrations land. If it's a rule, write it here; an agent
  follows what's written, not what's assumed.
- **Layout and where things live.** A short map of the directories and what each owns, so an
  agent navigates instead of guessing.
- **A docs map.** Where the deep material is (design docs, ADRs, the published site) so an
  agent can go deeper on demand.

Keep it current. When a convention changes, the brief changes in the same PR. A stale brief is
worse than none, because it's authoritative.

For the deep dive on crafting and maintaining this file well — what belongs in it, size
discipline, progressive disclosure, when to add a rule — see the `agent-brief` skill.

## Permission allowlist

Seed a per-developer permission allowlist (e.g. `.claude/settings.local.json`) so routine,
safe commands don't prompt every time: the test runner, the linter, `git commit`, the PR CLI,
the container tool. Curate it to the commands your workflow actually uses. Keep it per-machine
(git-ignored) so each person tunes their own.

Don't allowlist genuinely destructive commands. The prompt on a `reset --hard` or a `secrets
set` is a feature.

## Worktree isolation for parallel agent work

Give each parallel agent its own worktree so file edits can't collide. The harness that
sandboxes file writes to the worktree usually does **not** sandbox shell commands — so brief
each agent explicitly: run git only against your own worktree path, never `cd` into the parent
checkout. Serialize the landing even when implementation ran in parallel (see
`git-and-review.md`).

## Give agents the same gates, and let them self-check

An agent should run the fast pre-push checks itself before proposing a push, and treat CI as
the exhaustive backstop — exactly the human loop. In the brief, point at the fast-gate command
so the agent knows what "ready to push" means.

## Capture what agents learn

When an agent (or a person) hits a non-obvious gotcha — a flaky test that's really an infra
symptom, a tool that needs a restart to pick up config, a deploy quirk — record it somewhere
durable (the brief, a decision log, or a persistent memory). The second session shouldn't
rediscover the first session's traps.

## Orchestrating many agents

For larger efforts, one agent can act as a coordinator: read the work list, delegate each
slice to a worktree sub-agent, review the returned diff, and land PRs one at a time. The
coordinator holds the conventions (disjoint-files-only parallelism, serialized landing,
green-CI-before-merge) so the individual implementers don't each have to. Keep a board or task
list as the source of truth for what's in flight, and move an item to done only after its PR
is merged, not when the code is written.
