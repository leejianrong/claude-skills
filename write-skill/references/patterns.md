# Structure patterns

Worked shapes for splitting a skill across SKILL.md and its supporting files. Pick the one
that matches how the skill's content actually divides — don't force a pattern that doesn't
fit.

## Contents
- High-level guide with references
- Domain-split reference
- Conditional detail
- Description quality, side by side

## High-level guide with references

Use when the skill has one core workflow plus several deeper sub-topics that only some
tasks need.

```
pdf-processing/
├── SKILL.md       # quick start + pointers
├── FORMS.md        # form-filling, read only when filling a form
├── REFERENCE.md     # full API, read only when the quick start isn't enough
└── EXAMPLES.md       # common patterns, read only when asked for an example
```

SKILL.md itself just names the destination:

```markdown
## Advanced features
**Form filling**: see FORMS.md
**API reference**: see REFERENCE.md
**Examples**: see EXAMPLES.md
```

## Domain-split reference

Use when a skill spans multiple independent domains and a given task only ever touches one.
Splitting by domain means a request about domain A never pulls domain B's schema into
context.

```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md    # revenue, billing
    ├── sales.md       # pipeline, accounts
    ├── product.md      # usage, features
    └── marketing.md     # campaigns, attribution
```

SKILL.md maps the domains and, where the reference files are long, gives a grep entry point:

```markdown
**Finance**: revenue, ARR, billing → reference/finance.md
**Sales**: opportunities, pipeline → reference/sales.md

grep -i "revenue" reference/finance.md
```

## Conditional detail

Use when most requests need only the basic path, and a minority need one of several
specific deep dives. Show the basic content inline; link out only for the branches.

```markdown
## Editing documents
For simple edits, modify the XML directly.
**For tracked changes**: see REDLINING.md
**For OOXML internals**: see OOXML.md
```

The agent reads REDLINING.md or OOXML.md only if the task actually needs tracked changes or
OOXML detail — most edits never touch either file.

## Description quality, side by side

The description is the only thing loaded before the skill fires — it has to carry the whole
triggering decision on its own.

| | Description | Why |
|---|---|---|
| Bad | `Helps with documents` | No trigger terms, no scope — could mean anything. |
| Bad | `Processes data` | Same problem — "data" and "processes" match almost every task. |
| Good | `Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.` | Names the concrete capability and the concrete trigger words a real request would contain. |
| Good | `Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.` | Same shape: capability, then trigger phrasing. |

Write in third person even though it reads a little stiff — the description gets injected
into the system prompt alongside every other skill's, and switching person there is what
causes triggering to misfire, not a style preference.
