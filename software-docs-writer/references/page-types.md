# Page types

Rules from [Diátaxis](https://diataxis.fr/), tightened for software projects.

## Contents

- Tutorial
- How-to guide
- Reference
- Explanation
- Fixing a page that mixes types

## Tutorial

The reader is a newcomer who wants to learn by doing. You are responsible for their
success, so the path must work every time.

**Rules**

- State what they will build at the start ("In this tutorial we build a CLI that greets
  you"), not what they will learn.
- Produce a visible result at every step, however small.
- Say what they should see after each action. Show real output.
- Warn about likely failure points and what the symptom looks like.
- Keep explanation to a sentence and link out for more.
- No options, alternatives or branches. One path.
- Make steps repeatable where you can, so a reader who gets lost can rerun the step.
- Use "we" ("we create a file") to signal you are doing it together.

**Anti-patterns**: "In this tutorial you will learn…", a concepts section before the first
command, "you could also…", an irreversible step with no warning, steps never run end to
end.

**Title**: name the thing built or the first outcome ("Your first CLI", "First steps").

**Skeleton**

```text
# <Outcome>

<One sentence: what we build.>

## <Smallest working version>      <- full runnable file, then run it, then output
## <Add one thing>                 <- full file again, run, output
## <Add one more thing>
## Recap                           <- imperative bullets, one per step
## Next steps                      <- link to the next tutorial page and to a how-to
```

## How-to guide

The reader is competent, has a real goal, and wants the steps. Serve the job, not the
tool's feature list.

**Rules**

- Start from the user's goal ("How to add authentication to a route"), not from a
  feature ("Security features").
- Assume they know the basics. Don't re-teach.
- Action only: the steps and the judgement calls. Move background to explanation and
  option lists to reference, and link.
- Write it to adapt. Real situations vary, so say where steps fork ("If you use async
  routes, do X instead").
- Order by real dependency and by flow, so the reader doesn't jump around.
- Conditional imperatives work well: "If you want X, do Y."
- It can start and end at sensible points. It doesn't have to be complete.

**Anti-patterns**: a tutorial in disguise (explaining each concept), a procedure with no
judgement where judgement is needed, a title like "Authentication" that could be a
tutorial, an explanation or a reference.

**Title**: begin with "How to" and state exactly what it achieves. Open with "This guide
shows you how to…".

**Skeleton**

```text
# How to <do the specific thing>

This guide shows you how to <thing>. <Prerequisite in one line, linked.>

## <Step in the order the work happens>
## <Step>      <- include the fork: "If X, do Y"
## Verify it works
## Related     <- reference page, the explanation page, adjacent how-tos
```

## Reference

The reader is mid-task and needs a fact. They arrive by search or by scanning, never by
reading top to bottom.

**Rules**

- Describe and only describe. No teaching, no opinions, no "you should".
- Mirror the structure of the code (modules, commands, endpoints) so the docs and the
  product can be navigated in parallel.
- Use one pattern for every entry: name, signature, parameters (table), returns, errors,
  a short example. Consistency is how readers find things.
- List everything: every option, flag, default, limit, error message and exit code.
- Keep examples short and illustrative, never a walkthrough.
- State warnings where they apply (a flag that deletes data, a deprecated parameter).
- Generate it from the code where you can (docstrings, OpenAPI, `--help`), then edit,
  because generation alone leaves gaps and awkward wording.

**Anti-patterns**: a tutorial paragraph inside a parameter description, undocumented
defaults, entries that differ in layout, prose where a table would do.

**Skeleton (one entry)**

````text
### `function_name(arg, *, option=default)`

One sentence saying what it does.

| Parameter | Type | Default | Description |
|---|---|---|---|

**Returns** `type`: what it is.
**Raises** `ErrorName`: when.

```python
# the shortest example that shows typical use
```text
````

## Explanation

The reader wants to understand why. They are away from the keyboard, reading to build a
mental model.

**Rules**

- Frame it around a "why" question ("Why does the framework use dependency injection?").
  Without one the page has no edges.
- Cover context: design decisions, history, constraints, alternatives considered, and
  what was traded away.
- Take a view where it helps, and acknowledge the other views.
- Use analogies, and say where they stop holding.
- Connect to related topics.
- Leave out step-by-step instructions and exhaustive option lists. Link to those.

**Title**: reads naturally with an implied "About" in front ("About the request
lifecycle").

## Fixing a page that mixes types

| Symptom | What's wrong | Fix |
|---|---|---|
| A tutorial that pauses for a design discussion | Explanation inside a tutorial | Cut to one sentence, link to an explanation page |
| A how-to that lists every flag | Reference inside a how-to | Keep the flags the task needs, link the rest |
| A reference page with "first, install…" | Tutorial inside reference | Move to the tutorial, link from the reference |
| A page titled with a noun ("Authentication") | Type unclear | Split by reader goal: tutorial step, how-to, concept page |
| A README that is the whole docs | Four types in one file | Keep a quick start, move the rest into pages by type |
