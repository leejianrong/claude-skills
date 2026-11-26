# Assist mode

The user is reviewing the PR themselves and wants help understanding it. Your job is to
orient them and point them at what matters. Do not hand down a verdict or a findings list
unless they ask for one; that is review mode.

## Steps

1. Gather context as in SKILL.md step 1 (PR metadata, linked issue, diff, CI status).
2. Read the changed code and enough surrounding code to explain it accurately.
3. Produce the briefing below.
4. Stay available: answer follow-up questions about specific files or hunks, explain
   unfamiliar code, and trace callers on request. If the user then asks "any problems?",
   switch to review mode for that scope.

## Briefing format

```
## PR #<n>: <title>  (by <author>, <+adds/-dels>, <n> files)

**Why:** <the problem or issue this solves, 1-2 sentences, from the description/issue>
**What changed:** <the approach in plain language, 2-4 sentences>
**CI:** <status>

### Read these first (in this order)
1. `path/core.py` (the heart of the change: <what to look at>)
2. `path/other.ts` (<why it matters>)
3. ...

### Supporting changes
- `path/tests/...` tests for <behavior>
- `path/models.py` small wiring change

### Safe to skim or skip
- lockfile, generated files, formatting-only or rename-only changes

### Where to look carefully
- <place where the logic is subtle, risky, or the PR description is thin, with file:line>

### Questions worth asking the author
- <only genuine ambiguities, not filler>
```

## Guidelines

- Order "Read these first" by understanding, not alphabetically: the core logic, then what
  calls it or feeds it, then tests. Aim for 3-5 files; a PR with more needs the
  grouping explained.
- Say what a file does in the PR, not what the file is in general.
- "Where to look carefully" is a pointer, not a verdict. Phrase it as "check how X handles
  Y", not "bug".
- If the PR mixes unrelated changes, say so and split the briefing by concern.
- If the description and the diff disagree, say that up front.
- Explain unfamiliar patterns or libraries briefly when they matter to the change.
