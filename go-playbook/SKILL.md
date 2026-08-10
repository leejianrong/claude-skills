---
name: go-playbook
description: Go-specific engineering practices that the language-agnostic dev-playbook leaves as "translate to your stack". Covers the gates that only exist in Go (-race, -count=1 against test caching, gofmt as a hard failure, cross-compile as a gate, go mod tidy drift), test layering with build tags rather than directories, interface seams and the accept-interfaces rule, the CGo versus single-binary trade-off, enforcing architectural boundaries with internal/ plus a go/parser import test, error wrapping and context discipline, and the traps that cost real hours. Use when standing up a Go project or repo; writing a Makefile, .golangci.yml, or CI workflow for Go; structuring or layering Go tests; auditing a Go repo's gates; deciding whether a dependency is worth CGo; or debugging why a Go build, test cache, or .gitignore is behaving strangely. Read alongside dev-playbook, which owns the shape; this owns the Go specifics.
---

# Go playbook

`dev-playbook` decides the shape: layer checks by cost, gate by layer, never let a slow
check block a local push. It also says "adapt every specific to the stack in front of
you." This is that adaptation for Go, plus the handful of gates that have no equivalent
in other languages and so go unmentioned.

Read `dev-playbook` first. Where the two disagree on a principle, it wins. Where it
gives a command, this one gives the Go form.

## What translates, and how

| dev-playbook says | In Go |
| --- | --- |
| Separate test directories by cost | Build tags (`//go:build integration`) or `testing.Short()`. Go keeps `_test.go` next to the code it tests, so a `tests/` tree fights the language. |
| Lockfile committed, frozen installs | `go.sum` is the lockfile and is always committed. `-mod=readonly` has been the default since 1.16, so there is nothing to freeze. Add a tidy-drift check instead. |
| Dependency caching in CI | `actions/setup-go` with `cache: true` handles module and build cache. One line. |
| Vulnerability scan | `govulncheck`, which knows about Go's symbol-level reachability and reports far fewer false positives than a generic scanner. |
| Type-check step | The compiler. `go build ./...` and `go vet ./...` cover it; there is no separate type-checker to run. |
| Containerized integration deps | Still testcontainers if you need a real database. If your "infra" is temp directories, files, or git repos, `t.TempDir()` and a fixture helper are faster and need no daemon. |
| Deploy the validated SHA | For a CLI or library there is no deploy, there is a release: cross-compiled binaries attached to a tag, gated on green CI. |
| One-command dev loop | `make run`. |

## Gates that only exist in Go

These five have no counterpart in a Python or TypeScript playbook, which is exactly why
they get skipped.

**`-race` on every test run.** The race detector is cheap enough to leave on always
(roughly 2 to 10 times slower, on a fast suite that is still seconds) and it catches the
class of bug that otherwise reproduces once a month in production. One honest caveat: it
only reports races that actually happen during the run, so it is only as good as your
concurrent test coverage. It is not a static analysis.

**`-count=1` to defeat the test cache.** Go caches successful test results keyed on the
inputs it can see, and a cached pass prints `(cached)` but is otherwise indistinguishable
from a real run. This is a genuine gift for local iteration and a genuine hazard in a
gate, because a test whose behaviour depends on something Go cannot see (an environment
variable, a file outside the module, the clock) will happily serve you a stale green.
Put `-count=1` in every Makefile target and forget about it.

**`gofmt -l` as a hard failure.** Formatting in Go is settled, not a preference, so a
formatting gate costs no arguments. Fail the build on any file `gofmt -l` names.
`golangci-lint` can also run it as a formatter, but a bare `gofmt -l` in the Makefile has
no version skew and no config.

**Cross-compilation as a gate, not a release step.** `GOOS=windows go build` catches
platform-specific code the moment it lands, and platform-specific code is exactly what
you write without noticing: `syscall`, `flock`, process groups, path separators, signal
handling. Build every target you claim to support on every CI run. It costs seconds when
the code is pure Go, and if it starts costing minutes that is information too.

**`go mod tidy` drift.** An untidy `go.mod` means someone's local resolution differs from
CI's. Check it by copying the files aside, running tidy, diffing, and restoring:

```make
tidycheck:
	@cp go.mod go.mod.bak; [ -f go.sum ] && cp go.sum go.sum.bak || true; \
	go mod tidy; status=0; \
	diff -q go.mod go.mod.bak >/dev/null || { echo "go.mod not tidy"; status=1; }; \
	[ -f go.sum.bak ] && { diff -q go.sum go.sum.bak >/dev/null || { echo "go.sum not tidy"; status=1; }; }; \
	mv go.mod.bak go.mod; [ -f go.sum.bak ] && mv go.sum.bak go.sum || true; \
	exit $$status
```

## Test layering with build tags

`dev-playbook` wants a fast no-infra layer and a heavier one, each runnable alone. Go's
convention puts test files beside the code, so the split is by tag rather than by
directory:

```go
//go:build integration

package store_test
```

Then `go test -short ./...` is the fast layer and `go test -tags=integration ./...` is
everything. Use `testing.Short()` inside a test for the cases where one test has a slow
variant, and the tag for whole files that need infra.

Two things worth knowing. `go test ./...` compiles every package, so a build error
anywhere fails the run even in a package with no tests: that is free coverage of "does it
still build." And a tagged-out file is invisible to the compiler, so a rename that misses
it fails only when someone runs with the tag. Run the tagged build in CI on every push,
not nightly.

On package naming: `package foo` for tests that need internals, `package foo_test` for
tests that must go through the public surface. Prefer the external form. It stops a test
reaching past the seam and quietly documenting a private detail as behaviour.

## Seams, and the interfaces that make them

Go is the best mainstream language for the injection seams `dev-playbook` asks for,
because interfaces are structural and defined by the consumer. The rules that keep this
from turning into a maze of indirection:

**Accept interfaces, return structs.** A constructor returns `*Client`, and the function
that uses it takes the one-method interface it actually needs.

**Define the interface where it is consumed, not where it is implemented.** The package
that needs a `Journal` declares `type Journal interface { Append(Event) error }`. The
package that implements it declares nothing and imports nothing. This is the opposite of
the Java habit and it is what keeps the dependency arrow pointing one way.

**Keep them tiny.** One or two methods. A five-method interface is usually two seams
wearing one coat, and it forces every fake to implement methods the test does not care
about.

**Inject the clock and the randomness, always.** `time.Now()` and `math/rand` inside a
function are untestable by construction. Take a `func() time.Time` or a small `Clock`
interface, and a `*rand.Rand`. Retry with jittered backoff is the canonical case: with
both injected the test asserts exact delays, and without them it sleeps and hopes.

## Determinism

`dev-playbook` says a test that passes on re-run with no code change is a race, not luck.
The Go specifics:

- Never `time.Sleep` to wait for something. Use a channel, a `sync.WaitGroup`, or
  `context` with a deadline. If you truly must poll, poll with a generous timeout and say
  in a comment what you are waiting for.
- `t.Parallel()` is worth using, but a test that calls `t.Setenv` cannot be parallel and
  the runtime will tell you so. Subtests that share a loop variable are safe from Go 1.22
  onward, since loop variables are now per-iteration. The `copyloopvar` linter flags the
  defensive copies that are now redundant.
- `t.TempDir()` and `t.Cleanup()` over manual teardown. Both run on failure paths, which
  a `defer` in the test body does too but a helper's `defer` does not.
- Golden files for anything that produces text (CLI output, generated code, rendered
  diffs). Compare against a file under `testdata/` and add an `-update` flag that
  rewrites them. Review the diff when it changes, which is the whole point.

## CGo and the single-binary promise

Pure Go gives you `GOOS`/`GOARCH` cross-compilation from one machine, a static binary
with no libc dependency, `go install` working for anyone with a Go toolchain, and build
times measured in seconds. One CGo dependency costs all four.

Be precise about the cost, because it is often overstated. CGo does not stop you shipping
prebuilt binaries: you cross-compile with a C toolchain (zig cc is the least painful) or
build on a runner per platform, which plenty of projects do. What it actually costs is
cross-compilation without that toolchain, `go install` for users without a C compiler,
static linking without extra work (musl, or accept dynamic libc), and a real jump in
build time.

So the question is never "is CGo bad," it is "is this dependency worth those four
things." tree-sitter for multi-language parsing is the common case worth thinking hard
about, and the usual answer is to shell out to a binary instead of linking a library.
Shelling out to `git`, `gofmt`, or a language's own syntax checker keeps the dependency
surface at zero and degrades gracefully when the tool is missing. Do that first, and
reach for CGo when you have a reason you can write down.

If you do take a CGo dependency, put `CGO_ENABLED=0` in the cross-compile target anyway
for the packages that do not need it, so the boundary is visible.

## Enforcing architectural boundaries

`internal/` is the only compiler-enforced boundary Go gives you, and it is a good one:
nothing outside the module can import `internal/...`, no configuration required. Use it
for everything that is not deliberately public API.

What it does not do is constrain imports *within* the module, so "the CLI must go through
the engine's interface" is unenforced by default. A small test using `go/parser` closes
that gap and costs about forty lines:

```go
// Walk cmd/, parse imports only, and fail on any internal import
// outside the allowed set.
f, err := parser.ParseFile(token.NewFileSet(), path, nil, parser.ImportsOnly)
```

`parser.ImportsOnly` means the code does not need to compile for the check to run, so the
test still reports the violation cleanly rather than dying on a build error. Make the
failure message name the file, the offending import, the allowed set, and the ADR or doc
that decided it. A guard whose message does not explain itself gets deleted by whoever
hits it at 2am.

Then break it on purpose and watch it fail, per `dev-playbook`. Add a file that violates
the rule, confirm the message is right, delete the file. Since it is a new file, nothing
uncommitted is at risk.

## Errors and context

- Wrap with `%w` and read with `errors.Is` / `errors.As`. Comparing errors with `==`
  works right up until someone adds a wrap, and then it silently stops working. The
  `errorlint` linter catches this and is worth enabling on day one.
- `errors.Join` for the genuinely-multiple case (cleanup that partially failed).
- Error strings are lowercase and unpunctuated, because they get wrapped into longer
  sentences.
- `context.Context` is the first parameter, threaded explicitly, never stored in a
  struct. Anything that blocks takes one: HTTP calls, subprocesses, channel waits.
  Anything that spawns a goroutine gets a way to cancel it.
- Kill subprocesses by process group, not by PID, or you leave orphans. On Unix that
  means `SysProcAttr: &syscall.SysProcAttr{Setpgid: true}` and signalling the negative
  PID. It is platform-specific, which is one more reason the cross-compile gate matters.

## Dependency hygiene

Go's standard library is unusually complete, so "add a dependency" deserves more
resistance here than in most ecosystems. HTTP, JSON, templating, testing, crypto,
compression, and a decent CLI parser are all in the box. The `structured logging` case is
`log/slog` since 1.21.

- Commit `go.sum`. Run `govulncheck` in CI.
- Prefer `golang.org/x/...` over a third party when both exist: same release discipline
  as the standard library.
- Vendor only if your build must work with no network. Otherwise the module cache does
  the job and `vendor/` just makes diffs unreadable.
- Dependabot handles Go modules natively. Group patch updates so the noise stays low.

## Traps that cost real hours

Each of these has burned someone recently.

**`.gitignore` patterns without a leading slash match any path component.** A `.gitignore`
containing `myapp` (meant for the built binary at the repo root) also ignores
`cmd/myapp/`, taking your `main.go` with it. The symptom is a directory missing from
`git status` and a first commit that will not build. Anchor build artefacts:
`/myapp`, not `myapp`.

**A stale module path after an org rename.** `go install` fails with "module declares its
path as X but was required as Y" and the fix is to use the path in the module's own
`go.mod`, which may not match its current GitHub URL. gitleaks is the current example: it
lives at `github.com/gitleaks/gitleaks` but declares `github.com/zricethezav/gitleaks/v8`.

**`staticcheck` is already inside `golangci-lint`.** Installing and running both wastes
time and produces duplicate findings. Check `golangci-lint help linters` before adding any
standalone tool.

**`golangci-lint` v2 changed the config schema.** `version: "2"` at the top,
`linters.default` replacing the old enable-all-and-disable dance, and a separate
`formatters` block. A v1 config does not error helpfully. Validate by running it, not by
reading it.

**Writing to a nil map panics; reading from one does not.** A zero-value struct field of
map type is a landmine that only goes off on the write path, which is often the path with
less test coverage.

**`defer` in a loop runs at function exit, not iteration exit.** Ten thousand iterations,
ten thousand open files. Put the body in its own function or close explicitly.

**`err` shadowed inside an `if` block.** `if x, err := f(); err != nil` declares a new
`err`, so an outer assignment you expected never happens. `govet`'s shadow check is off by
default; the pattern is common enough to watch for by eye.

## Standing up a Go repo

In order. Each step is useful alone.

1. `go mod init`, then set the Go version in `go.mod` and point CI at it with
   `go-version-file: go.mod` so they cannot drift.
2. `Makefile` with `fmtcheck`, `vet`, `lint`, `tidycheck`, `check`, `test`, `test-all`,
   `build`, `xbuild`, `ci`. Make `help` the default goal.
3. `.golangci.yml`, validated by running it.
4. Pre-push hook running `make check && make test`, with the install documented and
   `--no-verify` named as the escape hatch.
5. CI with parallel jobs: static gates, fast tests, full suite, cross-compile, secret
   scan, `govulncheck`. Cancel in-progress runs on the same ref.
6. `internal/` for everything not deliberately public, plus the import-hygiene test if
   there is a boundary worth naming.
7. `CLAUDE.md` stating build status honestly and listing the exact `make` targets.
8. `.gitignore` with build artefacts **anchored**.

A copyable Makefile, `.golangci.yml`, and CI workflow are in
[`references/makefile-and-ci.md`](references/makefile-and-ci.md).

## Auditing a Go repo

Every "no" is a gap, roughly in priority order.

- Does `make` (or the documented command) exist, and does `help` list the targets?
- Is `-race` on in CI? Is `-count=1` on every gate?
- Is `gofmt -l` a hard failure?
- Does CI cross-compile every claimed platform?
- Is `go.sum` committed, and is tidiness checked?
- Are the fast tests runnable with no infra, and separated by tag from the slow ones?
- Are the clock and randomness injected anywhere retry, timeout, or backoff logic exists?
- Is `govulncheck` running?
- Are errors wrapped with `%w` and compared with `errors.Is`? Is `errorlint` enabled?
- Does every blocking call take a `context.Context`?
- Are build artefacts anchored in `.gitignore`?
- If there is a stated architectural boundary, is anything actually enforcing it?
