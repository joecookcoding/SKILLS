# Model guide for plan phases

As of **2026-11-16**. Distilled from Anthropic, "Which Claude model should you
build with" (https://claude.dev/blog/which-claude-model-should-you-build-with/),
read that day. Prices, model names and benchmark figures change: when one of
them decides a recommendation, fetch the page again (or ask the built-in
`claude-api` skill) and update this file and its date.

## The tiers

| Tier | Model on 2026-11-16 | Built for | Price (in/out per M tokens) |
|---|---|---|---|
| Small | Haiku 5.5 | High-volume, cost-sensitive work; side tasks | $0.10 / $0.50 (prompts up to 100K tokens) |
| Mid | Sonnet 5.5 | Fast, capable, well-scoped tasks | $2 / $10 |
| Large | Opus 5.5 | The daily driver for complex coding | $4 / $20 |
| Top | Fable 5.2 | The most ambitious, open-ended technical work | $8 / $40 |

If the session's environment lists different models, keep the tiers and swap
the names.

## Phase shape → where to start

| The phase is | Start with | Then |
|---|---|---|
| Copy and text changes; a bug fix with a known cause; one new table or screen that copies an existing pattern | Mid · medium | Mid · high if it carries an access policy, or ships alone with no review before deploy |
| New screens or modules with a close pattern to follow, plus some new storage or config | Large · medium | Large · high |
| A feature that changes shared code: a new kind of thing every reader must handle, several screens, a countdown or scheduler | Large · high | Top · medium |
| Integration with an outside API not yet read live; a new server function; the plan's main goal | Large · high | Top · medium |
| Documentation, runbooks, tracker close-out | Mid · medium | Large · medium if it includes a whole-system check or a browser walk-through |
| A major refactor, a data migration, architecture work | Top · medium | Top · high |
| One run of many hours with nobody watching | Top · medium | Top · high |
| Bulk classification, tagging, extraction | Small · medium | Mid |
| The lead session: reviewing the plan, coordinating phases | Top · medium | Large · high if cost matters more than depth |
| Unsure | Large · medium | Large · high |

A clear spec does not move a phase down a tier by itself. A migration or a
performance fix can be fully specified and still need the large or top model.

## Effort

- Adjust effort before changing models. It is the finer dial.
- Measured on the large model: `medium` scored about 2.5 points below `high`
  at about 70% of the cost; `low` about 8 points below at about a third;
  `xhigh` about 1.4 points above at 2.5 times the cost.
- Past `high`, one more effort level can cost as much as the next model. Test
  the next model up at a lower effort instead.
- Effort buys longer thinking, more tool calls and self-checking. It cannot add
  knowledge the model lacks; for that, move up a model.

## When a phase fails

1. Make sure the session can check its own work: a test, a build, a script.
2. Raise effort one level.
3. Move to the next model up, starting one effort level lower than the smaller
   model was on (mid · high → large · medium; large · high → top · medium).

## Switching and mixing

- The prompt cache belongs to the model that wrote it. The first turn on a new
  model pays the cache-write price. Start a fresh session with a short written
  plan instead of switching mid-session.
- A bigger model can read a smaller model's reasoning, not the reverse. Moving
  down a tier loses the earlier thinking.
- Keep the expensive model's context lean: each turn resends it. Verbose
  reading belongs in cheaper sessions.
- Small models suit work where a mistake is cheap to spot: finding files,
  running tests, reading logs. Code edits and judgement stay on the main model.
  This applies to subagents only where the project allows them.
- Skip orchestration for a single chain of dependent steps, or for work that
  fits in one context window.
