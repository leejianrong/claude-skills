# Launch gates

Run after the `frontend-design` browser checks pass. Each gate is pass or fail; fix and
re-run failures. State which gates you could not run.

## Table of contents
- Content gate
- SEO and sharing
- Performance
- Accessibility
- Conversion path
- Deploy

## Content gate

- Every section from the written structure renders, in order, with the planned copy.
- No placeholder text, lorem ipsum or `[Quote ...]` markers remain, unless deliberately
  listed in the report as missing real content.
- Layout holds at 375, 768, 1280 and 1536px: no overflow, clipping or overlapping text.
- The headline and primary CTA fit on a 390px-wide first screen.

## SEO and sharing

- Server-rendered HTML contains the headline and body copy (view the page with JavaScript
  off). Crawlers and AI agents do not run your client code reliably.
- One `h1`, containing the page's primary topic naturally. Heading order does not skip
  levels.
- `title` (about 60 characters), meta description (about 150 to 160), canonical URL, Open
  Graph and Twitter tags that match the page copy, and an OG image.
- `/robots.txt` and `/sitemap.xml` return 200 and are well-formed when the site has more
  than one page.
- Structured data (`Organization`, `Product` or `FAQPage`) only where the page really
  contains that content.

## Performance

- Run Lighthouse (CLI or the browser tool) against the built page, not the dev server.
  Targets: Performance 90 or higher, SEO 100, Accessibility 95 or higher. Lab scores are a
  guide; use field data when the site is live.
- Hero image has explicit dimensions, no lazy-loading on the largest above-the-fold image,
  and modern formats. Declared fonts load, with `font-display: swap` and no layout jump.
- Keep client-side JavaScript to what the page needs. Prefer CSS for motion; scroll effects
  must not block input.

## Accessibility

- WCAG 2.2 AA as the floor: semantic HTML before ARIA, text contrast, visible focus, tap
  targets of at least 24px, and labeled form fields.
- Every image has useful `alt` text, or `alt=""` if decorative.
- Motion respects `prefers-reduced-motion`.
- Do not add an accessibility overlay widget.

## Conversion path

- The primary CTA leads somewhere real. Click it in the browser and submit the form with
  test data in a non-production environment, or report that the path is unconnected.
- Analytics or event tracking exists for the primary action if the user asked for
  measurement; otherwise do not add trackers.
- Any A/B test is server- or edge-rendered to avoid flicker, with a sample size decided
  beforehand. Do not claim a winner from a few days of traffic.

## Deploy

Only deploy when the user asked for it and the gates above passed. Confirm the target and
that the working tree is clean first. After deploy, re-run the SEO and performance gates
against the live URL and report the results.
