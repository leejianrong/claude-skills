# HTTP-service pods: expose a port through the proxy and verify it

The rest of this skill is about **batch/artifact** jobs. This file covers the one
adjacent case that keeps coming up: standing up a **short-lived HTTP service** on a
pod, reaching it through RunPod's proxy, and **verifying** it — e.g. a smoke test
that an app's streaming/SSE survives RunPod's proxy (an "R2" check), or a quick
manual poke at a web UI.

This is **verification, not hosting.** A rented pod behind a Cloudflare-fronted
proxy with a ~100s cap is the wrong shape for a product request path (see the
main SKILL's "when not to"). Use it to *prove something works through the proxy*,
then terminate. Rule 0 (never leak a bill) applies unchanged — arm the
dead-man's-switch and trap teardown exactly as for a batch job.

## The proxy URL

Every exposed HTTP port is reachable at a stable, public, TLS URL — **no public IP
needed** (this is why it works on spot CPU pods where `publicIp` is often empty):

```
https://{podId}-{port}.proxy.runpod.net
```

- The port must be exposed at **create** time (you cannot add one to a running pod).
- The proxy is **Cloudflare-fronted with a ~100s idle cap** on a connection. A long
  poll or a quiet SSE stream is cut at ~100s. Anything long-lived must send bytes
  more often than that — e.g. an SSE heartbeat well under 100s — and/or resume on
  reconnect. (This cap is the whole point of an "R2" streaming smoke test.)
- First request after boot can 502 for a few seconds while the container's server
  binds; retry.

## Create a pod with an exposed HTTP port (REST)

`ports` is an array of `"<port>/<tcp|http>"`; use `http` for the proxy URL above.
A CPU pod is plenty for a web smoke test (no GPU). Full create-body field notes are
in `references/rest-api.md`; the HTTP-specific bit is just the `ports` entry:

```jsonc
{
  "cloudType": "SECURE",
  "computeType": "CPU",
  "vcpuCount": 2,
  "containerDiskInGb": 10,
  "imageName": "python:3.12-slim",
  "ports": ["8000/http"],            // -> https://{podId}-8000.proxy.runpod.net
  "dockerStartCmd": ["bash","-lc","<install + run your server on 0.0.0.0:8000>"]
}
```

Bind the server to **0.0.0.0** (not 127.0.0.1) or the proxy cannot reach it.

## Verify through the proxy (curl)

The proxy speaks ordinary HTTPS, so curl is enough to prove the path — you do not
need a browser to exercise the proxy's buffering, chunking, and idle cap:

```sh
BASE="https://${POD_ID}-8000.proxy.runpod.net"

# 1. Server is up through the proxy (retry past boot 502s):
until curl -fsS "$BASE/health" >/dev/null; do sleep 3; done

# 2. Stream an SSE endpoint and watch frames arrive incrementally (not one dump):
#    -N disables curl buffering; --max-time rides past the ~100s cap to prove the
#    heartbeat keeps the stream open.
curl -N --max-time 130 "$BASE/api/stream" &

# 3. Drive an event and see the stream react:
curl -fsS -X POST "$BASE/api/event" -H 'content-type: application/json' \
  -d '{"component":"n3","event":"input","payload":{"value":7}}'
```

What "pass" looks like for a streaming app (indah's R2, ADR-0002/0011): the SSE
frames arrive **incrementally**, a `ping`/heartbeat shows up during an idle gap,
the stream is still alive **past ~100s** (proving heartbeat beats the Cloudflare
cap), and an event posted mid-stream produces a patch frame.

## Teardown (unchanged from Rule 0)

Terminate the moment the check is done — a service pod bills the same as any other:

```sh
RUNPOD_API_KEY="$RUNPOD_API_KEY" runpodctl pod delete "$POD_ID"   # idempotent
RUNPOD_API_KEY="$RUNPOD_API_KEY" runpodctl pod list               # confirm it's gone
```

Prefer `scripts/rp` for the lifecycle so the dead-man's-switch and EXIT trap own
teardown even if your shell dies mid-check; this file only adds the port-exposure
and proxy-verification specifics on top of that.
