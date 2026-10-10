---
name: pandan
description: >-
  Read and write the Pandan board from an agent or the command line using the `pandan` CLI —
  the primary interface — with the `mcp__pandan__*` MCP tools as the fallback. Use whenever the task
  is to look at, create, update, move, or organise cards/epics/boards on Pandan (the board at
  simple-kanban-jian.fly.dev or a self-hosted instance): "add a card", "what's on the board", "move
  ENG-12 to done", "list my epics", "find card ENG-14", "which board am I on", "write up these
  stories", "break this into an epic", "track this work on kanban". For orchestrating a whole backlog as
  a scrum-master, see the pandan-pm skill; this skill is the tool reference it builds on.
---

# Driving Pandan with the `pandan` CLI

Pandan is API-first: every board action is a plain `/api/v1` REST call, and there are two thin
clients over it. The **`pandan` CLI is the primary way to drive the board** — it's a single binary, easy
to shell out to, scriptable, and works in CI. The **MCP server (`mcp__pandan__*` tools) is the
fallback**, for when the CLI isn't installed or errors. Cards, boards, epics, labels, saved views,
card templates, dependencies, work-links, comments, dispatch/claim, needs-human handoff, metrics and
the activity feed are all reachable from either.

> CLI/MCP parity is asserted mechanically in both directions by `pandan-cli/tests/test_parity.py` in
> the pandan repo. The only CLI verbs with no MCP twin are local ones (`login`, `config`, `context`,
> bare `overview`, `board use`/`current`).

Prefer `pandan`. Drop to MCP only when you have to, and say why when you do.

## Setup

`pandan` needs two config values (the server and your token), and resolves each one independently
from the first source that supplies it, in this precedence order:

1. **Environment** — `PANDAN_API_URL` / `PANDAN_TOKEN`.
2. **User config file** — `~/.config/pandan/config.toml` (`$XDG_CONFIG_HOME`-aware), written once by
   `pandan login` / `pandan config set` at mode `0600`. **This is how you authenticate one time and never
   pass the token again** (see below). A pre-rebrand `~/.config/kan/config.toml` is migrated across on
   first use and left in place (V40, KAN-423; `pandan_cli/config.py:100-107`).
3. **`.mcp.json`** — the nearest one walking up from the CWD, read from `.mcpServers.pandan.env.*`.

The two values:

- `PANDAN_API_URL` — the board origin, e.g. `https://simple-kanban-jian.fly.dev` (or a self-host URL).
- `PANDAN_TOKEN` — a PAT (`pandan_pat_…`). Minted at the board's **Tokens** tab after logging in.
  It acts as you and reaches boards you own **or are a member of**. `warmup` is the one command that
  needs no token.

### Pick a board — there is no default board

A board-scoped verb (`list`, `create`, `next`, `metrics`, `epic list`, `label list`, …) with **no
`--board` and no pin fails** with `error	board_required	…`, listing your boards (`id KEY 'name'`). That
is deliberate: a default is how an agent files a card on the wrong board. Say which board you mean,
once per session:

```bash
pandan board list            # id, key, name of every board you can reach
pandan board use ENG         # pin it: an id or a board KEY (case-insensitive)
pandan list                  # …every board-scoped verb now uses it
pandan list --board 7        # --board always overrides the pin
pandan board current         # which board is pinned here?     pandan board use --clear
```

The pin is a small state file **per working directory** (subdirectories inherit it), for the server it
was made against, and **lapses after 12 hours idle** — a fresh session re-picks instead of inheriting a
stale board. `PANDAN_BOARD_ID` and the config-file `board_id` are retired: a leftover one is ignored
with a stderr notice (`pandan config unset board_id` removes it). Verbs addressed by ticket (`get`,
`move`, `update`, …) need no board.

Because of the precedence chain, **in a Claude Code project you usually don't have to set anything**:
`pandan` finds the PAT in the repo's `.mcp.json` on its own (source 3). For a standalone machine or CI,
authenticate once with `pandan login` (source 2) — after that every `pandan` call just works.

### The token is a secret — never let it enter your context

**Treat the PAT as a credential you handle blind.** Do **not** `cat`/`grep`/`echo` the token, print
it, or paste the literal `pandan_pat_…` value into any command you write — anything you emit lands in
the model context (and the transcript). The value must only ever move *machine-to-machine*.

In a Claude Code project the token already lives in **`.mcp.json`** at the repo root, under
`.mcpServers.pandan.env.PANDAN_TOKEN` (alongside `PANDAN_API_URL`). Load it into
the shell **by reference** with command substitution, so the value is resolved by the shell at runtime
and never appears in what you write or in the output. The Bash tool starts a fresh shell each call and
does **not** persist env vars, so prefix every `pandan` call with the load:

```bash
# Both, straight from .mcp.json — the literal token never surfaces:
export PANDAN_TOKEN=$(jq -r '.mcpServers.pandan.env.PANDAN_TOKEN' .mcp.json)
export PANDAN_API_URL=$(jq -r '.mcpServers.pandan.env.PANDAN_API_URL' .mcp.json)
pandan board list
```

Collapse it into a reusable one-liner you paste at the front of each command (find `.mcp.json` by
walking up from the CWD if it isn't in the working directory):

```bash
eval "$(jq -r '.mcpServers.pandan.env | to_entries[] | "export \(.key)=\(.value|@sh)"' .mcp.json)" && pandan board list
```

If there is no `.mcp.json` (non–Claude Code shell, CI, self-host), expect the two vars to already be
in the environment — still don't echo `PANDAN_TOKEN`. If the token genuinely isn't reachable any way,
stop and ask the user rather than requesting they paste it into the chat. (The **MCP fallback** never
has this problem: the MCP server process inherits the token from `.mcp.json` directly, so
`mcp__pandan__*` tool calls never expose it — see below.)

Install the CLI (either works; the binary needs no Python):

```bash
# Prebuilt binary from the latest release (Linux glibc >= 2.28 / macOS arm64):
curl -L -o pandan https://github.com/leejianrong/pandan/releases/latest/download/pandan-linux-x86_64
chmod +x pandan && mv pandan ~/.local/bin/        # ~/.local/bin is on PATH, no sudo

# or, if you have Python + uv:
uv tool install "git+https://github.com/leejianrong/pandan.git#subdirectory=pandan-cli"
```

`pandan` is the only command name; make a symlink if you want a short one.

Confirm it works: `pandan --version`, `pandan warmup` (should print `ok`), `pandan me` (your id and
email; exit 3 means a bad token), then `pandan board list`.

`--version` prints **build provenance**, not just a number (V50, KAN-435) — `pandan 0.7.0 (bd28cf0)`
for a release build, or an explicit `pandan 0.7.0 (source checkout, not a released build)` when run
from a checkout. If you are chasing behaviour that doesn't match the docs, **check this first**: a
stale binary on `$PATH` has caused two false bug reports on this project. Audit from source with
`uv run python -m pandan_cli …` from `pandan-cli/`, never a binary on `$PATH`.

### Authenticate once (so the token never has to be entered again)

On a standalone machine or in CI (anywhere there's no `.mcp.json` to inherit from), authenticate a
single time and `pandan` persists it to `~/.config/pandan/config.toml` (mode `0600`, owner-only). Every
later `pandan` call — from any directory — then resolves the token from that file automatically. **Do
this without ever emitting the token**: `pandan login` reads the PAT from stdin (or a hidden prompt),
never from a command-line argument, so the literal `pandan_pat_…` never lands in argv, shell history,
or your context. Pipe it in from wherever it already lives, by reference:

```bash
# From a Claude Code .mcp.json (token resolved by jq at runtime, never printed):
jq -r '.mcpServers.pandan.env.PANDAN_TOKEN' .mcp.json \
  | pandan login --token-stdin \
      --api-url https://simple-kanban-jian.fly.dev   # persists both to ~/.config/pandan/config.toml (0600)
```

If you're setting up by hand and the PAT is in some other secret store, pipe *that* into
`pandan login --token-stdin` the same way. `pandan config show` prints the effective config with the token
**redacted** (safe to run), showing which source each value came from. `pandan config set` /
`pandan config path` round out the config commands. (These live in the released binary from **v0.2.3**
onward.) After this, drop the per-call env exports entirely — `pandan list`, `pandan create`, etc. just work.

> Requires a login-capable binary (v0.2.3+). If `pandan login` errors with `invalid choice: 'login'`,
> the installed binary predates the feature — re-download the latest release.

## Cold start: warm up first

The hosted board runs on a free tier that scales to zero, so the first request after a few minutes
idle is slow and can even fail outright (timeout / TLS reset), which looks exactly like the server
being down. Run `pandan warmup` before a batch of calls — it pings the health endpoint, needs no token,
rides out the wake, and exits `0` once the API is up. In a script:

```bash
until pandan warmup; do sleep 2; done
```

## Refer to cards by their board-local ref

Every card and epic carries a **board-local `ref`** — `ENG-14` for a card, `ENG-E7` for an epic, built
from the board's key. **Use it in your messages, commit/branch names, comments and notes, and as the
argument to every verb** (`pandan move ENG-14 done`). It is what human rows and `--json` `.ref` show,
and what people see in the web UI.

The canonical `KAN-955` (`ticket_number`) still resolves, but it is a cross-board address, not a name:
use it only when a board-local ref is ambiguous (the `ambiguous_ref` error says so and lists the
boards) or when no `ref` came back. Don't copy `ticket_number` out of `--json` into prose.

To **find** a card by ref, pass it: `pandan get ENG-14`, or `pandan list --q ENG-14` (also `KAN-955`
and `alice/ENG-14`; exact match, ranked above full-text hits). Partial refs don't match (`ENG-1` ≠
`ENG-12`).

## Command surface

Cards are the top-level verbs; `board`, `epic`, `label`, `view`, `template`, `dep`, `link`, and
`comment` are nested groups. Every command takes `--json` for machine-readable output; the human
line for a card is `ref  column  title  pts=N` (`pts=-` when unestimated).

See `references/command-reference.md` for the full verb list, the `--json` envelope shape per
verb, `--fields`, and exit codes.

## Writing epics and stories

Before you create or edit a card or epic, read `references/writing-epics-and-stories.md`. The short
version: a story is one slice a single agent can finish and demo (1–5 points, split anything bigger);
the title is a specific outcome with no status tags or ticket numbers; the description is
**Why / Do / Done when / Not in scope**, up to about 150 words; dependencies go through `dep add`,
progress goes in comments; an epic is a named outcome with a done-when, filed before its stories.

## Example workflows

Orient, pin a board, then pick up a card and start on it:

```bash
pandan warmup
pandan board list                         # which boards can I reach?
pandan board use ENG                      # once per session; --board N overrides per call
pandan list --column todo                 # what's available
pandan get ENG-42                         # read the card fully
pandan move ENG-42 in_progress            # start it
pandan update ENG-42 --assignee "agent:me"
```

Add a chunk of work under an epic:

```bash
EPIC=$(pandan epic create "Onboarding flow" --json | jq -r .ref)
pandan create "Landing page" --epic "$EPIC" --points 3
pandan create "GitHub login button" --epic "$EPIC" --points 2
```

Finish and close out: `pandan move ENG-42 done`.

## When to fall back to MCP

Use the `mcp__pandan__*` tools instead of `pandan` when the CLI isn't installed / not on PATH, or a
`pandan` command errors for an environment reason (not a 4xx from the API). Every board-touching
`pandan` verb has an MCP twin:

- **Cards:** `list_cards`, `get_card`, `create_card`, `create_cards` / `update_cards` (batch),
  `update_card`, `move_card`, `claim_card`, `delete_card`.
- **Dispatch & handoff:** `dispatch`, `next`, `needs_human`, `resolve`.
- **Dependencies / links / comments:** `add_dependency` / `remove_dependency` / `list_dependencies`,
  `add_link` / `remove_link`, `add_comment` / `list_comments`. (Card reads include
  `blocked_by`/`blocks`/`blocked` and `links` either way.)
- **Boards / epics / labels / views / templates:** `list_boards` / `create_board` / `get_board` /
  `update_board` / `delete_board`, and the parallel `*_epic`, `*_label`, `*_view`, and `*_template`
  (incl. `apply_template`) families.
- **Reporting & ops:** `metrics`, `activity`, `warmup`.
- **Board selection:** MCP has no default board either. Pass `board_id` on each board-scoped call, or
  call `use_board` once to set it for the stdio session (an explicit `board_id` still wins). On the
  hosted MCP endpoint `use_board` is refused — always pass `board_id`.

The MCP server loads at session start, so a newly added MCP *tool* isn't callable until Claude Code is
restarted; a new API *field*, though, shows up immediately since the tools pass JSON straight through.

## Access model (so errors make sense)

`/api/v1` is auth-required and access-gated by **ownership or membership**: a PAT resolves to its
owning user, and that user can see and change boards they **own** plus boards **shared with them** as
a member. Boards can be shared with other users at one of three roles — **viewer** (read-only),
**editor** (read + write cards/epics), or **owner** (full control incl. board settings + membership);
the board's creator always has full access. A PAT inherits its user's memberships, so an agent reaches
exactly the boards its user does. Errors that follow: a `401` means the token is bad or unset; a `403`
means you have no access to that board (or your role is too low for the write you attempted — e.g. a
viewer trying to create a card); a `404` means it doesn't exist. More detail is in the repo's
onboarding guide:
<https://github.com/leejianrong/pandan/blob/main/docs/guides/agent-onboarding.md>.

## Reporting bugs / opening issues

Pandan is developed at **<https://github.com/leejianrong/pandan>**. If you hit a bug, a
missing command, or a CLI↔MCP parity gap while driving the board, open an issue there with
`gh issue create --repo leejianrong/pandan` (the `gh` CLI is authenticated as the repo owner).
Keep it short and reproducible: include `pandan --version`, the exact command and its error, and the
workaround you used if any. Mention you were using the `pandan` skill.

Renaming a board: `pandan board update <id> --name "New name"`.
