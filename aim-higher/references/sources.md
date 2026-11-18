# Sources, and how they connect

Read when the user asks where an idea comes from, or wants the reading list. Dates are
publication dates; all were read on 2026-11-17.

## The core

- **Felix Rieseberg, "How to be more ambitious: a tutorial for humans with models"**
  (2026-10-13). https://felixrieseberg.com/how-to-be-more-ambitious-a-tutorial-for-humans-with-models/
  Four kinds of ambition: speed (skipped as obvious), altitude, depth, range. The QBR
  example climbs from "make slides" to "design a better way for leadership to catch
  problems, backtest it on our history, run it beside the deck for a quarter." Depth's
  four-question prompt, which steps 3 and 5 of this skill adapt. Range by turning nouns
  into verbs and assembling a crew, without role-play. Self-efficacy: specific hard
  goals beat "do your best" (Locke and Latham); Dantzig, Bannister.

## Altitude in practice

- **Vivek Nair, "Using a 'chaos loop' to harden the Claude Docs launch"** (claude.dev,
  2026-11-17). https://claude.dev/blog/chaos-loop-claude-docs-launch/
  Cites Felix by name. The outcome was "a service that survives launch," not "fix this
  query." Claude ran a staging cluster for two weeks against paranoid scenarios, read
  telemetry, fixed and reran. A person kept the hard-to-undo decisions (schema, storage
  layout), and two invariants held throughout. Legibility made it work: telemetry on
  every operation, and a runtime with no garbage collector, so every number traced back
  to their own code. Result: 60 server errors across 2 billion requests; ~50 pods
  instead of a planned 500+.
- **Anthropic, "Effective harnesses for long-running agents"** (2025-11-26).
  https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  How a high-altitude goal survives many context windows: a feature list in JSON, every
  item failing at the start; one feature per session; a progress file and git commits;
  an end-to-end check before an item is marked passing.
- **claude.dev, "Building effective agent automations"** (2026-10-08).
  https://claude.dev/blog/building-effective-agent-automations/
  Durable workflows that take the person out of the loop: bookmarks instead of fixed
  windows, a failed read is not a quiet day, confirm before recording, re-check live
  status just before posting.
- **Felix Rieseberg, "Hunger beats tenure: advice for junior engineers"** (2026-10-27).
  https://felixrieseberg.com/hunger-beats-tenure-advice-for-junior-engineers/
  Altitude for a career: find the goals of your manager's manager, pick a radical idea,
  build a working prototype over a weekend, carry one idea per prototype. Newcomers
  don't know what's "impossible," and often nobody has checked.

## Depth needs a judge

- **Terence Tao, via The Decoder, "AI drives idea generation cost to near zero but shifts
  the bottleneck to verification"** (2026-03-22).
  https://the-decoder.com/terence-tao-says-ai-drives-idea-generation-cost-to-near-zero-but-shifts-the-bottleneck-to-verification/
  Why every ambitious brief needs its judge named first.
- **Addy Osmani, "How the Claude Code team thinks about verification"** (claude.dev,
  2026-11-16). https://claude.dev/blog/how-the-claude-code-team-thinks-about-verification/
  The judge for code: run the change, end-to-end, property and differential tests;
  changes never edit their own checks. Carried in the `test-strategy` skill.
- **claude.dev, "Automating eval design and hillclimbing with Claude"** (2026-09-28).
  https://claude.dev/blog/automating-eval-design-and-hillclimbing/
  The judge for prompts, skills and agents: evals that mirror production, headroom, a
  grader checked by reading transcripts, a judge model that isn't the model under
  test, a held-out split, and a warning against sampling only the cases today's model
  fails.

## Why ambition has to be tried, not assumed

- **Ethan Mollick, "The Shape of AI: Jaggedness, Bottlenecks and Salients"**
  (2025-12-20). https://www.oneusefulthing.org/p/the-shape-of-ai-jaggedness-bottlenecks
  Capability is jagged. One weak spot (a bottleneck) can block a whole workflow until it
  is fixed (a "reverse salient"), and then everything jumps forward at once. So record
  where an ambitious attempt failed, and try again on the next model.
- **Helen Toner, "Taking Jaggedness Seriously"** (2025-11-24).
  https://helentoner.substack.com/p/taking-jaggedness-seriously
  Models keep getting better and keep failing at confusing things. Don't assume that
  success on one task carries over to the one next to it.
- **Patrick Collison, "Fast"** (ongoing). https://patrickcollison.com/fast
  Examples of ambitious things done fast with hard goals and tight deadlines: the case
  for step 3's "unreasonable target."

## How they tie together

Altitude says what to ask for. Depth says how well to do it. Range says who else to
borrow from. Tao, Osmani and the eval post say none of it counts without a judge outside
the model. The chaos loop, the long-running harness and the automations post show what a
high-altitude ask needs in order to run: instruments, invariants, a person for hard-to-undo
calls, and state between runs. Mollick and Toner explain why the ceiling is found by
trying, and why the trying is worth repeating with each model.
