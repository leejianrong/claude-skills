# CI/CD

The pipeline exists to make "it works on my machine" irrelevant. Two properties matter most:
it's **fast enough that people wait for it**, and its result is **trustworthy** — green means
shippable, red means broken.

## The pre-push hook: a fast local gate

Install a pre-push hook that runs the cheap CI jobs locally: lint, type-check, and the
no-infra test layer. It catches the common mistakes before they cost a CI round-trip, so a
push rarely lands red.

Rules that keep it useful:

- **Only fast, no-infra checks.** Integration and e2e stay in CI. A hook that needs Docker or
  a browser is a hook people disable.
- **A documented escape hatch.** `git push --no-verify` for the rare scoped exception (a
  docs-only change, a hotfix). CI is still the real gate, so the bypass is safe.
- **One-line install, in the repo.** Keep the hook script in the repo and symlink it in
  (`ln -sf ../../scripts/git-hooks/pre-push .git/hooks/pre-push`), so it's version-controlled
  and everyone runs the same one.
- **Scope it to what changed** if the repo has independent packages, so a change in one
  package doesn't run another's toolchain.

## CI workflow

One job per concern, running in parallel:

- **lint** — the linter, in check mode.
- **unit** — the no-infra test layer.
- **integration** — the infra layer, with a real service (a CI service container, or
  testcontainers on a Docker-capable runner).
- **build / type-check** — compile the frontend, type-check, produce the artifact.
- **e2e** — the browser/protocol smoke, booting the stack.
- Add one per extra package (an SDK, a CLI) that has its own toolchain.

Make it reproducible and quick:

- **Frozen, lockfile-based installs.** `--frozen` / `npm ci` / the equivalent, so CI resolves
  the exact versions a developer has. A CI install that resolves differently is a latent bug.
- **Dependency caching** keyed on the lockfile.
- **Cancel-in-progress** for the same ref, so a new push doesn't wait behind a stale run.
- **Path filters** so a docs-only change doesn't run the whole matrix — but keep required
  checks reporting green (a gate-safe skip), or branch protection blocks the merge forever.

## Keep pinned actions and the runner toolchain current

Third-party actions are pinned to a version (`@v3`, or a SHA) — and that pin rots. The runner
platform periodically **deprecates the runtime** an action runs on (e.g. GitHub's Node 20 →
Node 24 migration, deprecated Sept 2025): an action still targeting the old runtime keeps
working — the runner force-runs it on the new runtime — but emits a deprecation warning on
**every** run, and the grace period eventually ends in a hard failure. Don't let that warning
become background noise; treat it as a dated to-do.

- **Bump the flagged actions to their latest major**, which ships on the new runtime. Verify
  before trusting the tag: an action's `action.yml` declares `runs.using` (`node24`,
  `composite`, `docker`) — check it targets the new runtime, and skim the release notes for
  breaking input changes across the major jump (a `v5 → v7` bump can drop or rename inputs you
  pass).
- **Pin to a tag that actually resolves.** The latest *release* (`v8.3.2`) doesn't guarantee a
  matching *moving major* tag (`v8`) exists — some actions lag or stop publishing bare-major
  tags, so `@v8` fails with "unable to resolve action." List the repo's tags and pin to the
  highest major that exists (or the exact release SHA/tag). Don't infer `@vN` from a `vN.x.y`
  release name.
- **Composite and wrapper actions hide transitive versions.** A warning naming
  `upload-artifact@v4` may come from a *composite* action you call (e.g. an upload-pages
  wrapper) that pins the old one internally — bump the wrapper, not a direct dependency you
  don't have. Read the composite's `action.yml` to confirm what it now wraps.
- **Sweep every workflow file**, not just the one that surfaced the warning — the same stale
  action is usually pinned in several (`grep -rn 'uses:' .github/workflows/`). Actions already
  on the current runtime are left alone.
- **This is a docs/CI-only change** — it deploys nothing, so it's a safe, low-risk PR to land
  on its own.

## Required vs reported checks

Decide which jobs *block* a merge (branch protection) and which merely *report*. A common
split: lint / unit / integration / build are required; e2e and per-package jobs report but
aren't individually required, because they're slower or flakier. Be explicit — a job that
"passes" only because it was skipped by a path filter tells you nothing, so don't let a
skipped job stand in for a required one.

## Infra flake vs real failure

Before reacting to a red, read *why* it's red:

- **Infra symptoms:** every job failing at the same suspiciously round duration; "the job was
  not acquired by a runner"; a TLS/network error during setup; a red that a plain re-run
  clears. These are the CI platform, not your code. **Re-run**, don't touch code, don't move
  the work backward.
- **Real failure:** a specific assertion fails with a real diff, reproducibly. **Fix it.**
- **The trap:** a flaky test failing on an unrelated PR. It's neither infra nor that PR's
  bug — it's a determinism bug in the test (see `layered-testing.md`). Re-run to unblock, but
  file it and fix the race, or it taxes every PR.

When you re-run for a flake, say so out loud ("re-running; the failure is the known X flake on
an unrelated diff") so nobody mistakes it for ignoring a real red.

## Deploy: gated, validated, armable

Continuous deployment should ship only what CI validated:

- **Trigger on CI success**, not on merge directly, and **check out the exact SHA** CI tested
  — not the current tip of `main`, which may have moved.
- **Arm it explicitly.** A flag/variable and a deploy token you can flip off. Off by default
  until the app is actually live and someone owns rollbacks.
- **Skip non-deployable changes.** Docs-only, CI-only, and tooling-only merges shouldn't
  trigger a rollout. A merge that only touches the docs site or `.github/` should deploy
  nothing.
- **Know your rollout window.** A rolling deploy briefly serves the old and new versions; a
  superseded deploy (a later merge cancels an earlier one) is fine as long as the later one
  ships the newer commit. Verify prod reflects the intended SHA after a deploy, especially
  after a migration.

## Observability, briefly

You can't call it shipped if you can't see it running. The minimum: a **health endpoint** the
platform and your uptime check hit, **structured logs** (so you can grep by request/game/user
id), and **error tracking or basic metrics** so a spike is visible without tailing logs. This
is a production-readiness floor, not an observability program — add tracing and dashboards
when real traffic justifies them.
