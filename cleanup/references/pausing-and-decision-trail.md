# Pausing work and leaving a decision trail

Two ways to avoid leaving a mess of a different kind: unfinished work nobody can resume, and a
long autonomous run nobody can audit.

## Contents
- Pausing safely
- Decision trail for long runs

## Pausing safely

Pause only when explicitly asked. "Keep going" and "don't stop" mean don't pause.

1. **Stop at a safe point.** Finish the current indivisible step, or undo it if it can't be
   finished cleanly. Don't start anything new. Stop any subagents or background processes you
   started.
2. **Avoid irreversible actions.** Don't open a PR or push, unless one was already open.
3. **Save the work.** Commit uncommitted changes as a single `wip:` commit on the current
   branch. If the code is broken, say so in one line of the commit body.
4. **Write a resume note** and save it where the next session will find it (the scratchpad
   directory, or a path the user names). Include:
   - the goal
   - what you were doing
   - progress, and what has been verified
   - the current state
   - next steps
   - key files
   - gotchas

   If a decision trail already exists, link to it instead of copying it.

In your reply, say where you are, what is saved on disk (as file paths) and what exists only
in your head, the commits you made and whether the working tree is clean, and the first action
to take on resume.

## Decision trail for long runs

For a long or unattended run, keep an append-only log so a reviewer can see what happened and
why without reading the transcript. A TSV with one row per decision works, for example
`.audit/<task-slug>.tsv`. Columns:

| Column | Content |
|---|---|
| `ts` | ISO 8601 timestamp |
| `phase` | the phase or workstream |
| `decision` | what was chosen or done, in one line |
| `why` | the reason, in plain words |
| `evidence` | a pointer: commit SHA, PR number, `file:line`, or artifact path. Never a paragraph. |
| `result` | the outcome, such as `tests green`, `reverted`, `inconclusive` |

Log forks you chose, units you finished with their verification result, pivots and reverts with
their trigger, and blockers. Skip trivial actions. Fix a wrong row by adding a superseding row,
never by editing history. Keep each cell on one line.

Keep the log out of git by default. Commit it only when a reviewer needs the trail to trust the
result.
