---
name: natural-writing
description: Write prose that reads like a human wrote it, not an LLM. Use whenever drafting or editing articles, blog posts, docs, or any narrative prose for this project, especially the Tech Blog Pipeline articles. Covers the real AI tells (uniform sentence rhythm, hedging, "not just X but Y", stock vocabulary, em-dash overuse, title-case headings) and how to fix them.
---

# Natural writing

Your default prose has a texture that gives it away as machine-written. This skill
is about removing that texture. The goal isn't to beat AI detectors. It's to write
the way a thoughtful engineer writes, with rhythm and a point of view.

## The core move: imitate, don't generate

Showing a model good writing beats any list of rules. Given a sample of the user's
own writing, or a writer they admire, study its rhythm and diction and match it.
When in doubt, ask for a paragraph they consider "sounds like me" and use it as your
north star.

For this project the north star already exists: the [Jian's voice](#jians-voice)
profile below is the target for the Tech Blog Pipeline articles. Start there. The
rest of this skill is the floor everything else has to clear.

## Keep the rhythm natural

LLM prose settles into a metronome, sentence after sentence in the 18-to-24-word
range. The fix isn't to swing to the other extreme, a wall of two- and three-word
fragments, which is its own tell and reads as breathless. Aim for moderate sentences
that don't all land at the same length: join related clauses with "and" or "but,"
split an overlong one into two, and let the variation come from the ideas rather than
from chopping. Even, flowing prose is a perfectly human register, often a calmer and
more confident one.

Bad, uniform, every sentence the same length:

> Event-driven systems provide a number of benefits for modern applications. They
> allow services to communicate without being tightly coupled together. This makes
> the overall system more resilient to individual component failures. It also
> enables teams to scale different parts of the system independently.

Better, moderate and flowing:

> Event-driven systems buy you one thing above all: decoupling. A service drops a
> message and moves on, never knowing or caring who picks it up. This means a
> consumer can crash, restart, and catch up later without anyone upstream noticing.
> That's the resilience story, but it's also where the hard bugs live.

Read it aloud. If every sentence lands at the same length it's too flat; if you're
panting through fragments it's too choppy.

## Kill these tells

**"Not just X, but Y."** "This isn't just a cache, it's a contract." LLMs reach for
this constantly. Cut it and say the thing directly.

**Hedging into the polite middle.** "It's worth noting that there are several factors
to consider." Take a position. If you think something is a bad idea, write that it's
a bad idea.

**Rule-of-three padding.** Not every list wants exactly three items. Real emphasis
often comes in twos, or in one blunt clause.

**Stock vocabulary.** Delve, leverage, utilize, robust, seamless, foster, landscape,
realm, tapestry, testament, crucial, pivotal, underscore, "in the ever-evolving
world of." Reach for the plain word: use, not utilize; helps, not facilitates.

**Hollow openers and closers.** Don't open with "In today's fast-paced world." Don't
close with "In conclusion" or "Ultimately, the key takeaway is." Start on the idea
and stop when you're done.

**Empty intensifiers.** "Very," "really," "incredibly," "a powerful tool that."
Delete them, or swap in a concrete detail that earns the emphasis.

**Em-dashes.** Don't use them (—). They're a strong tell here, so set off asides
another way: rotate through commas, parentheses, a colon, or a full stop and a fresh
sentence. The ban is only on the em-dash; the plain hyphen "-" is fine (compounds
like "event-driven," ranges like "18-24 words").

**Formatting.** Use sentence case for headings, not Title Case ("Designing resilient
services," not "Designing Resilient Services"). Don't over-bullet: if ideas connect,
write a paragraph. Don't bold every other phrase; when emphasis is everywhere it
means nothing.

## Write like you know things

Vagueness is the deepest tell, because a real writer knows things and has a view.
Push every abstraction toward a concrete detail:

- "a recent study" becomes the study's name, or you drop the appeal to authority
- "many developers" becomes a number, or a specific situation you've watched happen
- "improves performance significantly" becomes "cut p99 latency from 400ms to 90ms"
- "various tools" becomes the actual tool names

Can't be specific? That's usually the sentence telling you it isn't carrying its
weight. Cut it.

And take a side. Machine prose is relentlessly neutral; good technical writing
argues. It says "most teams reach for Kafka here and regret it," then earns the
claim. Own the trade-offs. A reader should finish knowing what *you* think, not just
what the options were.

## Revision checklist

Before you call any draft done:

1. Read it aloud. Wherever you stumble or a phrase feels stiff, rewrite it.
2. Check the rhythm. Three sentences in a row at the same length? Break one, merge two.
3. Hunt the tells from the section above. Search the draft for "not just," "isn't
   just," "delve," "leverage," "seamless," "robust," "in conclusion," "it's worth
   noting," and any em-dash. Fix every hit.
4. Cut 10%. Almost every draft is padded: the qualifiers, the throat-clearing, the
   sentence that just restates the one before it.
5. Check the surface. Headings in sentence case, lists that aren't smuggling prose,
   bolding used sparingly.

## Jian's voice

The rules above are the floor. This is the target. When writing as Jian for the Tech
Blog Pipeline, match this profile. It was reverse-engineered from his hand-edits to a
draft, so it reflects what he actually does, not what sounds good in the abstract.
Revise it as more of his articles are edited and the evidence grows.

- **Even and flowing, not choppy.** He joins clauses with "and" and "but" rather than
  breaking them into fragments, consistently rewriting punchy two-word sentences into
  complete ones ("Both count." becomes "They're both valid approaches."). Don't reach
  for staccato with him. His rhythm still varies, but it's calm.
- **No narrator scaffolding.** He deletes every line that announces the structure of
  the post ("A little background first.", "So why start writing now?"). State the
  thing directly.
- **Understated, never showy.** He cuts quotable aphorisms and motivational
  punchlines ("you're not obsolete, you're early"), softens preachy phrasing, and
  swaps dramatic verbs for plain ones ("rot our maths" becomes "make kids bad at
  maths"). Avoid the thought-leader register entirely.
- **Peer, not teacher.** He writes "we" where a lecture would write "you" ("what we
  slow down for"). Keep "you" only for direct address, not for dispensing advice.
- **Confident on values, humble on advice.** He states beliefs flatly ("LLMs and
  coding agents are a good thing") but frames predictions and recommendations gently
  ("I think we can still learn"). This is the one place the general "don't hedge" rule
  bends for him: never hedge the core belief, but feel free to soften the takeaway.
- **Concrete and true beats vivid-but-vague.** He keeps vivid language when it's
  grounded ("tear through thousands of lines", "2am") and replaces cute filler with
  real detail. Accuracy about his own life matters to him; don't invent color.
- **Parentheses for asides.** His default aside punctuation is parentheses ("(one
  function at a time)"), not dashes.
- **British spelling and conventions.** "learnt", "specialised", "maths". He
  capitalises proper names properly, including his degree ("Electrical and Electronic
  Engineering").

When unsure, err toward plainer, calmer, and more modest. If a line feels clever,
he'll probably cut it.
