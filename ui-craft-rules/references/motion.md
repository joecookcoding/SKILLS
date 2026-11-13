# Motion (MOT)

Rules for choosing transitions, staging them, and easing them.

Each rule: **Why** it matters, then **Check**, what to verify in a design or in code.

**MOT-1 Choose the transition by what changed.**
Why: the transition tells users where they are; the wrong one, or one used for everything, confuses them without them knowing why.
Check:

| Change | Transition | Examples |
|---|---|---|
| Content changes, structure stays | **Context**: content swaps in place; chrome stays still | tab switching, applying a filter, state change |
| Move between levels of the IA | **Drill**: push in from the trailing edge; back reverses it | list → item, feed → post, summary → full view |
| The same object changes form | **Continuity**: shared elements persist and morph | card → full screen, collapsed → full player, grid → product page |

**MOT-2 Motion must communicate, not decorate.**
Check: every animation tells the user what just happened, what's coming next, or how the UI is responding. Feedback micro-interactions attach to a user action (a like-bounce, a streak celebration). Nothing moves for its own sake.

**MOT-3 Give motion a hierarchy (plan it with the layout).**
Why: a plain dissolve is "good UI"; staggered, layered motion is "great UI".
Check:
1. Identify the fixed controls; they only fade.
2. The primary element scales and fades in.
3. Secondary surfaces (an action sheet) slide in after a delay; the nav bar can slide away to make room.
4. Blur what's behind an overlay to create depth.

**MOT-4 Match the easing to the job.**
Check: an element changing size or position uses **ease-in-out**. Content arriving or settling uses **ease-out** (it starts with energy and slows into its final position). Inner content runs slightly later than its container, e.g. button text compresses after the button starts expanding. No linear easing except for continuous progress.
