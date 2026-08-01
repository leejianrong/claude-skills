---
name: write-tech-blog-post
description: >-
  Write a technical blog post / article that Jian intends to publish, and handle the
  logistics around it. Use when the user says things like "write a technical blog post
  about X", "turn this into a blog post / article", "write this up as a post I can
  publish", or "publish that article to Notion". Covers the whole pipeline: drafting in
  Jian's voice, where the file lives, the metadata block it needs, and how it reaches
  Notion. Not for internal design docs, ADRs, or READMEs — those are plain docs, not
  published articles.
---

# Writing a technical blog post

This is the playbook for producing an article Jian wants to **publish** (as opposed to
an internal doc). It ties three things together: writing in his voice, storing the file
consistently, and getting it into Notion. Follow it whenever the user asks for a blog
post or article, or asks to publish one that already exists.

## 1. Write it in Jian's voice

Always draft with the **`/natural-writing`** skill loaded — do not write the prose cold.
That skill carries the general anti-AI-tell rules *and* the reverse-engineered profile of
how Jian actually writes (even and flowing rather than choppy, no narrator scaffolding,
understated, "we" not "you" for advice, British spelling, parentheses for asides). A post
that skips it will read wrong and Jian will rewrite it.

A few things that matter specifically for the technical posts:

- Keep code blocks and real file paths. The voice rules are about the prose *around* the
  code, not the code itself — leave identifiers like `/auth/github/authorize` or
  `CookieTransport` exactly as they are in the source.
- Have a point of view. These posts make recommendations ("stay on one origin if you
  can"), own the trade-offs, and say plainly when something is a bad idea. Neutral
  survey-style writing is a failure mode here.
- Ground every claim in this repo's real behaviour. Read the actual source before
  describing it; don't reconstruct it from CLAUDE.md or memory, which can drift from the
  code.

When the post is done, append its baseline→final diff and any new voice patterns to the
natural-writing skill's case study at
`~/.claude/skills/natural-writing/references/case-study-hello-im-jian.md`, and update the
profile in that skill if the evidence disagrees with it. The profile is only as good as
the examples behind it.

## 2. Where the file goes

Published articles live under **`docs/blog/`**, one Markdown file per post, named with a
kebab-case slug that matches the post's `slug` metadata (e.g.
`docs/blog/one-origin-one-cookie.md`). This keeps them separate from the internal design
chain in `docs/` (PRD, SHAPING, BREADBOARD, `adr/`, etc.), which are specs, not articles.

Internal notes and Q&A references (like `docs/auth-notes-for-realtime-platform.md`) are
**not** blog posts and stay in `docs/`, not `docs/blog/`.

## 3. The metadata block

Every article opens with a metadata block: an HTML comment holding the front-matter,
then a `---` separator, then the body starting with the `# H1` title. Keeping metadata in
a comment means the file still renders cleanly on GitHub while carrying the fields the
Notion publish step needs.

```markdown
<!--
title: "One origin, one cookie: how GitHub login works here"
description: One or two sentences. Becomes the Notion excerpt / summary property.
slug: one-origin-one-cookie
author: Jian
date: 2026-07-11
status: Draft
tags: [auth, oauth, fastapi, svelte, cookies, cors, fly-io]
-->

---

# One origin, one cookie: how GitHub login works here

Body starts here…
```

Field notes:

- **title** — the human title; maps to the Notion page's title property. Keep it in sync
  with the H1.
- **description** — a short summary for the Notion excerpt and for link previews.
- **slug** — kebab-case; must match the filename.
- **date** — resolve relative dates to an absolute `YYYY-MM-DD` (the environment gives you
  today's date; don't write "today").
- **status** — `Draft` until Jian says it's ready; flip to `Published` when it goes live.
- **tags** — lowercase, kebab-case, and reused across posts where they overlap.

These are the fields we expect the Notion blog database to want. Treat them as the
intent, not gospel — the real property names come from the database schema at publish
time (next section).

## 4. Publishing to Notion

Jian publishes through the **hosted Notion MCP**, using the
`mcp__notion__notion-create-pages` tool — not the REST API, not a manual paste.

**Preconditions (check these first — they bite every time):**

- The Notion MCP must be **connected and OAuth-authorized**. It's registered in the user
  config (`~/.claude.json`) as `notion` → `https://mcp.notion.com/mcp`. If the
  `mcp__notion__*` tools aren't in the tool registry, the session predates the connection:
  the user needs to run `/mcp`, authorize **notion**, and **restart Claude Code** so the
  tools load. You cannot do these two steps for them — say so plainly and stop until it's
  done.
- Confirm which database is the blog target. If you don't have its id, use the Notion
  search/fetch tools to find it (or ask the user for the database URL/id). Don't guess.

**The publish steps:**

1. Read the article file and split it into the metadata (inside the HTML comment) and the
   body (everything below the `---`).
2. Fetch the target database's schema so you map to the **real** property names, not the
   assumed ones from §3. Title → the title property; description, date, status, tags → their
   matching properties (create/skip any the database doesn't have).
3. Call `mcp__notion__notion-create-pages` with the database as the parent, the mapped
   properties, and the body as the page content. Strip the leading `# H1` from the body
   before sending — the Notion title property already carries it, so leaving it in
   duplicates the heading on the page.
4. Report the created page's URL back to the user, and flip the file's `status` to reflect
   it if Jian confirms it's live.

If the MCP genuinely can't be used (not authorized, and the user doesn't want to restart),
the fallback is the Notion REST API via `curl` with an integration token — but only offer
this if asked; the MCP path is the default.

## Quick checklist

- [ ] Drafted with `/natural-writing` (Jian's voice), grounded in real source.
- [ ] Saved as `docs/blog/<slug>.md`, filename matches the `slug`.
- [ ] Metadata block present, dates absolute, tags kebab-case.
- [ ] Case-study reference updated with this article's diff.
- [ ] Notion MCP connected + authorized before attempting to publish.
- [ ] Properties mapped against the live database schema; leading H1 stripped from the body.
