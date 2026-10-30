---
name: software-docs-writer
description: Write, restructure, or review the content of technical documentation for a software project (library, CLI, framework, API, service), the way the FastAPI, Typer, and React docs do it. Picks the right page type (tutorial, how-to guide, reference, explanation), applies page-level craft (runnable full-file examples, shown output, check-it steps, callouts), and runs a style and consistency pass. Use when asked to write or improve a getting-started guide, tutorial, user guide, API or CLI reference, concept page, or "docs for this library", when docs feel confusing, bloated, or like one page doing four jobs, or when auditing docs for quality. For READMEs use readme-playbook, for docs site tooling and CI use dev-playbook, for prose tells use natural-writing.
---

# Software docs writer

Good docs fail in one of two ways: a page tries to be a tutorial, a reference and an
essay at once, or a page is the right type but the reader can't follow it (untested
code, no visible output, a wall of explanation before the first working thing). This
skill fixes both. Pick the page type first, then apply the craft.

## Workflow

Copy this checklist and tick it off:

```text
- [ ] 1. Read the code, not just the existing docs (what does it actually do?)
- [ ] 2. Name the reader and the job they came to do
- [ ] 3. Pick the page type with the compass (below)
- [ ] 4. Outline against that type's rules (references/page-types.md)
- [ ] 5. Draft: runnable examples first, craft patterns (references/craft-patterns.md)
- [ ] 6. Run every code block and paste the real output
- [ ] 7. Style and consistency pass (references/style.md), then scripts/check_docs.py
- [ ] 8. Cut: move anything off-type to the right page and link to it
```

Step 6 matters most. Docs written from memory of the API drift from the code, and a
tutorial with one broken step costs the reader their trust in every other step.

## The compass: which page is this?

Two questions place any piece of content (the Diátaxis framework):

| | The reader is studying | The reader is working |
|---|---|---|
| **Content is about doing** | **Tutorial** (we lead them through a build) | **How-to guide** (they have a goal, give them the steps) |
| **Content is about knowing** | **Explanation** (why it works this way) | **Reference** (the facts, to look up) |

Ask "is this about an action or about knowledge?" then "is the reader learning or
getting something done?". If a draft answers differently halfway down the page, split
it. Link between the pages instead of merging them: a how-to that stops to explain
design history loses the reader who just wanted the steps.

## Defaults when the request is vague

- "Write the docs for X" for a new project: build a **getting-started tutorial** first
  (one runnable path to a working result), then a **reference** generated from the
  code, then how-tos as real questions come in. Explanation pages come last.
- "Improve these docs": classify every existing page with the compass, list the pages
  that mix types, and fix the worst offender first. Report the classification before
  rewriting, because the fix is usually a split, not a polish.
- Unknown audience: assume a competent developer who is new to this library, not new
  to the language.

## What good looks like

The craft patterns come from reading the FastAPI, Typer and React tutorials closely.
The short version:

- Open on a complete, runnable example. No preamble.
- Every step changes one thing, shows the full file, and shows the output.
- Say what the reader should see after each action, and show the error before the fix
  when the error teaches something.
- Put depth the reader can skip (internals, edge cases, history) in callouts, so the
  main path stays short.
- End each page with a recap and a pointer to the next page.

Read `references/craft-patterns.md` before drafting any tutorial or how-to.

## Reference files

- `references/page-types.md`: rules, anti-patterns, titles and a skeleton for each of
  the four page types. Read at step 4.
- `references/craft-patterns.md`: page-level techniques with the docs they come from,
  plus code-example rules. Read before drafting tutorials and how-tos.
- `references/style.md`: the style rules worth enforcing (voice, headings, lists, links,
  terminology table, accessibility). Read at step 7.

## Checking a draft

Run the checker on the docs directory or a single file:

```bash
python3 scripts/check_docs.py docs/
```

It flags heading-level jumps, empty or unlabelled code fences, broken relative links,
sentences over 35 words, positional references ("as shown above"), and a short list of
filler words. It exits 1 on errors so it can run in CI. If the project has a `.vale.ini`,
leave prose style to Vale and use the script for the structural checks only. Treat the
output as a prompt to look, not a verdict: a long sentence in a reference table is fine.

## Related skills

- `readme-playbook` for the README (a README is a front door and a quick start, not the
  whole docs).
- `dev-playbook` (`references/docs-as-code.md`) for building and publishing the site.
- `natural-writing` for prose rhythm and the tells that mark machine-written text.
