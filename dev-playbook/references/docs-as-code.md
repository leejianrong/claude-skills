# Docs as code

Documentation that lives beside the code, ships with it, and breaks the build when it's wrong
stays true. Documentation in a separate wiki rots. Treat docs like code: in the repo, in
review, gated in CI, published on merge.

## Two kinds of docs, both in the repo

- **Decision records (ADRs)** — short, numbered, immutable-ish notes capturing *why* a choice
  was made, the alternatives, and the trade-off. Written when the decision is made. They're
  the memory an agent or a new hire reads to understand why the system is shaped as it is.
- **User-facing docs** — the guide someone reads to install, use, and build on the project.
  This is what you publish as a site.

Keep a `docs/` tree with an index, the user docs, and the ADRs. Cross-link them.

## Publish a site, gated on a build check

Author docs as markdown and render them to a static site. Two workflow rules make it reliable:

- **Publish on merge to `main`.** A push to `main` builds the site and deploys it (e.g. to
  GitHub Pages). The docs are never manually copied anywhere.
- **Build-check on PRs.** Add a build-only job that runs on pull requests, so a broken docs
  build (a bad link, invalid front matter, a diagram that won't parse) fails *before* merge.
  Gate the deploy step to non-PR events so PRs build but don't deploy. Without the PR check, a
  docs break only surfaces after it's already on `main`.
- **Ignore the build output.** The generated site directory is an artifact — gitignore it; CI
  rebuilds it fresh on deploy. Never commit it.

## Building a high-quality site with Zensical

[Zensical](https://zensical.org) is the successor to Material for MkDocs: a `zensical.toml`, a
`docs/` source tree, `zensical build` to a `site/` directory. It gives you the Material theme,
search, light/dark, code-copy, admonitions, and content tabs out of the box.

Minimal setup:

```toml
# zensical.toml
site_name = "Your Project"
site_url  = "https://<org>.github.io/<repo>/"
docs_dir  = "docs"
site_dir  = "site"      # generated — gitignore it
nav = [
  { "Home" = "index.md" },
  { "Guide" = "guide.md" },
]
[theme]
name = "material"
features = ["navigation.tabs", "navigation.sections", "content.code.copy", "search.suggest"]
```

Deploy on push to `main` and build-only on PRs (GitHub Actions): install `zensical`, run
`zensical build --clean`, upload the `site/` artifact to Pages, and gate the deploy job with
`if: github.event_name != 'pull_request'`.

Preview locally with `zensical build` (or `zensical serve`) from the repo root. Verify the
build exits clean and that new pages and diagrams actually render before you push — the PR
check will confirm it, but a local build is faster feedback.

## Writing docs users actually finish

Structure and prose both matter. For structure:

- **Lead with the runnable thing.** The first code block should be a complete, working example
  the reader can copy and run, before any conceptual preamble. Show the win, then explain it.
- **Build a tutorial ladder** for anything with a learning curve: each rung is runnable and
  changes exactly one idea from the rung below. For a bot SDK, that's random → material-count
  → search → bring-your-own-engine; for an API, unauthenticated read → authenticated write →
  webhooks. The reader climbs one concept at a time and always has something that works.
- **Use diagrams where a sequence or a flow is hard to hold in prose.** Zensical/Material
  renders fenced ` ```mermaid ` blocks (via superfences). A sequence diagram of the
  request/response lifecycle or a flowchart of the ladder earns its space; a decorative
  diagram doesn't. Keep labels legible, mark which step is *the reader's code*, and verify
  they render in the local build.
- **Reach for admonitions and content tabs deliberately** — `!!! note` / `!!! tip` /
  `!!! warning` for asides, tabbed code blocks for per-language or per-OS variants. Aids, not
  decoration.
- **An API reference with tables** — parameters, return values, error codes — as a table, not
  a wall of prose.

For prose, write like a knowledgeable human, not marketing copy or a machine (invoke the
`natural-writing` skill if it's available). In short: vary sentence rhythm; cut hedging
("perhaps", "it's worth noting"); avoid the "not just X, but Y" reflex and stock transitions
("Moreover", "Furthermore"); use em-dashes sparingly; write headings in sentence case; be
concrete; use "you" and the active voice. For the look of the site and its diagrams, the
`frontend-design` skill covers intentional, non-templated visual choices.

## Keep docs honest

Doc drift is a regression. When a change alters a command, an env var, or a behavior, update
the docs in the same PR. Pin the source of truth in code (or generate reference docs from it)
so prose can't silently disagree with reality — and where prose must be hand-maintained,
review it against the code, don't trust it.
