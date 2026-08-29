---
name: readme-playbook
description: Write or audit a project's README.md — audience-first structure (value prop, visual demo, quick start, usage, license), anti-patterns to avoid (badge walls, untested install steps, staleness), and what changes for a library vs CLI vs service vs internal-only repo. Use when creating a new README, reviewing or improving an existing one, or deciding what belongs in the README versus CONTRIBUTING.md.
---

# README playbook

A README has one job: let a stranger decide, in under a minute, whether this project is
worth their time, and if so, get it running. Everything else is secondary.

## Write for the reader who isn't staying

The largest audience for a README is people deciding whether to use the project, not people
about to contribute to it. Optimize for that reader:

- Lead with what it does and why it matters — two lines, no throat-clearing preamble like
  "This project is a..."
- Put contributor setup (dev environment, test suite, release process) in `CONTRIBUTING.md`
  and link to it. A contributor will look for it; a user shouldn't have to scroll past it.
- One clear usage example beats a link to full API docs. Show the two or three things
  someone would actually do with this, concretely — not an exhaustive method list.

## Core sections, in order

1. **Title + value prop** — what it is and why it matters, in about two lines.
2. **Visual** — a screenshot, terminal recording, or GIF of it running. If there's no UI, a
   simple diagram (Mermaid renders natively on GitHub) showing the shape of the thing beats
   a paragraph describing it. A picture earns understanding in seconds; prose takes longer
   and gets skipped.
3. **Quick start** — the actual install/run commands, copy-pasteable, in the order someone
   would run them. Test them yourself in a clean checkout before writing them down; a step
   that doesn't work is worse than no README at all, because it costs the reader time and
   trust.
4. **Usage** — two or three concrete examples of real use, not a dump of every option. Link
   to fuller docs for the rest.
5. **Configuration** — only if the project has meaningful config; list the options that
   matter, not every flag.
6. **Contributing** — one or two lines plus a link to `CONTRIBUTING.md`.
7. **License** — stated explicitly, not implied. A missing or ambiguous license blocks
   adoption at any company with a legal review step, regardless of how good the project is.

Badges, if used at all, go near the top and should be load-bearing (build status, published
version, license) — not a wall of decoration. A single well-chosen screenshot sells the
project harder than ten badges.

## Anti-patterns

- **A badge wall** — a dozen badges that carry no information the reader will act on.
- **Untested install steps.** If you haven't run them in a clean environment recently,
  they're a guess, not a quick start.
- **An API dump instead of usage.** Listing every function is what reference docs are for;
  the README needs the two things people actually do first.
- **Marketing language without proof.** "Blazing fast" means nothing without a number, a
  benchmark, or something the reader can see for themselves.
- **Staleness.** An inaccurate README is worse than a sparse one — it actively costs the
  reader time and erodes trust in everything else the project says. This is the failure mode
  that undoes every other practice on this list, because a reader can't tell which parts
  have gone stale without trying them.

## Keep it honest as the project changes

Update the README in the same PR that changes the setup, usage, or public interface it
describes — not as a follow-up. A README fix that lands separately from the change it
documents usually never lands at all.

For an existing README, see `references/audit-checklist.md` for a prioritized yes/no pass.
For how this structure shifts by project type (library, CLI, service, internal-only repo),
see `references/by-project-type.md`.
