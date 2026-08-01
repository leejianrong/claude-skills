# Security and supply chain

Most shipped security incidents are dull: a committed key, an unpatched dependency, a diff
nobody read for injection. The gates here are cheap and prevent a whole class of regressions.

## Secrets never enter git

- **Ignore secret-bearing files** from the start — `.env`, credential JSON, local MCP/tool
  configs that hold tokens. Add them to `.gitignore` before they exist, not after.
- **Scan for accidental commits.** Run a secret scanner (gitleaks, trufflehog, or your
  platform's push protection) in CI and ideally in the pre-commit/pre-push hook. Catching a
  key before it's pushed is worth far more than finding it after.
- **Keep secrets in the environment or a secret store**, injected at runtime. Never bake a
  credential into an image, a config committed to the repo, or client-side code.
- **If a secret leaks, rotate it.** Git history is forever, and removing the file in a later
  commit does not un-leak it. Rotate the credential, then scrub if you must — but assume
  anything ever committed (or pushed) is compromised.
- **Redact secrets from logs and tool output.** Read tokens into a variable rather than
  inlining the literal; don't print them. Safety tooling may block a literal credential in a
  command — read it from its file into an env var instead.

A concrete habit: when you find a secret-bearing file that isn't tracked yet, confirm it was
*never* committed (check history across all branches) before assuming exposure — a false alarm
is common when a `git ls-files` check is written carelessly. Verify, then act.

## Least privilege

- Scope tokens to what they need and expire them. A deploy token deploys; it doesn't admin the
  account.
- Cookies for humans: HttpOnly, Secure, SameSite. Don't hand a session token to JavaScript.
- Server-authoritative trust: never trust a client's claim about state, identity, or rules —
  validate on the server.

## Security review for sensitive diffs

Any change touching auth, session handling, input parsing, file paths, subprocess/shell
invocation, or anything near secrets or user data gets an explicit security pass in review.
Look for the standard failure modes: injection (SQL, shell, path traversal), missing
authorization checks, trusting client input, unsafe deserialization, and secrets in logs. For
agent-driven review, a dedicated security-review pass over the branch diff catches what a
correctness review skips.

## Dependency hygiene

Dependencies are code you didn't write but still ship. Keep them honest:

- **Commit lockfiles** and install **frozen/reproducibly** in CI, so the versions CI validates
  are the versions a developer runs and the versions you deploy. An uncommitted lockfile or a
  `latest` range means CI is testing something nobody else has.
- **Scan for known vulnerabilities** (the ecosystem's audit tool, or Dependabot/Renovate/GHSA
  alerts) and treat a high-severity advisory as a real bug.
- **Keep a patch cadence.** Automated update PRs (Dependabot/Renovate) that run through the
  full CI gate, merged regularly, so you're never years behind and forced into a risky
  big-bang upgrade.
- **Minimize the surface.** Fewer, well-maintained dependencies over many thin ones. Every
  dependency is a trust decision and an update burden.
- **Pin toolchain versions** (language runtime, package manager) so builds are reproducible
  across machines and CI.

## Monorepo and shared-package note

If you split shared code into a local package, prefer a path/relative source over a global
workspace that silently pulls every package into one resolution — an independent lockfile per
package keeps each buildable on its own and keeps a fresh CI checkout portable. Give any new
shared package its own CI job mirroring the others.
