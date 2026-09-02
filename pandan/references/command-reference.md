# Pandan command reference

The `--json` shape table, `--fields`, the full command surface, and exit codes for the
`pandan` CLI. Read this when you need the exact flags or the JSON envelope for a verb; the
overview and setup live in the parent `SKILL.md`.

## Contents
- JSON output shapes
- `--fields`
- Cards
- Agent operating verbs
- Dependencies, work-links, comments
- Boards, epics, labels, saved views, templates
- Reporting
- Ops
- Errors and exit codes

Cards are the top-level verbs; `board`, `epic`, `label`, `view`, `template`, `dep`, `link`, and
`comment` are nested groups. Columns are `todo`, `in_progress`, `done`. Story points are one of
{1,2,3,5,8,13}. Priority is one of `none`/`low`/`medium`/`high`/`urgent`. Every command takes `--json`
for machine-readable output you can pipe into `jq`; the human line for a card is
`ticket  column  title  pts=N` (`pts=-` when unestimated).

## JSON output shapes

**`--json` output is enveloped for list verbs, bare for single reads — don't guess the shape**
(KAN-434, verified 2026-07-31). `--json` is a verbatim passthrough of the shared client's return
value, and the *client* adds the envelope (a raw `GET /api/v1/cards` is a bare array), so the key
differs per verb:

| Verb | Top-level `--json` shape |
|---|---|
| `list` | `{"cards": [...]}` **+ `next_cursor`** when the page is full |
| `activity` | `{"activity": [...]}` + `next_cursor` |
| `board list` / `epic list` / `label list` / `view list` / `template list` / `comment list` / `cycle list` / `notify list` | `{"boards"}` / `{"epics"}` / `{"labels"}` / `{"views"}` / `{"templates"}` / `{"comments"}` / `{"cycles"}` / `{"notifications"}` |
| `next`, `next --claim` | `{"card": {...}}` — `{"card": null}` when nothing is ready |
| `batch-update` / `template apply` | `{"updated": [...]}` / `{"created": [...]}` |
| `dep add`/`rm`/`list` | `{"card_id", "blocked_by", "blocks"}` |
| `link add`/`rm` | `{"card_id", "links"}` |
| any `delete` | `{"deleted": <id>}` |
| `warmup` | `{"status", "health"}` |
| `get`, `create`, `update`, `move`, `needs-human`, `resolve`, `comment add`, `notify read`, and every `<group> create/update` | **bare entity object** — no envelope |
| `metrics`, `cycle metrics`, `config show` | **bare object** — no envelope |

```bash
pandan list --json | jq -r '.cards[] | "\(.ticket_number)\t\(.title)"'   # NOT .[]
pandan next --json | jq -r '.card.ticket_number // "none ready"'
pandan get KAN-7 --json | jq -r .title                                   # single reads are BARE
```

The envelope is load-bearing (`next_cursor` rides there, and a `summary` field is coming) — treat it
as the contract, not an accident.

## `--fields`

**`--fields a,b,c` widens the human row on any list verb** (V42/KAN-425) — cheaper than `--json` when
you want two or three extra columns rather than the whole record:

```bash
pandan list --column todo --fields ticket,title,priority   # tab-separated, `-` for null
```

The vocabulary is that row's own `--json` keys plus the aliases `ticket` and `pts`/`points`; an unknown
name is a clean error naming it. Omitting `--fields` leaves the default
`ticket  column  title  pts=N` row byte-identical, and `--fields` **does not** affect `--json` (that's
already the full record). Not available on single-entity verbs like `get` — there it's a usage error,
not a silent no-op. Don't confuse it with `--sort`, whose help line lists **`Sort keys:`**.

## Cards

- `pandan list [--board N] [--column C] [--epic ID] [--priority P] [--label ID] [--assignee A] [--due-before ISO] [--overdue] [--needs-human] [--q TEXT] [--sort SPEC] [--limit N] [--json]`
  — query/filter cards. `--q` is full-text search over title+description; `--sort` takes
  comma-separated keys, `-` prefix = descending (e.g. `--sort -priority,position`). Large results
  paginate; the output includes a next-cursor to continue.
- `pandan get <card_id> [--json]`
- `pandan create "<title>" [--board N] [--description D] [--column C] [--points N] [--assignee A] [--epic ID] [--priority P] [--due ISO] [--label ID ...] [--json]`
- `pandan update <card_id> [--title T] [--description D] [--points N] [--assignee A] [--epic ID] [--priority P] [--due ISO] [--label ID ...] [--json]`
  — field edits only. It does **not** change the column; use `move` for that. `--label` replaces the
  card's labels with the given ids.
- `pandan move <card_id> <column> [--position N]` — the dedicated column/position change.
- `pandan delete <card_id> --yes` — `--yes` is required as a guard.
- `pandan batch-update '<JSON array of {id, ...fields}>'` (or `-` for stdin) — atomically PATCH several
  cards in one call (all-or-nothing).

## Agent operating verbs

The write side of the human↔agent surface:

- `pandan next [--board N] [--claim] [--assignee A] [--label ID] [--priority P] [--json]` — show the next
  ready card (highest priority, unblocked, in `todo`); `--claim` atomically dispatches it (sets
  assignee + moves to `in_progress`), which is fleet-safe across concurrent agents.
- `pandan needs-human <card_id> [--note N]` — flag a card for a human decision. `pandan resolve <card_id>`
  — clear the flag. (Filter with `pandan list --needs-human`.)

## Dependencies, work-links, comments

Nested groups:

- `pandan dep add <card_id> --blocked-by <other_id>` · `pandan dep rm <card_id> --blocked-by <other_id>` ·
  `pandan dep list <card_id>`
- `pandan link add <card_id> --url <url> --label <label>` · `pandan link rm <card_id> --link-id <id>`
- `pandan comment add <card_id> --body "…"` · `pandan comment list <card_id>`

## Boards, epics, labels, saved views, templates

- `pandan board list [--json]` · `pandan board create "<name>" [--json]`
- `pandan epic list [--board N] [--json]` · `pandan epic create "<name>" [--board N] [--description D] [--json]`
- `pandan epic update <epic_id> [--name N] [--description D] [--json]` · `pandan epic delete <epic_id> --yes [--json]`
- `pandan label list [--board N] [--json]` · `pandan label create "<name>" [--color C] [--board N] [--json]` · `pandan label delete <label_id> --yes [--json]`
- `pandan view list|create|delete …` — saved named filter/sort views.
- `pandan template list|create|delete|apply …` — card templates; `apply` seeds a template's cards onto a board in one call.

## Reporting

Read-only, derived:

- `pandan metrics [--board N] [--since ISO] [--window SPAN] [--json]` — throughput / cycle time / aging WIP / per-assignee.
- `pandan activity [--board N] [--actor LABEL] [--action VERB] [--limit N] [--cursor C] [--json]` — the board's activity feed, newest-first.

## Ops

- `pandan warmup [--json]` — wake the server; no token needed.
- `pandan --version` / `pandan -v` — print the version **and build provenance**, then exit. A released
  binary reports `pandan 0.7.0 (bd28cf0)` (the commit it was built from); a source run says
  `(source checkout, not a released build)`. **If a `pandan` behaves unexpectedly, check this first** —
  a stale binary that predates a fix used to be indistinguishable from current source, which caused
  two false bug reports (KAN-435).
- `pandan login` / `pandan config set|show|path` — one-time auth + config file (see Setup in `SKILL.md`).

## Errors and exit codes

The machine contract, V43/KAN-426.

Exit codes: `0` success, `1` generic/runtime error, `2` usage (argparse rejected argv), `3`
unauthorised (401), `4` forbidden (403), `5` not found (404). So a script tells "bad token" from
"not your board" from "gone" without parsing text. The rule behind 1-vs-2: **argparse rejected argv →
2; the CLI rejected a runtime value → 1.**

**Errors go to stdout, structured** — not stderr as prose:

```
$ pandan get KAN-999999
error	not_found	no card found with ticket KAN-999999	KAN-999999      # exit 5
```

Tab-separated `error <code> <message> <arg>`, or under `--json` an
`{"error": {code, message, arg, status, exit_code}}` object with all five keys always present. Branch
on the stable `code` (`not_found`, `unauthorized`, `forbidden`, `config`, `unknown_field`,
`confirmation_required`, `invalid_ref`, `transport`, …), never on message text. Human `usage:` text
still goes to stderr.

**A card that doesn't exist reports the same code however you addressed it** — `pandan get 999999` and
`pandan get KAN-999999` both exit `5`. Before v0.7.0 the ticket-ref form exited `1`, so the code
depended on the identifier form rather than the failure.
