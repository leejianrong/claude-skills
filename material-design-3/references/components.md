# Component selection

Which M3 component to reach for, and when — pick by the job the element does, not by preference.

## Table of contents
- Buttons
- FAB
- Icon buttons
- Cards
- Navigation (bar / rail / drawer)
- Chips
- Text fields
- Top app bars
- State layers apply everywhere

## Buttons

Five variants, ordered by visual emphasis:

- **Filled** — highest emphasis. One per screen/section for the single primary action.
- **Filled tonal** — medium-high emphasis, `secondary-container` coloring. An alternative
  primary action, or filled's replacement where filled would be visually too heavy.
- **Outlined** — medium emphasis. Important but not the primary action; commonly placed next to
  a filled button.
- **Text** — lowest emphasis. The least important action available (e.g. a dialog's "Cancel").
- **Elevated** — like filled but rendered as shadow + surface tint instead of a solid fill; use
  atop images or busy/colored backgrounds where a solid fill would clash.

## FAB

The single most-promoted action on a screen — at most one FAB per screen. Sizes: small /
regular (default) / large. Extended FAB adds a text label next to the icon; use it when the
action needs a label for clarity, or there's little competition for space. Color variant
(primary/secondary/tertiary container) should match how much visual weight the action deserves
relative to the rest of the screen.

## Icon buttons

Standard / filled / filled tonal / outlined — same emphasis ladder as buttons, for icon-only
actions (toolbar actions, a list item's trailing action).

## Cards

- **Elevated** — shadow separates it from the background.
- **Filled** — a surface-container tint separates it, no shadow; quieter than elevated.
- **Outlined** — a hairline border only, no shadow or fill difference.

Pick one variant per context and keep it consistent across a list. Don't nest a card of the same
variant inside another — nest a different variant, or use a plain container instead.

## Navigation (bar / rail / drawer)

Choose by breakpoint/device class, not preference:

- **Navigation bar** — compact/mobile widths. 3-5 top-level destinations, docked to the bottom.
- **Navigation rail** — medium widths (tablet, or a collapsed desktop sidebar). Same destinations
  as the bar, along the leading edge, vertical.
- **Navigation drawer** — expanded/desktop widths. Standard (always visible, pushes content) or
  modal (overlays, temporary access) — reach for a drawer when there are more destinations, or
  items need grouping/labels beyond what a rail affords.

## Chips

- **Assist** — a suggested action related to on-screen content (e.g. "Get directions").
- **Filter** — toggles a filter on content; shows a selected/unselected state.
- **Input** — represents a discrete piece of user-entered info, removable (e.g. an email
  recipient).
- **Suggestion** — a set of dynamic recommendations (e.g. quick-reply options).

## Text fields

**Filled** (default — compact, opaque background) or **outlined** (transparent background,
bordered — reads better on colored/busy surfaces). Pick one and use it consistently across a
form; don't mix filled and outlined fields in the same form.

## Top app bars

**Small** (default, one line) / **medium** or **large** (two-line, for a page needing a
prominent title — collapses to small on scroll) / **center-aligned** (title centered, small
only — for top-level destinations rather than screens reached by drilling in).

## State layers apply everywhere

Every component above keeps its hover/focus/pressed/dragged state layer (opacities in
`scales-tokens.md`). Never strip it for a "cleaner" look — that's a spec regression, not a
legitimate style choice.
