---
name: runpod-jobs
description: >-
  Rent a RunPod pod, run a training/inference/eval/batch job on it, get the artifact out,
  and guarantee teardown so it stops billing. Use when deploying or running a job on RunPod,
  driving runpodctl or the RunPod REST API, renting a GPU or CPU pod for compute, or when a
  task needs more compute (GPU or high-RAM) than the local machine has. Covers cost-safe
  teardown (a dead-man's-switch), the current runpodctl/REST surface, spot pods, and moving
  code, data, and artifacts on and off a pod that has no public IP.
---

# Running jobs on RunPod

Rent an ephemeral RunPod pod, run a compute job on it (training, inference, an eval sweep, a
batch), collect the artifact, and **terminate the pod**. RunPod is rented compute whose failure
mode is a **bill, not a crash** — so everything here is organized around not leaking one.

Use the bundled wrapper `scripts/rp` (it bakes in the safety); reach for the raw `runpodctl` /
REST surface only for what it does not cover.

## Rule 0 — never leak a bill (read before launching anything)

RunPod has **no native idle-terminate, no max-lifetime, and no per-pod spend cap.** A
disconnected laptop does **not** stop a running pod. A merely **stopped** pod still bills for
storage — only **terminate/delete** frees all cost. Teardown therefore can never live only on
your machine. Use all three layers, every time:

1. **Account spend limit** (RunPod console) — a coarse backstop. Set it once.
2. **A pod-side dead-man's-switch baked into the launch command**, so it survives a laptop
   disconnect: a hard max-lifetime `sleep … ; terminate`, plus an idle watchdog that
   self-terminates when the job goes quiet. Recipe in `references/cost-safety.md`.
3. **A driver-side trap** — `trap … EXIT INT TERM` that terminates on success, failure, or Ctrl-C.

**Copy this checklist into your task and tick every box before you consider a job done:**

- [ ] An account spend cap is set in the console.
- [ ] The launch command bakes the dead-man's-switch (max-lifetime **and** idle watchdog).
- [ ] The driver traps EXIT/INT/TERM and terminates the pod.
- [ ] After the run, `runpodctl pod list` shows the pod **gone** (account at `$0` idle).

`scripts/rp` does layers 2 and 3 for you and verifies layer 4. Prefer it over hand-rolling
teardown — the dead-man's-switch is fiddly to get right and expensive to get wrong.

**The dead-man's-switch must be the literal first thing `dockerStartCmd` runs — nothing before
it may be able to hang or fail.** A wrapper that does `apt-get install curl && curl -o
entrypoint.sh <url> && exec entrypoint.sh`, where `entrypoint.sh` is where the watchdog actually
gets armed, puts an unprotected network/package step *before* any cost-safety exists: if that
step hangs, the watchdog never arms and the pod can run to your driver-side timeout (or forever,
if that's missing too) with zero teardown and zero diagnostic trail. This burned a real ~100
minutes and ~$2.77 with no artifact and unrecoverable logs (2026-09-21, solve-arc-agi-3/ARC-40).
`scripts/rp`'s `launch_command()` avoids this by inlining the entire watchdog as literal heredoc
content with no network dependency — arm-then-run, never fetch-then-arm. If you're reusing a
project's own committed entrypoint script instead of `rp` (a legitimate reason: it also does
asset download / offline install / a real smoke test your driver needs), get it onto the pod by
embedding its **content** directly into `dockerStartCmd` (read the file, JSON-encode it as the
`bash -lc "<contents>"` argument) rather than fetching it at boot — or if a fetch is
unavoidable, wrap only that fetch in its own `timeout Ns` with a fallback `terminate` on failure,
so a hang can't silently swallow every later safety layer.

## The 60-second happy path

Configure by environment (the API key is read **by reference**, never printed — see below), then
let the wrapper own the lifecycle:

```sh
export PATH="$PWD/scripts:$PATH"           # or call ./scripts/rp directly
export RUNPOD_API_KEY=…                     # a dedicated, limited-scope key (see runpodctl.md)
export RP_POD_IMAGE=ghcr.io/you/your-job:tag
export RP_MAX_HOURLY_USD=0.60               # rp refuses to launch above this
export RP_MAX_LIFETIME_SECS=3600            # hard ceiling; raise for long training
export RP_JOB_CMD='python train.py --out /workspace/ckpt'   # what the pod runs; it self-terminates when done

rp up            # create-or-reuse a spot pod, dead-man's-switch armed; prints the id
rp logs -f       # follow the job's output (works with NO public IP)
rp down          # TERMINATE (idempotent); the trap already does this, this is belt-and-braces
```

For an interactive/service pod (no `RP_JOB_CMD`), the pod runs the image's default command under
the dead-man's-switch and you drive it with `rp run <cmd>` / `rp exec` / `rp push` / `rp pull`.

To get a **file artifact** off a pod with **no public IP** (the common case — see below), have the
job `runpodctl send` it and echo `RP_ARTIFACT_CODE=<code>`, then `rp relay-get <dir>` pulls it over
the relay. A small text result (a number, a path, "done") is simpler still: print it and read it
with `rp logs`. Prefer these over `rp exec`/`push`/`pull`, which need the pod to have a public IP.

## Verify the surface before you rely on it

**RunPod's CLI and REST API move, and recently.** Re-check the shape at run time — do not trust
these docs (or your memory) blind:

- `runpodctl <verb> --help` before using a verb; `runpodctl version` to know what you have.
- In runpodctl 2.14.x the old top-level `get`/`create`/`remove`/`exec`/`config` are **deprecated**
  in favor of `runpodctl pod create|delete|list|logs|…`. Older muscle memory is stale.
- The REST **create** schema is strict and version-specific (`computeType`, `cloudType` +
  `interruptible`, flavor + vCPU vs `gpuTypeId`). A wrong body 400s or silently rents the wrong
  thing. See `references/rest-api.md`.

If a documented flag or field here does not exist, the surface moved — check `--help`/the REST
reference and adapt, don't force it.

**Never let a driver-side monitor wait silently for a completion marker for its full timeout with
zero interim visibility.** If you write a polling loop around `pod logs` (hand-rolled, not `rp
relay-get`), do an early sanity check within the first 1-3 minutes — one `pod logs` call — to
confirm the job has actually started producing output before committing to a long unattended
wait; a broken bootstrap is cheap to catch in minutes and expensive to catch at a 90+ minute
timeout. And have the loop persist (append to a local file) a raw snapshot of what it polls each
time, not just a silent grep — when nothing ever matches and the pod is later deleted, a silent
monitor leaves no way to tell "the job never started" from "the job ran and this script's pattern
was wrong" apart, which is exactly the ambiguity that made the incident above hard to diagnose
after the fact.

## Lessons from real runs (a GPU video-generation project, 11 attempts, 2026-09/10)

Each of these cost a pod launch or a hang before it was fixed. `scripts/rp` now handles the ones
marked (rp); the rest are on the driver or job author.

- **(rp) Every API `curl` needs `--connect-timeout`/`--max-time`.** One untimed call hung a driver
  for 30+ minutes, and `down` is a call too. rp uses 10s/30s.
- **(rp) The pod lingers `RP_EXIT_GRACE_SECS` (default 30) after the job exits, then terminates.** A
  deleted pod's logs are gone, so a crashing job's last traceback was unreadable. The max-lifetime
  guard keeps running during the grace, so the cost ceiling is unchanged.
- **(rp) `relay-get` saves each real log capture to `<dest>/pod.log`, and fails fast on a `not_found`
  reply** (pod gone) with the last 40 lines, instead of polling a 404 until the lifetime deadline.
  Poll interval is `RP_RELAY_POLL_SECS` (default 5). Error replies start `{"error"` and must never
  overwrite the saved log.
- **(rp) `up` prints RunPod's create-error reason** (stock vs a rejected field) instead of a bare
  "HTTP 500". If you pass secrets in pod `env`, redact those values from it first: the API echoes `env`.
- **Add a boot check to the driver:** after `up`, poll `pod logs` for the first few minutes and fail
  fast if the container never produces output. A stuck image pull sat `awaiting_container` for 35+
  minutes with no signal. Print a heartbeat each poll, and on timeout fetch `pod logs --source
  system` (platform narration: image pull, container start). The lifetime deadline is far too long
  to be an early warning.
- **Rehearse the job offline on CPU before a paid launch.** Run the real pod-side code path against a
  tiny randomly-initialised model in a throwaway venv that mirrors the pod (same torch/library pins).
  It caught a missing package and a wrong frame type, each of which would have cost a launch.
- **Match the pod image's framework version to the library you pin.** A library that calls a newer
  torch API fails only on the pod; reproduce it offline, then pick an image tag that exists on the
  registry (check the tag list, don't guess) and whose CUDA your hosts' drivers accept.
- **A cost cap refusing a pod is the safety net working.** Prices and stock move week to week;
  raise the cap per run (`RP_MAX_HOURLY_USD`) after checking the worst case (cap x lifetime), rather
  than editing a default. List several acceptable GPU types in `RP_GPU_TYPE`, since any one can be
  out of stock.
- **Timing varies a lot.** The same job's model download+load took ~8 minutes on a cold run and ~2
  on a later one. Size `RP_MAX_LIFETIME_SECS` for the cold case; the idle watchdog and teardown cover
  the rest.
- **When driving a launch from an agent session:** run the driver detached (`setsid ... &`) and
  redirect to a file, drop a marker file first, and judge "which run is mine" by `find -newer
  <marker>`, not "the newest directory". Check `pod list` is empty afterwards.

## Secrets: handle the key by reference, never in context

Treat `RUNPOD_API_KEY` as a credential you handle blind. **Never** `cat`/`echo`/`print`/`log` it
or paste its literal value into a command. Read it from the environment or a gitignored file, feed
it to `curl` via a config file on **stdin** (`curl -K -`, never in `argv`/a URL), and to
`runpodctl` via the environment (`RUNPOD_API_KEY=… runpodctl …`, by reference). Use a dedicated,
limited-scope, revocable key — not your account-wide one. `scripts/rp` follows all of this.

## When to use this / when not to

- **Use it for:** build-time and batch compute — a training run, an eval sweep, a one-shot
  inference/recognition job, anything that produces an **artifact** consumed offline, or work that
  needs a GPU or more RAM than the local machine has.
- **Do not use it as a low-latency product runtime dependency.** A rented pod behind a proxy with a
  ~100 s cap and machine-dependent networking is the wrong shape for a request path. If an app
  must call remote inference at runtime, that is a hosted-serving decision with its own tradeoffs,
  not this. (This skill is Pods-only; RunPod Serverless is a different contract, not covered yet.)
- **One exception — short-lived HTTP-service *verification*:** standing up a web app on a pod,
  reaching it at `https://{podId}-{port}.proxy.runpod.net`, proving something works *through the
  proxy* (e.g. that an app's SSE/streaming survives the ~100 s Cloudflare cap), then terminating.
  That is a bounded check, not a runtime dependency. See `references/http-service-pods.md`.

## References — load on demand

- **`references/cost-safety.md`** — the dead-man's-switch recipe, terminate-not-stop, spot vs
  on-demand, the account spend cap. Read this before writing any launch command by hand.
- **`references/runpodctl.md`** — installing and authenticating runpodctl; the current verb surface
  (`pod create/delete/list/logs`, `send`/`receive`); and the gotchas (deprecated verbs, the random
  relay-index in transfer codes, `pod logs` with no public IP).
- **`references/rest-api.md`** — REST v1 create bodies for CPU **and** GPU pods, field by field,
  and the verify-RAM-and-price-after-create pattern that catches a wrong flavor for cents.
- **`references/data-transport.md`** — getting code/data/artifacts on and off a pod, including the
  **no-public-IP reality** and the `runpodctl` relay recipe that works around it, why long
  synchronous HTTP requests die, and the thread-oversubscription gotcha.
- **`references/gpu-and-sizing.md`** — GPU types and cost ballparks, CPU flavor tiers
  (compute/general/memory) and how to size them, and a short section on long training jobs
  (checkpoints out, network volumes, tuning the lifetime ceiling).
- **`references/http-service-pods.md`** — expose an HTTP port at create time, reach it at
  `https://{podId}-{port}.proxy.runpod.net`, and verify a web app (incl. SSE/streaming) through
  the proxy with curl — the ~100 s cap, the 0.0.0.0 bind, teardown. For smoke tests, not hosting.
