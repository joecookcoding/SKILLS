# Enhancing an existing site or app

For "improve / enhance / polish this site with the rules": several pages that already ship,
not one new component. The order matters, because the cheapest mistake to make here is
undoing something the owner decided on purpose.

## 1. Read the project's own rules first

Find them before judging anything: a design doc (`DESIGN.md`, a tokens file, a Storybook), the
shared components, and the lint rules that guard them. Then look for **recorded decisions**:
dated comments ("owner, 2026-09-13: …"), and tests that pin copy or layout. A page that breaks
a rule here may be breaking it on purpose.

## 2. Take the "before" pictures

Capture the pages as they are, from the deployed or staging site when it matches the code you
are about to change: `node scripts/shot.mjs --base <origin> --out shots/before / /pricing …`.
Take the first viewport and the full page, at a desktop width and at 390px, and in dark mode
if the product has one. Look at the pictures. Reading JSX finds raw hex and two primary
buttons; only the rendered page shows a paragraph centred over six lines or nine lime chips
out-shouting one button.

## 3. Audit against the review list

Go page by page down the 22 rows in `SKILL.md`, then the reference file for anything the page
is mostly made of (forms → `components.md`). Write each finding as
`RULE-ID: what is wrong → the fix`, and sort them into three piles:

- **Fix**: a clear hit, no recorded decision against it.
- **Keep, and say so**: a hit that a recorded decision explains. The project wins; name the
  decision in the report so the owner can reopen it.
- **Needs something you don't have**: a picture for a card that lacks one, a real brand
  asset, a product decision (which CTA is the main one). Ask; write the brief if it is an
  image.

## 4. Give the plan before the diff

A short table: finding, rule, fix, pages touched. Lead with the changes that repeat across
pages (header buttons, one CTA wording, accent use), because one change to a shared component
fixes them everywhere. Prefer changing the shared component over each call site.

## 5. Make the changes the project's way

Use its components and tokens; add a variant or prop to a shared component instead of
restyling at the call site. Before changing a label, search the tests for it: copy is often
pinned, and the test tells you whether the wording was a decision. Follow the project's test
and lint rules, and run its gates.

## 6. Take the "after" pictures, same pages, same sizes

Build the changed site and capture into `shots/after` with the same paths and widths, so each
pair is comparable. Look at every pair: a fix often exposes the next problem (a callout that
loses its buttons now has a hole at the bottom). Show the pairs that changed most, side by
side, with the rule each one answers.

## 7. Write the rules into the project's design doc

Add what was decided to the project's own design document, in its words and with its
component names: the rule, why, the component that carries it, and every place the project
keeps its own answer instead. Rules that live only in a skill are forgotten by the next
person; rules in the design doc are held by review.

## What to report

1. The plan table (finding → rule → fix).
2. Before and after pictures for the pages that changed.
3. What was kept on purpose, and why.
4. What is waiting on the owner: images, decisions.
5. Which checks ran and what they said.
