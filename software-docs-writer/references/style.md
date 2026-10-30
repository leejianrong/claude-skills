# Style and consistency

A distillation of the [Google developer documentation style guide](https://developers.google.com/style)
(which defers to the Microsoft Writing Style Guide for technical style). Where a project
already has a style guide or a Vale config, that wins. Where the rules conflict with
clarity, clarity wins; deviate consistently.

## Contents

- Voice
- Headings
- Lists and tables
- Code and commands
- Links
- Images and accessibility
- Terminology table
- LLM-draft tells

## Voice

- Active voice, so it is clear who does what ("the server returns", not "is returned").
- Second person ("you"), or "we" in a tutorial where you build together. Avoid "the
  user" in instructions.
- Present tense for behaviour ("the function returns a list"), imperative for steps
  ("Run the command").
- Plain words: "use", not "utilise". Skip "simply", "just", "easy" and "obviously":
  they read as insults to the reader who is stuck.
- Put the condition before the action ("To deploy, run…").
- One idea per sentence where you can. Aim for under 25 words, and check anything over 35.

## Headings

- Sentence case ("Add a new route", not "Add A New Route").
- Task and tutorial headings describe the action; reference headings are the names of the
  things.
- No skipped levels (h2 to h4). One h1 per page.
- Don't stack two headings with nothing between them.
- Make headings unique within a page so anchor links work.

## Lists and tables

- Numbered lists for sequences, bullets for the rest.
- Parallel structure: every item starts the same way (all imperative, or all nouns).
- A table when items have several attributes (parameters, flags, status codes). A list
  when items are single phrases.
- One action per numbered step. If a step has a sub-action, make it a sub-list.

## Code and commands

- Code font for anything the reader types or reads in a terminal: commands, flags, file
  names, function names, values.
- Every fenced block has a language (` ```python `, ` ```bash `, ` ```text ` for output).
- Don't put prompts (`$`) in a block meant to be copied unless the page also shows output.
  If a block mixes commands and output, make that clear and keep it short.
- Place a destructive-action warning before the command it protects, never after.

## Links

- Descriptive link text (`see the [deployment guide](/docs/deploy/)`), never "click here" or a
  bare "here".
- Link the first meaningful mention of a concept, not every mention.
- Relative links for pages in the same docs, so they survive a domain change and the
  checker can verify them.
- Avoid positional references ("above", "below", "as shown earlier") that break when the
  page is reordered or read out of context by a search result or an agent. Name the
  section instead.

## Images and accessibility

- Alt text on every image that carries information; empty alt text for decoration.
- Don't rely on colour alone to convey meaning (red and green status).
- Prefer text (a code block, a table) to a screenshot of text. Screenshots rot and can't
  be searched.
- Give a diagram a text equivalent.

## Terminology table

Terminology drift is the strongest sign of machine-written docs: the same thing is called
"verify", "check" and "confirm" in three paragraphs. Readers then wonder whether the three
are different operations.

Before drafting, write a table of one approved term per concept and use it everywhere,
including code comments and headings. Put it in the docs repo if the project has no
glossary.

| Concept | Use | Don't use |
|---|---|---|
| (example) a function that handles a URL | path operation | route, endpoint, handler |

## LLM-draft tells

Run the `natural-writing` skill's revision checklist on the prose. For docs specifically,
also look for:

- A summary paragraph that restates the section heading.
- "Let's dive in", "In this section we will", and other announcements of what is
  coming. Start on the content.
- A bold phrase on every line. Bold the thing the reader must not miss, once.
- Three-item lists everywhere, including where there are two or five real items.
- Examples that avoid a real failure case because the draft was never run.
- Hedging inside instructions ("you may want to perhaps"). A step is either required or
  optional, so say which.
