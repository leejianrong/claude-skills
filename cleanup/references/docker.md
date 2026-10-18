# Docker cleanup

## Contents
- Why containers come back after a restart
- Inventory commands
- Spinning a stack down for good
- Reclaiming disk space
- Volumes: classify before deleting
- Prevention
- Optional: stop Docker starting at boot

## Why containers come back after a restart

Two things must both be true for a container to auto-start after a machine/WSL restart:

1. **The Docker daemon starts at boot.** On WSL with `systemd=true` in `/etc/wsl.conf`, the
   `docker`, `docker.socket` and `containerd` units are usually `enabled`.
2. **The container has a restart policy** other than `no`.

The policies differ in how they treat a manual stop:

| Policy | After `docker stop` / `compose stop` | After daemon restart |
|---|---|---|
| `no` (default) | stays stopped | stays stopped |
| `unless-stopped` | stays stopped | stays stopped |
| `always` | stopped | **starts again** |
| `on-failure` | stopped | only restarts if it failed |

So `compose stop` is enough for `unless-stopped`, but **not for `always`**. `compose down`
removes the containers entirely and works for every policy.

## Inventory commands

```bash
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.CreatedAt}}'

# restart policy + owning compose project + where its compose file lives
docker ps -aq | xargs -r docker inspect --format \
  '{{.Name}} restart={{.HostConfig.RestartPolicy.Name}} project={{index .Config.Labels "com.docker.compose.project"}} dir={{index .Config.Labels "com.docker.compose.project.working_dir"}}'

docker compose ls -a          # projects and their compose files
timeout 120 docker system df  # images / volumes / build cache totals
```

Group the output by compose project; decide per project, not per container.

## Spinning a stack down for good

```bash
cd <project working_dir>      # from the inspect output above
docker compose down           # removes containers + network; KEEPS volumes and images
```

- `down` is the right default: nothing is left for a restart policy to revive, and data in
  named volumes survives, so `docker compose up -d` later restores the old state.
- Add `-v` only for **throwaway** stacks (worktree/agent/test stacks) where the data is
  disposable. It deletes the stack's named volumes irreversibly.
- If you must keep the containers but stop them reviving: `docker update --restart=no <name>`.
- Leave shared infrastructure (e.g. a Traefik dev proxy) running if other projects route
  through it — check labels/hostnames before stopping it.

Verify afterwards with `docker ps -a` and `docker compose ls -a`.

## Reclaiming disk space

Safe, reproducible, and reasonable to do with a single confirmation:

```bash
docker builder prune -f                      # build cache; often the biggest easy win
docker builder prune -f --filter until=168h  # gentler: only cache older than a week
docker image prune -f                        # dangling (untagged) images only
```

`docker image prune -a` also removes tagged images not used by a container. They re-pull or
rebuild, but rebuilds can be slow, so ask first.

Avoid `docker system prune -a --volumes` — it bundles everything, including volumes, into one
unreviewable step.

## Volumes: classify before deleting

`docker volume ls -f dangling=true` lists volumes no container uses. "Unused" is **not**
"disposable" — stopping a stack makes its real data volumes dangling too.

| Class | Looks like | Action |
|---|---|---|
| Anonymous | 64-char hex name | Safe: nothing refers to them by name. `docker volume prune -f` removes only these (Docker 23+). |
| Throwaway session | `agent-<id>_*`, `<worktree>_*`, `*-t1_*` test stacks | Usually safe, but `pgdata` / `gitremote` may hold something; show the list first. |
| Real data | `<project>_pgdata`, `n8n_data`, `*_assets`, `minikube`, `ollama_data` | Keep. Back up (`pg_dump`, tar) before any delete. |

Procedure: list dangling volumes → write the proposed deletions to a file → show → confirm →
`docker volume rm` that file's contents (`docker volume rm` refuses in-use volumes, which is a
useful backstop) → re-run `docker system df`.

Volumes hold the bulk of the space on a dev machine (hundreds of leaked volumes can reach tens
of GB), so this step is usually where the real savings are.

## Prevention

- **No restart policy in dev compose files.** Put `restart: unless-stopped` only on things that
  should survive reboot, ideally in an override file the user opts into.
- **Unique project name per ephemeral stack:** `COMPOSE_PROJECT_NAME=<task>-<id> docker compose up -d`,
  then `COMPOSE_PROJECT_NAME=<same> docker compose down -v` when done. A worktree/agent session
  that starts a stack owns tearing it down.
- **Name volumes that matter** (`volumes: pgdata:`), and don't declare anonymous volumes in
  Dockerfiles/compose for data you care about.
- **Label throwaway resources** (`labels: ["ephemeral=true"]`) so
  `docker volume prune -f --filter label=ephemeral` targets exactly those.
- **Back up before destroying:** `docker exec <db> pg_dump -U <user> <db> > backup.sql`.
- **Scheduled sweep** (systemd timer or cron, monthly):
  `docker builder prune -f --filter until=720h && docker image prune -f && docker volume prune -f`.
  These only remove cache, dangling images and anonymous volumes.

## Optional: stop Docker starting at boot

Only if the user wants Docker fully off until needed:

```bash
sudo systemctl disable docker docker.socket containerd
```

Re-enable with `systemctl enable`. Usually unnecessary once no container has a restart policy —
an idle daemon is cheap and disabling it makes the next `docker` command fail.
