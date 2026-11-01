# Verify and polish

Look at the real page, then measure it. A screenshot shows layout; computed styles, console
output and the accessibility tree show what is actually wrong.

## Table of contents
- Loop
- Checks
- Polish order
- Cost

## Loop

1. Start the dev server and open the page with a browser tool (Playwright MCP, or a
   Playwright script if no MCP is configured). If no browser is available, say so and list
   the checks you could not run. Do not claim them.
2. Screenshot at 375px and 1280px. Add 768px for layouts that change in between.
3. Run the checks below, fix what fails, and re-run the failed ones.
4. Stop when the checks pass. Report what you ran.

## Checks

- **Console:** no errors or warnings on load.
- **Overflow:** no horizontal scroll at any tested width.
- **Tokens:** no hardcoded colors or radii in the changed files, e.g.
  `grep -rnE '#[0-9a-fA-F]{3,8}\b' src/ --include=*.{tsx,jsx,vue,svelte,css}` outside the token
  file.
- **Contrast:** every `on-*` pair passes in light and dark.
- **Keyboard:** Tab through the page. Focus is always visible and the order matches the
  visual order.
- **Reduced motion:** with `prefers-reduced-motion: reduce` emulated, non-essential motion
  stops.
- **Fonts:** every declared face actually loads. A face named in CSS but never loaded falls
  back silently.
- **Accessibility tree:** use the snapshot, not a screenshot, to find unlabeled controls and
  heading-order problems.

## Polish order

After the build works, one pass each, in this order, so later passes do not undo earlier ones:

1. Baseline: spacing, alignment, overflow, specificity clashes.
2. Accessibility: the keyboard, contrast and label checks above.
3. Motion and performance: remove motion that serves nothing, check images and fonts.
4. Last look: remove one thing. Then compare against the plan; if the page now reads like a
   default, revisit the plan, not the pixels.

## Cost

Screenshots are expensive. Take them for UI changes, not backend ones, and snapshot the
accessibility tree once per view instead of after every small edit.
