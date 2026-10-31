# Principles

The six ideas behind the loop in `SKILL.md`. Read the one that matches the decision in front
of you. They are adapted from the pstack skill collection (MIT, Lauren Tan).

## Contents
- Laziness protocol
- Subtract before you add
- Migrate callers, then delete the legacy API
- Outcome-oriented execution
- Minimize reader load
- Model the domain

## Laziness protocol

- **Consolidate decisions.** Don't repeat the same choice in several places. Put it behind one
  source of truth and pass the result along as a simple flag.
- **Minimize the diff.** Make the smallest change that solves the problem. Fewer lines beat
  elegant boilerplate.

Apply when you are about to add a layer, an abstraction, or a parameter threaded through
several functions.

## Subtract before you add

Remove complexity first, then build on the simpler base.

- Sequence removal before construction: dead code, redundant validators, stub references.
- Get to the minimum before you invest in polish.
- Design for observed usage, not speculative edge cases.
- No speculative validators, parsers or guards beyond what the requirement demands. This does
  not cover input from outside the program, which stays validated at the boundary.
- When a file or reference has nothing novel in it, delete it instead of leaving a stub.

Leave the design a little simpler and more capable than you found it.

## Migrate callers, then delete the legacy API

When you introduce a new internal API while old callers still exist, move the callers and
delete the old API in the same change. Don't keep a compatibility layer. Update tests to
assert the new contract, and delete tests that only protect pre-refactor implementation
details.

This applies when no external users depend on backward compatibility and the project can
absorb a coordinated breaking change. If external users do depend on it, deprecate with a
dated removal instead, and delete when the date passes.

## Outcome-oriented execution

Aim for the intended, verifiable end state rather than keeping every intermediate step stable.
Keeping each step fully working often creates temporary compatibility code that becomes
long-lived debt.

- Intermediate breakage is acceptable when it is planned, scoped and reversible.
- Say where temporary breakage is acceptable, and verify fully at the end.
- Use this for planned rewrites and migrations with clear phase boundaries, not for small
  routine changes.

## Minimize reader load

Maintainability depends on how much a reader must hold in their head. Two costs:

- **Layers to trace**: the indirections between a question and its answer.
- **State to hold**: hidden or mutable context.

Remedies:

- Collapse layers that don't pay for themselves: one-caller wrappers, adapters with no second
  implementation, speculative indirection. Inline them.
- Remove pass-through layers that repeat the same methods and arguments.
- Shrink state scope. Prefer pure functions, then locals, fields, module state, globals, in
  that order. Derive values instead of keeping them in sync.
- State invariants once, at the boundary, not in every consumer.
- A new layer or piece of state should reduce reader load elsewhere by at least as much as it
  adds.

The test: can a new reader answer "where does X come from?" and "what can change X?" in thirty
seconds? If not, cut layers or cut state.

## Model the domain

Put the real domain into a data structure instead of scattering its rules across conditionals.
A matching structure rules out invalid states and removes branches. Choosing it while writing
is far cheaper than refactoring later.

- A state machine in place of scattered booleans or lifecycle checks.
- A typed model in place of loose parameters or repeated shape assumptions.
- A map, registry, lookup table or discriminated union in place of branching across files.
- Organize modules around one body of domain knowledge. Execution order is not ownership.

Don't force an abstraction. Keep code plain when its shape is clear and unlikely to grow. Be
suspicious of indirection that removes no branch, no duplicated rule and no invalid state.

Warning signs: another branch added to an if/else chain, a second boolean kept in sync with the
first, modules split by phase (load, validate, transform, save) so the same rules repeat in
each.
