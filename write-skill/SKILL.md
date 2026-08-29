---
name: write-skill
description: Author a new SKILL.md or audit an existing one, for Claude Code or other agent harnesses (OpenCode, Codex CLI, Cursor, Gemini CLI). Covers frontmatter rules, degrees of freedom, progressive disclosure (SKILL.md vs references/scripts/assets), content hygiene, and a pre-share checklist. Use when creating a new skill, reviewing or trimming an existing one, deciding how to split content across files, or a skill isn't triggering/working as expected.
---

# Write skill

A skill is a directory of instructions an agent loads on demand, not a one-off prompt. The
agent's context window is a shared resource — every line in SKILL.md competes with the
actual task once the skill loads. Write accordingly.

## Before you write anything

Do the task yourself first, with an agent, no skill. Notice what you had to explain
repeatedly — that repeated explanation is the skill's actual content. A skill written for a
task you haven't done yet documents an imagined problem, not a real one.

Write 2-3 real prompts the finished skill should handle before drafting the body. Use them
to check the draft against, and after any real use, notice where the agent got confused or
skipped something — revise from that observation, not from guessing what might help.

## Frontmatter

Two required fields, both load into every session's context regardless of whether the skill
fires, so both must earn their tokens:

- `name`: lowercase letters, numbers, hyphens only, ≤64 chars, no XML tags. On Claude Code
  specifically, `claude` and `anthropic` are reserved and rejected — avoid them anywhere you
  want the skill portable. Prefer gerund form (`writing-tests`) or an action verb
  (`write-tests`); avoid vague nouns (`helper`, `utils`, `tools`).
- `description`: third person, ≤1024 chars, states **both** what the skill does **and** when
  to use it, with concrete trigger terms. Description quality is the single biggest lever on
  whether the skill fires at all — a skill with perfect instructions and a vague description
  never gets picked. Skew slightly pushy about triggers; skills under-fire more often than
  they over-fire.

  - Bad: `Helps with documents` — no trigger terms, no scope.
  - Good: `Extract text and tables from PDF files, fill forms, merge documents. Use when
    working with PDF files or when the user mentions PDFs, forms, or document extraction.`

## Degrees of freedom

Match specificity to how fragile the task is — don't default to one style everywhere.

- **High freedom** (prose, heuristics): multiple valid approaches, judgment depends on
  context. E.g. "review the diff for readability and edge cases."
- **Medium freedom** (a template or parameterized pattern): a preferred shape exists but
  some variation is fine. E.g. a report template with a "adapt as needed" note.
- **Low freedom** (an exact command, "do not modify"): the operation is error-prone or must
  run in a specific sequence. E.g. a migration script run verbatim.

Think of it as a bridge over a cliff (low freedom — one safe path, be exact) versus an open
field (high freedom — many paths work, just point the direction).

## Structure and progressive disclosure

SKILL.md is a table of contents, not the whole book. Keep the body well under 500 lines;
push depth into files the agent loads only when it needs them:

```
skill-name/
├── SKILL.md          # overview + navigation, always read once triggered
├── references/       # deeper material, read on demand, zero cost until then
│   └── topic.md
├── scripts/           # executed, never read into context (only its output is)
│   └── do_thing.py
└── assets/            # templates/boilerplate consumed by the output, not read as prose
```

Rules that matter more than they look:

- **One level deep.** Every reference file links directly from SKILL.md. Don't chain
  references (SKILL.md → advanced.md → details.md) — an agent following a reference to a
  reference often previews with something like `head -100` instead of reading the whole
  file, and silently works from a partial read.
- **Table of contents in any reference file over ~100 lines**, so a partial read still shows
  the full scope of what's there.
- **Name files by content**, not position: `form_validation_rules.md`, not `doc2.md`.
- **Split by domain, not by size alone**, when a skill covers multiple independent areas —
  so a request about one domain doesn't drag the others into context.
- **Scripts are for execution, not narration.** State explicitly whether the agent should
  run a script or read it as reference — those are different instructions. Prefer a script
  over asking the agent to regenerate the same logic each time: it's cheaper, more reliable,
  and consistent across runs. Handle errors inside the script instead of deferring to the
  agent, and justify any constant you hardcode (no unexplained magic numbers).

See `references/patterns.md` for worked examples of these shapes (high-level-guide-with-
references, domain-split, conditional-detail).

## Workflows and feedback loops

For a multi-step task, give a checklist the agent can copy into its own response and check
off — this measurably prevents skipped steps on fragile sequences. For anything
quality-critical, build a loop: run a check → fix what it flags → run the check again →
only proceed once it passes. Don't rely on a single-pass instruction for output that needs
to be right.

## Content hygiene

- **No time-bombed instructions.** "Before/after [date], do X" rots the moment that date
  passes and nobody notices. State the current approach as current; if the old approach
  still needs documenting, put it under a clearly labeled "old / deprecated" section instead
  of a date-conditional.
- **One consistent term per concept**, used everywhere in the skill. Switching between
  "endpoint" / "URL" / "route" for the same thing costs the agent parsing effort for no gain.
- **Concrete over abstract.** A real input/output example teaches faster than a paragraph
  describing the desired style.
- **One default, plus an escape hatch** — not a menu. "Use pdfplumber for text extraction;
  for scanned PDFs needing OCR, use pdf2image with pytesseract instead" beats listing five
  library options and letting the agent guess which one you meant.
- **Assume the agent is already competent.** Don't explain what a PDF is, what a linter
  does, or other domain background a capable model already has — every explained-obvious
  paragraph is tokens not spent on the part that's actually specific to this skill.

## Portability across harnesses

SKILL.md is now an open format that Claude Code, OpenCode, Codex CLI, Cursor, and others all
read, usually from the same directory unmodified. But a few things don't travel — see
`references/cross-harness-notes.md` before assuming a skill written here works unchanged
somewhere else (reserved words, directory search paths, MCP tool-naming syntax, and script
runtime assumptions all vary by harness).

## Pre-share checklist

- [ ] Description states what it does and when to fire it, with real trigger terms
- [ ] `name` is lowercase-hyphenated, no reserved words, not vague
- [ ] SKILL.md body stays well under 500 lines; deeper material moved to `references/`
- [ ] Every reference file linked directly from SKILL.md (no chained references)
- [ ] Reference files over ~100 lines have a table of contents
- [ ] No time-bombed instructions; terminology is consistent throughout
- [ ] Examples are concrete; one default is given rather than a menu of options
- [ ] Scripts, if any: handle their own errors, no unexplained constants, execute-vs-read
      intent is explicit
- [ ] Tried on 2-3 real prompts, including one that shouldn't trigger the skill
