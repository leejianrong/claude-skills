# Cost safety: never leak a bill

The one property that matters. RunPod gives you no safety net, so you build it. This file is the
recipe `scripts/rp` implements; read it before hand-rolling any launch or teardown.

## Contents

- The facts that force the design
- Three layers, always (spend cap → pod-side dead-man's-switch → driver-side trap)
- Terminate, not stop; idempotent
- Verify, don't assume

## The facts that force the design

- **No native idle-terminate, no max-lifetime, no per-pod spend cap.** RunPod will run a pod until
  you delete it or the account runs dry.
- **A disconnected laptop does not stop a pod.** Whatever you started keeps running after you close
  the lid, lose wifi, or the terminal dies.
- **Stopped still bills.** A *stopped* pod keeps billing for its storage. Only **terminate/delete**
  frees all cost.
- **Spot/interruptible pods appear discontinued** (observed 2026-09): a create with
  `"interruptible": true` now returns `500 {"error":"create pod: Spot pods are no longer offered"}`.
  Use **on-demand** (`interruptible: false`). Verify at run time (it may vary by account/region), but
  don't assume spot exists — default to on-demand and let the cost cap + verify-after-create guard the
  price.

Conclusion: teardown cannot live only on your machine, and "stop it later" is not teardown.

## Three layers, always

### 1. Account spend limit (console, once)

Set a spend limit in the RunPod console. Coarse, but it is the only thing that survives every bug
in the layers below. Do it once per account.

### 2. Pod-side dead-man's-switch (baked into the launch command)

This runs **inside** the pod, so it holds even if your machine disconnects. Bake it into the pod's
`dockerStartCmd` (REST) / the command the pod boots with. Two guards:

```sh
# Runs as the pod's start command. RunPod injects $RUNPOD_POD_ID into every container.
set -eu
LOG=/tmp/job.log ; : > "$LOG"

terminate() {
  echo "pod: self-terminating ($1)" >&2
  runpodctl pod delete "$RUNPOD_POD_ID" 2>/dev/null \
    || runpodctl remove pod "$RUNPOD_POD_ID" 2>/dev/null || true   # 'remove pod' is the deprecated fallback
  kill -TERM -1 2>/dev/null || true
}

# Guard 1 — hard max-lifetime ceiling. Terminate no matter what, so nothing runs forever.
( sleep "${MAX_LIFETIME_SECS:-3600}" ; terminate "max-lifetime reached" ) &

# Run the actual job, tee-ing its output so the idle watchdog can see progress.
( your_job_command 2>&1 | tee "$LOG" ) &
JOB=$!

# Guard 2 — idle watchdog. If the log stops GROWING for the timeout, the job is hung/done-and-idle: reap.
(
  idle="${IDLE_TIMEOUT_SECS:-900}"
  last_size=0 ; last_change=$(date +%s)
  while kill -0 "$JOB" 2>/dev/null; do
    sleep "${IDLE_CHECK_SECS:-60}"
    size=$(wc -c < "$LOG" 2>/dev/null || echo 0) ; now=$(date +%s)
    if [ "$size" != "$last_size" ]; then last_size=$size ; last_change=$now
    elif [ $(( now - last_change )) -ge "$idle" ]; then terminate "idle ${idle}s" ; break ; fi
  done
) &

wait "$JOB"
terminate "job exited"
```

Notes that bite:
- **Install runpodctl on the pod if the image lacks it** — a slim image often has neither
  `runpodctl` nor `wget`/`curl`. Best-effort the install; if it fails, layers 1 and 3 remain.
- **Idle-watchdog signal.** "Log grew" is a good generic liveness signal. If your job is silent for
  long legitimate stretches (a slow single inference), either raise `IDLE_TIMEOUT_SECS` or have the
  job print a heartbeat — otherwise the watchdog reaps it mid-work. A per-page job that prints one
  line per item, taking ~14 min/item, sat at 839 s against a 900 s timeout: too close. Raise it.
- **Long jobs:** the idle watchdog resets on output, but the **hard max-lifetime does not** — set
  `MAX_LIFETIME_SECS` above the whole job's expected wall-clock (training: hours).

### 3. Driver-side trap (on your machine)

Whatever happens to your driver command — success, failure, Ctrl-C, crash — terminate the pod:

```sh
trap 'runpodctl pod delete "$POD_ID" >/dev/null 2>&1 || true' EXIT INT TERM
```

Combined with layer 2 this is defence-in-depth: either side terminating is enough, and neither
alone is trusted.

## Terminate, not stop; idempotent

`down`/teardown must **delete**, and deleting an already-gone pod must be **success** (so a retry or
a double-trap never errors). With runpodctl: `runpodctl pod delete <id>`. With REST:
`DELETE /pods/{id}`. Treat a 404 / "not found" as done.

## Verify, don't assume

After any run, confirm the account is actually at zero:

```sh
runpodctl pod list          # must not list your pod
# and check network volumes too — they bill even with no pod:
runpodctl network-volume list
```

`scripts/rp` runs an equivalent sweep. If anything remains, delete it now — a forgotten pod or
volume is the whole failure mode.
