# Interaction & usability laws (INT)

Rules for how fast and how surely people can reach, read, type into, and repeat what a screen
offers. Most come from named usability laws; Hick's Law lives in `hierarchy.md` as HIE-7.

Each rule: **When** to apply it, **Why** it matters, then **Check**, what to verify in a design
or in code. Where a reel teaches the rule, a **Watch** line links it (Facebook may ask you to
sign in).

| You are building or reviewing | Rules |
|---|---|
| Where the main action goes; toolbars; row actions | INT-1, INT-7 |
| Icon buttons, checkboxes, chips, close ×, anything small and clickable | INT-2 |
| Headers, navigation, links, auth, search, cart; a custom control | INT-3 |
| Submit, save, search, upload, generate, payment: anything that waits | INT-4 |
| Long forms, multi-step flows, codes and IDs | INT-5 |
| Phone, card, date, postcode, amount, email, one-time-code fields | INT-6 |
| What sits on the home screen or toolbar versus Settings; daily-use tools | INT-7 |

**INT-1 Make important targets big and close (Fitts's Law).**
When: placing a screen's primary action, a form's submit button, toolbar and table-row actions, mobile bottom actions, and controls used one after another.
Why: the time to hit a target grows with its distance and shrinks with its size (Paul Fitts, 1954). Small, far targets cost time and cause miss-clicks.
Check:
- The primary action is the largest control in its group and sits where the user's attention ends: after the last field of a form, or within thumb reach at the bottom of a mobile screen.
- Controls used in sequence sit together (Previous · Next, Cancel · Save).
- Menus and popovers open next to their trigger; context menus open at the pointer.
- A row that opens something is clickable across its whole width, not only on its text.
- Fitts cuts both ways: what is easy to hit is easy to hit by mistake. Destructive actions sit apart from frequent ones, separated by space or moved into an overflow menu.

**INT-2 Hit areas: at least 24×24 CSS px, 44×44 on touch, however small the icon.**
When: every icon-only button (close ×, kebab, edit, favourite), checkbox, radio, switch, chip, stepper, pagination link, and table-row action; any controls closer than 8px apart.
Why: this is Fitts's Law applied to small controls. The visible glyph can stay small; the area that responds to a tap can't.
Check:
- Every target is ≥ 24×24 CSS px, or spaced so a 24px circle centred on it overlaps no other target or circle (WCAG 2.2 SC 2.5.8, AA). Exceptions: links inside a sentence, a control with an equivalent elsewhere on the page, browser-native controls, and sizes that are essential.
- On touch, aim for 44×44 pt (Apple HIG) or 48×48 dp (Material 3). 44×44 CSS px is WCAG's enhanced level (SC 2.5.5, AAA).
- Grow the button, not the icon: a 20px icon in a 44×44 button. When the layout can't grow, extend the target invisibly with `position: relative` and `::after { content: ""; position: absolute; inset: -10px; }`.
- Extended hit areas don't overlap each other.
- A checkbox's or radio's label is part of its target (`<label>` wraps the input or points at it with `for`).

**INT-3 Follow the conventions users already know (Jakob's Law).**
When: headers and navigation, links, sign-in and sign-up, search, cart and checkout, form controls, and any time a design invents a new interaction or restyles a native control.
Why: users spend most of their time in other products, so they expect yours to work the same way (Jakob Nielsen). A familiar pattern costs nothing to learn. In enterprise and government tools learnability beats novelty.
Check:
- The logo sits top left and links home; search sits near the top; account and cart sit top right.
- Links look like links (underlined in body text) and navigate with a real `<a href>`, so middle-click, open in new tab, and copy link work. Actions are `<button>`s. No `div onClick` for either.
- Native behaviour survives restyling: clicking a label toggles its checkbox, Enter submits a form, Esc closes a dialog or menu, the browser Back button goes back (in single-page apps too), and scroll position is restored on return.
- Platform gestures work: edge-swipe back on iOS, the system Back on Android.
- A new interaction ships only when it clearly beats the convention for this task. Teach it in place with a hint, and keep a conventional fallback.

**INT-4 Acknowledge every action at once; show progress past 400 ms (Doherty Threshold).**
When: any action that waits on the network or on computation: submit, save, search, filter, generate, upload, payment, and route changes that fetch data.
Why: people stay engaged when the system answers within about 400 ms (Doherty and Thadani, 1982). At 0.1 s a response feels instant, at 1 s the flow holds, and at 10 s attention is gone (Nielsen). The backend doesn't have to be that fast; the acknowledgement does.
Check:
- The press shows at once (MOT-7). In the same frame the button enters a pending state: disabled against a double submit, with a spinner or "Saving…", and the same width.
- Short waits get an inline indicator that appears only after ~300 ms, so fast responses don't flash a spinner.
- Content loads into a skeleton shaped like the final layout (nothing shifts when it arrives), not a page-wide spinner.
- Waits of 1–10 s show progress, determinate (a percentage or steps) when it can be measured.
- Past ~10 s the user can leave and keep working: run it in the background and notify on completion.
- Optimistic UI only for reversible actions that nearly always succeed (like, star, reorder, toggle, mark as read); on failure, roll back and say so. Payments, permanent deletions, and messages that can't be recalled show the real result.

**INT-5 Don't make users remember (Miller's Law).**
When: forms longer than one screen, multi-step flows (checkout, onboarding, wizards), comparisons across screens, and any code, ID, or number a user must read here and type elsewhere.
Why: working memory holds only a few chunks at once (George Miller, 1956, "7 ± 2"; later research puts it nearer 4). The number is not a cap on menu length. The lesson is to show things rather than make people recall them.
Check:
- Every field has a visible label that stays while the user types. A placeholder is never the only label.
- Hints and constraints ("At least 12 characters") stay visible beside the field while typing, not only in a tooltip or a placeholder.
- Long forms are split into titled sections of related fields. Multi-step flows show the step ("Step 2 of 4") and a summary of earlier answers.
- Nothing typed is lost: a validation error, going back a step, or switching tabs keeps the entered values.
- Long numbers and codes display in chunks (`4242 4242 4242 4242`) and have a copy button.
- Recognition over recall: recent items, autocomplete, and pickers instead of typing IDs from memory; applied filters stay visible as chips.

**INT-6 Accept input in the shapes people type; store one format (Postel's Law).**
When: fields with a known format (phone, card number, date, postcode, amount, email, one-time code) and any field people paste into.
Why: the robustness principle (Jon Postel, RFC 761, 1980): be liberal in what you accept and conservative in what you send. Rejecting a space or a dash fails people for nothing.
Check:
- Formatting is stripped before validating: spaces, dashes, brackets, dots, and leading or trailing whitespace. `(386) 555-0100`, `386-555-0100`, and `3865550100` are all valid.
- Values are normalised to one form when saved (E.164 for phone numbers, ISO 8601 for dates, integer minor units for money) and shown back formatted.
- The keyboard and autofill help: `type="tel"`, `type="email"`, `inputmode="numeric"`, `autocomplete="tel"`, `autocomplete="one-time-code"`. Never `type="number"` for phone, card, postcode, or codes: it drops leading zeros and adds spinner arrows.
- A one-time code accepts a paste of the whole code, even when it is split across boxes.
- Validation runs on blur or submit, not on every keystroke, and the error says what is accepted, with an example.
- Ambiguous input is not guessed: `03/04/2026` could be March or April, so use a date picker or an unambiguous format.
- Names accept apostrophes, hyphens, spaces, and non-Latin characters.
- Liberal is not unsafe: the server validates everything again and rejects malformed or dangerous input with a clear message.

**INT-7 The more often an action is used, the closer it sits (frequency of use).**
When: deciding what goes in the main navigation, a toolbar, a header, or the home screen versus Settings and overflow menus; designing daily-use tools (admin, dashboards, internal apps, point of sale).
Why: one extra click on an action done 200 times a day costs more than ten clicks on one done monthly. This is a prioritisation rule, not a named law; it decides *which* options survive HIE-7's cut.
Check:
- Tasks are ranked by how often and how much they matter (analytics, support tickets, or asking users). The top one to three are one click or tap from the landing screen; rare configuration lives in Settings.
- Frequent actions have keyboard shortcuts, shown in their tooltip or menu item (`/` to search, `⌘K`).
- The product remembers last-used filters, sort order, view, and form values, and uses them as defaults.
- An action repeated over many items has a bulk version.
- Frequent, reversible actions have no confirmation dialog; they offer Undo. CMP-3's dialog is for rare, destructive ones.

**INT-8 Show values the way people say them.**
When: displaying a date, date range, time, duration, count, or amount the user picked or will read back: field values, summaries, confirmations, lists.
Why: `08/09/2026 15/09/2026` is how a database stores a trip, not how anyone says one. It makes the reader parse, and it is ambiguous: 8 September or 9 August (INT-6). INT-6 is the input half of Postel's Law; this is the output half.
Check:
- Ranges say shared parts once: `8–15 May`, `28 May – 4 Jun`, `9:00–10:30`. Use an en dash, not a hyphen and not two separate values.
- Leave out what the reader already knows: the year when it is this year, or next year in a booking flow that only goes forward; seconds on times.
- Month names, not month numbers. Add the weekday where it matters for a plan (`Fri 8 May`).
- Format for the user's locale: `Intl.DateTimeFormat(locale, { day: 'numeric', month: 'short' }).formatRange(start, end)` in JavaScript. Store ISO 8601 underneath (INT-6).
- Counts read as phrases: `2 adults, 1 infant`, not `A2 I1` or `3 pax`.
Watch: [Memorisely, 2026-11-23](https://www.facebook.com/reel/1149022317721443): `08/09/2026 15/09/2026` rewritten as `8 - 15 May`.
