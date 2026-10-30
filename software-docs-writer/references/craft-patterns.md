# Craft patterns

Techniques observed in the Typer first-steps page, the FastAPI first-steps page and the
"Thinking in React" page. Use them as defaults; the source is named so you can look at a
live example.

## Contents

- Opening
- The tutorial ladder
- Code examples
- Showing output and the check-it step
- Errors and pitfalls
- Callouts and progressive disclosure
- Diagrams
- Recap and handoff
- Tone

## Opening

- **Go straight to a runnable example.** Typer's first page opens on a three-line script
  and "save it as `main.py`". FastAPI does the same with a six-line app. Explanation
  comes after the reader has something that works.
- A one-sentence statement of the outcome is enough. Skip "In this guide you will learn".

## The tutorial ladder

- **One concept per rung.** Typer's page edits the same `main.py` through: no argument,
  one argument, two arguments, a boolean option, an option with a value, a docstring.
  Each rung changes exactly one idea.
- **Repeat the full file at each rung** (FastAPI repeats its six-line app at every step)
  so the reader never has to reconstruct earlier code, and any rung can be copied alone.
  In longer files, highlight the changed lines (React uses `{2,3,10,11}` line highlights)
  and keep the prose on those lines.
- **End each rung or section in an artifact the reader can see** (React: a hierarchy list,
  a static app, a list of state variables, working state).
- **Teach a process with a checklist the reader can reuse.** React's step 3 applies three
  explicit tests to each piece of data, so the reader leaves with a method, not a
  conclusion.

## Code examples

- Every example runs as written. Run it, don't eyeball it.
- Full files in tutorials, trimmed fragments only in reference and explanation.
- Put the minimum version above the block when it matters ("Python 3.10+"). If versions
  differ in syntax, show the current one and put the old one in a tab or collapsed block.
- Pull snippets from real, tested source files and include them by path where the site
  generator supports it (Typer does this), so the docs break when the example breaks.
- Use realistic names (`greet`, `invoice`, `user_id`), not `foo` and `bar`, unless the
  concept is deliberately abstract.
- Show the install and import lines the first time. Skipping them is the most common
  reason a copied snippet fails.
- Put secrets, tokens and real hostnames out of examples; use obvious placeholders and
  say where the real value comes from.
- Comment sparingly: a comment should say something the code cannot, such as why.
- Terminal sessions: `$` before commands you type, no prefix on output, `//` or `#`
  comment lines to narrate what to notice (Typer does this).

## Showing output and the check-it step

- **After every action, say what the reader should see**, then show it. FastAPI's pattern:
  "Open `http://127.0.0.1:8000`, you will see `{"message": "Hello World"}`", then
  "open `/docs`, you will see Swagger UI" with a screenshot.
- Point at the one line that matters in a block of output ("there's a line with
  `Uvicorn running on http://127.0.0.1:8000`, that line shows the URL").
- Truncate long output with `...` and say it is truncated.
- Show rendered output after each change when the code shapes it (Typer shows `--help`
  after every signature change).
- Use real output captured from a run. Invented output is how docs end up lying.

## Errors and pitfalls

- **Show the failure before the fix** when the error teaches the rule. Typer shows
  "Missing argument 'name'" before passing the argument. React shows a form that ignores
  typing, with the real console error, before introducing the state that fixes it.
- Place a Pitfall callout at the exact step where the mistake happens, not in a list at
  the end ("at this point you should not be using any state values").
- In tutorials, tell the reader the symptom of the most likely wrong turn and the fix.
  In how-tos, one line per known trap is enough.

## Callouts and progressive disclosure

Use a small, fixed set of callout types and keep them out of the main flow:

| Type | Use for |
|---|---|
| Tip | A shortcut or editor hint, safe to skip |
| Note | A cross-reference or small clarification |
| Warning | Data loss, security, a destructive command |
| Technical details / deep dive | Internals or pedantry that some readers want and most don't |

- Put the optional depth in a callout (or collapsed block) so the main path stays short
  and a reader can skip it without losing the thread. FastAPI parks "FastAPI inherits from
  Starlette" in Technical Details.
- Defer formal terminology until the concept has been shown. Typer's argument-versus-option
  vocabulary section comes after the examples that demonstrate the difference.
- Mark optional steps as optional (FastAPI's deploy step).
- Ground an abstract term in a tool the reader already knows (Typer explains options with
  `ls ./myproject --size`).

## Diagrams

- Use a diagram where a sequence or relationship is hard to hold in prose (a request
  lifecycle, a component hierarchy). A decorative one earns nothing.
- Always give a text equivalent next to it (React follows its diagram with an indented
  list).
- Label what is the reader's code and what is the framework.

## Recap and handoff

- End a tutorial page with a short imperative recap, one bullet per step ("Import
  `FastAPI`", "Create an `app` instance").
- Optionally walk the code once more, step by step, after the reader has run it.
- Finish with the next page and one or two links by goal ("to deploy, see… ; to
  understand X, see…"). Never end on a dead stop.
- Cross-link at the point of need, not in a bibliography at the bottom (React links
  `useState` where the term first appears).

## Tone

- Second person for instructions, "we" in tutorials where you build together.
- Be candid about trade-offs ("this is a matter of preference") and say when something
  is optional.
- Keep humour to a light touch, and skip it in reference.
- Acknowledge progress briefly ("Nicely done", "That's it!") in tutorials and nowhere
  else.
