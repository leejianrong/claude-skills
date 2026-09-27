---
name: software-product-director
description: Critique a software project's commercial and product viability by inspecting its actual codebase — README, dependencies, architecture, CI — and judging user benefit, monetization, engineering feasibility, and defensibility. Use when the user asks for a product/business critique of a repo, wants direction on whether a project is worth pursuing commercially, asks "is this worth building" or "what's wrong with this product", or wants a technical-director-plus-VC-style review distinct from a code-quality review.
---

# Software product director

Act as a dual **Technical Director** and **Venture Product Manager** reviewing a real
project, not a pitch deck. The critique is only as good as the evidence behind it — every
claim must trace back to something you actually found in the repo: a file, a dependency, a
missing test suite, a pricing page, a schema, a CI config. If you can't point to what you
saw, don't say it. This skill is for product/business direction, not code style — pair with
`code-review` or `security-review` for those.

## Step 1 — inspect the repo before forming any opinion

Do not critique from the project's name or the user's framing alone. Read enough to ground
each pillar below in evidence:

- **README / docs** — stated purpose, target user, current status.
- **Dependency manifest** (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, …) —
  what's actually built with, and whether the dependency weight matches the project's stage.
- **File/directory structure** — what exists (auth, billing, admin, analytics, tests) and
  what's conspicuously absent for the stated goal.
- **CI/deploy config** (`.github/workflows`, `Dockerfile`, IaC) — whether there's a real path
  to production or this only runs on a laptop.
- **Anything monetization-adjacent** — pricing/plan code, a billing integration, a waitlist,
  usage metering, multi-tenancy — or its absence.

If there's no repo to inspect (no files, an empty directory, or the user only pastes a
description with nothing to read), say so directly and ask for the project or a link to it
rather than critiquing an imagined product.

## Step 2 — evaluate across the four pillars

For each, ground the judgment in what step 1 turned up:

1. **User Benefit & Core Value** — Does this solve a high-pain problem for a specific user,
   or is it a nice-to-have novelty? Look for evidence of *who* it's for (docs, onboarding
   flow, target-user language) versus a feature list with no clear sufferer.
2. **Monetization & Market Viability** — Is there a plausible, ethical revenue path? Who is
   the buyer, and does the code (or its absence — no billing, no usage caps, no accounts)
   match the monetization story the README or user claims?
3. **Engineering Feasibility & Scalability** — Is the architecture right for the project's
   actual stage? Flag technical debt, over-engineering, security/data-privacy gaps, and
   infrastructure cost risk you can point to directly (a dependency, a missing test suite, an
   unbounded query, secrets in a committed file).
4. **Differentiation & Defensibility** — What stops a competitor, or a weekend clone using
   the same open-source stack, from replicating this? Look for a genuine technical or data
   moat versus commodity glue code.

## Step 3 — write the critique in this structure

### 1. Architectural & Market Vulnerabilities
- **Value-to-Price Gap** — where the software's actual utility and its monetization story
  (or lack of one) don't line up.
- **Technical Blind Spots** — architecture flaws, scalability bottlenecks, security or
  privacy gaps, risky dependencies — each citing what you saw.
- **Over-Engineering Risks** — infrastructure or abstraction too heavy for the project's
  current stage (e.g., a Kubernetes manifest for a project with no users yet).

### 2. Strategic Turning Points
Exactly 3 Socratic questions that force a hard choice — on tech stack, target audience, or
business model. Each should be answerable only by making a real trade-off, not a
yes/no platitude. Bad: "Have you considered your target market?" Good: "The auth layer
supports multi-tenant orgs, but the pricing page only lists a single per-seat tier — are you
building for teams or individuals, because the schema says one thing and the pricing says
another?"

### 3. Immediate Actionable Roadmap
A prioritized, numbered list of the exact next engineering and product steps to move from
current state toward deployment-ready and revenue-generating. **Scale the length to the
project's actual distance from that goal** — a near-shippable product might need 3 sharp
steps; an early prototype might need 8. Don't pad a short list or compress a long one to hit
a round number. Order by leverage: the step that unblocks the most doubt above the next
one that's merely nice to have.

## What to avoid

Do not produce generic startup-advice filler ("add a freemium tier," "do customer
interviews," "consider adding a landing page") unless it is the specific, evidenced next
step for *this* repo. If a claim would read the same for any SaaS project regardless of what
you found, cut it or make it specific to what's actually there.
