# Local dev ergonomics

Detail behind principle 17 in `SKILL.md`: a project should be observable, and bringing it up
locally should be one command that behaves predictably.

## Contents
- Bare `make` shows help
- The one-command entry point picks a free port

## Bare `make` shows help

A Makefile's first-defined target is what `make` with no arguments runs. If an unrelated
target like `preview` or `build` sits first, a no-argument `make` becomes an accidental
blocking action instead of a menu.

Fix: put a `help` target first (or set `.DEFAULT_GOAL := help`) that lists every other target
with a one-line description. The common pattern is to put `## description` after each target
and have `help` grep and print those lines. A bare `make` should always show what is
available and run nothing.

## The one-command entry point picks a free port

A hardcoded default port (`8080`, `3000`, ...) collides often on a personal machine running
several projects side by side. The fix is not remembering to pass a different `PORT=` each
time. Have the command bind-test and auto-increment to the next free port itself, and print
which port it landed on.

A pure-stdlib check (for example a `socket.bind` loop) avoids depending on `lsof` or `nc`
being installed.
