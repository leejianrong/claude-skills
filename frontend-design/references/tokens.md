# Design tokens

Tokens are the contract between the design plan and the code. The plan picks values; the code
only ever references roles. A role name says what a value is *for*, never what it looks like
(`surface`, not `cream`).

## Table of contents
- Role schema
- CSS variables and Tailwind v4
- Rules
- When the brief asks for Material

## Role schema

The smallest set that covers most pages. Role names follow Material 3 naming so a later move
to full M3 is a re-valuing, not a rewrite. Add a role only when a real element needs it.

| Group | Roles |
|---|---|
| Surface | `surface`, `surface-raised`, `on-surface`, `on-surface-muted`, `outline` |
| Accent | `primary`, `on-primary`, `secondary` (optional), `on-secondary` |
| Status | `error`, `on-error`; add `success`/`warning` only if the UI shows them |
| Type | `font-display`, `font-body`, `font-utility` (optional); sizes as a scale `text-xs … text-4xl` |
| Space | one scale, e.g. 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 |
| Shape | `radius-sm`, `radius-md`, `radius-lg`; `radius-full` only if used |
| Motion | `duration-fast` (~120ms), `duration-base` (~240ms), one `ease` curve |

Every background role has an `on-*` partner. Check contrast on each pair (4.5:1 for body
text, 3:1 for large text and UI borders) in light and dark. `on-surface-muted` is the usual
failure.

Values come from the plan's 4–6 colors and type roles. Do not reuse M3's baseline purple
(`#6750A4`) or any value from the defaults listed in SKILL.md.

## CSS variables and Tailwind v4

Define tokens once, in CSS. Dark mode overrides roles, never components.

```css
@import "tailwindcss";

:root {
  --color-surface: #…;
  --color-on-surface: #…;
  --color-primary: #…;
  --color-on-primary: #…;
  --radius-md: 0.5rem;
}
:root[data-theme="dark"] {
  --color-surface: #…;
  --color-on-surface: #…;
}

@theme inline {
  --color-surface: var(--color-surface);
  --color-on-surface: var(--color-on-surface);
  --color-primary: var(--color-primary);
  --color-on-primary: var(--color-on-primary);
  --radius-md: var(--radius-md);
}
```

`@theme inline` makes utilities like `bg-surface` and `text-on-surface` resolve through the
variables, so the dark override works. On Tailwind v3 (check `package.json`), map the same
variables in `tailwind.config.js` under `theme.extend.colors`. Without Tailwind, use the
variables directly.

## Rules

- No hex, rgb or arbitrary pixel radius in components. If a value has no role, add the role
  first.
- One spacing scale and one radius scale. Skipping a step needs a reason.
- Keep tokens in one file. Record them in `DESIGN.md` at the repo root (palette with role
  names, type roles, spacing and radius scales, the signature element) so later sessions
  extend the design instead of redrawing it.
- Existing project tokens always win. Read them and extend them; do not add a second set.

## When the brief asks for Material

If the brief names Material, M3 or Material You, or the product is a Google-ecosystem app,
use the `material-design-3` skill for values, components and the full role list. This schema
is the minimal default, not a replacement for it.
