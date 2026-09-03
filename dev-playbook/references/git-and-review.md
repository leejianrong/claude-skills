# Git workflow and review

The workflow exists so that `main` is always shippable and every change is reviewable in
isolation. The mechanics are simple; the discipline is the point.

## Branch per slice, PR-only, protected main

- **One branch per vertical slice**, cut from fresh `main`. A slice is a change small enough
  to review in one sitting and revert in one click.
- **`main` is protected.** No direct pushes. Every change lands through a PR after CI is
  green. Even when server-side protection isn't available (a private free repo), follow it by
  convention — the discipline is what keeps `main` green, not the enforcement.
- **Small, per-step commits** with messages that explain *why*, not just *what*.

## Worktrees for parallel work

When you have more than one thing in flight, use git worktrees rather than stashing and
switching branches in place. Each task gets its own directory backed by the one clone:

```bash
git worktree add ../proj-<slice> -b feat/<slice> main
git worktree list
git worktree remove ../proj-<slice>     # when merged
```

Each worktree needs its own installed dependencies; shared services (a local database) are
shared across them. Coding agents have built-in worktree isolation that maps onto this
directly — prefer it for parallel, file-mutating agent work.

**Keep the primary checkout on `main`.** After merging a PR, update local `main` from the
remote before cutting the next branch, or the next branch starts from a stale base. An agent
working in a worktree should run git only against its own worktree path, never `cd` into the
parent checkout.

**Give each worktree its own stateful infra** — don't share one local database across
worktrees. Worktrees share a filesystem-level dev DB, so one branch's migration stamps a
revision the others don't have, and their apps then fail to boot against a DB ahead of their
own migration chain. Isolate per worktree (a throwaway DB container on a per-worktree port, or
a separate DB name on the shared server) and expose it as a make target; ephemeral,
self-provisioning test infra like testcontainers sidesteps this automatically.

**Don't let worktrees accumulate.** A fresh worktree per task silently piles up full checkouts
and clogs disk — an agent harness that auto-creates isolated worktrees is the worst offender.
Prefer a **pool manager** that recycles a fixed set of detached-HEAD worktrees and prunes
idle/merged ones — e.g. **[treehouse](https://github.com/kunchenguid/treehouse)** (`treehouse
get` to acquire, `treehouse return` to release, `treehouse prune` to reclaim). Without one,
make removal part of the land step (`git worktree remove` when a branch merges) and
periodically `git worktree prune` plus delete merged branches (`git branch --merged main`).

## Parallelize implementation, serialize the landing

You can have several branches coded at once **only if their file sets are provably disjoint** —
check the actual files, don't guess from a "same-ish area" hunch. Then **land one PR at a
time**: review, get CI green, merge, update `main`, and only then merge the next. That keeps
`main` reviewable and bisectable.

**Squash against your own base commit, never against `origin/main`.** `git reset --soft
origin/main` is the usual way to collapse WIP commits into one, and it is *actively unsafe*
while sibling branches are landing: `origin/main` moves under you, so the reset diffs your tree
against a newer commit and stages **every file a sibling landed as a deletion**. Nothing warns
you — the tree looks right, the index does not, and committing publishes a PR that silently
reverts someone else's merged work. Record the base when you branch and squash against that:

```bash
BASE=$(git rev-parse HEAD)        # right after branching
git reset --soft "$BASE" && git commit    # NOT: git reset --soft origin/main
```

Two independent agents hit this in a single afternoon on one repo. Both caught it in
`git status` before committing, which is the only thing standing between it and a bad merge —
so check `git status` after any soft reset, and treat a deletion you did not make as a stop
sign. To pick up a sibling's landed work, rebase or merge deliberately; that is a separate
action from squashing your own history.

A change that carries a database migration **lands alone** and gets verified against the
deployed environment before the next change stacks on it.

## Merge vs squash

- **Merge commit** when preserving per-commit authorship matters — a fork contributor's
  commits, or a slice whose individual commits tell a useful story. It also auto-closes the
  contributor's PR as *merged*.
- **Squash** when the branch is a scratch history you don't want on `main`.

Pick one per repo and state it in the agent brief so it's not relitigated per PR. Delete the
branch after merge.

## Small and reversible; risky changes behind a flag

Prefer many small merges over one big one. When a change alters live behavior in a way you're
not ready to fully commit to, **ship it behind a config flag that defaults to the current
behavior.** The deploy is then a no-op until you flip the flag, which de-risks landing a core
change to a live system: you can merge the mechanism, test the flag-on path in CI, and turn it
on deliberately later. Removing the old path becomes a separate, clean follow-up.

## Review adversarially

A review is an attempt to break the change, not a rubber stamp. Read the diff for:

- **Correctness under edge inputs** — empty, null, concurrent, out-of-order, the second call.
- **Seams over reaches** — reject a test or a caller that pokes at private state when a public
  seam exists; ask for the seam instead.
- **Known warts** — don't merge a "we'll fix it later" you already see. Bounce it back now;
  later rarely comes.
- **Blast radius** — does this touch a shared file another in-flight branch also touches? Does
  it change a default? Does it deploy?
- **Security-sensitive surface** — auth, input handling, anything touching secrets or user
  data gets the security pass in `security-and-supply-chain.md`.

For agents: an independent reviewer agent that's told to *refute* a change catches more than
one told to check it. When several verifiers disagree, believe the skeptics.
