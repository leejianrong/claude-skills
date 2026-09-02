---
name: material-design-3
description: Apply Google's Material Design 3 (M3) system — color roles and dynamic color, type scale, shape and elevation tokens, state layers, motion, and components — when building or restyling a frontend in React, Svelte, plain JavaScript, or HTML/CSS. Use when the user asks for Material Design, Material 3, M3, Material You, or "Google's design system," or references M3 components/concepts like filled/tonal buttons, FABs, navigation rails, or dynamic color.
---

# Material Design 3

M3 is a token system, not a look you eyeball. Every visual decision — color, type, shape,
elevation, motion — maps to a named role or scale step defined by the spec. The job here is
to wire the real tokens through, not approximate "Google-ish" styling with arbitrary hex
codes and border-radii.

## Core mental model

- **Roles, not raw values.** Never hardcode a hex color or an arbitrary `border-radius`/`box-shadow`
  where a token exists. Assign the *role* (`primary`, `on-primary-container`, `corner-large`,
  `elevation-level2`) and let the generated token value fill it in.
- **Elevation = shadow + surface tint**, not just a bigger shadow. Higher elevation also washes
  more of the primary color over the surface. See `references/scales-tokens.md`.
- **Pick a real seed color.** M3's demos default to Google's baseline purple (`#6750A4`). Don't
  reflexively reuse it for a real product — derive the seed from the brand/subject, the same
  instinct as avoiding templated defaults in general frontend work. Baseline purple is fine only
  for a genuine, brand-less demo.

## Decision tree: pick the implementation path

1. **Project already has a mature component library** (MUI, Chakra, shadcn/ui, Vuetify, Ant
   Design, …)? Re-theme it — map its token layer onto M3 roles/type/shape. Don't bolt on a second
   component library. → `references/framework-setup.md` § Retheming an existing library.
2. **React or plain HTML/JS, no existing library** → Google's official `@material/web` custom
   elements. → `references/framework-setup.md` § @material/web.
3. **Svelte** → `m3-svelte`. → `references/framework-setup.md` § m3-svelte.
4. **Hand-rolled markup, no component library wanted** → apply the M3 CSS custom properties
   directly to your own elements. → `references/framework-setup.md` § Tokens only.

## Workflow checklist

Copy this into your response and check items off as you go:

1. [ ] Pick or derive a seed color (confirm whether dark mode is in scope)
2. [ ] Generate the full role token set from the seed, light + dark (`references/color-system.md`)
3. [ ] Wire tokens in as CSS custom properties, scoped so light/dark can swap as one block
4. [ ] Pick components per screen from `references/components.md` — canonical M3 components,
       not ad hoc HTML approximations
5. [ ] Apply type scale roles by the text's *purpose* (`references/scales-tokens.md`), not by
       picking a size that "looks right"
6. [ ] Apply the shape scale by component convention, not an arbitrary `border-radius`
7. [ ] Confirm every interactive element keeps its state layer (hover/focus/pressed/dragged)
8. [ ] If any role's color was overridden by hand, double check it didn't break its `on-*` pairing

## References

- `references/color-system.md` — full color role list, pairing rules, surface container tiers,
  generating a scheme from a seed color, dark theme, CSS custom property naming
- `references/scales-tokens.md` — type scale, shape scale, elevation, state layer opacities,
  motion durations/easings — exact values pulled from the spec source
- `references/components.md` — which M3 component to reach for and when: buttons, FAB, icon
  buttons, cards, navigation (bar/rail/drawer), chips, text fields, top app bars
- `references/framework-setup.md` — concrete setup per stack: `@material/web` (React/HTML),
  `m3-svelte` (Svelte), retheming an existing library, tokens-only
