# Layered testing

The goal is a test suite you actually run. That means the checks you run constantly are fast
and need nothing installed, and the slow, high-fidelity checks are quarantined where their
cost is paid once, in CI.

## The layers

Sort tests into tiers by what they need to run:

- **Unit / fast layer — no external infra.** In-process. The web app runs through an
  in-memory test client; the database, auth, and network boundaries are swapped for fakes.
  Runs in seconds, so it can live in the pre-push hook and every CI job. This is where most
  of your tests belong.
- **Integration layer — real infra, self-provisioned.** A real database, a real message
  broker, spun up by the test run itself (see testcontainers below) so there's no
  hand-managed service to remember. Slower; CI and local-with-Docker only.
- **End-to-end layer — the whole stack, through the real interface.** A browser driving the
  real UI against a real backend, or a real client speaking the real wire protocol. Slowest
  and most valuable per test, so keep it a thin smoke layer over the critical journeys, not
  a mirror of the unit suite.

Keep the layers in separate directories or behind fixture markers so each runs alone. A
newcomer should be able to run the fast layer without installing anything.

## Build for testability: dependency-injection seams

The fast layer only stays infra-free if the code lets you replace its boundaries. Design for
that:

- **Inject the database session.** The app acquires its session through one function/provider;
  tests override that provider with a transaction that rolls back, or a fake. Don't let
  handlers construct their own connections.
- **Inject auth.** Resolve the caller's identity through an injected authenticator with a
  real implementation and a fake that returns known identities for known tokens. Tests use
  the fake and stay database-free.
- **Inject external clients.** Anything that leaves the process — an HTTP client, a queue, a
  socket — sits behind an interface with a real impl and an in-memory impl.
- **Provide a fake for your own protocol.** If your system has a wire protocol (WebSocket,
  gRPC, a custom framing), write one fake client that speaks it in-memory. It becomes the
  primary seam for driving the server in tests without real sockets.

The test for whether your seams are right: can a unit test exercise a handler end-to-end
without touching a network or a disk, and without monkeypatching internals? If it has to
reach into private state, the seam is missing, not the test.

## Integration tests with containerized infra

Use a library that starts real dependencies in throwaway containers for the test session
(the `testcontainers` family, or your ecosystem's equivalent). The suite starts a real
database, runs migrations, tests against it, and tears it down. No developer has to install
or seed a database by hand, and CI needs only Docker.

Run migrations as part of the fixture so the schema under test is the one you ship.

## End-to-end that boots its own stack

Let the e2e runner start the stack (a `webServer` config in Playwright, or a compose file the
suite brings up) and wait for health before the first test. The suite owns the lifecycle, so
`run e2e` is one command with nothing to start by hand.

Make e2e data self-cleaning and prefixed (`e2e-bot-*`) so runs don't collide and a failed run
doesn't poison the next. Keep the suite small: the journeys that would embarrass you if they
broke, not every field validation.

## Determinism: kill the races

Flaky tests are worse than no tests — they train everyone to ignore red. The usual culprits:

- **Wall-clock waits.** A test that sleeps and hopes a background loop finished by then. Drive
  the loop explicitly, or await a signal, instead of sleeping.
- **Short-lived state.** Polling for an event that appears and disappears faster than the poll
  interval on a slow runner. Widen the window deterministically (e.g. slow the producer in a
  test-only config), or await the state change rather than polling for a snapshot.
- **Shared mutable state across tests.** Prefixed, isolated data per test; restore any global
  you mutate in a `finally`.

When a test flakes, treat it as a bug in the test's determinism, not noise. Reproduce, then
remove the race — don't just bump the timeout and move on, though a justified timeout bump is
sometimes the honest fix. Prove stability by running the once-flaky test many times in a row.

## Every fix gets a test

A bug fix without a regression test is unfinished. Reproduce the bug in a failing test, watch
it fail, then fix it. The same applies to a flake: encode the determinism you added as an
assertion so the race can't return.

## Prove a guard by watching it fail

A test that passes says nothing about a compatibility promise or a safety check until you have
seen it go red: temporarily break the thing it protects, confirm the failure names the right
thing, then restore. "I added a test" is not evidence a regression cannot recur until you've
watched that test catch the regression once.

Do the mutation **non-destructively**. `git checkout -- <file>` and `git restore <file>`
overwrite the working tree from the **index**, silently discarding uncommitted changes to that
file — and unstaged work never entered the object database, so no reflog or `fsck` can bring it
back. Safe options, cheapest first: commit (or `git stash push -- <file>`) before mutating; edit
a copy; or apply the mutation as a patch and reverse exactly it with `git apply -R`.
