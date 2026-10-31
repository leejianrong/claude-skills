# Comments

## What earns a comment

A comment earns its place when it holds something the code can't say:

- A hidden constraint ("the vendor API rate-limits to 5 requests per second").
- A workaround for a specific bug, ideally with a pointer to it.
- A surprising invariant or ordering requirement.
- The reason the obvious approach doesn't work.

## What doesn't

- A restatement of the code ("increment the counter").
- A narration of the change ("added retry to fix the timeout"). That belongs in the commit
  message or the PR.
- Commented-out code. Version control has it.
- A section banner that a function or file name would replace.
- A TODO with no owner or condition. Either do it, or file it where it will be seen.

If a comment explains confusing code, make the code clear instead, then drop the comment:
rename the variable, extract a well-named function, or reshape the data.

## Docstrings are separate

Docstrings document the contract of public APIs and of anything others call: what it is for,
the arguments, what it returns or raises, a short example where it helps. Keep writing them in
the project's style. They describe use, not implementation.

## Constraint comments

A comment that says "don't change this because ..." is a rule held in prose. Prefer to enforce
it:

1. If it can be a type, a runtime check, a test or a lint rule, encode it, then delete the
   comment.
2. If it records something outside the team's control (a third party's behavior), keep it.
3. If you can't verify it either way, keep it and flag it for review in your summary, so a
   human can decide. Don't delete a rule you can't check.

## Removing comments in a diff

During the diff audit, remove comments you added that fail the test above. Leave pre-existing
comments alone unless the task is about them, or your change makes one wrong. A comment your
change made false is a bug: fix or remove it.
