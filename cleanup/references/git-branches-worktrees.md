# Git branch and worktree cleanup

## Contents
- Ground rules
- Local branches
- Remote branches
- Worktrees
- Prevention

## Ground rules

- **Never touch protected branches:** `main`, `master`, `develop`, `release/*`, `gh-pages`, and
  whatever the repo's default branch is (`git symbolic-ref refs/remotes/origin/HEAD`). Also skip
  the currently checked-out branch.
- **Unmerged work is not clutter.** A branch with commits that exist nowhere else is someone's
  work. Report it; don't delete it.
- **Remote deletion affects other people** and can't be undone from your side. Always confirm the
  exact branch list, and only delete branches the user (or the branch's author) owns.
- Delete with the safe flag first: `git branch -d` refuses unmerged branches. Use `-D` only after
  confirming the work landed some other way (see squash merges below).
- Write the proposed deletions to a file and show them before running anything destructive.

## Local branches

```bash
git fetch --prune                                    # drop stale remote-tracking refs first
git branch --show-current
git branch --merged origin/main                      # fully merged into main: safe for -d
git branch -vv | grep ': gone]'                      # upstream deleted (usually = merged and auto-deleted)
git for-each-ref --sort=committerdate refs/heads \
  --format='%(committerdate:short) %(refname:short) %(upstream:track)'   # oldest first
```

**Squash and rebase merges fool `--merged`.** The branch's commits never land in main, so the
branch looks unmerged even though its PR closed. Handle with:

```bash
gh pr list --state merged --head <branch> --json number,mergedAt   # confirm the PR merged
git cherry -v origin/main <branch>                                 # lines starting with '-' are already applied
```

If the PR merged, `git branch -D <branch>` is fine. If there's no PR and `git cherry` shows `+`
commits, the branch has unique work — keep it and report it.

Check for unpushed work before deleting: `git log origin/<branch>..<branch>` (empty = nothing
unpushed; error = the remote branch is gone, so also check merged status above).

Delete in bulk from a reviewed file:

```bash
xargs -r git branch -d < branches-to-delete.txt
```

## Remote branches

```bash
git fetch --prune
git for-each-ref --sort=committerdate refs/remotes/origin \
  --format='%(committerdate:short) %(authorname) %(refname:short)'
git branch -r --merged origin/main                   # merged remote branches
gh pr list --state open --json headRefName,author    # branches with a live PR: keep
```

A remote branch is a candidate for deletion when it is **merged or its PR is closed, AND has had
no commits for a long time (default: 30+ days), AND has no open PR**. Never delete a branch
that's the head of an open PR.

```bash
git push origin --delete <branch>        # one reviewed branch at a time, or from a confirmed list
```

Better than hand-cleaning: turn on "Automatically delete head branches" in the GitHub repo
settings (`gh repo edit --delete-branch-on-merge`) so merged PR branches disappear on their own.

## Worktrees

Worktrees are directories checked out from the same repo. Agent and review workflows create many,
and they linger after the work is done.

```bash
git worktree list --porcelain          # every worktree, its branch, and whether it's prunable
git worktree prune --dry-run           # registrations whose directory no longer exists
```

For each worktree besides the main one, check before removing:

```bash
git -C <path> status --short           # uncommitted changes? (non-empty = keep and report)
git -C <path> log @{u}..HEAD --oneline # unpushed commits? (non-empty = keep and report)
git -C <path> branch --show-current    # and is that branch merged? (see local branches)
```

Remove only when the tree is clean, nothing is unpushed, and its branch is merged or abandoned
with the user's OK:

```bash
git worktree remove <path>             # refuses a dirty tree; don't add --force without asking
git worktree prune                     # clear registrations pointing at deleted dirs
git branch -d <branch>                 # then delete the branch it was on, if merged
```

Also look for worktree-adjacent leftovers: `.claude/worktrees/` directories, and Docker
stacks/volumes created per worktree (project names derived from the directory — see
[docker.md](docker.md)). Removing the worktree does **not** remove its containers or volumes.

A directory deleted by hand leaves a stale registration; `git worktree prune` fixes that.
A locked worktree (`git worktree list` shows `locked`) needs `git worktree unlock` first — ask
before doing so, since it was locked on purpose.

## Prevention

- **One branch = one PR = short life.** Merge or close within days; delete on merge.
- **Enable auto-delete of head branches** on the remote.
- **Create a worktree and remove it in the same task.** If an agent makes one, the agent's
  end-of-task checklist removes it.
- **Name branches with an owner/ticket prefix** (`jian/PAN-123-thing`) so stale ones can be
  traced to someone.
- **Monthly sweep:** `git fetch --prune`, review `gone` branches and the oldest remote branches,
  `git worktree prune`.
- Run `git config --global fetch.prune true` so every fetch drops stale remote-tracking refs.
