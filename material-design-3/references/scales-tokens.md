# Type scale, shape, elevation, state layers, motion

Exact values below are pulled from `material-components/material-web`'s generated token source
(`tokens/versions/v0_192/`), not reconstructed from memory — treat them as authoritative for
classic M3.

## Table of contents
- Type scale
- Typeface defaults
- Shape scale
- Elevation
- State layer opacities
- Motion

## Type scale

15 roles, each with a font-role, size, line-height, weight, and letter-tracking. `rem` values
assume a 16px root.

| Role | Font role | Size | Line height | Weight | Tracking |
|---|---|---|---|---|---|
| display-large | brand | 3.5625rem | 4rem | 400 | -0.015625rem |
| display-medium | brand | 2.8125rem | 3.25rem | 400 | 0 |
| display-small | brand | 2.25rem | 2.75rem | 400 | 0 |
| headline-large | brand | 2rem | 2.5rem | 400 | 0 |
| headline-medium | brand | 1.75rem | 2.25rem | 400 | 0 |
| headline-small | brand | 1.5rem | 2rem | 400 | 0 |
| title-large | brand | 1.375rem | 1.75rem | 400 | 0 |
| title-medium | plain | 1rem | 1.5rem | 500 | 0.009375rem |
| title-small | plain | 0.875rem | 1.25rem | 500 | 0.00625rem |
| body-large | plain | 1rem | 1.5rem | 400 | 0.03125rem |
| body-medium | plain | 0.875rem | 1.25rem | 400 | 0.015625rem |
| body-small | plain | 0.75rem | 1rem | 400 | 0.025rem |
| label-large | plain | 0.875rem | 1.25rem | 500 (700 prominent) | 0.00625rem |
| label-medium | plain | 0.75rem | 1rem | 500 (700 prominent) | 0.03125rem |
| label-small | plain | 0.6875rem | 1rem | 500 | 0.03125rem |

The "prominent" weight variants on the label roles are for emphasized labels (e.g. a selected
tab) — swap in only when the spec calls for it, not as a general bolding.

## Typeface defaults

Two independent font slots: `brand` (display, headline, title-large) and `plain` (title-medium/
small, body, label). Both default to Roboto at weights 400/500/700 (regular/medium/bold). You can
swap in a distinctive display face for `brand` while keeping `plain` a neutral, highly-legible UI
font — don't use the same face for both if you want a real typographic identity, but keep the
relative role assignment (which roles use which slot) intact.

## Shape scale

| Token | Radius |
|---|---|
| corner-none | 0px |
| corner-extra-small | 4px |
| corner-small | 8px |
| corner-medium | 12px |
| corner-large | 16px |
| corner-extra-large | 28px |
| corner-full | 9999px (pill) |

Directional variants exist for asymmetric shapes — `corner-large-top`, `corner-large-start`,
`corner-large-end`, `corner-extra-large-top`, `corner-extra-small-top` — used for things like a
bottom sheet (rounded top corners only) or a segmented button's end caps. Assign the scale step by
component convention (see `components.md`), never a one-off `border-radius` number.

## Elevation

| Level | dp |
|---|---|
| 0 | 0 |
| 1 | 1 |
| 2 | 3 |
| 3 | 6 |
| 4 | 8 |
| 5 | 12 |

M3 elevation is rendered as **shadow plus a surface-tint wash** — at higher levels, more of the
`surface-tint` role (normally equal to `primary`) is blended over the surface color, on top of a
correspondingly larger shadow. Prefer the elevation level/attribute built into whatever component
library you're using (`@material/web` and `m3-svelte` components set sensible defaults per
component) over hand-computing a `box-shadow`; when you do need to hand-roll it, pair the shadow
with the tint wash — a shadow alone is an M2 look, not M3.

## State layer opacities

Applied as an overlay of the element's content color (usually its `on-*` role) over the resting
surface, not by lightening/darkening the base color:

| Interaction | Opacity |
|---|---|
| hover | 0.08 |
| focus | 0.12 |
| pressed | 0.12 |
| dragged | 0.16 |

Every interactive component keeps a state layer for all of these — removing it for a "flatter"
look is a spec regression, not a style choice.

## Motion

**Durations** — short for small, local changes; long/extra-long for full-screen or
large-spatial transitions:

| Token | ms |
|---|---|
| short1 / short2 / short3 / short4 | 50 / 100 / 150 / 200 |
| medium1 / medium2 / medium3 / medium4 | 250 / 300 / 350 / 400 |
| long1 / long2 / long3 / long4 | 450 / 500 / 550 / 600 |
| extra-long1 / extra-long2 / extra-long3 / extra-long4 | 700 / 800 / 900 / 1000 |

**Easings**:

| Token | cubic-bezier |
|---|---|
| standard | 0.2, 0, 0, 1 |
| standard-accelerate | 0.3, 0, 1, 1 |
| standard-decelerate | 0, 0, 0, 1 |
| emphasized | 0.2, 0, 0, 1 (spec approximation of a multi-segment curve) |
| emphasized-accelerate | 0.3, 0, 0.8, 0.15 |
| emphasized-decelerate | 0.05, 0.7, 0.1, 1 |
| legacy | 0.4, 0, 0.2, 1 |
| legacy-accelerate | 0.4, 0, 1, 1 |
| legacy-decelerate | 0, 0, 0.2, 1 |
| linear | 0, 0, 1, 1 |

Use `standard` easing for most in-place transitions (a menu opening, a value changing). Reach for
`emphasized` on large, spatial transitions between contexts — a screen transition, a nav
drawer opening — paired with a `long`/`extra-long` duration.
