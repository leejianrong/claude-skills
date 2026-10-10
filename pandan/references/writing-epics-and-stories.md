# Writing epics and stories

Read this before creating or editing a card or epic. Overview and setup live in the parent `SKILL.md`.

## Contents
- Stories
- Epics
- Before and after
- Filing in bulk

A card is read by someone with none of your context — often another agent, cold. Write it so they
can start without asking. The failure to avoid is the **wall of text**: one paragraph mixing why,
what, history, status and half-remembered constraints.

## Stories

One vertical slice a single agent can finish in one sitting and demo. Points 1–5; an 8
or 13 is a signal to split it, or to make it an epic. If you can't say how you'd check it's done,
it isn't a story yet.

- **Title**: outcome in the imperative, specific, ≤ ~70 chars — `Search cards by board-local ref`, not
  `Search improvements`. No status tags (`DONE`, `DEFERRED`, `(human)`), no ticket numbers, no
  milestone prefixes. Status lives in the column, assignee and `needs-human`, never in the title.
- **Description** (Markdown, ≤ ~150 words; longer means split it or link a doc). This shape, in this
  order, dropping a section only when it would be empty:

  ```markdown
  **Why** — one or two sentences: who needs this and what hurts today. Link the issue/ADR by URL.

  **Do** — what should be true after, not a step-by-step. Name a file or endpoint only when the
  choice isn't obvious.

  **Done when**
  - [ ] 2–5 observable, checkable outcomes (a command's output, a status code, a screen state)
  - [ ] Tests/docs updated where the change needs them

  **Not in scope** — what a reader might assume is included but isn't.
  ```
- **Dependencies are structure, not prose**: `pandan dep add ENG-14 --blocked-by ENG-9`. Reference other
  cards by board-local ref. Never write "blocked by X" or "see KAN-424" as the only record.
- **Progress, findings and history go in comments** (`pandan comment add`), not the description. The
  description states intent and stays true after the card ships; don't edit it into a changelog.
- **One card, one outcome.** "And also…" means a second card. Checklists of unrelated chores belong
  as separate cards; a checklist inside **Done when** is for verifying one outcome.
- Need a human decision or console work? `pandan needs-human ENG-14 --note "…"` or assign it — don't
  encode it in the title.

## Epics

An outcome with a boundary, usually 3–10 stories. Name it as the outcome
(`Board collaboration`, `Hosted MCP server`), not an activity (`Backend work`) or a date bucket.
Description, three short parts: **Goal** (the outcome, one sentence), **Done when** (how you'd know
the *epic* is finished, observable), **Not in scope**. File the epic first, then its stories with
`--epic ENG-E3` so every story traces to a goal. A grab-bag of unrelated cards is a label or a
backlog, not an epic.

## Before and after

Typical wall of text:

> `Search stuff` — Users can't find cards. Should probably support the ticket numbers like KAN-12 and
> the new board ones, see the thing from last week, also check the palette, might need backend
> changes, ask about partial matches, DONE for the UI part already.

Rewritten:

> `Search cards by board-local ref` (3 pts, epic `Legible at scale`)
> **Why** — typing `ENG-14` in the search box returns nothing, so people fall back to scrolling.
> **Do** — treat a query that is exactly a card ref (`ENG-14`, `KAN-12`, `alice/ENG-14`) as an exact
> match ranked above full-text hits.
> **Done when**
> - [ ] `pandan list --q ENG-14` returns that card first
> - [ ] The web search box does the same
> - [ ] A ref on a board you can't see returns nothing
> **Not in scope** — partial refs (`ENG-1` does not match `ENG-12`).

## Filing in bulk

 write the epic, then `pandan batch-create - < stories.json` with each
object's `title`, `description` (the template above), `story_points` and `epic_id`. Re-read one card
back with `pandan get` before filing forty.

