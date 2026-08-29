# Cross-harness portability notes

The SKILL.md format (a directory with `SKILL.md` frontmatter + body, optionally
`references/`, `scripts/`, `assets/`) is now read natively by Claude Code, OpenCode, Codex
CLI, Cursor, Gemini CLI, and Copilot. Most skills work unmodified across all of them. These
are the places that don't.

## Contents
- Directory search paths
- Frontmatter validation differences
- MCP tool-naming syntax
- Script runtime assumptions
- What to do about it

## Directory search paths

Each harness looks in its own default location, and some also read others':

- Claude Code: `.claude/skills/` (project) or `~/.claude/skills/` (global, user-level — this
  repo).
- OpenCode: `.opencode/skills/` and `~/.config/opencode/skills/` — and it also reads
  `.claude/skills/`, so a Claude Code skill is picked up automatically in a shared repo.
- Codex CLI: its own skills directory, resolved similarly (check current Codex docs — this
  is a fast-moving area).

If a skill needs to be discoverable in a specific harness and you're not sure it reads
`.claude/skills/`, don't assume — check that harness's current docs, or place a copy (not a
rewrite) at its expected path.

## Frontmatter validation differences

Claude Code specifically rejects `name` values containing `claude` or `anthropic` as
reserved words. This is a Claude Code rule, not a cross-harness one — but avoiding those
words costs nothing and keeps the name portable everywhere, so treat it as a default rather
than a Claude-only exception.

Length limits (`name` ≤64 chars, `description` ≤1024 chars) come from Claude Code's
validation; other harnesses may be looser, but there's no reason to rely on that slack.

## MCP tool-naming syntax

Claude Code requires fully-qualified MCP tool references in the form `ServerName:tool_name`
(e.g. `GitHub:create_issue`) to avoid "tool not found" errors when multiple MCP servers are
connected. This qualified-name syntax is Claude Code-specific.

If a skill needs to name an MCP tool and also travel to other harnesses, don't hardcode the
qualified form as the only phrasing — describe the tool's purpose in prose ("use the GitHub
MCP tool for creating issues") so the instruction still resolves correctly wherever the
qualification syntax differs or is absent.

## Script runtime assumptions

`scripts/` execution environments are not equivalent across contexts:

- Claude on claude.ai can install packages from npm/PyPI and pull from GitHub at runtime.
- The Claude API's code execution tool has **no network access** — nothing installable at
  runtime; every dependency must already be present.
- Claude Code runs scripts through its own bash tool under whatever permissions the user has
  granted; other harnesses sandbox shell execution differently or may not offer code
  execution at all.

Don't assume any particular install capability. State required packages explicitly in the
skill body, and prefer scripts with minimal or standard-library-only dependencies if the
skill is meant to run in more than one of these environments.

## What to do about it

Default to writing the harness-agnostic version — most content should have nothing harness-
specific in it at all. When something genuinely differs (a tool-naming syntax, a directory
path, a runtime capability), name the harness it applies to explicitly rather than writing
the instruction as if it's universal. Don't fork the whole skill per harness for a
difference that only affects one line.
