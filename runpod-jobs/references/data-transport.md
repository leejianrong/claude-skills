# Moving code, data, and artifacts on and off a pod

The hard part of a headless job is not compute — it's getting the inputs in and the artifact out
when the pod has **no public IP**. This file covers the reality and the working recipes.

## Contents

- The no-public-IP reality
- Why long synchronous HTTP requests die
- Options, in order of robustness
- The relay recipe (both directions, with the code-coordination trick)
- Thread over-subscription (a speed gotcha, not a transport one)

## The no-public-IP reality

Spot CPU pods frequently come up with `publicIp: ""` and `portMappings: null` — **no direct-TCP
public endpoint.** Direct-TCP IPs are machine-dependent on RunPod and the spot scheduler places you
wherever there's capacity. So **ssh/scp over `publicIp:port` is unreliable** — it works only on a
pod that happens to get an IP. Anything that must always work has to use an **outbound-only**
channel: `runpodctl` relay, `runpodctl pod logs`, or the pod fetching/pushing to a store itself.

## Why long synchronous HTTP requests die

Do not run a multi-minute job behind one HTTP request to the pod:

- RunPod's **HTTP proxy** (`https://{id}-{port}.proxy.runpod.net`) is Cloudflare-fronted with a
  ~100 s response cap — a long request returns **524**.
- **Direct TCP** forwarding (when you even get a public IP) was inconsistent host-to-host for
  multi-minute holds.
- HTTP clients impose their own timeouts (e.g. undici's ~5-min default) shorter than a real job.

The fix is **co-location**: run the work **on the pod** and move only inputs and outputs, or use an
async submit/poll contract. Never a single synchronous request that must survive minutes.

## Options, in order of robustness

1. **Small text result → `runpodctl pod logs`.** Have the job print the number/path/status; read
   it with a `--tail N` poll (`references/runpodctl.md`). No public IP, no files. Best for evals,
   metrics, a "done" signal.
2. **Files, no public IP → `runpodctl` relay** (recipe below). Outbound-only; works anywhere.
3. **Persistent artifact → a network volume.** Attach one; the job writes checkpoints there; the
   volume outlives the pod. Best for training. (It bills while it exists — delete when done.)
4. **Public IP present → ssh/scp** (`rp exec/push/pull`). Simplest, but only when the pod actually
   got a direct-TCP endpoint — check the pod's *Direct TCP Ports* / `portMappings`.
5. **Pod pulls it itself → `git clone` / object store.** The pod fetches inputs and pushes outputs
   to a store you both reach. Heaviest setup; fine when you already have the store.

## The relay recipe (both directions)

The catch (`references/runpodctl.md`): `send` picks a **random relay index** and prints the final
code; `receive` needs that exact final code. So the sender's code must reach the receiver out of
band. The direction determines how.

**Down (pod → your machine) — the easy direction, and a first-class wrapper command.** The pod is the
sender; it prints its final code to stdout, which you read via `pod logs`. `scripts/rp` wraps the
receive side as **`rp relay-get <dir>`** — the job just has to send and echo the code with the
`RP_ARTIFACT_CODE=` marker the wrapper greps for:

```sh
# On the pod (inside the job / dead-man's-switch script), when the artifact is ready:
tar cf out.tar -C /workspace/results .
BASE=myjob-$RANDOM                      # any code with >= 2 dash-separated parts
runpodctl send --code "$BASE" out.tar > /tmp/send.log 2>&1 &
echo "RP_ARTIFACT_CODE=$(grep -oE "${BASE}[-0-9]+" /tmp/send.log | head -1)"   # surfaces in `pod logs`
wait                                    # hold the relay room until your machine receives

# On your machine — the wrapper polls the logs for the code and receives:
rp relay-get ./results
# (equivalent by hand:)
code=$(runpodctl pod logs "$id" --tail 5000 --max-wait 5s | grep -oE 'RP_ARTIFACT_CODE=[^"]+' | cut -d= -f2)
runpodctl receive "$code"               # writes out.tar into the current dir
```

**Up (your machine → pod) — the hard direction**, because the pod (receiver) can't see your random
code, and `pod logs` only flows pod→you. The trick: **pre-start your `send`, read its final code,
then bake `runpodctl receive <final>` into the pod's launch command** — so the pod knows the exact
code before it boots. Your send holds the room while the pod comes up:

```sh
# On your machine, BEFORE creating the pod:
runpodctl send --code myjob-$UP_BASE in.tar > /tmp/up.log 2>&1 &   # holds the room
final_up=$(until grep -oE "myjob-${UP_BASE}[-0-9]+" /tmp/up.log | head -1; do sleep 0.5; done)
# Now create the pod with a dockerStartCmd that runs:  runpodctl receive "$final_up"  (with retries)
```

Package multiple files as one tar so the transfer is a single file. If the pod's baked-in code age
matters (the image's own code is stale), ship your current code up in the same tar and run it via
`PYTHONPATH`/an explicit path rather than trusting what's installed in the image.

## Thread over-subscription (a speed gotcha)

Not transport, but it bites every CPU job: a container **sees the host's core count** (often
44-128) but is **cgroup-throttled** to your vCPU allocation. ML runtimes (onnxruntime, OpenMP,
BLAS) then spawn one thread per *visible* core and thrash — you'll see floods of
`pthread_setaffinity_np failed … Specify the number of threads explicitly`. The result is a job far
slower than the vCPU count predicts, and adding vCPUs barely helps. Cap threads explicitly in the
launch env to match your allocation:

```sh
export OMP_NUM_THREADS=$VCPU OPENBLAS_NUM_THREADS=$VCPU MKL_NUM_THREADS=$VCPU NUMEXPR_NUM_THREADS=$VCPU
```

(A framework with its own thread-pool setting — e.g. onnxruntime's `intra_op_num_threads` — may
need that set in the job's code, not just the env.) A GPU sidesteps the CPU thrash entirely.
