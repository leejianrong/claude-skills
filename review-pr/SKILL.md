---
name: review-pr
description: Review a pull request written by a teammate or another agent, either as structured severity-ranked feedback or as a guided walkthrough while the user reviews it themselves. Use when the user says "review PR 123", "look at this PR", "review this branch", "is this ready to merge", "give feedback on this diff", "help me understand this PR", "walk me through this PR", or "which files should I look at". Not for writing PR descriptions, fixing the code, or merging.
---

# Review a PR

## Modes

- **Review mode (default):** you review the PR and report findings. Follow this file.
- **Assist mode:** the user is reviewing it themselves and wants help understanding it
  ("walk me through", "what's this PR about", "which files matter", "I'll review it, help
  me"). Read `references/assist-mode.md` and follow it instead of the workflow below. If
  the request is ambiguous, default to review mode and offer a walkthrough.

## Review mode

Produce a review the author can act on. You draft; the user decides. **Never approve,
request changes, merge, close, or post a comment unless the user explicitly asks.** Default
output is text in the terminal.

## Workflow

Copy this checklist and tick it off:

- [ ] 1. Gather context
- [ ] 2. Check intent: does the diff do what the PR and linked issue say?
- [ ] 3. Check tests (blocking if missing)
- [ ] 4. Review the code against `references/review-checklist.md`
- [ ] 5. Run the checks if cheap (tests, linter) and note the result
- [ ] 6. Write the review in the format below

### 1. Gather context

```bash
gh pr view <n> --json title,body,author,baseRefName,headRefName,files,statusCheckRollup,closingIssuesReferences
gh pr diff <n>
```

Read the PR description and any linked issue before the diff. Note CI status. If the PR is
large (roughly 400+ changed lines or many unrelated files), say so as a finding; don't
silently skim it.

Read surrounding code for anything non-trivial in the diff. A diff alone hides callers,
invariants, and existing helpers the change should have reused.

### 2. Intent

State in one sentence what the PR does, then check it against the description and issue.
Flag missing scope (issue asks for X, PR does half) and extra scope (unrelated changes
bundled in).

### 3. Tests

Tests are required for any behavior change. A PR with new or changed behavior and no tests
is **blocking**. Also check that the tests are real: they fail without the change, assert
outcomes rather than just "doesn't throw", and weren't weakened, skipped, or deleted to get
CI green. Pure refactors need existing tests to still pass, not new ones.

### 4. Review the code

Work through `references/review-checklist.md` (correctness, security, design, readability,
error handling, docs, plus Python and TS/JS notes). Read it once per review.

### 5. Run checks

Check out the PR in a worktree or use `gh pr checkout` only if the user is fine with
switching branches; otherwise rely on CI status. Don't claim tests pass unless you ran them
or CI shows it.

## Severity

| Tier | Meaning | Author must |
|---|---|---|
| **Blocking** | Bug, security issue, missing tests for new behavior, breaks existing behavior, leaked secret | fix before merge |
| **Should fix** | Real maintainability or correctness risk that isn't an outright bug | fix or reply with a reason |
| **Nit** | Style or preference | optional |

Cap nits at about three and group the rest ("naming is inconsistent in a few places"). If a
linter or formatter could catch it, say that instead of listing every instance. Only report
what you can point to in the diff; if unsure, phrase it as a question.

## Output format

```
## PR review: <title> (#<n>)
**What it does:** <one sentence>
**Verdict:** ready to merge | ready after should-fix items | needs changes
**CI:** <passing / failing / not run>

### Blocking
- `path/file.py:42` <problem>. <why it matters>. <suggested fix>

### Should fix
- ...

### Nits
- ...

### Done well
- <one or two specific things, not generic praise>
```

Omit empty sections. Keep each finding to what, why, and how to fix. Be direct and kind;
critique the code, not the author.

## If the author is an agent

Also look for the failure modes agents have more often than people: tests that assert
nothing or mirror the implementation, over-engineering (new abstractions for one use),
duplicated helpers that already exist, unrelated edits, invented APIs or parameters, and
comments that narrate the code. Apply the same severity bar; don't be softer or harsher.

## Posting

Only if the user asks, post with `gh pr review <n> --comment --body-file <file>` (summary)
and, for inline comments, the review API as a pending review for the user to submit.
Show the exact text to be posted first. Never use `--approve` or `--request-changes`.
