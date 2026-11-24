---
name: ui-craft-rules
description: UI/UX craft rules for building or reviewing web and mobile screens in code or Figma. Use for a page, card, form, modal, menu, tab bar, button, or empty state; animation, press feedback, or loading states; tap targets; UX laws (Fitts, Hick, Jakob) or animation principles; design tokens or dark mode; or making a UI look less AI-generated. Includes a 34-point review list of AI UI tells.
---

# UI Craft Rules

61 rules for interface craft, each written as something you can check and each opening with a
**When** line that says when it applies, plus a review list of the fingerprints AI-generated
UI leaves behind. The 12 principles of animation and the named usability laws (Fitts, Hick,
Miller, Doherty, Postel, Jakob) are in here, translated into checks; find them by name in
[Find a rule by principle](#find-a-rule-by-principle). The rules apply to any stack (React,
HTML/CSS, SwiftUI, Flutter) and to design tools (Figma, Figma Make, Claude Design).

AI-generated UI goes wrong in predictable ways. It pattern-matches components it has seen
(tab bars, dropdowns, "Are you sure?") without knowing when they are the right move. These
rules supply the "when".

## How to use

1. **Before building**, read the reference file for what you are making. Most UI needs two or
   three: a form needs `components.md`, `interaction.md`, and `motion.md` for its feedback.
   In each file, scan the **When** lines and apply the rules that match.

   | Building | Read |
   |---|---|
   | Any screen, card, list, or layout | `references/hierarchy.md` |
   | Forms, dialogs, menus, tab bars, buttons, empty states, icons | `references/components.md` |
   | Anything clicked, tapped, or typed into; loading and waiting; links and navigation; what goes where | `references/interaction.md` |
   | Colour, dark mode, radius, gradients, shadows and elevation, typefaces, icon sizes | `references/visual.md` |
   | Transitions, animation, easing, durations, press and error feedback, reduced motion | `references/motion.md` |
   | Tokens, theme files, CSS variables, component props/variants | `references/tokens.md` |
   | Design-system docs, component specs, Figma file structure, layer naming | `references/ai-readiness.md` |
   | Improving pages that already ship (audit, plan, before and after pictures) | `references/enhancing.md` |

2. **The project's own design system wins.** If it already has tokens, components, a radius
   scale, motion tokens, or a brand palette, use them. These rules decide how to apply and
   name things, not which values to replace. Flag conflicts instead of silently rewriting them.
3. **Before handing over**, run the review list below against your output and fix every hit.
   Say which rows you checked.
4. **When reviewing someone else's UI**, report each finding as
   `RULE-ID: what is wrong → the fix`, most severe first. Don't list passes.
5. **When enhancing an existing site or app**, read `references/enhancing.md` first. It gives
   the order: the project's own rules, "before" pictures, the audit, a plan, the changes,
   "after" pictures, then the rules written into the project's design doc. Take the pictures
   with `node scripts/shot.mjs` (headless Chrome, no packages); don't rewrite it each time.

## Review list: AI calling cards

| # | Calling card | Fix | Rule |
|---|---|---|---|
| 1 | An action button (usually a big "+") inside the tab bar | A normal tab, or the action in context on its screen | CMP-1 |
| 2 | A dropdown for 2–7 options | Radio list (single) or chips (multi) | CMP-2 |
| 3 | "Are you sure?" with YES / NO | Verb + noun title, named object, action-labelled buttons | CMP-3 |
| 4 | Two primary buttons side by side | One primary, one secondary or ghost | CMP-6 |
| 5 | Stacked centre-aligned text | One left alignment anchor | HIE-5 |
| 6 | Every stat the same size; labels as loud as values | Hero metric + secondary row | HIE-1, HIE-2 |
| 7 | Boxes inside boxes | White space for grouping, a surface tint for emphasis | HIE-4 |
| 8 | 9+ equal options; an oversized logo at the top | 3–5 options; the primary action (search) at the top | HIE-7 |
| 9 | Some menu items with icons, some without, in two columns | One plain column, grouped and labelled | CMP-4 |
| 10 | Brand colour on buttons, failing contrast | Darkened brand or a separate product colour, ≥ 4.5:1 | VIS-4 |
| 11 | The same radius on nested rounded shapes | outer = inner + padding | VIS-1 |
| 12 | Two-stop gradient with a muddy middle | HSL, one hue, four stops | VIS-3 |
| 13 | Raw hex values; invented token or component names | The system's semantic tokens and real component names | TOK-1, SYS-4 |
| 14 | Hand-drawn or mixed-library icons | One library, one style | CMP-5 |
| 15 | One dissolve for every change; linear easing | Transition chosen by what changed; staged, eased motion | MOT-1, MOT-3, MOT-4 |
| 16 | Colour everywhere: coloured top bar, nav icon, avatar circles, 5+ colours in a section; the primary colour filling labels, step numbers, and bullets | Neutral chrome, two background levels, the primary colour on actions only | VIS-6 |
| 17 | White or light cards on a dark-mode screen | Lighter-toned *dark* surfaces for elevation | VIS-7 |
| 18 | "Sign in" and "Sign up" both primary | Ghost for returning users, primary for new users | CMP-6 |
| 19 | Fractional values (padding 13.5, radius 15.3); one-off unnamed hex | Snap to the scale and the token set | SYS-5 |
| 20 | A bare "No items" empty state | Situation + invitation + one CTA, then an illustration | CMP-7 |
| 21 | Option rows with no visual anchor, or anchors on only some rows | A distinct icon or image leading every row | HIE-9 |
| 22 | Generic labels ("Submit", "Yes", "Get started"); one action worded differently on each page | Verb + object; verb + product + value for sign-up; one wording per action | CMP-8 |
| 23 | Icon-only buttons whose hit area is the glyph (a bare 16px ×) | ≥ 24×24 CSS px, 44×44 on touch, padding around a small icon | INT-2 |
| 24 | `transition: all 0.3s ease` on everything; no reduced-motion branch | Named properties, durations by size, a `prefers-reduced-motion` fallback | MOT-5, MOT-6 |
| 25 | `scale-105` and the biggest shadow on every card's hover; shadows falling different ways | Lift only what's clickable, one step up an elevation scale, one light source | VIS-8 |
| 26 | Placeholder text as the only label; hints that vanish when typing starts | A visible label, and hints that stay beside the field | INT-5 |
| 27 | A submit button with no pending state; a blank page or page-wide spinner while loading | Pending state on press, no double submit; skeletons in the final layout | INT-4 |
| 28 | `div onClick` for navigation; a restyled control that loses its native behaviour | Real `<a href>` and `<button>`; Enter, Esc, Back, and labels work as usual | INT-3 |
| 29 | An error shown only by a red border or a shake | Text and an icon by the field, focus moved there, announced | MOT-8 |
| 30 | `type="number"` or a strict regex on phone, card, or postcode fields | Text input with `inputmode`, formatting stripped, one stored format | INT-6 |
| 31 | Icons sized by eye: heavier or smaller than the label beside them, a different size on each row | Icon box = the label's line height (20 beside 14px text on a 20px line), centred on it, 8px gap, one keyline | VIS-9 |
| 32 | A form with a submit button per job ("Show flights", "Show holidays"); a tab row cut off at the edge | One job and one submit per form; the other job a tab; 3–5 tabs that fit; modes as a segmented control above the fields | CMP-10 |
| 33 | Every field dressed the same (floating label, leading icon, clear ×) at equal gaps; a From/To pair as two unrelated fields | One label per question above its group, the pair joined with a swap button, decoration dropped, more space between groups | HIE-10 |
| 34 | Values shown as stored: `08/09/2026 15/09/2026` | Said the way people say them: `8–15 May`, shared parts once, this year left out, locale-aware | INT-8 |

## Find a rule by principle

The 20 principles of UI design and animation, and where each lives. Rows 1–12 are the classic
animation principles, 13–19 the usability laws, 20 a prioritisation rule. Where a principle
was already covered, the existing rule carries it.

| # | Principle | Rule | Use it when |
|---|---|---|---|
| 1 | Squash and stretch | MOT-7 | A button, card, tile, or toggle is pressed |
| 2 | Anticipation | MOT-12 | A large transition the user triggers, in an expressive product |
| 3 | Staging | MOT-3, HIE-1, CMP-6 | A dialog, sheet, or overlay opens; any view needs one focal point |
| 4 | Pose to pose | MOT-10 | A component has three or more states, or is dragged |
| 5 | Follow through | MOT-11 | A container brings content in (drawer, sheet, menu, list) |
| 6 | Slow in and slow out | MOT-4 | Anything moves, resizes, enters, or leaves |
| 7 | Arcs | MOT-13 | An object travels to a destination on both axes (add to cart) |
| 8 | Secondary action | MOT-9 | An action's result completes, or lands elsewhere on screen |
| 9 | Timing | MOT-5 | Every animation |
| 10 | Exaggeration | MOT-8 | An error, a failure, or a high-stakes success that must not be missed |
| 11 | Solid drawing (depth) | VIS-8 | Anything floats above the page (hover lift, menu, dialog) |
| 12 | Appeal | The review list; VIS-2, VIS-6, CMP-5, SYS-5 | The final pass before handing over: appeal is coherence, not decoration |
| 13 | Fitts's Law | INT-1 | Placing primary, frequent, and destructive actions |
| 14 | Bigger hit areas | INT-2 | Any icon button or small control |
| 15 | Hick's Law | HIE-7 | One level of a screen offers more than five choices |
| 16 | Miller's Law | INT-5 | Long forms, multi-step flows, codes and IDs to copy |
| 17 | Doherty Threshold | INT-4 | Anything that waits on the network or on computation |
| 18 | Postel's Law | INT-6, INT-8 | Phone, card, date, amount, email, and code fields; dates and counts shown back |
| 19 | Jakob's Law | INT-3 | Navigation, links, auth, search, cart; any custom control |
| 20 | Frequency of use | INT-7 | Deciding what is one click away and what goes in Settings |
| + | Reduced motion | MOT-6 | Every animation |
| + | Testable standards | SYS-6 | Documenting a component in a design system |

**What to get right first** in a typical app: targets and conventions (INT-1, INT-2, INT-3);
then focus, choices, and memory (MOT-3, HIE-7, INT-5); then response, input, and frequency
(INT-4, INT-6, INT-7); then easing, timing, and feedback (MOT-4 to MOT-9). The rest of motion
(MOT-10 to MOT-13) and depth (VIS-8) are situational.

## Rule index

**Hierarchy & layout**, in `references/hierarchy.md`
- HIE-1 One primary element per group; build hierarchy with weight and colour, not only size.
- HIE-2 Lead with a hero metric; small muted labels above strong values.
- HIE-3 Remove duplicates; compress meta onto one line with a `·` separator.
- HIE-4 Group with white space and a surface tint, not boxes inside boxes.
- HIE-5 One alignment anchor per block; left-align multi-line text.
- HIE-6 Group by proximity: tighter inside a group than between groups.
- HIE-7 Show 3–5 choices with the most important first; group the rest (Hick's Law).
- HIE-8 Design for the scroll, not a fixed phone frame.
- HIE-9 Lead every option row with a distinct visual anchor.
- HIE-10 Lay out a form by its questions: one label per group, pairs joined, no per-field decoration.

**Component choice**, in `references/components.md`
- CMP-1 The tab bar is navigation only; no action button in it.
- CMP-2 2–7 options → radios; multi-select → chips; dropdowns only for long lists.
- CMP-3 Confirmation dialogs: verb + noun title, the named object, action-labelled buttons.
- CMP-4 Mobile menus: one plain column, grouped under labels.
- CMP-5 One established icon library at one style.
- CMP-6 One primary button per group; ghost + primary for sign in / sign up.
- CMP-7 Empty states: situation, invitation, one CTA, then an illustration.
- CMP-8 Button labels: verb + object; verb + product + value for sign-up CTAs.
- CMP-9 One card with a variant picker, not a card per variant.
- CMP-10 A form does one job: one submit, sibling jobs as tabs, modes as a segmented control above the fields.

**Interaction & usability**, in `references/interaction.md`
- INT-1 Make important targets big and close; keep destructive ones apart (Fitts's Law).
- INT-2 Hit areas ≥ 24×24 CSS px, 44×44 on touch, however small the icon.
- INT-3 Follow the conventions users know; real links, native behaviour (Jakob's Law).
- INT-4 Acknowledge every action at once; progress past 400 ms (Doherty Threshold).
- INT-5 Don't make users remember: visible labels, kept input, chunks (Miller's Law).
- INT-6 Accept input in the shapes people type; store one format (Postel's Law).
- INT-7 The more often an action is used, the closer it sits (frequency of use).
- INT-8 Show values the way people say them: `8–15 May`, not `08/09/2026 15/09/2026`.

**Visual craft**, in `references/visual.md`
- VIS-1 Nested corner radius: outer = inner + padding.
- VIS-2 Radii come from a small scale and stay consistent per component.
- VIS-3 Gradients in HSL: one hue, four stops.
- VIS-4 Action colours pass 4.5:1; the brand colour isn't automatically the action colour.
- VIS-5 Choose type by anatomy; micro-test at real UI sizes.
- VIS-6 Less colour: neutral chrome, two background levels, one primary colour.
- VIS-7 Dark mode: no light surfaces; elevate with lighter shades of dark.
- VIS-8 Depth: one light source, elevation from a scale; only clickable things lift (solid drawing).
- VIS-9 Size icons from the text beside them: the box is the line height, 8px to the label, one keyline.

**Motion**, in `references/motion.md` (starts with a "which rules apply" table)
- MOT-1 Pick the transition by what changed: context, drill, or continuity.
- MOT-2 Motion communicates; it never just decorates.
- MOT-3 Stage motion: fixed controls fade, the primary element scales in, a scrim behind overlays (staging).
- MOT-4 Ease-in-out for size and position, ease-out in, ease-in out; never linear (slow in and slow out).
- MOT-5 Durations by size and distance, from tokens; never block input (timing).
- MOT-6 Respect reduced motion; never carry meaning in motion alone.
- MOT-7 Pressable controls compress to about 0.97 on press (squash and stretch).
- MOT-8 Exaggerate only what must not be missed, always with text (exaggeration).
- MOT-9 One small secondary cue confirms the result (secondary action).
- MOT-10 Design the rest states first; snap between them (pose to pose).
- MOT-11 Content settles just after its container; short, capped staggers (follow through).
- MOT-12 A small wind-up before a large transition, started on press (anticipation).
- MOT-13 Objects travelling to a destination move in an arc (arcs).

**Tokens & component API**, in `references/tokens.md`
- TOK-1 Hex → primitive → semantic; components use semantic tokens only.
- TOK-2 Name semantic colours `color-{element}-{priority}-{state}`.
- TOK-3 Light and dark are modes of the semantic layer.
- TOK-4 Component names follow `Base / Purpose / Size / State`.
- TOK-5 Design properties match code props: `variant`, `tone`, `size`.

**Design-system AI readiness**, in `references/ai-readiness.md`
- SYS-1 Name every layer and frame by its role.
- SYS-2 Use a standard file name, status, and page order.
- SYS-3 Make wrong tokens fail the build.
- SYS-4 Give agents machine-readable docs (an MCP server or a skill).
- SYS-5 Every value comes from a scale: no fractions, no unnamed hex.
- SYS-6 Every interactive component documents target size, keyboard, focus, loading, error, motion, and reduced motion.

## Numbers to remember

- Nested radius: `outer = inner + padding` (12 + 8 = 20, 24 + 16 = 40).
- Contrast for buttons and links: ≥ 4.5:1.
- Radio buttons for 2–7 options; 3–5 visible choices in a launcher; 3–5 tabs, none cut off; one submit button per form.
- Gradient stops: light source 0%, hold ~40%, falloff ~65%, anchor 100%, all at one hue.
- Token name: `color-{bg|bg-surface|bg-fill|text|border|icon}-{primary|secondary|tertiary}-{default|hover|active|disabled}`.
- Component name: `Button / Secondary / Large / Default`. Props: `variant` (emphasis), `tone` (intent), `size` (sm | md | lg).
- Hit area: ≥ 24×24 CSS px (WCAG 2.2 AA); 44×44 pt on iOS, 48×48 dp on Android.
- Icon beside text: the icon's box is the label's line height (14px text on a 20px line → 20 × 20), centred on the line, 8px to the label.
- Durations: press 100–150 ms, small surfaces 150–200, dialogs and sheets 250–300, full screen 300–400, never over 500. Exits about a fifth shorter.
- Response: acknowledge at once; spinner only after ~300 ms; progress past 1 s; background past 10 s.
- Press scale ~0.97; stagger 20–40 ms per item, the whole list in within ~200 ms; an error shake under 10px, ~300 ms, once.

## Gotchas

- **Motion principles are a menu, not a quota.** Told about the 12 principles, an agent tends to
  put all of them on one button. Use the "Which motion rules apply" table in `motion.md`;
  dense, daily-use tools skip MOT-12 and MOT-13 and keep durations short.
- **Fewer choices, not fewer frequent ones.** HIE-7 shrinks what is visible and INT-7 decides
  what survives. Never hide a frequent action to get down to five, and never make a
  destructive action big and close just because it is primary somewhere else (INT-1).
- **Icons in lists:** CMP-4 removes icons from navigation menus, and HIE-9 adds them to option
  lists. These don't conflict. Navigation menus are scanned by label; comparison lists (ride
  types, plans, payment methods) are scanned by shape. In both cases the rule is all rows or
  none.
- **Group labels and INT-5.** HIE-10 lifts labels from each field to its group, and the reel's
  final form shows From and To with no visible label. That is fine only where the order is a
  convention people know (origin before destination, start before end) and each field keeps an
  accessible name. In a long or unfamiliar form INT-5 wins: every field keeps a visible label.
- **Centre alignment** is allowed for one short block: an empty state or a hero headline.
  Everything multi-line is left-aligned.
- **Brand colour** still belongs in the product (illustration, accents, a header surface tint).
  VIS-4 only keeps it off buttons and links when it fails contrast.
- **Don't fix what isn't in scope.** When asked to change one component, apply the rules to that
  component and *mention* other violations rather than rewriting the page.
- **A rule hit may be a recorded decision.** Before changing one, look for a dated comment or
  a test that pins it. A sign-in page kept two filled buttons because first-time users
  arriving from a QR code could not find a quiet sign-up link; a test said so. Keep it, and
  report it as kept, with the reason.
- **Copy is often pinned by tests.** Search the tests for a label before rewording it, and
  update the assertion to the new intended wording, not to whatever renders.
- **Nested radius against a radius scale.** VIS-1's sum (outer = inner + padding) is easy to
  honour when the shapes sit close together (a segmented control, a picture in a padded
  well). At 24px of padding it asks for a radius most scales don't have. When the project has
  a scale (VIS-2), the scale wins there: apply VIS-1 where both radii land on it.
- **Judge the rendered page, not the JSX.** A centred six-line paragraph, a hole left in a
  card after its buttons were removed, and nine accent chips out-shouting one button are all
  invisible in code review. Take pictures before and after (`scripts/shot.mjs`). Motion is
  invisible in a still: check durations and the reduced-motion branch in the code.
- **Not covered here:** spacing and type scale values, focus styles and tab order, error-message
  wording beyond INT-6, and breakpoints. Use the platform guidelines (WCAG 2.2, Apple HIG,
  Material 3) for those.

## Credits

Distilled from the public UI design reels of Memorisely (memorisely.com), April–November 2026,
and rewritten as checkable rules; a rule a reel teaches links it on a **Watch** line. The 20-principle list (MOT-5 to MOT-13, VIS-8, INT-1 to
INT-7, and extensions to HIE-7, MOT-3, and MOT-4) follows a summary by Charles Liu, built on the
12 principles of animation (Frank Thomas and Ollie Johnston, *The Illusion of Life*, 1981) and
the usability laws collected at Laws of UX (lawsofux.com). Product examples (Uber, Airbnb,
Revolut, Mailchimp, Headspace, Material Design 3, Atlassian, Polar) are cited as public
references, not endorsements.
