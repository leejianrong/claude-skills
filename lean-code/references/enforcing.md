# Enforcing the rules

A rule held only in prose gets forgotten. Where a check is cheap, add one. Order of preference:
a check that fails the build, then a script the agent runs, then a line in the repo's agent
brief (see `dev-playbook`, `references/agent-enablement.md`).

## Net line change

```bash
git diff --shortstat origin/main...HEAD
```

Put the result in the PR description. It takes one command and makes growth visible.

## Dead and commented-out code

Use whichever of these the stack already has. Check the tool's docs for current options.

- Python: `ruff` rule `ERA001` flags commented-out code. `vulture` finds unused code.
- TypeScript: `knip` reports unused files, exports and dependencies.
- Go: `golang.org/x/tools/cmd/deadcode` reports unreachable functions. See `go-playbook`.

Run them in the fast pre-push gate only if they are quick. Otherwise run them in CI.

## When not to automate

The diff audit's judgment calls (is this abstraction justified? does this comment earn its
place?) can't be linted. Leave those to the audit, and keep the instruction short with one
example of the failure.
