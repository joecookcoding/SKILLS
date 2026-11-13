---
name: ui-craft-rules
description: UI/UX craft rules for building, generating, or reviewing web and mobile screens in code or Figma. Use when building or critiquing a page, card, form, modal, menu, tab bar, button, or empty state; when asked to polish a UI or make it look less AI-generated or templated; or when setting up design tokens, dark mode, or component naming. Includes a 22-point review list of AI-generated UI tells.
---

# UI Craft Rules

39 rules for interface craft, each written as something you can check, plus a review list of
the fingerprints AI-generated UI leaves behind. They apply to any stack (React, HTML/CSS,
SwiftUI, Flutter) and to design tools (Figma, Figma Make, Claude Design).

AI-generated UI goes wrong in predictable ways. It pattern-matches components it has seen
(tab bars, dropdowns, "Are you sure?") without knowing when they are the right move. These
rules supply the "when".

## How to use

1. **Before building**, read the reference file for what you are making:

   | Building | Read |
   |---|---|
   | Any screen, card, list, or layout | `references/hierarchy.md` |
   | Forms, dialogs, menus, tab bars, buttons, empty states, icons | `references/components.md` |
   | Colour, dark mode, radius, gradients, typefaces | `references/visual.md` |
   | Transitions, animation, easing | `references/motion.md` |
   | Tokens, theme files, CSS variables, component props/variants | `references/tokens.md` |
   | Design-system docs, Figma file structure, layer naming | `references/ai-readiness.md` |
   | Improving pages that already ship (audit, plan, before and after pictures) | `references/enhancing.md` |

2. **The project's own design system wins.** If it already has tokens, components, a radius
   scale, or a brand palette, use them. These rules decide how to apply and name things, not
   which values to replace. Flag conflicts instead of silently rewriting them.
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

## Rule index

**Hierarchy & layout**, in `references/hierarchy.md`
- HIE-1 One primary element per group; build hierarchy with weight and colour, not only size.
- HIE-2 Lead with a hero metric; small muted labels above strong values.
- HIE-3 Remove duplicates; compress meta onto one line with a `·` separator.
- HIE-4 Group with white space and a surface tint, not boxes inside boxes.
- HIE-5 One alignment anchor per block; left-align multi-line text.
- HIE-6 Group by proximity: tighter inside a group than between groups.
- HIE-7 Show 3–5 choices with the most important first (Hick's Law).
- HIE-8 Design for the scroll, not a fixed phone frame.
- HIE-9 Lead every option row with a distinct visual anchor.

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

**Visual craft**, in `references/visual.md`
- VIS-1 Nested corner radius: outer = inner + padding.
- VIS-2 Radii come from a small scale and stay consistent per component.
- VIS-3 Gradients in HSL: one hue, four stops.
- VIS-4 Action colours pass 4.5:1; the brand colour isn't automatically the action colour.
- VIS-5 Choose type by anatomy; micro-test at real UI sizes.
- VIS-6 Less colour: neutral chrome, two background levels, one primary colour.
- VIS-7 Dark mode: no light surfaces; elevate with lighter shades of dark.

**Motion**, in `references/motion.md`
- MOT-1 Pick the transition by what changed: context, drill, or continuity.
- MOT-2 Motion communicates; it never just decorates.
- MOT-3 Stage motion: fixed controls fade, the primary element scales in, secondary surfaces follow.
- MOT-4 Ease-in-out for size and position, ease-out for arrivals; never linear.

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

## Numbers to remember

- Nested radius: `outer = inner + padding` (12 + 8 = 20, 24 + 16 = 40).
- Contrast for buttons and links: ≥ 4.5:1.
- Radio buttons for 2–7 options; 3–5 visible choices in a launcher; 3–5 tabs.
- Gradient stops: light source 0%, hold ~40%, falloff ~65%, anchor 100%, all at one hue.
- Token name: `color-{bg|bg-surface|bg-fill|text|border|icon}-{primary|secondary|tertiary}-{default|hover|active|disabled}`.
- Component name: `Button / Secondary / Large / Default`. Props: `variant` (emphasis), `tone` (intent), `size` (sm | md | lg).

## Gotchas

- **Icons in lists:** CMP-4 removes icons from navigation menus, and HIE-9 adds them to option
  lists. These don't conflict. Navigation menus are scanned by label; comparison lists (ride
  types, plans, payment methods) are scanned by shape. In both cases the rule is all rows or
  none.
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
  invisible in code review. Take pictures before and after (`scripts/shot.mjs`).
- **Not covered here:** spacing and type scale values, focus and keyboard states,
  touch-target sizes, loading and error states, form validation copy, breakpoints, and reduced
  motion. Use the platform guidelines (WCAG 2.2, Apple HIG, Material 3) for those.

## Credits

Distilled from the public UI design reels of Memorisely (memorisely.com), April–November 2026,
and rewritten as checkable rules. Product examples (Uber, Airbnb, Revolut, Mailchimp,
Headspace, Material Design 3, Atlassian, Polar) are cited as public references, not
endorsements.
