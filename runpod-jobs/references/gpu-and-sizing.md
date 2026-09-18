# GPU types, CPU flavors, and sizing

How to pick and size a pod. Prices move constantly and vary by cloud type (SECURE vs COMMUNITY) and
spot vs on-demand — treat every number here as a **ballpark to sanity-check against the console**,
not a quote. Enforce a real cap with `RP_MAX_HOURLY_USD` and the verify-after-create step
(`references/rest-api.md`).

## CPU flavor tiers

RunPod CPU flavors are `cpu<gen><tier>`, e.g. `cpu3m`, `cpu5c`. Gen is 3 or 5; tier sets the
RAM-per-vCPU ratio:

| Tier | Letter | ~RAM per vCPU | Use for |
|---|---|---|---|
| compute | `c` | ~2 GB | compute-bound work, cheapest per vCPU |
| general | `g` | ~4 GB | balanced |
| memory  | `m` | ~8 GB | RAM-bound work (large models in RAM) |

RAM = tier ratio × `vcpuCount`. Pick the tier by what bounds the job: a model that needs ~7 GB RAM
clears easily on a small memory-tier pod; a compute-bound job wants the compute tier and more
vCPUs. Verify the actual RAM/price after create — the requested flavor may be unavailable and you
get substituted.

**More vCPUs help less than you'd hope for ML CPU inference** because of thread over-subscription
(`references/data-transport.md`) — cap threads to the vCPU count, and if the job is genuinely
compute-bound, a GPU is the real fix, not more CPU cores.

## GPU types and rough cost

List exact ids with `runpodctl gpu list` (the create body needs the exact string). Rough
spot/community ranges (verify live):

| Class | Examples | ~$/hr (spot/community) | Good for |
|---|---|---|---|
| Entry | RTX A4000, RTX 3090 | ~$0.2–0.4 | inference, small training |
| Mid | RTX 4090, RTX A5000, L4 | ~$0.3–0.8 | most training, fast inference |
| Large | A40, A100 40/80 GB, H100 | ~$1–3+ | big models, large-batch training |

**Key economics:** a GPU's higher $/hr is often offset by finishing far faster, so a GPU job can
cost the *same or less per run* than a slow CPU job — compare `$/hr × wall-clock`, not `$/hr`. And
for anything compute-bound, the GPU also sidesteps the CPU thread-thrash. Match the smallest GPU
whose VRAM fits the model; oversizing VRAM you don't use is wasted money.

## Sizing checklist

- **RAM** ≥ the model's peak resident set, plus headroom (CPU: pick the tier; GPU: watch VRAM).
- **`containerDiskInGb`** ≥ image size + scratch. Ephemeral, freed on terminate.
- **`volumeInGb`** = 0 unless you need persistence across pods (then it bills while it exists).
- **`RP_MAX_LIFETIME_SECS`** above the whole job's expected wall-clock — training is hours, so
  raise it well past the default, or the dead-man's-switch reaps mid-run.

## Long training jobs (the thin version)

Training is the same lifecycle with three adjustments; the cost-safety and transport recipes are
unchanged:

1. **Persist checkpoints to a network volume**, not the ephemeral container disk — a spot reclaim
   (~5 s warning) or a crash otherwise loses everything. Attach the volume, write checkpoints there,
   and have the job **resume from the latest checkpoint on restart** so a reclaim is survivable.
2. **Raise `RP_MAX_LIFETIME_SECS`** to comfortably exceed the run, and make the idle watchdog's
   signal real — training logs steadily, so log-growth liveness works; a long silent phase needs a
   heartbeat print or a higher `IDLE_TIMEOUT_SECS`.
3. **Get the trained artifact off** via a network volume (simplest) or the relay recipe
   (`references/data-transport.md`); then **delete the volume** when done — it bills while it exists.

## GPU training gotchas (verified 2026-09, an ONNX-export CRNN run)

A first GPU-training run over the relay (ship corpus + code up on a pytorch base image, train, ship
the model back — no public IP) hit these in order; each cost one pod cycle to find, none leaked:

- **Spot is gone.** `interruptible: true` → `500 "Spot pods are no longer offered"`. Use on-demand.
- **Pick the GPU from live availability, not memory.** Many types 500 or are out of stock; the
  wrong-priced one gets picked and then rejected by the cost cap. `runpodctl gpu list` gives the exact
  `gpuId` strings, `secureCloud`/`communityCloud`, on-demand price, and stock. Put several affordable
  available types in `gpuTypeIds` and drop any above your cap (e.g. an RTX 4090 at $0.74 secure), or
  the scheduler may pick the pricey one. Community cloud is often ~half the secure price.
- **Pin `numpy<2` on the pod.** `pip install onnx`/`tensorboard` pulls numpy 2.x, whose ABI break
  makes `torch.from_numpy` raise `RuntimeError: Numpy is not available` against an older baked torch
  (e.g. torch 2.1 in `runpod/pytorch:2.1.0-...`). Install `"numpy<2"` alongside the extras.
- **Keep the model ONNX-exportable.** Dynamic-output ops fail `torch.onnx.export`: an
  `AdaptiveAvgPool2d((1, None))` gives *"adaptive pooling, since output_size is not constant"*. Use a
  static equivalent (a mean/`ReduceMean` over the axis) so the graph traces.
- **Surface the create response when it fails.** A `--fail-with-body` curl puts the JSON error on
  stdout but `set -e` can abort before you print it; capture with `|| true` behind a debug flag so a
  500's message (like the spot one above) is visible instead of a bare `curl: (22)`.

Note item 1 above ("persist checkpoints, resume on restart") mattered *because of* spot reclaims; on
on-demand a pod isn't reclaimed, so for a short run the ephemeral disk + a final artifact push is
enough. Keep checkpointing for genuinely long runs where a crash is costly.

Training on spot is fine *because* it's checkpoint-resumable; if a job can't resume, use on-demand
(pricier, not reclaimed) or accept the restart cost.
