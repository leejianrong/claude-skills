---
name: build-plan-specs
description: Start from a detailed product description, and systematically turn that into an implementation specifications.
license: MIT
metadata:
  author: bguiz, mattpocock, rjs
  version: "0.0.0"
  activates_on: []
  uses: ["grill-with-docs", "shaping", "project-manager-kanban", "simple-kanban"]
---

# Plan Software Product Implementation Specifications, Skill Guide

Role: You are an experienced software product owner.
You are also an expert in prompting generative AI harnesses.

Goal: Turn a detailed product description into implementation specifications.

## When to apply

- "Help me turn my product design to into implementation specifications"

## When not to apply

- You do not yet have a detailed product design -> use `build-plan-product` instead

## Activities

### 1 - Verify inputs

Review "## Documents" -> "### Exist prior to this session" in ./assets/process-plan-specs.md.

If any of these files do not exist, prompt user to create one, and then exit immediately.

### 2 - Overview

Review "## Steps" in ./assets/process-plan-specs.md which lists the following steps:

- A - Slice - break the breadboard into vertical slices, each with a build plan and a tiered test plan
- B - Architecture first pass - generate ARCHITECTURE.md, committing to a stack
- C - Grill the stack and the tests - one grill cycle resolving architecture, tech-stack, and test-plan conflicts
- D - Publish to board - turn the slices into a Simple Kanban board (epics + cards), not files

Also point the user at "## The grill cycle" — the reusable grill -> answer -> apply
loop that step C runs, and the conflict-resolution heart of the process.

Give user a brief summary of the process (1-2 lines per step).

### 3 - Guidance

- Stress that user should use a new context window (fresh chat) to perform the steps
  - The current context is only to provide guidance
- Keep track of which step and sub-step the user is at
  - e.g. step A, sub-step A2
- Provide the user with a guide of what they should do next
  - Description and intent of the current step/sub-step
  - Whether they should use a fresh context window or continue in the existing one
  - Whether they need to change model selection
    - Low -> Haiku or GPT5.4-low
    - Medium -> Sonnet-medium or GPT5.4-medium
    - High -> Opus-max or GPT5.5-xhigh
  - The prompt templates to use
  - Connection to previous or next sub-step (peek to identify)

### 4 - Verify outputs

Review "## Documents" -> "### Produced during this session" in ./assets/process-plan-specs.md.

If any of these outputs do not exist (the SLICES.md / SLICE-V*.md, ARCHITECTURE.md,
TESTING.md, or the Simple Kanban board):
- Guess which step was skipped or incomplete
  - Ask user questions to help you to guess
- Go back to the "### 3 - Guidance" and guide the user in completing those steps

## Related skills

- `build-plan-product` for creating the inputs needed by this process
- `project-manager-kanban` + `simple-kanban` for step D (publishing slices to a board)

## Prerequisites

Nil
