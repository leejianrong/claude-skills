# claude-skills

My global [Claude Code](https://claude.com/claude-code) skills. This repo *is*
`~/.claude/skills` — every directory here is a skill Claude Code loads
automatically.

## Setting up a new machine

Clone straight into the skills path:

```bash
git clone https://github.com/leejianrong/claude-skills.git ~/.claude/skills
```

If `~/.claude/skills` already exists and you want to keep it, move it aside
first (`mv ~/.claude/skills ~/.claude/skills.bak`). Nothing else is needed —
there is no install step, no symlinks, and no external skill manager. Start
Claude Code and the skills are there.

## Contributing (to myself)

`main` is protected: no direct pushes. Every change goes through a branch and a
pull request.

```bash
git switch -c add-some-skill
# edit or add a skill directory
git commit -am "Add some-skill"
git push -u origin add-some-skill
gh pr create --fill
gh pr merge --squash
```

## Layout

A skill is a directory containing `SKILL.md` with YAML frontmatter (`name`,
`description`) followed by the instructions. Supporting material lives in
`references/` or `assets/` alongside it and is read on demand.

```
pandan/
└── SKILL.md
dev-playbook/
├── SKILL.md
└── references/
    ├── ci-cd.md
    └── ...
```

## Skills

### Mine

**Engineering practice**

| Skill | What it does |
| --- | --- |
| `agent-brief` | Write, trim, or audit a CLAUDE.md/AGENTS.md file: the discoverability filter, size discipline, and when to add a rule. |
| `cleanup` | Audit and safely clean Docker, stale git branches and worktrees, and other dev clutter, plus the habits that stop it piling up. |
| `dev-playbook` | Project-agnostic engineering practices — layered testing, quality gates, branch/PR discipline, secrets hygiene, docs-as-code. |
| `go-playbook` | The Go specifics `dev-playbook` leaves as "translate to your stack": `-race`, the test cache, build tags, CGo versus a single binary, boundary enforcement, plus a copyable Makefile and CI. |
| `handling-secrets` | Keep API keys, tokens, and passwords out of transcripts, logs, git history, and files. |
| `lean-code` | Keep feature work small: read before adding, smallest diff, delete what the change supersedes, comments only for the non-obvious why, and a diff audit before the PR. Fires on any feature work. |

**Writing and docs**

| Skill | What it does |
| --- | --- |
| `natural-writing` | Write prose that doesn't read like an LLM wrote it. |
| `readme-playbook` | Write or audit a project README: audience-first structure, anti-patterns, what changes by project type. |
| `software-docs-writer` | Write or audit technical docs (tutorials, how-tos, reference, explanation) using Diátaxis and the page-level craft of the FastAPI, Typer and React docs, with a style pass and a checker script. |
| `write-tech-blog-post` | Draft a publishable technical blog post in my voice and get it to Notion. |

**Planning and product**

| Skill | What it does |
| --- | --- |
| `pandan` | Read and write the Pandan kanban board via the `pandan` CLI. |
| `plan-new-project` | Turn a rough idea into a PRD-grade plan, ADRs and implementation slices in one interview. |
| `software-product-director` | Critique a repo's commercial and product viability from its actual codebase. |

**Infrastructure and ops**

| Skill | What it does |
| --- | --- |
| `airgap-image-transfer` | Move OCI/Docker images to an airgapped machine with skopeo/regctl, avoiding `docker save`'s dropped layers. |
| `runpod-jobs` | Rent a RunPod pod, run a job, get the artifact out, and guarantee teardown so it stops billing. |
| `traefik-dev-proxy` | Set up one machine-wide Traefik reverse proxy that auto-discovers Docker Compose dev stacks via labels, giving every project a stable `<project>.localhost` hostname. |

**Design and media**

| Skill | What it does |
| --- | --- |
| `explainer-artifacts` | Build diagram-led explainer artifacts for teaching a concept or supporting a decision. |
| `material-design-3` | Apply Google's Material Design 3 system when building or restyling a frontend. |
| `video-demo` | Record a 10-30s MP4 showcase video of a CLI or web app for a GitHub README — agent-scripted capture (VHS/Playwright), bundled music + cued SFX, no voiceover. |

**Meta**

| Skill | What it does |
| --- | --- |
| `write-skill` | Author or audit a SKILL.md for Claude Code or other agent harnesses. |

`lean-code`, and parts of `dev-playbook`, `natural-writing`, `software-docs-writer` and `cleanup`,
are adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan
(MIT licence), rewritten for this library.

Skills stay flat at the top level because the harness only discovers top-level
directories. The grouping above is for reading, not for the filesystem.

### Vendored from upstream

These were installed from public repos and are copied in here verbatim so a
clone is self-contained. Credit to their authors; check each source repo for
its licence before reusing.

| Skill | Source | Path upstream |
| --- | --- | --- |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) | `skills/find-skills/` |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | `skills/frontend-design/` (LICENSE.txt included) |

To pull an upstream fix, copy the updated directory in and open a PR — there is
no lock file or updater in play anymore.
