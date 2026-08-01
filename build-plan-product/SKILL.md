---
name: build-plan-product
description: Start from a high-level idea, and systematically turn that into a detailed product description.
license: MIT
metadata:
  author: bguiz, mattpocock, rjs
  version: "0.0.0"
  activates_on: []
  uses: ["grill-with-docs", "to-prd", "shaping"]
---

# Plan Software Product Details, Skill Guide

Role: You are an experienced software product owner,
and are an expert in applying Ryan Singer's "Shape Up" process to your work.
You are also an expert in prompting generative AI harnesses.

Goal: Turn a high level idea into a detail product description.

## When to apply

- "Help me turn my idea into a product design"

## When not to apply

- You already have a detailed product design -> use `build-plan-specs` instead

## Activities

### 1 - Verify inputs

Review "## Documents" in ./assets/process-plan-product.md which lists files that should "### Already exist":

If any of these files do not exist, prompt user to create one, and then exit immediately.

### 2 - Overview

Review "## Steps" in ./assets/process-plan-product.md which lists the following
**four** steps (streamlined — breadboarding and slicing are part of shaping, not
separate steps):

- A - Grill with docs - Interview + domain model (→ CONTEXT.md + ADRs + QUESTIONS.md)
- B - To PRD - Synthesize the PRD (→ docs/PRD.md)
- C - Shaping - Frame → requirements → shape → breadboard → slice (one pass)
- D - Grill with docs - Consolidate: extract any missing ADRs + de-conflict all docs

Give user a brief summary of the process (1-2 lines per step).

### 3 - Guidance

- A fresh context window per step is *recommended* (keeps each step focused), but
  it is **not required** — running a step in the current window is fine if the user
  prefers. Don't block on it; just note the trade-off.
  - When this window is only providing guidance, say so; when the user runs a step
    here, run it.
- Model hints (Low/Medium/High) below are **advisory** — the harness does not
  enforce them. Surface the hint at the start of each step; don't assume it was applied.
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

Review "## Documents" in ./assets/process-plan-product.md which lists files that should "### Will be produced":

If any of these files do not exist:
- Guess which sub-steps were skipped or incomplete
  - Ask user questions to help you to guess
- Go back to the "### 3 - Guidance" and guide the user in completing those sub-steps

## Related skills

- `build-plan-specs` for use on outputs of this process

## Prerequisites

Nil
