# Observability: seeing what a pod is doing, and failing fast

A pod's failure mode is a bill. A silent pod that hangs costs the same per minute as a busy one,
and when it is deleted its logs vanish. So the job must narrate itself, fail loudly, and publish
something even when it fails. Everything below came from real runs (a CPU render job in 2026-11
lost about $1 to three of these mistakes).

## What to build into every job script

Copy the structure; it is about 60 lines.

1. **A stage marker.** `stage() { echo "$1" > $RUN/stage; echo "STAGE $1"; }`, called before each
   step (install, ingest, render, train, publish). It tells a watcher where the job is.
2. **An ERR trap that names the stage.** `trap 'fail "line $LINENO"' ERR` with
   `fail() { echo "STAGE failed ($1; was: $(cat $RUN/stage))"; echo failed > $RUN/status; }`.
   Grep-able: `STAGE failed`.
3. **A heartbeat every 60 s**, as a background loop printing: stage, load or GPU utilisation, disk %,
   RAM %, and seconds since the job log last changed. It also keeps `rp`'s idle watchdog quiet
   during a long silent step. Add `WARN` lines when quiet > 10 to 15 minutes, disk > 90%, RAM > 90%,
   or a GPU is under 5% for several minutes during a training stage.
4. **Tee everything to a log file** (`exec > >(tee -a $RUN/job.log) 2>&1`), so the heartbeat can
   measure quiet time and the final tarball can include it.
5. **An EXIT trap that always publishes.** Results are logged as they appear (a
   `RP_REPORT_BEGIN ... RP_REPORT_END` block with compact JSON), then the artifact is sent over the
   relay and `RP_ARTIFACT_CODE=` is echoed, on success **and** on failure. If the relay fails, the
   numbers are still in the pod logs.
6. **Pod-side smoke test first.** Run the real code path on a tiny input (30 training steps, one
   region) before the long step, so a broken command fails in minutes.

## Rules that would have saved real money

- **Never use a bare `wait`.** It waits for every background job, including your own heartbeat and
  log streamer, which never exit, so the job hangs forever after the real work is done. Capture
  `p1=$!` and `wait "$p1" "$p2"`. A job that did its work and then sat silent for 50 minutes was
  this bug, and it looked like a hung model.
- **Put a `timeout N` on every long step**, sized at about 3x the expected time. On expiry, log
  `ERROR <step> timed out` and carry on to publish, rather than burning the lifetime ceiling.
- **Stream background jobs' own logs into the job log.** If a render or synth runs as
  `cmd > step.log &`, nobody can see it. Add a loop that prints the last line of each log every
  60 to 90 s with a `[name]` prefix.
- **Publish partial results.** A job that only publishes at the very end loses everything to a
  lifetime kill. Publish after each major step when that is cheap, or make the final stage tolerate
  missing pieces (build figures from whichever sets exist, with a `WARN` for the rest).
- **Check the early signal within 1 to 3 minutes of launch.** One `pod logs` call should show
  `STAGE install`. A stuck image pull or a bad bootstrap is cheap to catch early.
- **Rehearse offline first.** Run the figure or report script locally on any existing data, nicely
  (`nice -n 19`), before paying for the pod.
- **Do not saturate the laptop.** Heavy local renders can freeze a dev machine. Run them on a CPU pod
  (`RP_COMPUTE_TYPE=CPU`, 16 vCPU is about $0.56/hr) instead; a GPU is only needed for training.
- **Set `RP_MAX_LIFETIME_SECS` from the expected time, about 3x.** The cap is the last line of
  defence, not the plan.

## Watching from the driver

- Run the driver detached: `setsid bash drive.sh > drive.out 2>&1 &`, and poll with bounded loops
  (`timeout 590 bash -c 'until grep -q DRIVER_DONE drive.out; do sleep 10; done'`). Foreground
  `sleep` is blocked in some agent tools.
- A status helper that greps the pod logs gives a one-screen view. Keep the grep-able tokens in one
  place: `STAGE`, `hb`, `WARN`, `ERROR`, `STAGE failed`, `RP_ARTIFACT_CODE`, `RP_REPORT_BEGIN`.
- Take the pod id as an argument, never hard-coded in a helper script.
- **Killing a stuck driver:** do not `pkill -f drive.sh`; the pattern can match the shell running
  the command and kill your own session, leaving the pod running. Kill by PID, or run `rp down`
  with the same env (it terminates by name and verifies). Then confirm with `runpodctl pod list`.
- Persist a raw snapshot of what you poll, so "never started" and "pattern was wrong" can be told
  apart afterwards.

## After a failure

Read `pod.log` that `rp relay-get` saved, grep for `STAGE`, `ERROR`, `WARN`, then read the last 25
lines. Fix the mechanism, not only the instance, and add the missing signal to the job template.
