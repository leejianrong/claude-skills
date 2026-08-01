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

| Skill | What it does |
| --- | --- |
| `airgap-image-transfer` | Move OCI/Docker images to an airgapped machine with skopeo/regctl, avoiding `docker save`'s dropped layers. |
| `dev-playbook` | Project-agnostic engineering practices — layered testing, quality gates, branch/PR discipline, secrets hygiene, docs-as-code. |
| `explainer-artifacts` | Build diagram-led explainer artifacts for teaching a concept or supporting a decision. |
| `natural-writing` | Write prose that doesn't read like an LLM wrote it. |
| `pandan` | Read and write the Pandan kanban board via the `pandan` CLI. |
| `pandan-pm` | Act as scrum-master over the Pandan board, delegating cards to sub-agents. |
| `plan-new-project` | Turn a rough idea into a PRD-grade plan, ADRs and implementation slices in one interview. |
| `write-tech-blog-post` | Draft a publishable technical blog post in my voice and get it to Notion. |

### Vendored from upstream

These were installed from public repos and are copied in here verbatim so a
clone is self-contained. Credit to their authors; check each source repo for
its licence before reusing.

| Skill | Source | Path upstream |
| --- | --- | --- |
| `build-plan-product` | [bguiz/build-agent-skills](https://github.com/bguiz/build-agent-skills) | `skills/build-1-plan-product/` |
| `build-plan-specs` | [bguiz/build-agent-skills](https://github.com/bguiz/build-agent-skills) | `skills/build-2-plan-specs/` |
| `find-skills` | [vercel-labs/skills](https://github.com/vercel-labs/skills) | `skills/find-skills/` |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | `skills/frontend-design/` (LICENSE.txt included) |
| `grill-with-docs` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/grill-with-docs/` |
| `shaping` | [rjs/shaping-skills](https://github.com/rjs/shaping-skills) | `shaping/` |
| `to-prd` | [mattpocock/skills](https://github.com/mattpocock/skills) | `skills/engineering/to-prd/` |

To pull an upstream fix, copy the updated directory in and open a PR — there is
no lock file or updater in play anymore.
