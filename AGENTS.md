# claude-skills

## WHAT

This repo *is* `~/.claude/skills` — every top-level directory is a skill Claude
Code (or another agent harness) loads automatically. A skill is a directory
with `SKILL.md` (YAML frontmatter: `name`, `description`, then instructions),
plus optional `references/`, `scripts/`, `assets/`. See `README.md` for the
full skill list and layout, and the `write-skill` skill before authoring or
editing one.

## WHY

Personal skill library for leejianrong, shared across machines by cloning
this repo into `~/.claude/skills`. `main` is protected: it must stay in sync
with a working checkout on every machine, so nothing here is meant to sit
uncommitted or unpushed for long.

## HOW

**Every change goes through a branch and a PR — never push to `main`
directly:**

```bash
git switch -c add-some-skill
# edit or add a skill directory
git commit -am "Add some-skill"
git push -u origin add-some-skill
gh pr create --fill
gh pr merge --squash
```

**Finish every work session in sync with the remote.** Before ending a task
(or handing off), run `git status`: if there are uncommitted or untracked
files, or a local branch with commits not on `origin`, commit and push them
and open the PR — don't leave finished work sitting only on disk. A skill
that exists as files but never reached a PR does not exist for any other
machine or session.

- Check `git status -sb` and `gh pr list` when starting work in this repo, so
  you know whether prior work is still pending a PR before adding more.
- One PR per skill (or per focused change) — mirrors the existing PR history
  (`gh pr list --state all`).
- New skill authoring conventions (frontmatter rules, degrees of freedom,
  progressive disclosure, the pre-share checklist) live in `write-skill/` —
  read it before drafting a new `SKILL.md`, not just before sharing one.
- Trust the code over this file where they disagree, and fix this file.
