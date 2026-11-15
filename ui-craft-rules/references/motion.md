# Motion (MOT)

Rules for choosing, timing, staging, and easing transitions, and for motion as feedback. Most
of the classic 12 principles of animation (Thomas and Johnston, 1981) live here, translated
to interfaces. The map from principle to rule is in `SKILL.md`.

Each rule: **When** to apply it, **Why** it matters, then **Check**, what to verify in a design
or in code. Where a reel teaches the rule, a **Watch** line links it (Facebook may ask you to
sign in).

## Which motion rules apply

| You are animating | Rules |
|---|---|
| Anything at all | MOT-2, MOT-4, MOT-5, MOT-6 |
| A move between screens or views, or content changing in place | MOT-1, MOT-3 |
| A button, card, tile, or toggle being pressed | MOT-7 |
| A result: an error, a success, an upload finishing, an item landing in a cart | MOT-8, MOT-9 |
| A component with three or more states, or one the user drags (sheet, sidebar, player) | MOT-10 |
| A container bringing content in (drawer, sheet, menu, list) | MOT-11 |
| A large expansion the user triggered, in an expressive product | MOT-12 |
| An object travelling to a destination (add to cart, move to folder) | MOT-13 |

**Match the amount of motion to the product.** Dense, daily-use tools (admin, dashboards,
enterprise, government) use MOT-1 to MOT-11 at the short end of MOT-5's ranges and skip MOT-12
and MOT-13. Consumer, brand, onboarding, and celebration moments can use all of them. The
principles are a menu, not a quota: one button needs MOT-5, MOT-6, and MOT-7, not all thirteen.

## Every animation

**MOT-1 Choose the transition by what changed.**
When: moving between screens or views, or changing content in place (tabs, filters, state changes).
Why: the transition tells users where they are; the wrong one, or one used for everything, confuses them without them knowing why.
Check:

| Change | Transition | Examples |
|---|---|---|
| Content changes, structure stays | **Context**: content swaps in place; chrome stays still | tab switching, applying a filter, state change |
| Move between levels of the IA | **Drill**: push in from the trailing edge; back reverses it | list → item, feed → post, summary → full view |
| The same object changes form | **Continuity**: shared elements persist and morph | card → full screen, collapsed → full player, grid → product page |
Watch: [Memorisely, 2026-10-12](https://www.facebook.com/share/r/1BvyEFq8K4/): context, drill and continuity side by side.

**MOT-2 Motion must communicate, not decorate.**
When: before adding any animation; ask what it tells the user.
Check: every animation tells the user what just happened, what's coming next, or how the UI is responding. Feedback micro-interactions attach to a user action (a like-bounce, a streak celebration). Nothing moves for its own sake.

**MOT-3 Give motion a hierarchy (staging).**
When: a transition brings in more than one element (an overlay with a sheet, a screen with fixed controls), and whenever a dialog, sheet, or overlay opens.
Why: a plain dissolve is "good UI"; staggered, layered motion is "great UI". Staging also tells the eye where to look first.
Check:
1. Identify the fixed controls; they only fade.
2. The primary element scales and fades in.
3. Secondary surfaces (an action sheet) slide in after a delay; the nav bar can slide away to make room.
4. Dim (a scrim) or blur what's behind an overlay, so the overlay is the only thing in focus and its one primary button (CMP-6) is the first thing seen.
Watch: [Memorisely, 2026-10-30](https://www.facebook.com/share/r/1FAE4b7EZ7/): a card overlay staged: the nav bar slides down, the card scales in, its sheet slides up after.

**MOT-4 Match the easing to the job (slow in and slow out).**
When: any animation that moves, resizes, enters, or leaves.
Why: real objects speed up and slow down; constant speed reads as mechanical.
Check: an element changing size or position uses **ease-in-out**. Content arriving or settling uses **ease-out** (it starts with energy and slows into place). Content leaving uses **ease-in** (it accelerates away). No linear easing except for continuous progress and spinners. Starting curves, when the project has no motion tokens: ease-in-out `cubic-bezier(0.4, 0, 0.2, 1)`, ease-out `cubic-bezier(0, 0, 0.2, 1)`, ease-in `cubic-bezier(0.4, 0, 1, 1)`.

**MOT-5 Time it by size and distance; never make users wait for decoration (timing).**
When: every animation. Set the duration on purpose, never from a default such as `transition: all 0.3s`.
Why: timing sets how heavy and how responsive a thing feels. Too slow and the interface feels sluggish; too fast and the change is missed.
Check:

| What moves | Duration |
|---|---|
| Press, hover, toggle, checkbox | 100–150 ms |
| Small surfaces: tooltip, dropdown, menu, popover | 150–200 ms |
| Medium surfaces: dialog, sheet, drawer, card expanding | 250–300 ms |
| Full-screen and page transitions | 300–400 ms, never over 500 ms |

- Exits run about a fifth shorter than entrances.
- Longer travel takes longer within the range; desktop sits at the short end, large phone and tablet travel at the long end.
- Transitions name their properties (`transition: transform 200ms, opacity 200ms`), never `all`, and animate `transform` and `opacity` rather than layout properties (`width`, `top`, `margin`).
- Input is never blocked by an animation: the next click works while the last transition is still running.
- Durations and curves come from motion tokens (`--ds-motion-duration-short`, `--ds-motion-easing-standard`), like any other value (SYS-5). The project's tokens win over these starting values.

**MOT-6 Respect reduced motion; never rely on motion alone.**
When: every animation that moves, scales, zooms, parallaxes, or plays by itself.
Why: motion can trigger nausea and dizziness for people with vestibular disorders, and a screen reader user never sees it.
Check:
- Under `@media (prefers-reduced-motion: reduce)` (Tailwind `motion-reduce:`, SwiftUI `accessibilityReduceMotion`), movement becomes a short opacity fade or an instant change. The state change itself still shows.
- Motion triggered by an interaction can be turned off unless it is essential (WCAG 2.2 SC 2.3.3). Anything that moves by itself for more than 5 s can be paused (SC 2.2.2).
- Motion never carries meaning on its own: an error or a success also appears as text (MOT-8).
- Animation never moves, delays, or traps keyboard focus, and content stays usable while it runs.

## Feedback

**MOT-7 Pressable controls compress slightly when pressed (squash and stretch).**
When: buttons, cards, tiles, list rows that open something, and toggles, on touch and pointer. Skip text links, disabled controls, and dense table cells.
Why: a press that visibly gives makes the control feel physical and confirms the tap before anything else happens.
Check: on press the control scales to about `0.97` (0.95–0.98) in ~100 ms and springs back on release with ease-out. Scale with `transform`, so nothing around it moves. Scale both axes together; uneven stretch is for playful brand moments only. A shadow, if any, tightens at the same time (VIS-8).

**MOT-8 Exaggerate only what must not be missed, and never with motion alone (exaggeration).**
When: a validation error on submit, a failed action, a high-stakes success (payment sent, booking confirmed), or a change the user caused but could miss. Not routine saves, hovers, or every field.
Why: amplifying a response makes its meaning unmistakable, but only when it is rare. A clear message and focus handling matter more than the shake.
Check:
- An error shake is horizontal, under 10px, and about 300 ms, once. Under reduced motion it doesn't play.
- Every error also shows as text next to the field with an icon, not colour alone (WCAG 1.4.1). Focus moves to the first invalid field, and the message is announced (`aria-invalid`, `aria-describedby`, or a live region).
- A success morph (button → checkmark) holds for about 1–2 s, then moves on or resets. It too is announced as text.

**MOT-9 One small secondary cue confirms the result (secondary action).**
When: an action completes after a visible wait, or its result lands somewhere else on screen (an upload finishing, a save, an item reaching a cart or a folder).
Why: a supporting cue reinforces the main action without competing with it.
Check: one cue per action: the progress bar completes and a checkmark appears, or the cart badge bumps and its count updates. The cue is smaller and shorter than the main motion and starts as it settles. Never two celebrations at once. It has a text equivalent (a live-region status such as "Uploaded").

## Spatial transitions

**MOT-10 Design the rest states first, then animate between them (pose to pose).**
When: a component with three or more states (a sidebar that is closed, collapsed to icons, or open; a bottom sheet with peek, half, and full; a mini and full player), or anything the user drags.
Why: planning the key states first gives predictable, controlled motion instead of whatever falls out of the code.
Check:
- Each rest state is designed and named, in design and in code (`data-state="closed | peek | open"`, a TOK-4 variant). Motion runs only between named states.
- A drag released between states snaps to the nearest one, or the next one in the direction of a fast flick. No resting in between.
- State changes use transitions, which reverse smoothly from wherever they are when interrupted, not keyframe animations, which restart.

**MOT-11 Parts settle in sequence, not all at once (follow through and overlapping action).**
When: a container brings content in: a drawer, sheet, menu, card expanding, or list appearing.
Why: real things don't stop all at once; content that settles just after its container gives the move weight and makes it easier to follow.
Check:
- Inner content starts about 50 ms after its container (button text compresses after the button starts expanding; a drawer's items settle after the drawer).
- List items stagger by 20–40 ms each, and only the first six or so stagger; the rest arrive with the last of them, so the whole list is in within about 200 ms.
- Overshoot, if any, is a few pixels and only in expressive products. No bounce in dense tools.

## Expressive motion

Use these for consumer, brand, onboarding, and celebration moments. Skip them in dense,
daily-use tools.

**MOT-12 Wind up before a large transition (anticipation).**
When: a large transition the user triggers, such as a card opening to full screen, a sheet launching, or a send or launch moment. Not for dropdowns, hovers, or keyboard shortcuts.
Why: a small preparatory move signals that something bigger is about to happen and what it will be.
Check: the wind-up is under 100 ms and small: the card lifts (scale about `1.02` and one elevation step, VIS-8) or pulls back slightly. Start it on press, so it hides the wait rather than adding to it; the main transition starts on release. Under reduced motion it is skipped.

**MOT-13 Objects travelling to a destination move in an arc (arcs).**
When: an element flies between two distant points on both axes to show where it went: add to cart, move to folder, minimise to a dock, a button turning into a sheet. Moves along one axis (drawers, sheets, page pushes, list reordering) stay straight.
Why: natural movement follows curves, and a curve is easier to track to its destination.
Check: animate x and y with different easings (x ease-out, y ease-in) on nested elements, or follow a CSS `offset-path`. It takes 300–500 ms, and the destination reacts on arrival (MOT-9). Under reduced motion there is no travel: the destination updates.
