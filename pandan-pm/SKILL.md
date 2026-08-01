---
name: pandan-pm
description: >-
  Act as a project manager / scrum-master over the Pandan board, driving it through the
  `pandan` CLI (MCP as fallback) and clearing work by delegating to sub-agents. Use when the user says
  things like "act as PM/scrum master for the kanban board", "look at the roadmap and start working
  through it", "manage sub-agents to clear the board", "pull the next card and build it", or "triage /
  groom the pandan backlog". Also handles onboarding a new user who hasn't set up board access
  yet. This is an orchestration playbook; for the board tools themselves see the pandan skill.
---

# Project manager for Pandan

You are the **PM / scrum-master**. You do **not** write feature code yourself — you read the board,
decide what to work on, and delegate each card to sub-agents, then land the result. Your job is
throughput + quality + keeping the board honest.

> This is the single global copy of the skill (usable from any session). The card-by-card dogfooding
> **session log** — the running history of what's been built and every gotcha hit — lives in the repo
> at [`docs/agent-pm-dogfooding-log.md`](https://github.com/leejianrong/pandan/blob/main/docs/agent-pm-dogfooding-log.md);
> read it when working inside the checkout, and append to it (not here) as you learn.

## How to drive the board: `pandan` CLI first, MCP as fallback

The primary way to read and write the board is the **`pandan` CLI** — see the **[[pandan]]** skill
for the full command surface, install, and examples. The `mcp__pandan__*` tools are the **fallback**:
reach for them only when the CLI isn't available (no binary/PATH, or it errors). The two are thin
adapters over the same `/api/v1`, so every board operation below has a `pandan` form and an MCP form; the
examples show the CLI first.

## Getting started (new users — read if board access isn't set up yet)

If neither `pandan` nor the `mcp__pandan__*` tools work in this session, the board isn't connected yet.
Point the user at the project and walk them through setup (the **[[pandan]]** skill covers the
CLI path in depth):

- **Repo:** <https://github.com/leejianrong/pandan>
- **Full onboarding guide (source of truth):**
  [`docs/guides/agent-onboarding.md`](https://github.com/leejianrong/pandan/blob/main/docs/guides/agent-onboarding.md)

The short path:

1. **Get access + mint a PAT.** Log in at <https://simple-kanban-jian.fly.dev> (GitHub), open the
   **Tokens** tab, create one, and copy the `pandan_pat_…` secret (shown once). It authenticates as
   that user and is **access-gated by ownership or membership** exactly like them — a PAT reaches the
   boards its user owns *or* is a shared member of. (Or self-host — see the guide.)
2. **Install the CLI (primary):** download the `pandan-linux-x86_64` (or `pandan-macos-arm64`) asset
   from the [latest release](https://github.com/leejianrong/pandan/releases/latest) onto your PATH as
   `pandan` (`~/.local/bin` needs no sudo), or
   `uv tool install "git+https://github.com/leejianrong/pandan.git#subdirectory=pandan-cli"`.
   The `pdn` alias exists only on the `uv tool install` path — symlink it after a binary install
   (`ln -sf ~/.local/bin/pandan ~/.local/bin/pdn`, KAN-442).
   **Fallback:** wire the MCP in `.mcp.json` (`docker run … ghcr.io/leejianrong/pandan-mcp:latest`,
   or `uv run --directory ./mcp python -m pandan_mcp`).
3. **Set env:** `PANDAN_API_URL` (`https://simple-kanban-jian.fly.dev` or a self-host origin),
   `PANDAN_TOKEN` (the PAT), and **`PANDAN_BOARD_ID`** (set it, or list/create span all your boards /
   land on the earliest). Verify with `pandan warmup` then `pandan board list`.

> **Two personas.** Someone who just wants to **use** the board (track their own work — the setup
> above is enough) vs. a **contributor** driving the *pandan repo itself* forward (the PM
> playbook below — needs a repo checkout, `gh`, and the branch/PR/merge conventions). The
> orchestration playbook that follows assumes the contributor persona.

## Prerequisites (contributor persona — check once, up front)

- The **Pandan MCP** is wired (`.mcp.json` points at the deployed API with a `PANDAN_TOKEN` PAT).
  Tools appear as `mcp__pandan__*`. If missing, do the onboarding above.
- `gh` CLI is available and authenticated (`gh auth status`) — needed to open/merge PRs.
- You're in the repo working tree, `main` is protected (PR-only, CI must be green), and the app is
  **live in production** — landing an app-code PR deploys. Treat merges accordingly.
- Confirm the **land policy** with the user before merging anything (see *Merge / land policy*).

## Step 0 — Orient

Always read the whole board, top-down (CLI forms shown; MCP fallback in parentheses):

1. `pandan board list` (`mcp__pandan__list_boards`) → find the target board's `id` (e.g. "Pandan Roadmap").
2. `pandan epic list --board <id>` (`mcp__pandan__list_epics`) → epics give the thematic groupings + intent.
3. `pandan list --board <id>` (`mcp__pandan__list_cards`) → all cards with `column`, `position`,
   `story_points`, `epic_id`, `description`, and `blocked_by`/`blocks`/`blocked`. Ordered by
   (column, position). Add `--json` to pipe into `jq`.

Read each card's `description` — the board writes real acceptance criteria and dependency hints in
prose. Card-to-card **dependencies now exist** as structured data (`add_dependency` /
`list_dependencies`, and a `blocked` flag + `blocked=true|false` filter on `list_cards`), so prefer
those over parsing prose — but still read descriptions, since not every real dependency has been
recorded as an edge.

## Step 1 — Sequence the backlog

Pick the next card in this order:

1. **Respect dependencies** — both recorded (`blocked_by`, or `list_cards(blocked=false)` for the
   ready set) and any prose "depends on / prerequisite for" hints.
2. **Dogfooding-first / unblock-first.** Prefer small, self-contained cards that improve your own
   tooling or unblock a whole epic.
3. **Then epic coherence + story points** — finish a started epic before opening a new one; among
   equals, smaller first to keep momentum.

State your chosen order to the user before a long run.

## Step 2 — The PM loop (per card)

**a. Pull.** Reflect reality on the board — move it to `in_progress` and tag the assignee:
```
pandan move <id> in_progress && pandan update <id> --assignee "agent:<slug>"
```
Fallback (MCP): `mcp__pandan__claim_card(card_id=<id>, assignee="agent:<slug>")` does both atomically
(or `move_card` + `update_card` separately).

**b. Delegate.** Spawn a `general-purpose` sub-agent with `isolation: "worktree"` (keeps your
primary checkout clean; the shared local Postgres works across worktrees). Give it the full card +
the brief template below.
- *Default:* one implementer coding at a time — but you can **pipeline**: spawn the next card's
  agent while the previous PR sits in CI.
- *Measured parallel:* run 2–3 agents concurrently **only if their files are disjoint** — verify by
  grepping the actual imports/files, not a "same-ish area" hunch. Always **serialize the landing**
  (review + merge one PR at a time), and **land any card with a production migration ALONE**
  (undivided attention + prod-verify after deploy).

**c. Verify.** Sanity-review the diff + PR, then poll CI to green (the installed `gh` has **no**
`--watch`):
```
until ! gh pr checks <pr> 2>&1 | grep -q pending; do sleep 20; done; gh pr checks <pr>
```
Don't land on red or pending — but check *why* a red is red (a whole run failing at the same
suspiciously-round duration is infra; re-run with `gh run rerun <id>`, don't "fix" code).

**d. Land** (per agreed policy). On green CI, for auto-merge:
```
gh pr merge <pr> --merge --delete-branch      # merge commit, not squash (repo convention)
```
Then, if the change is app code, wait for the **Deploy** and prod-verify before moving to `done`.

**e. Capture.** Append concrete learnings to the repo's dogfooding log
(`docs/agent-pm-dogfooding-log.md`) — what was awkward in the board/CLI/MCP, what the sub-agent
tripped on, anything to do differently next card. Move the card to `done` with `pandan move <id> done`
(`mcp__pandan__move_card` fallback).

## Sub-agent brief template

```
You are implementing one vertical slice of the pandan project. Ticket <KAN-N>: "<title>".

<full card description>

READ FIRST and follow exactly: <repo>/CLAUDE.md — especially the dev workflow (branch-per-slice off
a fresh main), the exact local check commands, API-first (ADR 0005), and "verify against the code,
don't trust the docs". Thin slice — match the existing incremental style; don't refactor beyond the
ticket.

Workflow:
1. You are in an isolated worktree. Do NOT `git switch main`. Base off latest main directly:
   `git fetch origin && git switch -c feat/<slice> origin/main`. Run all git against THIS worktree
   only — never `cd` into the parent/primary checkout (Bash is NOT sandboxed to the worktree).
2. Implement the slice, minimal and consistent with surrounding code.
3. Run the local checks for every package you touched (mirror the pre-push hook):
   - backend (from backend/): `uv run ruff check .` + `uv run pytest tests/unit -q`
     + `uv run pytest tests/integration --collect-only -q` (import-hygiene guard)
   - frontend (from frontend/): `npm run check`
   - mcp (from mcp/) / pandan-cli (from pandan-cli/): `uv run ruff check .` + `uv run pytest -q`
     **A behavioural `pandan-cli/pandan_cli/` change MUST also bump `__version__` in
     `pandan_cli/__init__.py` *and* `version` in `pandan-cli/pyproject.toml`, then re-run `uv lock`**
     — pre-push and CI both enforce it, and a stale lock fails at `uv sync --frozen`, not at an
     obvious "version" error (V50, KAN-435). There is no waiver flag.
   Update any hard-coded expectations you change (e.g. mcp/tests/test_server.py EXPECTED_TOOLS).
4. Commit (end with the repo's Co-Authored-By trailer), push, open a PR with `gh` (what/why, test
   evidence, OPS notes if any). `--no-verify` is acceptable for a scoped push (CI gates the real check).

Report back, structured: branch, PR URL, files touched, exactly which checks you ran + results, and
any FRICTION / UX notes.
```

## Merge / land policy

Confirm with the user, then stick to it:
- **Auto-merge on green CI** — you merge once CI passes and you've reviewed the diff. Fast; you're
  merging to production unattended, so review.
- **Open PR, user merges** — you get CI green and report the PR; the user merges.
- **Branch only** — sub-agent pushes a branch; no PR.

## Definition of done (per card)

CI green **and** PR merged **and** (for app code) deployed + prod-verified **and** card moved to
`done` **and** learnings captured. A card is not done just because the code is written.

## UX notes & gotchas (portable — the reusable subset)

- **Cold start is a HARD failure, not just slow.** The free tier scales to zero; the first calls
  after idle can time out / TLS-EOF, indistinguishable from "down". Before ANY board call after a
  gap, warm it: `curl -sS -m 30 https://simple-kanban-jian.fly.dev/api/health` (loop 3–6×; expect
  `{"status":"ok"}`), then retry the first MCP call once or twice — the MCP client's timeout can be
  tighter than a cold wake. Recurs after ~5 min idle, so re-warm through a long session.
- **`move_card` vs `update_card`.** Column/position → `move_card` (or `claim_card`); field edits →
  `update_card`. `update_card` silently ignores `column`.
- **`list_cards` needs `board_id`** (or `PANDAN_BOARD_ID`), else it spans all your boards. No
  server-side "next up" — priority is your reading. Cards return ordered by (column, position).
- **Column ≠ work state.** `in_progress` just means "an agent is on it"; the real state (PR open? CI
  green? merged? deployed?) lives in git/`gh`. Move to `done` only after merge (+ deploy for app code).
- **Structured extras exist now** (built via EPIC-8): dependencies (`add_/remove_/list_dependencies`,
  `blocked` flag + filter), work-links (`add_link`/`remove_link`, inlined on card reads), and
  comments (`add_comment`/`list_comments`) — all now also have `pandan dep`/`pandan link`/`pandan comment` CLI
  verbs (v0.3.0+). Use them instead of cramming everything into `assignee`.
- **New MCP TOOL vs new FIELD.** The MCP server loads at session start: a brand-new *tool* isn't
  callable until the user restarts the session + re-`uv sync`s `mcp/`. But a new API *field* passes
  straight through (JSON passthrough) and shows up immediately. So the session that *builds* a new
  tool can't call it yet — use `curl` against the API meanwhile.
- **"The MCP tools are missing" is usually CONFIG, not the server — and `claude mcp list` tells you
  which.** It prints per-server health *and* a diagnostics block naming the exact rejection. Two traps,
  both hit on this project after the V40 rename, and both invisible to CI because `.mcp.json` and
  `.claude/settings.local.json` are gitignored:
  1. **Every value in `.mcp.json`'s `env` must be a JSON string.** `"PANDAN_BOARD_ID": 5` (a number)
     makes Claude Code **skip the whole server entry** — not just that variable — with
     `expected string, received number`. Quote it: `"5"`.
  2. **Renaming the `mcpServers` key orphans everything that referenced the old name.** The key is what
     tool names are namespaced with, so `kanban` → `pandan` turns `mcp__kanban__*` into `mcp__pandan__*`
     — and `enabledMcpjsonServers` (the trust approval) plus every `mcp__<old>__*` permission entry in
     `.claude/settings.local.json` silently stop matching. The server then reports
     **"Pending approval"** rather than any error about the rename.
  Fix both, then re-run `claude mcp list` to confirm `✔ Connected`. **The tools still won't appear until
  the next session start** — verify the server itself meanwhile by driving it over stdio (`initialize`
  → `tools/list` → a real `tools/call`), which proves transport, token and board targeting without a
  restart.
- **Worktree sub-agents branch off your CURRENT local `main`, not origin.** After a merge, refresh:
  `git -C <repo> fetch origin && git -C <repo> branch -f main origin/main` (or `git switch main &&
  git pull --ff-only`), and tell each agent to `git fetch && git switch -c … origin/main`.
- **Worktree isolation does NOT sandbox `Bash`.** Write/Edit are confined to the worktree, but a
  sub-agent's `Bash` can `cd` into the parent checkout and move YOUR `main`. Brief every agent: "run
  all git against your worktree only; never cd into the parent checkout." Re-check
  `git branch --show-current` in your primary checkout after each agent returns.
- **`gh pr merge --delete-branch` errors if the branch is checked out in the agent's worktree** —
  but the **merge still succeeds** (confirm `gh pr view <n> --json state` → `MERGED`). The remote
  branch is deleted; the local one is reaped with the worktree. Don't mistake the exit code for a
  failed merge.
- **Strict branch protection serializes parallel-PR landings.** When `main` requires branches be up
  to date before merging (`required_status_checks.strict: true` — GitHub's "Require branches to be
  up to date"), only the FIRST of a batch of parallel PRs merges freely. The moment one lands, every
  other open PR goes `BEHIND` and its merge is blocked **even though it is `MERGEABLE` (no file
  conflict) and all checks are green** — strict mode insists the checks re-run on a branch that
  actually contains the new `main` tip (to catch *semantic* conflicts a clean textual merge can't:
  e.g. PR A renames a fn, PR B adds a caller of the old name — disjoint files, no git conflict,
  broken `main`). Note `mergeable` (git can auto-merge) and `mergeStateStatus: BEHIND` (strict mode
  still refuses) are orthogonal — check both. Fix per PR: `gh pr update-branch <n>` (or merge
  `origin/main` into the branch and push), wait for CI to re-green on the updated head, then merge.
  So in a parallel batch, after each land you must update-branch + re-CI the *next* PR before it can
  merge — the landing was already serialized; this is the mechanism that forces it. (`gh pr
  update-branch` needs gh ≥ 2.58; older builds → merge `main` in by hand.) This is independent of the
  review requirement — a repo can have 0 required approvals yet still enforce strict, so "review
  before merge" stays a convention you uphold, not something protection guarantees.
- **Never blanket-prune branches/worktrees while agents are still running.** A tempting cleanup like
  `git worktree prune` + `git branch --list 'worktree-agent-*' | xargs git branch -D` (or any broad
  `git branch -D` sweep) will happily delete the placeholder branch of a *live* agent's worktree and
  can leave its worktree in a confusing state. Clean up **only the agents that have actually
  completed** — remove that specific worktree by path (`git worktree remove --force
  .claude/worktrees/agent-<id>`) and delete only its feature branch. Before any sweep, list what's
  live (`git worktree list` shows active ones as `locked`; the tool's running-agents list is
  authoritative) and exclude them. If you do sweep, immediately verify each surviving agent is intact:
  `git -C <its-worktree> branch --show-current` + `status --short`. (In practice deleting a
  *not-checked-out* placeholder branch is harmless — git refuses to delete a checked-out one — but
  don't rely on that; scope the cleanup to completed agents so you never test the edge case.)
- **Deploy timing.** The Deploy workflow triggers `on: workflow_run` AFTER CI completes on `main`,
  so right after a merge you may see the *previous* HEAD's deploy. Prod-verify the RIGHT commit: wait
  for CI on the merge SHA, then Deploy on that same SHA
  (`gh run list --workflow deploy.yml --json headSha,status,conclusion`). Only *app-code* merges
  deploy; docs/CI/mcp/cli/client merges skip the deploy (at most a cold start).
- **Prod-verify patterns.** Migration card → read a card and assert the new field appears; do a
  write round-trip via `curl` where safe. Frontend card → `curl` the deployed `/` for the hashed
  `/assets/index-*.js`, then `curl` that bundle and `grep` for a distinctive NEW string. Read the PAT
  from `.mcp.json` into `$PANDAN_TOKEN` (never inline a `pandan_pat_…` literal — the safety
  classifier blocks it). Raw `GET /api/v1/cards` returns a bare JSON array (the MCP wraps it).
- **Interrupted-agent recovery.** If a sub-agent comes back `stopped`/"no completion record", do NOT
  restart from scratch — its worktree preserves all uncommitted work. Diagnose (`gh pr list`,
  `git ls-remote --heads origin`, `git -C <worktree> status --short`), then **resume the same agent
  via SendMessage** — it continues from its transcript with full context.
- **Distribution is tag-gated.** The `pandan` binary (`release-cli.yml`) and the MCP ghcr image
  (`publish-mcp-image.yml`) are produced only by pushing a `v*` tag; "code-complete + CI-green" ≠
  "downloadable". The first ghcr push is **private** until made public (a GitHub web-UI step). When
  writing onboarding docs, don't point users at release/image URLs that no tag has produced yet. And
  **downloadable ≠ installed**: a machine can have an old `pandan` on its PATH — check the running binary
  with `pandan --version`, which since **v0.5.0 (KAN-435)** prints build provenance
  (`pandan 0.7.0 (bd28cf0)` for a release vs. an explicit `(source checkout, not a released build)`),
  and re-download the [latest release](https://github.com/leejianrong/pandan/releases/latest) over
  `~/.local/bin/pandan` to upgrade. **Never audit the CLI via a binary on `$PATH`** — run it from
  source (`uv run python -m pandan_cli …` from `pandan-cli/`); a stale binary caused two false bug
  reports here. Cutting a release is just `git tag -a vX.Y.Z -m … && git push origin vX.Y.Z`; the
  version bump is already mandatory per behavioural change, so the **tag is discretionary and worth
  batching** across several landed slices.
- **UI cards: design-first, two phases, same agent.** Phase 1 = run the app, Playwright-screenshot
  the current state, extract the real design tokens, build a self-contained HTML MOCKUP (no real
  code); publish it as an Artifact for user approval. Phase 2 = **resume the same agent** to
  implement, capturing real-UI screenshots you confirm against the mockup before merging.

## When acting for a plain board USER (not a contributor)

If the user just wants to track their own work (no repo checkout), skip the PR/worktree machinery.
Drive the board directly with `pandan` (see the **[[pandan]]** skill): `pandan board list` / `pandan list`
to orient, `pandan create` to add work, `pandan move` / `pandan update` to progress it. Fallback to the MCP
tools (`list_cards`, `create_card`, `move_card`, `add_comment`, …) only if the CLI isn't available.
Warm the server first (`pandan warmup`; cold-start note above). Everything is access-gated to their PAT —
the boards their user owns or is a shared member of.
