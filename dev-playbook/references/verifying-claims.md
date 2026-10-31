# Verifying claims before you report them

Two habits that stop an agent or a person from reporting something that isn't true: check
the real artifact, and check a performance number against seven questions before shipping it.

## Contents
- Check the real artifact
- Before reporting a performance number
- Reporting a result
- Re-verify before landing

## Check the real artifact

Indirect signals such as a successful build, a file timestamp, or an agent's own summary can
hide errors. Reading the source directly is cheaper than acting on a wrong assumption.

- Confirm that a process is running, read the actual value, and inspect the actual diff.
- If a check fails, suspect the way you observed the system before you suspect the system.
- A script that reruns the same comparison is stronger proof than a one-time look. Keep its
  output so a reviewer can rerun it.
- For a large migration, save the verification output in the repo so it can be audited later.

## Before reporting a performance number

Answer each question with evidence from a run:

1. **Why not double?** Profile in a separate run to find the bottleneck. If the load generator
   saturates first, you measured the generator. If a change didn't move the number, find the
   limiter that explains why.
2. **Was it tuned?** Run both sides under production-like conditions: release builds,
   production flags, matching versions and data, realistic caches and connection pools. A side
   left on defaults means you compared configurations, not implementations.
3. **Did it break limits?** Check the arithmetic against disk, network, CPU, and the time the
   changed piece takes. A result beyond a hard limit probably measured a cache, a no-op, or
   a bug.
4. **Did it error?** Count failures, non-success responses, and timeouts, and verify the
   outputs are correct. Fast failures look like speedups.
5. **Does it reproduce?** Run each side at least five times, alternating between them. Report
   the median and range. If the gap is smaller than the run-to-run variation, there is no
   measurable difference.
6. **Does it matter?** Measure the end-to-end path with realistic sizes and concurrency, and
   state the micro result as a share of the total. A part that takes 1% of a request can
   speed it up by at most 1%.
7. **Did it happen?** Confirm the work ran inside the timed region. Lazy code, unawaited
   promises, and timeouts produce numbers for work that never completed.

Before running, write the claim as you would ship it, read the measurement script to see what
it times, and check machine load (`uptime`, `nproc`). If the machine is busy and you can't stop
the load, alternate the sides so both see the same noise.

## Reporting a result

Lead with the verdict: faster, slower, no measurable difference, or inconclusive. Give the
number with its unit, the run count, the range, and the limiter. Call a result inconclusive if
you can't name the limiter, a side ran untuned, or you couldn't verify questions 4 and 7. In
a PR description, give one primary number and link to a file for the detail.

## Re-verify before landing

A green CI run is not proof the change is safe to land. Before merging, rerun the original
reproduction or the key behavior check yourself against the merged result, and look at the
actual diff once more. This matters most when several branches landed since you last looked.
