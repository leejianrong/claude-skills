# Review checklist

Contents: Correctness · Security · Design and scope · Readability · Error handling ·
Dependencies and config · Docs · Language notes

Use as prompts for what to look for, not a form to fill in. Report only what you find.

## Correctness
- Edge cases: empty, null/None/undefined, zero, very large, duplicates, unicode, timezones.
- Off-by-one, wrong operator, inverted condition, mutated shared state.
- Concurrency: races, missing awaits, unhandled promises, shared mutable state, retries
  that aren't idempotent.
- Does the change break callers? Search for usages of changed signatures and behavior.
- Migrations and data changes: reversible, safe on existing data, safe to deploy in either
  order with the code.

## Security
- Secrets, tokens, or credentials in code, tests, fixtures, logs, or config.
- Untrusted input reaching SQL, shell, file paths, HTML, templates, or deserializers.
- Authn/authz checks present on new endpoints and actions.
- New dependencies: needed, maintained, pinned.
- Sensitive data written to logs or error messages.

## Design and scope
- Smallest change that solves the problem; nothing unrelated bundled in.
- Reuses existing helpers and patterns instead of adding a parallel one.
- No abstraction without a second use. No dead code, commented-out code, or leftover debug.
- Boundaries respected: logic in the right layer, no reaching across modules.

## Readability
- Names say what things are. Functions do one thing and fit on a screen.
- Comments explain non-obvious why, not what.
- Consistent with the surrounding code, even where you'd choose differently.

## Error handling
- Errors are handled or propagated deliberately, never swallowed (`except: pass`,
  empty `catch`).
- Failure messages carry enough context to debug.
- Resources are released (files, connections, timers, listeners).

## Dependencies and config
- Lockfile updated with manifest. No unrelated version bumps.
- New env vars or config documented and given safe defaults.

## Docs
- User-visible behavior, CLI flags, API shape, or setup steps changed: README and docs
  updated.
- Public functions with non-obvious contracts have docstrings.

## Language notes
Apply these on top of the general points; for other languages use the language's own
common pitfalls.

**Python:** mutable default arguments; bare `except`; missing type hints on public
functions where the repo uses them; blocking calls inside `async` code; `open()` without a
context manager; tests that rely on ordering or real network.

**TypeScript / JavaScript / React:** `any` or unchecked casts hiding errors; missing
dependency-array entries or stale closures in hooks; state derived in an effect instead of
during render; missing `key` or index-as-key on reorderable lists; floating promises;
effects without cleanup; `==` vs `===`; accessibility on new interactive elements.
