---
name: dev-playbook
description: Project-agnostic engineering practices for shipping high-quality software and preventing regressions — layered testing, quality gates (pre-push → CI → gated deploy), testability seams, deterministic tests, branch/PR/worktree discipline, secrets & dependency hygiene, the agent-brief (CLAUDE.md) pattern, and docs-as-code with Zensical. Use when setting up a new project or repo; adding or restructuring tests, CI, or deploys; establishing team or agent workflow conventions; auditing whether a repo has adequate quality gates; hardening against regressions; or deciding how to test, structure, document, and ship work in any stack.
---

# Dev playbook

A portable set of engineering practices for shipping software that stays correct as it
grows. It works in any language or stack — the specifics change, the shape doesn't. Use it
three ways: to **stand up** a new project, to **audit** an existing one, and to **operate**
day to day so regressions don't slip through.

Two audiences, one playbook: human developers and coding agents follow the same gates. An
agent should run the cheap checks itself before proposing a push and lean on CI as the
backstop, exactly as a careful human would.

## The core idea: layer by cost, gate by layer

Sort every check by what it costs to run. Cheap checks — lint, type-check, unit tests with
no external services — run everywhere: on the machine before a push, and on every CI job.
Expensive checks — a real database, a browser, a full deploy — run in CI only. The rule that
keeps this honest: **never let a slow check gate a local push.** If the fast gate is slow,
people bypass it, and then it protects nothing.

Everything below is that idea applied to a different part of the loop.

## Principles

Each principle names the practice and the smell that means it's missing. Depth lives in the
`references/` files, loaded when you need them.

### Testing and correctness

1. **Layer tests by cost.** A fast layer with no external infra (in-process, mocked or
   injected boundaries) and a heavier layer that needs real infra. Keep them in separate
   directories or marked with fixtures so each runs on its own. *Smell: a single `test`
   command that needs Docker before it runs one assertion.* See `references/layered-testing.md`.

2. **Build for testability with dependency-injection seams.** Inject the database session,
   the auth check, and any external client through a seam the app already uses, so tests
   swap in an in-memory fake and need zero infra. A protocol/interface with a real impl and
   a fake impl is the pattern. *Smell: unit tests that reach into private attributes or
   monkeypatch internals because there's no seam.*

3. **Make tests deterministic.** No dependence on wall-clock timing or scheduler luck. Drive
   time and background loops explicitly; when you must poll, use a generous, justified
   timeout and self-clean with prefixed test data. *Smell: a test that passes on a re-run
   with no code change — that's a race, not luck, and it will erode trust in the whole gate.*

4. **Every bug and flake becomes a test.** Reproduce it in a failing test first, then fix.
   A fixed bug without a test is a bug waiting to come back. *Smell: the same regression
   twice.*

5. **Prove a guard by watching it fail.** A test that passes says nothing about a
   compatibility promise or a safety check until you have seen it go red: temporarily break
   the thing it protects, confirm the failure names the right thing, then restore. *Smell:
   "I added a test" offered as the whole evidence that a regression cannot recur.* Do the
   mutation **non-destructively** — `git checkout -- <file>` and `git restore <file>`
   overwrite the working tree from the **index**, silently discarding uncommitted changes to
   that file, and unstaged work never entered the object database so no reflog or `fsck` can
   bring it back. Safe options, cheapest first: commit (or `git stash push -- <file>`) before
   mutating; edit a copy; or apply the mutation as a patch and reverse exactly it with
   `git apply -R`.

### Gates and CI/CD

6. **A fast pre-push hook mirrors the cheap CI jobs.** Lint + type-check + the no-infra test
   layer, run locally before a push so it rarely lands red. Give it a one-line escape hatch
   (`--no-verify`) for the rare scoped exception, and document the install. See
   `references/ci-cd.md`.

7. **CI runs jobs in parallel with reproducible installs.** One job per concern (lint, unit,
   integration, build, e2e), lockfile-frozen installs, dependency caching, and
   cancel-in-progress on new pushes to the same ref. Keep pinned actions current: when the
   runner deprecates a runtime (e.g. Node 20 → 24), bump the flagged actions to their latest
   major across *all* workflows, checking composite wrappers for transitive pins. *Smell: a
   20-minute serial pipeline nobody waits for, or a deprecation warning on every run nobody
   acts on.*

8. **Tell infra flakes apart from real failures.** A whole run failing at a suspiciously
   round duration, or "no runner available," is infrastructure — re-run it. A specific
   assertion failing is your code — fix it. Never "fix" a red that's actually an outage, and
   never re-run a red that's a real bug. See `references/ci-cd.md`.

9. **Gate deploys on green CI and ship the validated commit.** Deploy triggers off a
   successful CI run and checks out that exact SHA, not whatever `main` is now. Make it
   armable (a flag/token you can turn off) and skip deploys for docs-only changes.

### Change management and review

10. **Branch per slice, PR-only, protected main.** One branch per vertical slice off fresh
   `main`; every change lands via PR after CI is green; no direct pushes. Use worktrees (or
   an agent's worktree isolation) for parallel work so in-flight branches don't collide. See
   `references/git-and-review.md`. *Give each worktree its own stateful infra — don't share one
   local database across worktrees. Worktrees share a filesystem-level dev DB, so one branch's
   migration stamps a revision the others don't have and their apps then fail to boot against a DB
   ahead of their own migration chain. Isolate per worktree (a throwaway DB container on a
   per-worktree port, or a separate DB name on the shared server) and expose it as a make target;
   ephemeral, self-provisioning test infra like testcontainers sidesteps this automatically.*
   *Don't let worktrees accumulate — a fresh worktree per task silently piles up full checkouts and
   clogs disk (an agent harness that auto-creates isolated worktrees is the worst offender). Prefer a
   **pool manager** that recycles a fixed set of detached-HEAD worktrees and prunes idle/merged ones —
   e.g. **[treehouse](https://github.com/kunchenguid/treehouse)** (`treehouse get` to acquire,
   `treehouse return` to release, `treehouse prune` to reclaim). Without one, make removal part of the
   land step (`git worktree remove` when a branch merges) and periodically `git worktree prune` +
   delete merged branches (`git branch --merged main`).*

11. **Keep slices small and reversible; flag risky changes off by default.** A change that
    alters live behavior ships behind a config flag defaulting to the current behavior, so
    the deploy is a no-op until you turn it on. Parallelize implementation only across
    provably-disjoint file sets; serialize the landing so `main` stays reviewable. *Smell: a
    single PR that rewrites a core subsystem and flips its behavior in one merge.*

12. **Review for correctness before merging, adversarially.** A reviewer (human or agent)
    reads the diff to break it, not to approve it. Prefer a public seam over a private reach;
    reject a known wart rather than merge it. Security-sensitive diffs get a security pass
    (see below).

### Security and supply chain

13. **Secrets never enter git.** Ignore secret-bearing files, scan for accidental commits,
    and keep credentials in the environment or a secret store. If one leaks, rotate it — git
    history is forever. Redact secrets from logs and tool output. See
    `references/security-and-supply-chain.md`.

14. **Keep dependencies honest.** Commit lockfiles, install frozen/reproducibly in CI, run a
    vulnerability scan, and keep a patch cadence (automated update PRs). Minimize the
    dependency surface. *Smell: `latest` versions, an uncommitted lockfile, or a CI install
    that resolves differently than a developer's.*

### Enablement, docs, and operability

15. **The agent brief is the highest-leverage artifact.** A `CLAUDE.md` (or `AGENTS.md`) at
    the repo root that states build status honestly ("trust the code over the docs"), lists
    the exact commands, and spells out the branch/PR/test conventions. Every agent session
    then follows your workflow by default. Pair it with a permission allowlist for routine,
    safe commands. See `references/agent-enablement.md`.

16. **Treat docs as code.** Author user-facing docs in the repo, publish them to a site on
    merge, and add a PR build-check so a broken docs build fails before merge. Record the
    "why" behind decisions as short ADRs. See `references/docs-as-code.md` (covers building a
    high-quality Zensical site).

17. **Make it observable, and runnable in one command.** You can't call it shipped if you
    can't see it running: a health endpoint, structured logs, and minimal metrics or error
    tracking. And a single command (a `Makefile`/`Taskfile` target) that brings the whole
    stack up locally — the first thing a newcomer or agent runs.

## Checklist A — adopt in a new project

Copy in roughly this order; each step is independently useful.

1. An **agent brief** (`CLAUDE.md`) with build status, exact commands, and conventions.
2. **Split tests** into a no-infra fast layer and a heavier infra layer.
3. **Dependency-injection seams** for the DB, auth, and external clients, with in-memory fakes.
4. A **pre-push hook** running the fast layer + lint/type-check; document the install.
5. A **CI workflow** with parallel jobs, lockfile-frozen installs, and caching.
6. **Containerized integration deps** (e.g. testcontainers) so integration tests self-provision.
7. **E2E that boots the stack itself** and uses self-cleaning, prefixed data.
8. **Deploy gated on green CI**, shipping the validated SHA; armable and skippable.
9. **Branch-per-slice + PR-only**, protected `main`, worktrees for parallel work.
10. **Secrets ignored + scanned**; **lockfiles committed + vuln-scanned**; an update cadence.
11. **Docs-as-code** published on merge with a PR build-check; **ADRs** for decisions.
12. **Health check + structured logs**, and a **one-command** dev/demo loop.

## Checklist B — audit an existing repo

Ask each question. Every "no" is a high-value next add, roughly in priority order.

- Can a newcomer bring the whole stack up with **one command**?
- Do the **fast tests run with no infra**, and are the slow ones separated?
- Is there a **pre-push gate** that mirrors the cheap CI jobs?
- Does **CI** use **frozen installs + caching + parallel jobs**?
- Do **integration tests self-provision** their infra (no hand-managed DB)?
- Is **deploy gated on green CI**, shipping the **tested SHA**?
- Is **`main` protected and PR-only**?
- Are **secrets absent from history** and **scanned** for?
- Are **dependencies locked, scanned, and updated** on a cadence?
- Is there an **agent brief** so agents follow the conventions?
- Is the **"why" captured** (ADRs), and are **user docs published** with a build-check?
- Can you **see it running** (health, logs, errors)?

## How to use this skill

- **Standing up a project:** work Checklist A top-down; read the reference for each step as
  you reach it.
- **Auditing:** run Checklist B, report the gaps in priority order, and propose the smallest
  change that closes the highest-value one.
- **Operating:** apply the principles per change — fast gate before push, small reversible
  slices, a test for every fix, CI green before merge.

Adapt every specific to the stack in front of you. The gates and their ordering carry over;
the commands don't.
