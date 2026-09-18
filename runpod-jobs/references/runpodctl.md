# runpodctl: install, auth, and the current surface

`runpodctl` is the CLI that drives pods and transfers files. **Its surface moves** — the shape
below is current as of the 2.14.x line; run `runpodctl version` and `runpodctl <verb> --help`
before relying on any verb.

## Contents

- Install
- Authenticate (by reference)
- Pod verbs (create / list / delete / logs)
- `pod logs` — the feedback channel with no public IP
- File transfer: `send` / `receive` and the random-relay-index gotcha
- Deprecated verbs to unlearn

## Install

```sh
wget -qO- cli.runpod.net | sudo bash          # verify the current method on RunPod's docs
# or grab a pinned release binary (no sudo):
wget -qO ~/.local/bin/runpodctl \
  https://github.com/runpod/runpodctl/releases/download/vX.Y.Z/runpodctl-linux-amd64
chmod +x ~/.local/bin/runpodctl
```

**Pin the version when a relay transfer must rendezvous** (see below): the pod and your machine
must run the **same** runpodctl, or a `send`/`receive` code can resolve to different relays and
never connect.

## Authenticate (by reference)

runpodctl reads `RUNPOD_API_KEY` from the environment, or you can persist it with
`runpodctl doctor` (interactive). Pass it **by reference**, never as a literal:

```sh
RUNPOD_API_KEY="$RUNPOD_API_KEY" runpodctl pod list      # value comes from the env, not argv text
```

Use a dedicated, limited-scope, revocable key — not the account-wide one. Never echo/log it.

## Pod verbs

```sh
runpodctl pod list                 # your pods (JSON by default; -o yaml also)
runpodctl pod create …             # prefer the REST API for CPU/GPU create bodies (rest-api.md)
runpodctl pod delete <id>          # TERMINATE; treat "not found" as success (idempotent)
runpodctl pod logs <id> [flags]    # see below
```

`pod create` via the CLI is coarser than the REST create body; for precise CPU flavor / GPU type /
port control use REST (`references/rest-api.md`). Use the CLI for list/delete/logs.

## `pod logs` — the feedback channel with no public IP

The most useful verb, and the one that makes headless jobs workable: it streams the pod's logs
**through the RunPod API**, so it needs **no public IP** on the pod.

```sh
runpodctl pod logs <id>                         # last 100 lines, then exit
runpodctl pod logs <id> --follow                # stream live
runpodctl pod logs <id> --tail 5000 --max-wait 5s   # replay up to 5000 lines, then exit
runpodctl pod logs <id> --since 30m --source system # platform lines only (image pull, create…)
```

Output is JSON-lines: `{"source":"container|system","line":"…","ts":"…"}`. `container` is your
workload's stdout/stderr; `system` narrates image pull / container start (a stalled deploy shows
up as repeated pull progress there).

**Poll with `--tail N`, do not lean on `--follow --tail 0`.** RunPod's log pipeline lags several
seconds, and a live-only follow both misses lines printed before it connected and loses history on
every reconnect. To wait for a specific marker your job prints, poll in a loop with a large
`--tail` (replaying history each call) and grep the snapshot — a replaying poll cannot miss it:

```sh
until RUNPOD_API_KEY="$RUNPOD_API_KEY" runpodctl pod logs "$id" --tail 5000 --max-wait 5s \
        | grep -oE 'MY_MARKER=[^"]+' ; do sleep 10 ; done
```

## File transfer: `send` / `receive`, and the random-relay-index gotcha

`runpodctl send`/`receive` move files over a **relay** (croc under the hood) — **outbound network
only, no public IP required.** This is how you get files on/off a pod that has no direct-TCP
endpoint. But the code handshake has a sharp edge:

- `runpodctl send --code <base> <file>` accepts a **custom base** code — but **appends a random
  relay index** at send time and prints the final code as `<base>-<index>` (its first stdout line).
- `runpodctl receive <final>` needs that **exact** final code, index included. A mismatched index
  fails with `room not ready`.
- The code must have **≥ 2 dash-separated parts** (e.g. `myjob-abc123`), or you get
  `malformed code`.

So a purely pre-shared code does **not** work by itself — the sender's random final code has to
reach the receiver out of band. `references/data-transport.md` has the full recipe for both
directions (including the trick for sending *to* a pod, where the receiver can't see the sender's
code). The croc sender **holds its relay room** while waiting for the receiver (verified ≥ 80 s),
which is what makes it survive a pod boot.

## Deprecated verbs to unlearn

In 2.14.x the old top-level verbs are **deprecated** in favor of resource-scoped ones:

| Old (deprecated) | Current |
|---|---|
| `runpodctl get pod` | `runpodctl pod list` / `pod get` |
| `runpodctl create pod` | `runpodctl pod create` (or REST) |
| `runpodctl remove pod` | `runpodctl pod delete` |
| `runpodctl exec …` | ssh into the pod, or `pod logs` for output |

The deprecated forms often still run (keep `remove pod` as a fallback in a pod-side script where
you can't be sure which version is installed), but write new code against the current verbs.
