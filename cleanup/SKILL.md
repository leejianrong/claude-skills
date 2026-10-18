---
name: cleanup
description: Audit and clean up development leftovers safely — Docker containers/volumes/images/build cache and restart policies, stale local and remote git branches, old git worktrees, plus other accumulated clutter (node_modules, caches, temp files, background processes, rented cloud resources). Also sets the habits that stop clutter from accumulating, for agents and teams. Use when the user says cleanup, clean up, tidy, prune, free disk space, "what's still running", "spin down", "old branches", "stale worktrees", "containers keep restarting", or at the end of a task that started containers, worktrees, branches or pods.
---

# Cleanup

Leftovers accumulate because creating is cheap and nobody owns deleting. This skill covers
two jobs: **audit and clean** what exists now, and **prevent** the next pile.

## Safety protocol (applies to every deletion)

Deletion is the one place to be slow. Follow this order, always:

1. **Inventory** with read-only commands. Report what exists, how big, how old.
2. **Classify** each item: `keep` (in use, holds real data, unmerged work), `safe` (reproducible
   or provably orphaned), `ask` (can't tell).
3. **Write the exact delete list to a file** and show it. Never feed `rm`/`delete` a list that
   is computed at the moment of deletion (`ls | grep | xargs rm`) — neither you nor the user can
   review it, and permission classifiers block it for that reason.
4. **Get an explicit yes** for the specific list. Approval for one category (e.g. build cache)
   doesn't cover another (e.g. volumes).
5. **Delete, then verify** by re-running the inventory and reporting before/after numbers.

Never delete anything that holds data you can't regenerate (databases, uploaded assets,
unpushed commits, uncommitted changes) without a backup or the user's explicit say-so.
Prefer the reversible form first: `docker compose down` before `down -v`, `git branch -d`
before `-D`, `git worktree remove` (refuses dirty trees) before `--force`.

## What to clean

| Area | Reference |
|---|---|
| Docker: containers, restart policies, volumes, images, build cache, WSL autostart | [references/docker.md](references/docker.md) |
| Git: stale local/remote branches, old worktrees, merged PRs | [references/git-branches-worktrees.md](references/git-branches-worktrees.md) |
| Everything else: dependency dirs, caches, temp files, processes, cloud resources, team habits | [references/other-clutter-and-habits.md](references/other-clutter-and-habits.md) |

Read only the reference that matches the request. For a general "clean up my machine/repo",
run the quick audit below first, then open the relevant references.

## Quick audit (all read-only)

```bash
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}'   # what's running
docker system df                                                       # slow with many volumes; use timeout
git fetch --prune && git branch -vv | grep ': gone]'                   # local branches whose remote is deleted
git worktree list                                                      # worktrees and their paths
df -h ~ | tail -1                                                      # disk headroom
```

Run `docker system df` with `timeout 120` — with hundreds of volumes it can take minutes.

## End-of-task checklist (for agents)

Before finishing any task that created infrastructure, copy this and tick it off:

```
- [ ] Containers/stacks I started are down (`docker compose down`; add `-v` only for throwaway stacks)
- [ ] No restart policy was added to a dev compose file
- [ ] Worktree I created is removed, or the user was told it still exists and why
- [ ] Branch I created is merged/deleted, or pushed and listed in my summary
- [ ] Temp files are in the scratchpad dir, not scattered in the repo or /tmp
- [ ] Background processes/tasks I started are stopped
- [ ] Rented or cloud resources (pods, dev DBs, tunnels) are torn down
- [ ] Anything left running on purpose is named in my final message
```

## Prevention, in one screen

- Dev compose files get **no restart policy**. Reserve `unless-stopped` for the few things that
  should survive a reboot (e.g. a shared reverse proxy).
- Ephemeral stacks get a **unique `COMPOSE_PROJECT_NAME`** and are removed with `down -v`.
- Real data lives in **named volumes**, with a dump taken before any destructive step.
- Branches are **short-lived**; enable "delete head branch on merge" on the remote.
- Worktrees are **created and removed in the same task**.
- Run a **scheduled sweep** (monthly is enough) rather than waiting for the disk to fill.

To have an agent enforce these automatically, put the end-of-task checklist in `CLAUDE.md`, or
use a session-end hook (see the `update-config` skill) — hooks run regardless of whether the
agent remembers.
