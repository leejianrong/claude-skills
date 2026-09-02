# Framework setup

Concrete setup per stack. Pick the branch that matches the decision tree in `SKILL.md`.

## Table of contents
- @material/web (React / plain HTML/JS)
- m3-svelte (Svelte)
- Retheming an existing component library
- Tokens only (no component library)

## @material/web (React / plain HTML/JS)

Google's own Material 3 web components — framework-agnostic custom elements.

```bash
npm install @material/web
```

Each component is a side-effecting import that registers its custom element:

```js
import '@material/web/button/filled-button.js';
```

Use it as a custom element, in plain HTML or JSX:

```html
<md-filled-button>Save</md-filled-button>
```

**React specifics**: JSX only sets DOM *attributes*, but several `@material/web` properties are
complex (objects, or booleans that need to be real DOM properties, not string attributes). Plain
string/boolean attributes (`disabled`, `label`) work fine directly in JSX. For anything more
complex, either grab a ref and set the property in `useEffect`, or wrap the element with
`@lit/react`'s `createComponent` to get a properly-typed React component:

```jsx
import { createComponent } from '@lit/react';
import { MdFilledButton } from '@material/web/button/filled-button.js';

const FilledButton = createComponent({
  tagName: 'md-filled-button',
  elementClass: MdFilledButton,
  react: React,
});
```

**Theming**: set `--md-sys-color-*`, `--md-sys-typescale-*`, and `--md-sys-shape-*` custom
properties at `:root` (generated per `color-system.md`) — components read them automatically.
Don't reach into a component's internals to restyle it directly; that fights the token system
instead of using it.

## m3-svelte (Svelte)

```bash
npm install m3-svelte vite-plugin-functions-mixins -D
```

Add the Vite plugin — required for the library's CSS mixins (`@apply --m3-title-large` etc.) to
compile:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";
import { functionsMixins } from "vite-plugin-functions-mixins";

export default defineConfig({
  plugins: [sveltekit(), functionsMixins({ deps: ["m3-svelte"] })],
});
```

Import components directly and use them:

```svelte
<script>
  import { Button } from "m3-svelte";
</script>

<Button onclick={() => alert("Hello world")}>Click me</Button>
```

**Theming**: m3-svelte uses its own custom-property prefix — `--m3c-<role>` for color roles (e.g.
`--m3c-primary-container`) and `--m3-*` for other tokens (e.g. `--m3-font`, `--m3-title-large`).
Generate the role values from your seed color (`color-system.md`), remap them onto the `--m3c-*`
names, and paste the block into your global CSS (`app.css`). Set `--m3-font` if you're not using
the library's default typeface.

## Retheming an existing component library

If the project already ships a mature component library — MUI, Chakra, shadcn/ui, Vuetify, Ant
Design — don't add a second one. Re-theme the one that's there: keep its components and API,
replace only its token layer.

- **MUI**: map the generated M3 role tokens into `createTheme()`'s `palette` (`palette.primary.main`
  ← `primary`, `palette.primary.contrastText` ← `on-primary`, etc.) and `typography` (M3 type scale
  → MUI's typography variants). Set `shape.borderRadius` per-component from the M3 shape scale
  (buttons often map to `corner-full`, cards to `corner-medium`/`corner-large`) rather than one
  global radius.
- **shadcn/ui** (Tailwind + CSS variables): its `--primary`, `--card`, `--radius`, etc. variables
  map directly onto M3 roles and shape tokens — set them from the generated scheme instead of
  shadcn's defaults.
- **General approach for any other library**: find its token/theme layer (palette, spacing,
  radius, elevation/shadow config) and substitute M3-generated values there; leave its component
  markup and behavior untouched.

## Tokens only (no component library)

Hand-write markup and CSS, defining the same custom properties directly at `:root`:
`--md-sys-color-*` (`color-system.md`), plus type scale, shape scale, elevation, and state-layer
values (`scales-tokens.md`). Build each component to the shapes described in `components.md`
(variants, sizing, state layers) using those variables. This is more work and easier to drift
from spec than using a library — prefer `@material/web` or `m3-svelte` when the stack allows it.
