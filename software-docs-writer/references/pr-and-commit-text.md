# PR descriptions and commit messages

A PR description is a briefing for a reviewer who already has the diff. It is not a log of
how the work was done. The same writing rules as the rest of the docs apply (plain words, one
idea per sentence, real names from the code), minus the page-type choice.

## Contents
- Commits
- PR title
- PR body
- What to leave out
- Check before opening

## Commits

- Commit freely while working, then rebase into small, ordered commits before opening the PR.
  Each commit should land on its own and tell part of the story.
- Amend when a fix belongs in the last commit. Add a new commit when the change is separable.
- The subject line is short and imperative. The body explains why, not what the diff already
  shows.
- If the repo has a commit convention, follow it. If it has none, use Conventional Commits.

## PR title

Use Conventional Commits unless the repo says otherwise: `type(scope): subject`, no trailing
period.

- **type**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf`.
- **scope**: the affected area.
- **subject**: short and imperative. Name a real symbol when it carries the change.

## PR body

Aim for something a reviewer reads in under a minute, and under about 40 lines (with squash
merges it becomes the commit body). Use `##` headings in this order and drop any section with
nothing to say:

1. **Why**: the problem and the approach, in one to three sentences.
2. **What changed**: one to three bullets. Name both sides of a rename or move.
3. **Scope**: what the change covers and what it leaves out. Always include this one.
4. **Tradeoffs**: only the rejected alternatives a reviewer would likely question.
5. **Blast radius**: one or two sentences on what the change touches and whether that is
   safe. If it changes a default or deploys, say so.
6. **Verification**: one to three bullets, each with a real command or path and its outcome.
   For a performance change, give one primary number as before and after with its unit, and
   link the detailed results (see `dev-playbook`, `references/verifying-claims.md`).

For a change that touches code, state the net line change ("+84 / -212"). If the diff only
grew, say why in one sentence.

Attach a screenshot or video only when it proves a claim.

## What to leave out

- Full SHAs, rebase history, and "based on main" preambles.
- Logs of parallel agent runs, and sample-size methodology.
- Metric tables and file-by-file checklists. Link them from a separate file instead.
- Verdicts like "CLEAN" with no evidence behind them.

## Check before opening

- Can a reviewer say what the change does and why after the first paragraph?
- Does every claim in Verification name something that was actually run?
- Did you use the same name for each thing throughout?
- Run the `natural-writing` revision checklist over the text.
