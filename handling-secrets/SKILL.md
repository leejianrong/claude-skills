---
name: handling-secrets
description: >-
  Prevent API keys, tokens, passwords, and other credentials from leaking into chat
  transcripts, logs, git history, or files -- both when sending a secret (never inline in a
  command, URL, or printed body) and when receiving one back (many APIs echo the request,
  including secret fields, straight into their response). Use whenever a task touches an API
  key, token, password, PAT, or other credential: building an authenticated curl/API call,
  reading a .env or config file, constructing a request body with a secret field, or
  displaying/printing any command or API output that might contain one. Also use immediately
  if a secret is accidentally exposed, to contain and disclose it correctly.
---

# Handling secrets

Two leak directions matter, and most guidance only covers the first:

1. **Sending** -- a credential going INTO a command, URL, or request body.
2. **Receiving back** -- a credential coming OUT of a response, log, or error message, often
   because the API you sent it to echoed it straight back.

Both need a hard rule, applied every time, not just when a leak seems likely.

## Sending: never inline, always by reference

- Never type or paste a literal credential into a command you write, a URL, or anything
  you're about to print. Read it from the environment or a gitignored file and pass it **by
  reference**, so the value is resolved by the shell/tool and never appears in what you write:
  ```sh
  export TOKEN=$(jq -r '.token' config.json)   # value never printed, just piped through
  ```
- `curl`: auth goes in a config file fed on **stdin** (`-K -`), never in argv or a URL --
  argv lands in `ps`/shell history, URLs land in access logs:
  ```sh
  printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | curl -K - https://api.example.com/...
  ```
- A JSON body containing a secret field: build it in a script that writes straight to a file
  (never print the constructed body), then send with `curl --data-binary @file`.
- **Exception, not a loophole:** some platforms require a secret to travel as a literal value
  into a resource you're creating -- e.g. an API key injected as a container's environment
  variable so a job running on that container can call back. That's fine; the secret has to
  go there. The rule is about never typing/echoing it into *your own* terminal or transcript,
  not about the secret never existing anywhere at all.

## Receiving: redact before you look

The overlooked half. Many create/update APIs **echo the full request back in the response**
-- including whatever secret field you just sent. Printing "the response" without checking
what's in it re-exposes exactly what you were just careful about sending.

- Before displaying *any* tool or API response, assume it might contain a field you (or the
  request) just sent as a secret: a request body, a config block, an `env` map, an
  `Authorization` header reflected in an error message.
- Redact known-sensitive keys before printing -- every time, not only when a leak seems
  likely. Pipe the response through `scripts/redact_secrets.py` (run it, don't re-derive its
  logic inline):
  ```sh
  curl ... | python3 ~/.claude/skills/handling-secrets/scripts/redact_secrets.py
  ```
  It walks the JSON recursively and replaces the value of any key whose name contains `key`,
  `token`, `secret`, `password`, `auth`, `credential`, or `cookie` (case-insensitive) with
  `[REDACTED]` -- add more with `--extra name1 name2`. Everything else stays visible, so
  non-secret context (IDs, image names, timeouts) is still there to debug with.
- The same logic applies to logs: a verbose HTTP client, a stack trace, or a CI log can print
  request headers/bodies. Redact before saving or displaying, or configure the tool not to
  log bodies at all.
- When genuinely unsure whether a field is sensitive, redact it. Under-redacting once costs a
  real leak; over-redacting once costs a re-run of one command.

## Cleanup

- Delete any local file that held a plaintext secret (request bodies, curl config files,
  saved responses) as soon as you're done with it -- don't leave them sitting in a scratch
  directory after the task moves on.
- Prefer files/env over inline literals specifically so there's nothing sensitive left in
  shell history to clean up afterward.

## If a leak happens anyway

Contain, disclose, rotate -- in that order, immediately, in the same turn you notice it:

1. **Contain.** Reverse anything the leaked credential could still be used for right now --
   e.g. tear down a cloud resource it authenticated -- before doing anything else.
2. **Disclose.** Tell the person plainly what leaked, how, and where (which message or tool
   output). Lead with it; don't bury it in a longer update or downplay it.
3. **Rotate.** The credential is compromised the moment it's in a transcript, log, or file
   outside your control, even after you delete your own copy. Recommend the owner revoke and
   reissue it -- deleting your local copy is cleanup, not remediation.
4. **Fix the mechanism, not just the instance.** If a response echoed a secret back, redact
   that endpoint's response shape for every future call, not just retroactively for this one.

## Real example

A cloud provider's pod-create API required `KAGGLE_KEY` and `RUNPOD_API_KEY` in the request
body's `env` field -- correctly, since the pod needed them at runtime to authenticate its own
teardown call. The input side followed the rules above: both values were sourced from a
gitignored `.env` file by reference, never typed literally. But the create endpoint's
response echoed the entire request back, `env` block included, and piping that response
through a JSON pretty-printer for display put both plaintext credentials into the
conversation transcript. The fix wasn't "be more careful that one time" -- it was adding
`redact_secrets.py` to this workflow permanently, so every future response from that endpoint
(and any other) gets filtered before anyone looks at it, regardless of whether that specific
call seems risky.
