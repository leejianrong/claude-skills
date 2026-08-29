# Agent-brief audit checklist

Work through an existing CLAUDE.md/AGENTS.md against this list. Fix accuracy issues first —
a wrong command or a stale convention is actively harmful, not just wasted space.

## Contents
- Accuracy
- Discoverability filter
- Size and structure
- Placement

## Accuracy

- [ ] Every command in the file actually runs, as written, today
- [ ] Every file/path referenced still exists
- [ ] Workflow conventions described (branching, PR process, review requirements) match what
      the repo actually enforces, not an aspirational or outdated process
- [ ] No convention described that architecture changes have since made false

## Discoverability filter

Go line by line and ask "would an agent reading this repo already know this?"

- [ ] No codebase overview or file-by-file walkthrough that duplicates exploring the tree
- [ ] No generic framework/language explanation the model already knows
- [ ] No dependency list duplicating `package.json`/`go.mod`/`requirements.txt`
- [ ] No content copy-pasted from the README
- [ ] Everything remaining is genuinely non-obvious: a tool substitution, a hidden
      constraint, a security boundary, a review standard, a real gotcha

## Size and structure

- [ ] Under ~150 lines, or a clear reason it needs more
- [ ] If over ~300 lines, content has been moved to `agent_docs/*.md` with pointers from the
      root file, not left inline
- [ ] The highest-priority items (the ones that cause the worst failures if missed) appear
      near the top, not buried at the end
- [ ] Code is referenced by `file:line` pointer, not pasted as a snippet that can drift
- [ ] No rule that traces back to a single one-off incident rather than a repeated pattern

## Placement

- [ ] Exactly one canonical file exists (`AGENTS.md` preferred); any tool-specific filename
      (`CLAUDE.md`, `.cursorrules`) imports it rather than duplicating its content
- [ ] The file sits at the repo root, where every harness actually loads it from
