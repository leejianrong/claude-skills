---
name: explainer-artifacts
description: Build explainer artifacts that teach or support a decision — technical concepts, architecture, data flows, tradeoffs, audits, comparisons — where the job is comprehension, not aesthetics vetting. Lead with diagrams (workflow, swimlane, timeline, matrix, pipeline, fan-out, A-vs-B), keep prose as support. Use when the user asks for an artifact to help them understand or decide something, or asks for "more diagrams / visuals / workflow / swimlane diagrams" in an artifact. Composes on top of artifact-design + frontend-design + natural-writing.
---

# Explainer artifacts

Jian builds essentially two kinds of artifact: ones for vetting UI and aesthetics,
and **explainers** whose only job is to make something understood or decidable. This
skill is for the second kind. The default design instinct optimises for visual
identity; an explainer optimises for comprehension, and the two pull in different
directions. Here the diagram is the content and the prose is the caption, not the
other way round.

Apply this on top of `artifact-design` (the built-in, which frames things around
visual identity) and the usual companions `frontend-design` and `natural-writing`.
When they conflict, comprehension wins: a plainer page that lands the idea beats a
striking one that doesn't.

## The one rule

**Lead with a diagram, keep prose as support.** For every key idea, ask what picture
makes it obvious, draw that first, then let a sentence or two underneath do the
explaining. If a section is all text, it's a candidate for a diagram or it's cut.
Text-heavy explainers are the failure mode this skill exists to prevent.

## Match the diagram to the idea

Pick the form from what the idea actually is, not from habit:

- **Workflow / flow** — a sequence of steps or a data path. Boxes and arrows.
- **Swimlane** — anything with concurrent actors, threads, or timing. Label lanes on
  the left, time flows right. Reach for this whenever two things happen at once (a
  worker vs an API thread, an event vs a timeout, client vs server).
- **Timeline** — an ordered sequence of events or states, especially when a specific
  transition or gap is the point. Pills on a line, with the meaningful ones highlighted.
- **Matrix** — coverage or capability across two dimensions (feature × slice, tool ×
  case). Ticks and dashes read at a glance.
- **Pipeline** — a value transformed through stages, especially with a branch/merge
  (a size gate, a redactor). Shows where each stage sits in the order.
- **Fan-out** — one thing spawning many (parallel map, retries, children), useful for
  showing partial states: some done, some failed, some re-running.
- **A-vs-B split** — for a decision, put the options side by side in one figure so the
  contrast is visible before any prose. Mark the recommended one; mark the cost on the
  other. This is the highest-value form for decision-support artifacts.

## Build the diagrams so they hold up

- **Hand-author in the page's own palette using HTML/CSS (or inline SVG), not generic
  mermaid.** A themed diagram in the artifact's own tokens reads as one designed system;
  a mermaid render reads as bolted on and won't follow light/dark.
- **Prefer a small reusable CSS diagram kit over bespoke SVG coordinates.** Nodes as
  bordered boxes, connectors as chevrons or thin rules, lanes as CSS grid, matrices as
  grid. It reflows on mobile and can't develop coordinate-overlap bugs. Use inline SVG
  only where a true branch/merge arrow genuinely needs it.
- **Theme both light and dark** through the same tokens as the rest of the page.
- **Keep every diagram legible small.** Short labels, few elements. If a diagram needs a
  paragraph to decode, it's too busy; split it.

## A shared visual language

Define the encoding once, near the top, and hold it across every diagram:

- An **accent** colour for the highlighted / recommended / "this is the path" element.
- A **dashed warning** style for the cost, the risk, or the rejected path.
- **State dots** where things have status (done, failed, in-progress, re-running).

State the legend explicitly on the page. Consistency is what lets the reader stop
decoding and start understanding. Semantic status colour (good / bad) is separate from
the page accent.

## Prose, trimmed

Follow `natural-writing`: sentence-case headings, no throat-clearing, take a position.
In an explainer specifically:

- One or two sentences per idea, sitting under its diagram. Not a wall.
- Name the tension or the takeaway in the first clause; the diagram already carried the
  structure.
- For decisions, always relate the choice back to the product goal, briefly. The reader
  is deciding, and "how does this serve the thing we're building" is the deciding question.
- Cut anything the diagram already says.

## Make a decision brief operable

When the explainer supports a decision (not just teaches), treat it as a tool:

- Summary and stakes up front; group by theme; encode priority as a chip.
- Each decision: the tension, the A-vs-B diagram, the options with what you gain and
  what it costs, and the recommendation with a one-line why.
- Light interactivity that serves the work, not decoration: a filter to focus on the
  high-stakes items, a "reviewed" toggle with a progress count for working through a
  long list. Respect reduced-motion and keyboard focus.

## Before publishing, check

- Could someone grasp each idea from the diagrams alone, with the prose hidden?
- Is the visual legend consistent across every figure, and stated on the page?
- Does every diagram theme correctly in light and dark, and reflow on a phone?
- Is there any section that's all text? Diagram it or cut it.
- For a decision brief: is every choice tied back, briefly, to the product goal?
