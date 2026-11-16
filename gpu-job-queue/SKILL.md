---
name: gpu-job-queue
description: Schedule, monitor and reorder long GPU jobs (model evals, vLLM runs, training) on a machine with its own local GPU using pueue, so jobs run one after another instead of colliding on VRAM. Use when queueing or checking a job on a local or WSL2 GPU, when asked to "queue a run", "what is on the GPU", "reorder or remove a queued job", or before starting anything that loads a model locally. Not for rented pods or cloud GPUs.
---

# GPU job queue with pueue (local GPU only)

One GPU, several agents and people. Nothing stops two processes from loading models at once, and an
oversubscribed card can stall jobs or, under WSL2, take the Windows desktop with it. So every GPU job goes
through one pueue queue, one job at a time.

## Rules

1. **Queue, never launch directly.** No bare `python train.py` or `vllm serve` on the GPU. pueue orders jobs
   from sessions that use it; it cannot stop a program that grabs the GPU on its own.
2. **Check before adding.** `pueue status` and `nvidia-smi --query-gpu=memory.used,memory.total --format=csv`.
   Other users' jobs may be queued or running; the queue is shared.
3. **Only touch your own jobs.** Never `kill`, `remove`, `clean` or `reset` a job you did not add. `pueue reset`
   kills everything: never.
4. **Never auto-restart failed jobs from an agent.** A failed job may fail identically forever (one third-party
   report: a queue growing from 60 to about 12,800 jobs). Read the log, fix the cause, add a new job by hand.
5. **Keep secrets out of jobs.** pueue stores the whole environment of the shell that adds a job. Add jobs with
   a minimal environment (`env -i PATH=... HOME=... USER=... XDG_RUNTIME_DIR=... pueue add ...`), never with
   tokens or `.env` values in scope.
6. **Leave VRAM headroom.** Give a server about 80% of the card, not 90%+. At 88% a job stalled for ~35 min when
   another process held 1.3 GB; the cause was not proven, but a CUDA job that drives free VRAM to zero can
   crash a WSL2 host. Treat any run that saw under ~500 MiB free as suspect and do not trust its numbers.

## Commands

| Task | Command |
|---|---|
| Add a job | `pueue add -l "RUN_ID\|MODEL\|N" -w "$PWD" -- ./job.sh ARGS` |
| Add behind another job | `pueue add -a ID -- ./job.sh ...` |
| Queue and hold | `pueue add -s -- ...` then `pueue enqueue ID` |
| List | `pueue status` |
| Reorder two queued jobs | `pueue switch A B` (never the running one) |
| Remove a queued job | `pueue remove ID` |
| Stop your running job | `pueue kill ID`, then `pueue remove ID` |
| Output | `pueue log ID` (finished), `pueue follow ID` (running) |

One-time setup: `pueue group` shows the default group; `pueue parallel 1` keeps it to one job at a time. The
daemon `pueued` should run as a service (on WSL2 a systemd user unit, `systemctl --user status pueued`).
A new session that cannot reach it usually lacks `XDG_RUNTIME_DIR`.

## Waiting for a job

Do not poll in a loop of short sleeps. Use a background watch that ends on a condition, for example
`until ! pueue status | grep -E "^ ID " | grep -q Running; do sleep 10; done`, run as a background command or
monitor, and keep working. A foreground wait that exceeds the tool timeout gets moved to the background anyway.

## What a good job wrapper does

Put these in the script pueue runs, so every queued job gets them:

- Wait until free VRAM covers the job's share of the card plus a margin (about 512 MiB), then start.
- Sample VRAM and GPU use every ~30 s into the run folder; at the end, flag the run if free VRAM ever dipped
  under the threshold.
- Run model-written or downloaded code only in a container with no network and resource limits.
- Print an ETA for the queue from the median time of past runs of the same model times the task count.

Example from a real project (a wrapper around pueue with these four): `scripts/gpu_queue.py add RUN_ID BUNDLE
MODEL [--seed N] [--tasks N] [--util 0.80]`, `gpu_queue.py eta`. If the project has one, use it instead of
raw `pueue add`.

## Checklist before adding a job

- [ ] `pueue status` read; no job of mine already covers this
- [ ] VRAM free is enough for the job's share plus margin
- [ ] Job goes through the wrapper (or waits for VRAM itself) and uses a minimal environment
- [ ] Label says what it is (`RUN_ID|MODEL|N`), so others can read the queue
- [ ] Order is deliberate: probes and cheap checks go before the long runs (`pueue switch`)
- [ ] I will read the log when it ends, and not restart it blindly

## Gotchas

- A job that is "Success" in pueue only means the script exited 0. Check the job's own result files.
- Jobs build from the working tree when they start. Do not switch branches or delete files that a queued job
  needs until the queue has drained.
- Foreign jobs may appear in the queue. Report them to the user; do not remove them.
- A VRAM share set too low can make a model server fail to start, and the job then exits fast with an error.
  vLLM needs the model plus KV cache for its full context: a 9.7 GiB model at a 0.75 share of a 16 GB card
  left 0.4 GiB for a 0.6 GiB KV cache. Keep the default share unless you know the model fits; read the job's
  own log (not just pueue's "Failed") for the first `ValueError` or `ERROR` line.
- Tell the other agent sessions on the machine when you queue work (list them, then message the local
  interactive ones): the queue only protects the GPU if everyone uses it.
