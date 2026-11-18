# Durable loops: altitude that runs

Read before setting the limits (step 7) when the chosen rung runs as a loop rather
than a single session. Each section is a pattern from a source in `sources.md`.

## Hardening against an outcome (chaos loop)

- **Loop:** pick a scenario, run the harness, read the telemetry, propose a fix, ship it to
  staging, run again.
- **Scenarios a little paranoid:** 10x the launch estimate; every client reconnecting
  at once; a server killed mid-load; the database stalling.
- **Decide up front which calls need a person:** anything hard to undo (schema, key
  layout, storage format). The agent stops on those and brings a recommendation.
- **Two or three invariants** that every iteration must keep (open time, no lost
  acknowledged writes).
- **Make the system legible:** telemetry on every operation (for example, each query
  reports its name and rows scanned against rows returned). Have the agent add missing
  telemetry as it goes. Prefer tech choices where a measurement traces back to code you
  wrote; noise such as garbage-collector pauses hides the signal the agent climbs on.

## Work that spans many sessions (long-running harness)

- **First session sets up the environment:** an init script, a progress file, a first
  commit, and a **feature list in JSON** with every item `"passes": false`. JSON is
  less likely than Markdown to be rewritten carelessly.
- **Later sessions may only flip `passes`,** never edit or delete items.
- **One feature per session.** Commit with a descriptive message, update the progress
  file, and leave the tree mergeable.
- **Each session starts** by reading the progress file and git log, then running the
  smoke test before touching anything. A broken start found later costs the whole session.
- **Mark an item passing only after an end-to-end check,** not after unit tests.

## Scheduled automations (agent automations)

- **Bookmarks, not fixed windows.** "The last 24 hours" leaves gaps when a run is late and
  repeats items when it is early. Store the newest item read from each source.
- **A failed read is not a quiet day.** When a source fails, keep its bookmark where it
  was, report from the others, and name what couldn't be read.
- **Confirm before recording.** Count a post as sent only when the destination confirms
  it (`ok: true` and an ID). Check for today's edition before posting. When unsure,
  mark "maybe posted" and change nothing else.
- **Re-check right before acting.** Drop items resolved since they were read. Copy links
  from the source, never build them by hand.
- **Dates in the reader's time zone,** stated in the run's first message.
- **Read-only credentials where the agent only reads; a spending cap per run.**

## Climbing a score (eval and hillclimbing)

- **The eval mirrors production,** leaves headroom below 100% for the best model, and
  varies little between runs. A case that fails every run is usually ambiguous, not hard.
- **Validate the grader** by reading scored transcripts, and by running it twice on the
  same output to see whether the verdict changes. The judge model is not the model
  under test.
- **Split train and test.** The climber reads only the training cases' transcripts and
  never pastes a failure into the prompt. If training improves while test stays flat,
  revert.
- **One change per round,** big enough to show above the noise. When the score stalls for
  two or three rounds, sort the remaining failures by cause before trying more.
- **When quality is saturated,** climb cost at equal quality instead.
- **If the gain is within noise, say so** and don't merge it.
