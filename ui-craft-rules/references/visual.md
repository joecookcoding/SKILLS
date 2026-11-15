# Visual craft (VIS)

Rules for corner radius, colour, gradients, dark mode, type, depth, and icon size.

Each rule: **When** to apply it, **Why** it matters, then **Check**, what to verify in a design
or in code. Where a reel teaches the rule, a **Watch** line links it (Facebook may ask you to
sign in).

**VIS-1 Nested corner radius: outer = inner + padding.**
When: a rounded element sits inside a rounded container (an image in a card, a button in a pill, a segmented control).
Why: putting the inner radius on the outer shape too leaves an awkward, uneven gap at the corners. macOS 26 Tahoe shipped with this inconsistency.
Check: for any rounded element inside a rounded container, `outer = inner + padding`. This holds at every density: 12 + 8 = 20 (tight), 16 + 20 = 36, 20 + 24 = 44, 24 + 16 = 40, 24 + 32 = 56 (loose). In CSS: `border-radius: calc(var(--inner) + var(--pad))`.

**VIS-2 Corner radii come from a small scale and are consistent per component.**
When: setting the radius of any component, or adding a new component type.
Why: one radius rule applied everywhere is a large part of why a product feels premium.
Check: the same component type always has the same radius whatever its contents (Tahoe's windows changed radius depending on whether a toolbar was present). Airbnb's scale as a reference: buttons 8px, property cards 14px, search bar fully rounded (pill), and square corners only on the image grid.

**VIS-3 Gradients: HSL, one hue, four stops.**
When: making any gradient (backgrounds, hero art, buttons, illustrations).
Why: a two-stop dark-to-light gradient passes through a grey limbo and looks muddy.
Check: every stop has the same hue; only saturation and lightness move. The four stops are **light source** (highest S and L, 0%), **hold** (~40%), **falloff** (~65%), and **anchor** (darkest, 100%). Change the light-source angle to suit the layout. To build a gradient palette, change only the hue. In CSS, prefer `linear-gradient(in oklch, …)`.

**VIS-4 The brand colour is not automatically the action colour.**
When: choosing a button or link colour, especially from a brand palette.
Why: brand colours (orange, yellow) often fail contrast on buttons.
Check: every button and link colour is ≥ 4.5:1 against its text and background. If the brand colour fails, darken it (lower brightness, raise saturation) or pick a complementary "primary product" colour from the colour wheel. Keep the brand colour for accents and illustration. Worked example: a brand orange failed; a darkened orange passed at 5.2:1 and a complementary blue at 5.4:1. Mailchimp, Headspace, and Airbnb do this.

**VIS-5 Choose type by anatomy, then micro-test.**
When: choosing a typeface or a type pairing.
Why: choosing by the font-picker preview means choosing on vibe.
Check: compare x-height and ascender height (balance at small sizes), descender height (readability in dense text), open counters (legibility when small), and the horizontal strokes on letters like T. Then run micro-tests: render the candidates at real UI sizes, side by side on a shared baseline, and run a kerning test on awkward pairs (Ty, ra, og) for gaps or collisions.

**VIS-6 Less colour, more clarity.**
When: colouring any screen, and before giving a top bar, nav icons, avatars, chips, labels, or step numbers their own colour.
Why: competing colours are noise, not personality. The more colours you add, the less any one of them means; a neutral base gives the primary colour somewhere to stand out.
Check:
- A screen section uses two background levels: the background and one elevated surface. Not a different colour per block.
- No heavy block colour behind content; use a light elevated surface and put the accessible primary colour only on the main action.
- Chrome is neutral: tab-bar icons share one neutral colour (selected state aside), and avatar placeholders are neutral or the user's photo, not a brand-colour circle.
- Category chips do not each get their own colour.
- The primary colour's *fill* is for actions and for state (selected, in progress). A label, a step number, or a bullet filled with it competes with the button: nine accent chips on a page make its one accent button the least noticeable thing there. Use a neutral surface or the text colour for those.
- The top bar and the tab bar are in the same mode (both light or both dark).

**VIS-7 Dark mode: one mode per screen, elevation by lighter dark.**
When: building or reviewing a dark theme.
Why: a light card on a dark screen mixes modes and reads as broken.
Check: in dark mode no surface is light. Hierarchy comes from progressively lighter-toned *dark* surfaces (background < card < raised element). The primary button may invert (light fill, dark text); everything else stays dark. Never mix light and dark sections on one screen.

**VIS-8 Depth: one light source, elevation from a scale (solid drawing).**
When: anything that floats above the page: cards that lift on hover, menus, popovers, dropdowns, dialogs, sheets, sticky headers, and drag previews.
Why: consistent depth tells users what sits above what and what can be picked up. Shadows that point different ways, or a lift on everything, read as noise. Depth is for hierarchy; the interface doesn't need to look 3D.
Check:
- A small elevation scale (about four levels) maps to roles: resting card, raised or hovered, menu and popover, dialog and sheet. Each level is a shadow token (`--ds-shadow-1`…`--ds-shadow-4`), never an ad hoc `box-shadow`.
- All shadows fall the same way (light from above, offset downward). A shadow pairs a tight, darker contact layer with a larger, softer ambient layer, and both grow with the level.
- Only clickable things lift on hover: one level up and about 2px up (`translateY(-2px)`), in 150–200 ms. Not `scale(1.05)` with the largest shadow on every card; a lift promises a click.
- In dark mode shadows barely show, so elevation comes from lighter surfaces (VIS-7).
- One depth cue per element: not a border, a heavy shadow, and a tint on the same card (HIE-4). Perspective and 3D tilt only where they mean something (a card flipping over), never as decoration.

**VIS-9 Size icons from the text beside them.**
When: an icon sits next to a label: navigation items, menu and list rows, buttons, chips, form hints.
Why: an icon sized by eye ends up too big and heavy, or too small to read, and a little different on every row. AI-generated UI hard-codes these sizes, so a list feels slightly off without anyone knowing why.
Check:
- Set the label's line height on the 4px grid first (14px text on a 20px line), then make the icon's box that line height (20 × 20) and centre it on the line. In CSS, `width: 1lh; height: 1lh` keeps the two tied when the text size changes.
- 8px between the icon and its label.
- The icons in a list share one left keyline, and every row has an icon or none does (HIE-5, HIE-9). The row's padding comes from the same 4px grid (SYS-5).
- The icon's box is not its hit area: an icon-only button still needs INT-2's target around it.
Watch: [Memorisely, 2026-11-13](https://www.facebook.com/share/r/1A7Z25DQ5S/): a sidebar's icons snapped to a 20px line height, on one keyline, 8px from their labels.
