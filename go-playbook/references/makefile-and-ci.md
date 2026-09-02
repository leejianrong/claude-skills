# Copyable Makefile, linter config, CI, and hook

Everything here has been run. Adjust the module path, the binary names, and the platform
list, and it works as-is. A scaffold with two stub binaries and one test package passes
the whole `ci` target in under five seconds, which is the point: a gate people wait for is
a gate people keep.

## Contents
- Makefile
- .golangci.yml
- CI workflow
- Pre-push hook
- .gitignore
- Installing Go itself

## Makefile

Tabs, not spaces, for recipe lines.

```make
.DEFAULT_GOAL := help
SHELL := /bin/bash

MODULE    := github.com/you/yourapp
VERSION   ?= $(shell git describe --tags --always --dirty 2>/dev/null || echo dev)
LDFLAGS   := -s -w -X main.version=$(VERSION)
BIN       := bin
PLATFORMS := linux/amd64 linux/arm64 darwin/amd64 darwin/arm64 windows/amd64

.PHONY: help
help: ## List the targets
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

.PHONY: dev
dev: ## Download deps and install the dev tools
	go mod download
	go install github.com/golangci/golangci-lint/v2/cmd/golangci-lint@latest
	go install golang.org/x/tools/gopls@latest

.PHONY: fmt
fmt: ## Format in place
	gofmt -w .

.PHONY: fmtcheck
fmtcheck: ## Fail if any file is unformatted
	@out=$$(gofmt -l .); \
	if [ -n "$$out" ]; then echo "unformatted files:"; echo "$$out"; exit 1; fi

.PHONY: vet
vet: ## go vet
	go vet ./...

.PHONY: lint
lint: ## golangci-lint (staticcheck is one of its linters, not a separate tool)
	golangci-lint run

.PHONY: tidycheck
tidycheck: ## Fail if go.mod/go.sum are not tidy
	@cp go.mod go.mod.bak; [ -f go.sum ] && cp go.sum go.sum.bak || true; \
	go mod tidy; \
	status=0; \
	if ! diff -q go.mod go.mod.bak >/dev/null; then echo "go.mod is not tidy: run 'go mod tidy'"; status=1; fi; \
	if [ -f go.sum.bak ] && ! diff -q go.sum go.sum.bak >/dev/null; then echo "go.sum is not tidy"; status=1; fi; \
	mv go.mod.bak go.mod; [ -f go.sum.bak ] && mv go.sum.bak go.sum || true; \
	exit $$status

.PHONY: check
check: fmtcheck vet lint tidycheck ## All the cheap static gates

# -race: the class of bug that otherwise reproduces once a month.
# -count=1: Go caches results and a cached pass looks like a real one.
.PHONY: test
test: ## Fast tests, no infra: the inner loop
	go test -short -race -count=1 ./...

.PHONY: test-all
test-all: ## The full suite, as CI runs it
	go test -race -count=1 -tags=integration ./...

.PHONY: cover
cover: ## Fast tests with a coverage profile
	go test -short -race -count=1 -coverprofile=coverage.txt ./...
	@go tool cover -func=coverage.txt | tail -1

.PHONY: build
build: ## Build for this host
	mkdir -p $(BIN)
	go build -ldflags '$(LDFLAGS)' -o $(BIN)/yourapp ./cmd/yourapp

.PHONY: xbuild
xbuild: ## Cross-compile every target: proves the pure-Go promise
	@set -e; for p in $(PLATFORMS); do \
	  os=$${p%/*}; arch=$${p#*/}; ext=""; \
	  [ "$$os" = "windows" ] && ext=".exe"; \
	  echo "  $$os/$$arch"; \
	  CGO_ENABLED=0 GOOS=$$os GOARCH=$$arch \
	    go build -ldflags '$(LDFLAGS)' -o $(BIN)/$$os-$$arch/yourapp$$ext ./cmd/yourapp; \
	done

.PHONY: run
run: build ## Build and run
	$(BIN)/yourapp

.PHONY: secrets
secrets: ## gitleaks over history and the tree
	gitleaks detect --redact --verbose
	gitleaks dir . --redact --verbose

.PHONY: vuln
vuln: ## govulncheck
	go run golang.org/x/vuln/cmd/govulncheck@latest ./...

.PHONY: ci
ci: check test-all xbuild ## Everything CI gates on

.PHONY: install-hooks
install-hooks: ## Install the pre-push hook
	./scripts/install-hooks.sh

.PHONY: clean
clean:
	rm -rf $(BIN) coverage.txt
```

Two notes. `VERSION` uses `git describe`, so any CI job running a target that needs it
also needs `fetch-depth: 0`. And keep money-spending or long-running targets out of `ci`
and out of the hook, documented but not wired up.

## .golangci.yml

This is the **v2** schema. A v1 config does not fail with a helpful message, so validate
by running `golangci-lint run`, not by reading the file.

```yaml
version: "2"

linters:
  default: standard        # errcheck, govet, ineffassign, staticcheck, unused
  enable:
    - bodyclose            # a leaked HTTP response body is a real leak
    - errorlint            # errors.Is/As over == and bare type asserts
    - copyloopvar          # flags copies made redundant by Go 1.22 loop vars
    - misspell
    - nilerr
    - revive
    - unconvert
    - usestdlibvars
    - wastedassign
  settings:
    revive:
      rules:
        - name: exported
          disabled: true   # doc comments are review's job, not a linter's
  exclusions:
    generated: lax
    rules:
      - path: _test\.go
        linters: [errcheck]

formatters:
  enable:
    - gofmt
```

Start near the standard set and add linters when one would have caught a real bug. A
config that enables everything gets disabled wholesale the first time it blocks a release.

## CI workflow

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  check:
    name: Static gates
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-go@v6
        with:
          go-version-file: go.mod    # single source of truth for the version
          cache: true
      - run: make fmtcheck
      - run: make vet
      - run: make tidycheck
      - uses: golangci/golangci-lint-action@v9
        with:
          version: v2.12.2           # pin it; a floating lint version breaks unrelated PRs

  test:
    name: Fast tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-go@v6
        with: { go-version-file: go.mod, cache: true }
      - run: make test

  test-all:
    name: Full suite
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-go@v6
        with: { go-version-file: go.mod, cache: true }
      # Only if your fixtures shell out to git, which needs an identity to commit.
      - name: Configure git for fixtures
        run: |
          git config --global user.email ci@example.com
          git config --global user.name  CI
          git config --global init.defaultBranch main
      - run: make test-all

  xbuild:
    name: Cross-compile
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0             # VERSION uses git describe
      - uses: actions/setup-go@v6
        with: { go-version-file: go.mod, cache: true }
      - run: make xbuild

  secrets:
    name: Secret scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0             # scans history as well as the tree
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"

  vuln:
    name: Vulnerability scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: golang/govulncheck-action@v1
        with:
          go-version-file: go.mod
```

**Do not add a job that is red until some future PR lands.** A check that is always
failing teaches everyone to ignore CI, which costs more than the missing coverage.
Comment the job out with a note naming the PR that should enable it.

## Pre-push hook

`scripts/pre-push`:

```bash
#!/usr/bin/env bash
# Mirrors the cheap CI jobs so a push rarely lands red. Deliberately excludes
# anything slow or anything that spends money.
# Escape hatch: git push --no-verify
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

start=$(date +%s)
echo "pre-push: cheap gates"

make check
make test

# An optional tool missing must not block a push; a leaked key must not land.
# CI runs this unconditionally.
if command -v gitleaks >/dev/null 2>&1; then
  make secrets
else
  echo "pre-push: gitleaks not on PATH, skipping (CI still runs it)"
fi

echo "pre-push: passed in $(( $(date +%s) - start ))s"
```

`scripts/install-hooks.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
hooks="$(git rev-parse --git-path hooks)"
install -m 0755 "$root/scripts/pre-push" "$hooks/pre-push"
echo "installed: $hooks/pre-push"
echo "bypass with: git push --no-verify"
```

`git rev-parse --git-path hooks` rather than a hardcoded `.git/hooks`, so it works inside
a worktree where `.git` is a file.

## .gitignore

```gitignore
# Build output.
# These MUST keep the leading slash: a bare `yourapp` pattern matches any path
# component with that name, which silently ignores cmd/yourapp/ and its source.
/bin/
/dist/
/yourapp

# Go
*.test
*.out
coverage.txt

# Editors / OS
.DS_Store
.idea/
.vscode/
```

Verify both directions after writing it, because the failure is silent:

```bash
git status --short                      # is cmd/ listed?
git check-ignore -v yourapp bin/yourapp # are the binaries ignored?
```

## Installing Go itself

Distribution packages lag badly (Ubuntu 22.04 ships a Go several years old), so take the
official tarball and verify it. Installing under `~/.local` needs no root:

```bash
VER=go1.26.5; TARBALL=$VER.linux-amd64.tar.gz
WANT=$(curl -s 'https://go.dev/dl/?mode=json&include=all' \
  | python3 -c "import json,sys;print([f['sha256'] for r in json.load(sys.stdin) for f in r.get('files',[]) if f['filename']=='$TARBALL'][0])")
curl -sLO "https://go.dev/dl/$TARBALL"
echo "$WANT  $TARBALL" | sha256sum -c -   # stop here if this fails
rm -rf ~/.local/go && tar -C ~/.local -xzf "$TARBALL"
export PATH="$HOME/.local/go/bin:$HOME/go/bin:$PATH"   # add to ~/.bashrc
```

`~/go/bin` is where `go install` puts things, so both directories belong on `PATH`.
`https://go.dev/VERSION?m=text` gives the current stable version if you want to fetch it
rather than pin it.
