---
name: lean-code
description: Keep feature work small and the codebase from growing without need - read what exists before adding, write the smallest diff, delete what the change supersedes, and keep comments to the non-obvious why. Use on any feature work, whenever adding or changing behavior in a codebase, and also for refactors and bug fixes. Apply before writing code and again as a diff audit before opening a PR. Triggers include "add a feature", "implement", "build", "change how X works", "refactor", and "fix this bug".
---

# Lean code

Every line added is a line someone must review, test and maintain. The default for any
change is to leave the codebase the same size or smaller behind the same or a smaller
surface. The aim is less for a reviewer to read, not fewer characters. Don't golf readable
code into something clever, and don't delete something just because you don't yet
understand why it is there.

## The loop

1. **Restate the goal and the smallest change that would satisfy it.** One line, then keep
   going. Don't wait for a reply unless the goal is genuinely ambiguous.
2. **Read before you add.** Look for something to reuse, extend or replace. Search for the
   existing helper, the existing type, the existing pattern. Adding a second way to do a thing
   is the most common way a codebase bloats.
3. **Name the data shape first.** Decide the types and states before the logic. An explicit
   state or lookup table beats a pile of booleans or another branch in an if/else chain. See
   `references/principles.md` (model the domain).
4. **Write the smallest diff that meets the done-condition.** No speculative options,
   parameters, wrappers, or abstractions that have a single caller. Design for the behavior
   asked for, not imagined future cases.
5. **Delete as you go.** If the new code supersedes something, remove the old path in the same
   change: the dead code, the unused exports, the old call sites, the compatibility shim. Move
   callers to the new API and delete the old one instead of keeping both. Delete tests that
   only protect an implementation you removed. See `references/principles.md`.
6. **Verify against the real behavior.** Run the thing and look at the result. "It compiles"
   and "tests pass" are not enough if the tests would pass without the change. For testing
   practice and for claims about performance, see `dev-playbook`.
7. **Run the diff audit** (below) on your own diff.
8. **Open the PR with the net line change in the description**, for example "+84 / -212". If
   the diff only grew, say in one sentence why that was necessary. PR text standard: see
   `software-docs-writer` (`references/pr-and-commit-text.md`).

**Bug fix, in one line:** reproduce it first, find the root cause rather than the symptom, and
ship the smallest change the evidence supports. A speculative "might help" edit is a
hypothesis, not a fix.

## Diff audit

Before opening the PR, read your own diff (`git diff origin/main...HEAD`) and ask:

- What can be deleted? Dead code, unused imports and exports, leftover debug output,
  commented-out code.
- What duplicates something that already exists? Reuse it, or consolidate into one place.
- Which abstraction, wrapper or adapter has exactly one caller and no second implementation?
  Inline it.
- Is the same decision made in more than one place? Put it behind one source of truth.
- Did I add a validator, guard or fallback for a case that can't happen? Remove it. Keep
  validation at real boundaries (user input, network, files), where input is untrusted.
- Which comments restate the code, narrate the change, or hold code that was turned off?
  Remove them. See the comments rule below.
- Does each new layer or piece of state save a reader at least as much effort as it costs?

Then check the number: `git diff --shortstat origin/main...HEAD`. A feature that mostly adds
lines should be able to say why.

## Comments

Comment only a **non-obvious why**: a hidden constraint, a workaround for a specific bug, a
surprising invariant, a reason the obvious approach doesn't work. Write nothing that restates
what the code does, narrates the change ("added X to fix Y"), or keeps old code around.

Docstrings are a separate thing and are good. Write them for public APIs and for anything
others call, in the project's docstring style. A docstring says what a function is for and how
to use it. Don't turn a docstring into a narration of the implementation.

If a comment records a rule you can't verify (an external system's behavior, a team decision),
keep it and flag it for review. Don't silently delete it. If a constraint can be encoded as a
type, a check, a test or a lint rule, encode it and delete the comment. Details:
`references/comments.md`.

## Reference files

- `references/principles.md`: the six principles behind the loop, each with when it applies.
- `references/comments.md`: what earns a comment, what doesn't, and how to handle constraint
  comments.
- `references/enforcing.md`: turning these rules into checks (lint, dead-code tools, a
  net-lines line in the PR), so they don't rely on remembering.

## Related skills

- `dev-playbook` for tests, gates and verifying claims.
- `natural-writing` for how an agent writes replies and summaries (short, answer first,
  claims labeled measured, inferred or guess).
- `software-docs-writer` for PR descriptions, commit messages and docs.
- `cleanup` for removing the branches, worktrees and processes your task created.
