# RunPod REST API: creating pods precisely

Use the REST API when you need exact control over the pod spec — CPU flavor + vCPU count, GPU
type, ports, no persistent volume. The CLI's `pod create` is coarser. **This surface moves; verify
against the current REST reference.** As of writing, v1 is stable and v2 is beta.

## Base and auth (by reference)

```sh
API=https://rest.runpod.io/v1
```

Feed the key to `curl` via a **config file on stdin**, so it never appears in `argv`/`ps`/a URL:

```sh
rp_api() {   # $1=METHOD $2=PATH [$3=json body]
  local args=(--silent --show-error --fail-with-body -X "$1")
  [ -n "${3:-}" ] && args+=(-H 'content-type: application/json' --data-binary "$3")
  printf 'header = "Authorization: Bearer %s"\n' "$RUNPOD_API_KEY" \
    | curl "${args[@]}" -K - "${API}${2}"
}
```

## Create a CPU pod

The v1 CPU create schema is strict — a wrong body 400s or silently rents a GPU:

```json
{
  "name": "my-job",
  "imageName": "ghcr.io/you/your-job:tag",
  "computeType": "CPU",
  "cloudType": "SECURE",
  "interruptible": true,
  "cpuFlavorIds": ["cpu5m", "cpu3m"],
  "vcpuCount": 8,
  "containerDiskInGb": 20,
  "volumeInGb": 0,
  "ports": ["8000/tcp"],
  "dockerStartCmd": ["bash", "-lc", "<your dead-man's-switch + job here>"]
}
```

Field notes:
- **`computeType: "CPU"`** is required for a CPU pod.
- **`cloudType`** (`SECURE`/`COMMUNITY`) and **`interruptible`** (spot) are **separate** — cloud
  type is not the same axis as spot. `COMMUNITY` is cheaper and less predictable.
- **RAM comes from the flavor tier × `vcpuCount`**, not a RAM field. `cpuFlavorIds` is tried in
  order for availability. See `references/gpu-and-sizing.md` for the tiers.
- **`ports` is an array** of `"<port>/<tcp|http>"`. Omit or keep minimal if the job needs no
  inbound — a relay/`pod logs` job needs none.
- **`volumeInGb: 0`** avoids a persistent (billed) volume. Use one only to persist across pods.
- **`dockerStartCmd`** is where the dead-man's-switch is baked (`references/cost-safety.md`).

## Create a GPU pod

Swap the CPU fields for a GPU type; everything else (cost cap, dead-man's-switch, spot) is the same:

```json
{
  "name": "my-training",
  "imageName": "ghcr.io/you/train:tag",
  "computeType": "GPU",
  "cloudType": "SECURE",
  "interruptible": true,
  "gpuTypeIds": ["NVIDIA GeForce RTX 4090"],
  "gpuCount": 1,
  "containerDiskInGb": 40,
  "volumeInGb": 50,
  "ports": ["22/tcp"],
  "dockerStartCmd": ["bash", "-lc", "<dead-man's-switch + training>"]
}
```

- List valid GPU type ids with `runpodctl gpu list` (the exact string matters).
- Training usually wants a **network volume** for checkpoints (`volumeInGb` > 0, or an attached
  named volume) so a spot reclaim doesn't lose progress — see `references/gpu-and-sizing.md`.

## Read back and verify (catch a wrong pod for cents)

Create returns an id; immediately read the pod and **verify what you actually got** before trusting
it — the right flavor may be unavailable and you can be given something bigger/pricier:

```sh
info=$(rp_api GET "/pods/${id}")
ram=$(printf '%s' "$info"  | jq -r '.. | (.memoryInGb? // .memoryGb? // empty)' | head -1)
cost=$(printf '%s' "$info" | jq -r '.. | (.costPerHr? // empty)' | head -1)
# If ram < what you need, or cost > your cap: DELETE it now and abort. A wrong guess cost seconds.
```

Also resolve the pod's endpoint here if you exposed a tcp port: `publicIp` is empty until the pod
is running, and **on spot pods it is often never assigned** (`publicIp: ""`, `portMappings: null`)
— direct-TCP is machine-dependent. Do not build a flow that assumes a public IP; see
`references/data-transport.md`.
