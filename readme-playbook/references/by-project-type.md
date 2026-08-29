# README by project type

The core sections in SKILL.md hold for any project. What shifts is emphasis and what counts
as the "quick start."

## Contents
- Library / package
- CLI tool
- Service / application
- Internal-only repo

## Library / package

- Quick start is the install command plus the smallest possible working code snippet — the
  "hello world" of the API, not a full integration.
- Usage examples should map to the 2-3 things most consumers actually call; link to
  generated API docs for the rest rather than reproducing them.
- Versioning and compatibility (supported language/runtime versions, semver policy) matter
  more here than for an application — a consumer is committing to a dependency.
- Badges are more load-bearing than usual: published version and build status are genuinely
  useful signals for someone deciding whether to add this as a dependency.

## CLI tool

- Quick start is install-and-run-one-command, ending in visible output — a terminal
  recording or a copy-pasted transcript works better here than a screenshot.
- Usage should show the 2-3 most common invocations with real flags, not an exhaustive
  `--help` dump (that's what `--help` is for).
- If the tool has subcommands, show one full example per major subcommand rather than
  listing every flag combination.

## Service / application

- Quick start is "get it running locally," ending in a working local instance — the
  one-command dev-loop, if the project has one (see the docs-as-code / observability
  guidance in `dev-playbook` if it doesn't yet).
- A screenshot or short demo GIF of the running application does more work here than
  anywhere else — this is the project type where "visual" most directly answers "what is
  this."
- Configuration section matters more: environment variables, required external services,
  ports. List what's required to run versus what's optional.
- Deployment/production instructions, if any, belong in a separate ops doc, not the README —
  the README's job is "run this locally," not "operate this in production."

## Internal-only repo

- Skip the pitch — the audience already knows why the project exists. Lead straight with
  "how do I run this" and "where do things live."
- Link to runbooks, on-call docs, or architecture decision records rather than reproducing
  their content.
- A license section is usually unnecessary; note the internal-use status instead if that
  matters (e.g. "internal use only, not for external distribution").
- The agent-brief file (`CLAUDE.md`/`AGENTS.md`) carries the machine-actionable version of
  this content — see the `agent-brief` skill. Don't duplicate the same command list in both;
  the README stays human-oriented (why this exists, how a person gets oriented), the brief
  stays agent-oriented (exact commands, conventions).
