# Component choice (CMP)

Rules for picking the right component or pattern, and the copy on it.

Each rule: **Why** it matters, then **Check**, what to verify in a design or in code.

**CMP-1 The tab bar is for navigation only.**
Why: an action in the tab bar breaks the bar's symmetry, creates tension between the two groups of tabs, and is ambiguous (does "+" add money? add a card?). AI does this because it has seen tab bars, not learned when they are misused.
Check: every item navigates to a destination and has a selected state, all in one continuous style. No FAB or "+" embedded in the bar. Replace it with a normal tab (e.g. "Send") or put the action in context on its screen. 3–5 tabs. (Revolut, Airbnb, Spotify, and Strava all follow this.)

**CMP-2 Don't default to dropdowns.**
Why: dropdowns hide choices and have a high interaction cost. AI picks them because they handle any count and compress well.
Check: single choice from 2–7 options → radio list. Multi-select from a known set → selectable chips that keep the selections visible. Dropdown or combobox only for long or unknown-length lists. Phrase the field label as a question with intent ("How large is your team?", not "Team size").

**CMP-3 Confirmation dialogs say exactly what will happen.**
Why: "Are you sure?" tells users nothing and adds a click.
Check:
- Title = verb + noun: "Delete file?", "Remove member?"
- Body names the object and the consequence: "This will permanently delete "Project brief.pdf". This action cannot be undone."
- Buttons are labelled with the action (`Cancel` · `Delete file`), never Yes/No/OK, and never ALL CAPS.
- Order: secondary then destructive, with the destructive button in the danger colour on the trailing side.
- Three blocks: header (title + dismiss ×), body, actions. Remove decorative icons (a "?" glyph adds nothing).
- Left-aligned, with separate anchors for content and actions.
- The body is short and informs rather than asks: "This can't be undone", not "Are you really sure you want to…".
- The secondary action lets the user continue their journey: `Cancel`, not `Discard`. For unsaved work: "Discard unsaved changes?" with `Keep editing` · `Discard`.
- Check it in dark mode.

**CMP-4 Mobile menus: one boring column.**
Why: multi-column menus save vertical space but are slower to scan and have inconsistent anchors. Boring lists are fast.
Check: a single vertical list; icons removed unless every item has one; gaps tightened; long lists grouped into categories with small section labels. Use one control in one position that changes state (☰ ↔ ×), not separate open and close controls in different places.

**CMP-5 Use an established icon library; don't draw icons.**
Check: all icons come from one library at one style (e.g. Lucide, Heroicons, Phosphor, or Untitled UI Icons; 3dicons for 3D illustration). Outline and solid are not mixed within a control set unless solid marks the selected state. On a React/shadcn stack, prefer Lucide so design and engineering use the same set.

**CMP-6 One primary button per view or group.**
Why: two primary buttons leave users unsure which action is the main one, and overusing primaries flattens hierarchy.
Check: with two actions, one is primary and the other secondary or ghost, side by side when space allows. In auth headers, the returning-user action (`Sign in` / `Log in`) is a ghost button and the new-user action (`Sign up`) is primary.

**CMP-7 Empty states invite the first action.**
Why: an empty screen is the first moment of a feature; a bare "No items" wastes it.
Check: write the copy first. Title states the situation in the user's terms ("You don't have any sushi"), one line invites the first step ("Feeling hungry? Order your first sushi roll to get started."), and one primary CTA names it ("Order sushi"). Then add an illustration in the product's illustration style, optionally with subtle motion. Centre alignment is fine here (single short block).

**CMP-8 Button labels: verb + object.**
Why: a label that names the action removes the need to read the surrounding text.
Check: labels start with a verb and name what they act on (`Delete file`, `Order sushi`, `Remove member`). Acquisition CTAs on a free tier use **verb + product + value** (`Get Claude free`). Never `Yes`/`No`/`OK`/`Submit`, never ALL CAPS. One action has one wording across the product: "Start a trial", "Start a pilot", and "Start your free trial" on three pages read as three offers. Keep the label in one constant, with a short form for tight spaces such as a header.

**CMP-9 One card with a variant picker, not a card per variant.**
Why: duplicate cards for each colour or model make users compare near-identical blocks.
Check: product variants (colour, size, trim) are a swatch or segmented picker inside one card that updates the image and details in place.
