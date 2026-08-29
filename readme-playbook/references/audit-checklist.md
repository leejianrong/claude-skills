# README audit checklist

Work top to bottom against the current README. Each "no" is a fix, roughly in priority
order — fix staleness and broken install steps before worrying about visuals or badges.

## Contents
- Accuracy (fix first)
- Structure
- Content quality
- Governance

## Accuracy (fix first)

- [ ] The install/quick-start commands actually work, run today in a clean checkout
- [ ] Version numbers, supported languages/runtimes, and prerequisites match what the repo
      actually requires
- [ ] Every linked file (`CONTRIBUTING.md`, `LICENSE`, docs) exists at the path referenced
- [ ] No claim in the README contradicts the current code or CI status

## Structure

- [ ] A value prop appears in the first two lines — no scrolling needed to know what this is
- [ ] There's a visual: screenshot, GIF, terminal recording, or a diagram if there's no UI
- [ ] Quick start is copy-pasteable, in run order, with no missing steps assumed as "obvious"
- [ ] Usage shows 2-3 concrete examples, not a full API listing
- [ ] Contributor-only material (dev setup, release process) lives in `CONTRIBUTING.md`, not
      inline
- [ ] License is stated explicitly

## Content quality

- [ ] No badge wall — every badge present is one someone would actually act on
- [ ] No unproven marketing claims ("blazing fast", "enterprise-grade") without a number or
      something the reader can verify
- [ ] Terminology is consistent (one name per concept, not three)
- [ ] Config section, if present, lists options that matter — not every flag that exists

## Governance

- [ ] A way to get help or report an issue is stated (issue tracker link, discussions, etc.)
- [ ] If the project's maturity/stability matters (alpha, unmaintained, breaking-changes-
      expected), that's stated up front, not discovered the hard way
