# Hierarchy & layout (HIE)

Rules for what users see first, how content groups, and how much they must choose between.

Each rule: **Why** it matters, then **Check**, what to verify in a design or in code.

**HIE-1 One primary element per group; build hierarchy with weight and colour, not only size.**
Why: if everything is emphasised, nothing is.
Check: each card or section has exactly one dominant element (name, title, or hero metric). Secondary text steps down in weight *and* colour. Bigger isn't automatically better. On a profile card the avatar was shrunk and moved beside the name to free up space.

**HIE-2 Lead with a hero metric; values beat labels.**
Why: equal stats increase cognitive load; users come back for the number, not the label.
Check: one hero metric is large (`35m 37s`, with the units `m`/`s` smaller and lighter than the digits). Secondary metrics sit in a row below as `label (small, muted)` above `value (strong)`. Use a comparable number (`★ 4.85`) instead of a row of star icons. Stack each label with its value so pairs read together.

**HIE-3 Cut and compress before you style.**
Why: hierarchy is easier when there is less to rank.
Check: no fact appears twice. Meta is compressed onto one scannable line with a soft `·` separator (`Lunch run · 1 day ago`). Captions and bios are capped at about two lines and still pass contrast. Context that belongs to a visual moves onto it (a location label on the map instead of in a metadata list).

**HIE-4 Use content layout, not container layout.**
Why: using containers for layout makes a boxy UI full of visual noise.
Check: no bordered or filled box inside a card unless it is interactive. Groups are formed by white space. Emphasis comes from one surface tint on a region (e.g. the header), and that tint can carry the brand colour. Verify in dark mode.

**HIE-5 Use one alignment anchor per block; left-align multi-line text.**
Why: stacked centre-aligned lines give every line a different start point ("too many alignment anchors"), which makes reading hard.
Check: within a card, list, form, or menu, title, body, meta, and CTA share one left edge. In a modal, content gets one anchor and actions get another, each used consistently. Centre alignment is only for a single short line (empty state, hero headline). Decorative icons on *some* items break the anchor, so remove them or give every item one.

**HIE-6 Group by proximity.**
Why: distance is the strongest grouping signal.
Check: spacing inside a group is smaller than spacing between groups. Product card order: heading + image (a carousel if there are several images), then price + CTA together. Fine print is trimmed, not wedged between the title and the CTA. Tighten spacing until each group reads as one unit.

**HIE-7 Show 3–5 choices with the most important first (Hick's Law).**
Why: decision time grows with the number of choices, so more buttons means fewer clicks on any of them.
Check: a launcher or menu shows 3–5 primary options. The rest go behind "More". The remaining options have consistent label length, colour, and shape. The top of the screen goes to the primary action (e.g. search), not an oversized logo when the context is already clear.

**HIE-8 Design for the scroll, not a fixed phone frame.**
Why: designing inside a fixed iPhone frame treats the screen like a poster and squeezes the UI.
Check: mobile screens are auto-height or flowing layouts. Check the first viewport separately for what must sit above the fold (image, title, price, primary action).

**HIE-9 Lead every option row with a visual anchor.**
Why: users recognise shape before they read text. Strip the vehicle images from Uber's ride list and people have to read every block to compare options; with them, they scan vertically and decide faster.
Check: in a list of comparable options (ride types, plans, payment methods, categories), every row starts with an icon or image in the same position and size, and each one is distinct. All rows or none: a partial set breaks the alignment anchor (see CMP-4).
