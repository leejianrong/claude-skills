---
name: traefik-dev-proxy
description: Set up one machine-wide Traefik reverse proxy that auto-discovers Docker Compose dev stacks via labels, giving every project on a laptop a stable <project>.localhost hostname instead of a per-project nginx container or manual port juggling. Use when setting up a new development machine or laptop that will run multiple full-stack web app projects locally, when asked to add or configure Traefik, when replacing a project-local nginx dev proxy with a shared one, when projects' dev stacks keep colliding on host ports, or when the user mentions *.localhost, Docker label-based service discovery, or a machine-wide reverse proxy.
---

# Traefik as a machine-wide dev proxy

One Traefik instance for the whole machine, not one reverse proxy per
project. A new project opts in by adding labels to its own Compose file —
never by editing Traefik's own config — so onboarding a project is zero-touch
on the proxy side.

## TL;DR

1. Stand up Traefik once, anywhere on the machine, independent of any
   project: [`assets/dev-proxy-compose.yml`](assets/dev-proxy-compose.yml),
   `docker compose up -d`.
2. Per project, copy
   [`assets/project-compose.override.yml.example`](assets/project-compose.override.yml.example)
   to `docker-compose.override.yml` (gitignored, auto-loaded by Compose),
   fill in the placeholders, and keep the project's own `docker-compose.yml`
   publishing its port directly too — the override only adds a second way
   in, it never replaces the first.
3. Read the three gotchas below before you conclude something is broken —
   each one looks like a different failure and isn't.

## The machine-wide instance

Everything non-obvious is commented inline in
[`assets/dev-proxy-compose.yml`](assets/dev-proxy-compose.yml):

- `--providers.docker.exposedbydefault=false` — opt-in only. A container
  with no `traefik.enable=true` label is invisible to Traefik, not
  accidentally exposed. Never flip this to `true`.
- The `proxy` network gets an explicit `name:`, not Compose's default
  `<directory>_proxy` prefix, so every project's own compose file can
  reference it by a fixed name via `external: true` regardless of what
  Compose project name that project happens to use.
- `restart: unless-stopped` plus the Docker daemon's own start-on-boot
  behavior is what makes this "always on" — no systemd unit needed.

## Per-project opt-in

The layering idiom that makes this safe to add incrementally: a project's
`docker-compose.yml` must keep working completely standalone, with its
service publishing a host port directly — that's what a fresh clone and CI
both get, no override file present. `docker-compose.override.yml` is
strictly additive on top: it attaches the service to the external `proxy`
network and adds the `traefik.*` labels. Never make the override a
requirement for the base file to work; treat it as a personal, gitignored
convenience layered on top of a project that's already complete without it.

**New-project checklist:**

- [ ] Copy `project-compose.override.yml.example` into the project, filling
      in the service name, `<project>.localhost` hostname, and the
      service's container port.
- [ ] Add `docker-compose.override.yml` to `.gitignore`; commit the
      `.example` file instead.
- [ ] Confirm `docker compose up` still works with no override present
      (delete it locally and retest) — this is what CI and a first clone
      exercise.
- [ ] Copy the override in, confirm the service answers at
      `http://<project>.localhost/` too, with both paths live at once.

## Gotcha: Traefik looks up but routes nothing

If `docker ps` shows the Traefik container `Up` and healthy but it never
discovers any service, check `docker logs <traefik-container>` before
touching the network or labels — it's almost certainly this:

> `Error response from daemon: client version 1.24 is too old. Minimum
> supported API version is 1.40, please upgrade your client to a newer
> version`

Traefik v3.5's vendored Docker client hardcodes its opening
version-negotiation request at API 1.24. A recent Docker Engine (29.x,
minimum supported API 1.40) rejects that opening request outright instead
of tolerating it and letting negotiation proceed, so the provider fails
silently in a retry loop forever — the container itself never crashes, it
just never routes anything. `DOCKER_API_VERSION` does **not** fix this: the
rejection happens on the request that env var would otherwise influence.
The fix is to not pin an old Traefik minor — bumping to `v3.7` (confirmed
against Engine 29.3.1) resolved it immediately. If you're on an even newer
engine and still see this, try `traefik:latest` first before debugging
anything else.

## Gotcha: HMR breaks or 403s through the proxy

Some dev servers validate the `Host` header more strictly on a
websocket/HMR upgrade than on a plain HTTP request. Vite is the concrete
case: its `allowedHosts` check only looks at the hostname, but the HMR
websocket upgrade separately requires `hostname:port` matching its own
listening port. Fronting the dev server through Traefik on port 80 means
the browser's `Host` header arrives as just the hostname (no port) — that
passes the loose check and fails the strict one, either breaking HMR
silently or hard-failing the whole page with a bare "Blocked request" 403.

Fix with a Traefik headers middleware that rewrites the forwarded `Host`
back to `hostname:port` before it reaches the dev server — see the
commented block in
[`assets/project-compose.override.yml.example`](assets/project-compose.override.yml.example).
Check whether your dev server has an equivalent strict-Host check on
upgrade before assuming this middleware is unnecessary; the plain-HTTP path
working is not proof the websocket path will.

## Gotcha: `*.localhost` isn't free outside a browser

Modern browsers resolve any `*.localhost` hostname to loopback with no
`/etc/hosts` entry needed (RFC 6761) — but that's a browser convention, not
a system resolver guarantee. `curl http://project.localhost/` from a
terminal, a script, or CI will fail to resolve. Use
`curl --resolve project.localhost:80:127.0.0.1 http://project.localhost/`
instead, or add a real `/etc/hosts` entry if you need a plain shell to
resolve it without `--resolve` every time.

## Not the fix for intra-project port collisions

This setup solves "give each *project* a stable hostname" — it does nothing
for multiple *worktrees of the same project* colliding with each other on
host ports (e.g. several agents each running their own `docker compose up`
against the same repo). That's a separate, orthogonal problem: an
auto-port-allocation script that reassigns a worktree's own `.env` ports on
collision. The two are complementary, not alternatives — a project can have
both a stable Traefik hostname for normal use and per-worktree port
reassignment for the rare case of running several checkouts at once.
