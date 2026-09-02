# Color system

## Table of contents
- The rule: assign roles, never raw values
- Full role list
- Pairing rules
- Surface container tiers
- Generating a scheme from a seed color
- Choosing a seed color
- Dark theme
- CSS custom property naming

## The rule: assign roles, never raw values

M3 color is a set of ~50 named roles, each resolved to a concrete color by whatever scheme
(light/dark, and the seed color) is active. Write code against the role name, never a literal
hex value pulled from a screenshot or guessed — the whole point of the system is that swapping
the seed or the theme mode re-derives every role consistently, including contrast.

## Full role list

Grouped by family. Every non-neutral family (primary/secondary/tertiary/error) follows the same
shape: a base color, its `on-*` content color, a lower-emphasis container pair, and (except
error) a pair of "fixed" roles that don't change between light and dark.

**Primary** — `primary`, `on-primary`, `primary-container`, `on-primary-container`,
`primary-fixed`, `primary-fixed-dim`, `on-primary-fixed`, `on-primary-fixed-variant`,
`inverse-primary`

**Secondary** — `secondary`, `on-secondary`, `secondary-container`, `on-secondary-container`,
`secondary-fixed`, `secondary-fixed-dim`, `on-secondary-fixed`, `on-secondary-fixed-variant`

**Tertiary** — `tertiary`, `on-tertiary`, `tertiary-container`, `on-tertiary-container`,
`tertiary-fixed`, `tertiary-fixed-dim`, `on-tertiary-fixed`, `on-tertiary-fixed-variant`

**Error** — `error`, `on-error`, `error-container`, `on-error-container`

**Surface / neutral** — `background`, `on-background`, `surface`, `on-surface`,
`surface-variant`, `on-surface-variant`, `surface-dim`, `surface-bright`,
`surface-container-lowest`, `surface-container-low`, `surface-container`,
`surface-container-high`, `surface-container-highest`, `surface-tint`, `inverse-surface`,
`inverse-on-surface`

**Outline** — `outline`, `outline-variant`

**Utility** — `scrim`, `shadow`

`background`/`on-background` are legacy roles kept for compatibility — for new surfaces, use
`surface`/`on-surface` and the surface-container tiers instead.

## Pairing rules

- A color role and its `on-*` counterpart are the only correct content/background pair:
  `on-primary` text sits on `primary`, `on-primary-container` sits on `primary-container`. Never
  put `on-primary` text on `primary-container` or vice versa — contrast is only guaranteed within
  the matched pair.
- The `*-container` pair is the lower-emphasis variant of a family — use it for the "filled tonal"
  version of a component (e.g. a filled tonal button = `secondary-container` +
  `on-secondary-container`), not by manually lightening the base color.
- The `*-fixed` / `*-fixed-dim` / `on-*-fixed` / `on-*-fixed-variant` roles hold a constant value
  across light and dark themes — reach for these only when a color genuinely must not flip with
  theme mode (e.g. a brand accent inside a shared illustration).

## Surface container tiers

Five steps — `surface-container-lowest`, `surface-container-low`, `surface-container`,
`surface-container-high`, `surface-container-highest` — express hierarchy between stacked
surfaces (a card above a page, a nav bar above a sheet) as a tonal step, not just a bigger
shadow. Pick the tier by how far "above" the base surface an element sits; pair a higher tier
with a higher `elevation-level*` (see `scales-tokens.md`), don't use one without the other.

## Generating a scheme from a seed color

Use Google's own `@material/material-color-utilities` package rather than inventing hex values:

```js
import { themeFromSourceColor, argbFromHex, hexFromArgb } from '@material/material-color-utilities';

const theme = themeFromSourceColor(argbFromHex('#3E6837')); // your seed color

// theme.schemes.light and theme.schemes.dark each expose every role as an ARGB int
const primaryLightHex = hexFromArgb(theme.schemes.light.primary);
```

Walk both `theme.schemes.light` and `theme.schemes.dark`, convert each role to hex, and emit them
as CSS custom properties (see naming convention below). For a one-off scheme with no build step,
Google's Material Theme Builder (linked from m3.material.io) exports the same CSS directly from a
seed color picker.

## Choosing a seed color

Derive the seed from the product's brand mark or its subject's dominant color — treat reflexively
reaching for Google's baseline demo purple (`#6750A4`) the same way you'd treat any other
templated default: fine for a throwaway demo, wrong for something that's supposed to look like
*this* product.

## Dark theme

Generate `theme.schemes.dark` alongside `light` and swap the *entire* custom-property block behind
a `prefers-color-scheme: dark` media query or a `data-theme="dark"` attribute. Don't hand-darken
individual roles — the dark scheme is derived from the same seed with its own contrast-correct
tonal mapping, and partial overrides break the pairing guarantees above.

## CSS custom property naming

`@material/web` and the wider M3 spec use `--md-sys-color-<role>`, e.g. `--md-sys-color-primary`,
`--md-sys-color-on-primary-container`. `m3-svelte` uses a different prefix, `--m3c-<role>` (e.g.
`--m3c-primary-container`). Match whichever your chosen library expects — see
`framework-setup.md`.
