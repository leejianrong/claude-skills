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
