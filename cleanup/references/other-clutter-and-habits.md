# Other clutter and cleanup habits

## Contents
- Disk: dependency dirs, caches, build output
- Temp files and scratch work
- Processes and background tasks
- Cloud and rented resources
- Repo hygiene
- Habits for agents
- Habits for teams

## Disk: dependency dirs, caches, build output

Find the big things first, then decide:

```bash
du -sh ~/* ~/.[!.]* 2>/dev/null | sort -rh | head -20        # biggest top-level dirs
find ~ -name node_modules -type d -prune -print0 2>/dev/null | xargs -0 du -sh 2>/dev/null | sort -rh | head
find ~ -name target -maxdepth 4 -type d 2>/dev/null          # Rust build output (check Cargo.toml next to it)
```

| Item | Safe to delete? | How |
|---|---|---|
| `node_modules/` in projects not touched recently | Yes, reinstall regenerates | `rm -rf` after listing paths |
| Package caches (`~/.npm`, pnpm store, `~/.cache/pip`, `~/.cargo/registry`) | Yes, re-downloads | `npm cache clean --force`, `pnpm store prune`, `pip cache purge`, `cargo cache -a` |
| Build output (`target/`, `dist/`, `.next/`, `__pycache__/`, `.venv/` of dead projects) | Yes if reproducible | list, then delete |
| Model weights, datasets (`~/.ollama`, HF cache) | Only if the user confirms | large and slow to re-fetch |
| Kubernetes/minikube clusters | Ask | `minikube delete` removes the cluster and its volume |

On WSL, the virtual disk (`ext4.vhdx`) doesn't shrink when files are deleted. After a big
cleanup, the user may need to compact it from Windows (`wsl --shutdown`, then `Optimize-VHD`
or `diskpart` `compact vdisk`) to actually recover host disk space.

## Temp files and scratch work

- Agents write intermediate files to the session scratchpad directory, never into the repo and
  not to bare `/tmp`. That keeps cleanup to one directory and keeps `git status` clean.
- Look for strays: `git status --short` (untracked files), `*.orig`, `*.rej`, `*.bak`,
  `nohup.out`, `core.*`, stray `.env.*` copies.
- Don't commit scratch output; add the patterns to `.gitignore` instead of deleting repeatedly.

## Processes and background tasks

```bash
ps -eo pid,etime,cmd --sort=-etime | grep -E 'node|python|vite|webpack|ollama|tail -f' | head -20
ss -ltnp 2>/dev/null | head -20      # what is listening on which port
```

Stop dev servers, watchers and tunnels you started once the task is done. Identify a process
before killing it; don't kill by name pattern across the whole machine.

## Cloud and rented resources

These cost money while idle, so they outrank disk clutter in priority:

- Rented GPU/CPU pods (RunPod etc.): list and terminate; see the `runpod-jobs` skill.
- Dev databases and preview deployments (Neon branches, Fly machines, Supabase branches).
- Tunnels (cloudflared, ngrok) and open ports.
- Check each provider's CLI for running resources at the end of a session, and report anything
  left running with its hourly cost if known.

## Repo hygiene

- Close or triage stale PRs and issues instead of letting them age; label what's deferred.
- Remove dead code, unused dependencies and old feature flags once their rollout finishes.
- Rotate or revoke tokens created for a finished task (see the `handling-secrets` skill).
- Delete committed build artifacts and large binaries; use `.gitignore` going forward.
- Don't hand-edit history to remove clutter on a shared branch.

## Habits for agents

1. **Own what you create.** Anything an agent starts (container, worktree, branch, process, pod,
   temp file) is the agent's to remove, or to name explicitly in the final message.
2. **Prefer ephemeral by default.** Unique names, scratchpad paths, `down -v` for throwaway stacks.
3. **Audit before deleting, and show the list.** Never delete from a list computed at execution time.
4. **End every task with the checklist** in `SKILL.md`, and say which items were skipped and why.
5. **Report cleanup in numbers:** what existed, what was removed, what was kept and why, disk
   before/after.
6. **Leave intentional leftovers labelled.** If a stack must stay up, say so and give the
   command to remove it.

To enforce rather than hope: add the end-of-task checklist to `CLAUDE.md`, add a SessionStart
hook that prints `docker ps` and `git worktree list`, and add a SessionEnd/Stop hook that tears
down the session's own stacks. Hooks are configured in `settings.json` (see the `update-config`
skill).

## Habits for teams

- **Time-box everything temporary:** branches, preview environments, feature flags, test data.
  Put an owner and an expiry in the name or description.
- **Automate the boring half:** auto-delete merged branches, scheduled stale-PR bots, a monthly
  CI job that lists (not deletes) resources older than N days.
- **Make cleanup part of "done":** a definition of done that includes "branch deleted, preview
  env torn down, flag removed".
- **Tag cloud resources** with owner and purpose so orphans can be traced and reaped.
- **Run a monthly sweep** with a rotating owner: branches, worktrees, volumes/images, cloud
  resources, stale PRs. Short and regular beats a heroic annual purge.
- **Keep shared dev infrastructure explicit** (one documented reverse proxy, one shared DB),
  so personal stacks can be torn down without breaking it.
