# UX notes & gotchas

Portable field notes from running the PM loop — the reusable subset, not project-specific
trivia. Read this once you're actually executing Step 2 of the PM loop; skip it for a first
read of the playbook.

## Contents
- Cold start
- API surface quirks (`move_card` vs `update_card`, `list_cards` scoping, column vs work state)
- Structured extras (dependencies, links, comments)
- MCP tool vs field visibility, and "tools missing" config traps
- Worktree and branch hygiene
- Branch protection serializing parallel landings
- Cleanup safety
- Deploy timing and prod-verify patterns
- Interrupted-agent recovery
- Release/distribution gating
- UI cards: design-first workflow

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
