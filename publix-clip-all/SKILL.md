---
name: publix-clip-all
description: Clip every available Publix digital coupon at once with a browser DevTools console script that clicks "Clip coupon" in throttled batches and presses "Load more" until the list is exhausted. Use when the user wants to "clip all Publix coupons", "clip every coupon", "auto-clip Publix digital coupons", "Publix coupon clipper", or mentions publix.com/savings/digital-coupons. Runs in the user's own signed-in browser session; never asks for credentials or calls private APIs.
---

# Publix Clip All Coupons

Automate clipping all currently available Publix digital coupons from the Publix Digital Coupons page using your browser's DevTools console.

## What this skill does

This skill provides a browser-console script that:

- Finds all currently loaded **Clip coupon** buttons
- Clicks coupons in parallel batches for speed
- Finds and clicks Publix's **Load more** button
- Waits for additional coupons to render
- Repeats until no more coupons are available to load
- Prints progress to the DevTools console

## When to use

Use this when someone wants to quickly clip many Publix digital coupons from:

https://www.publix.com/savings/digital-coupons

This is intended for a user running code manually in their own authenticated browser session.

## Safety / scope

- Do not ask the user for Publix credentials.
- Do not attempt to bypass authentication.
- Do not reverse-engineer private Publix APIs when browser automation is sufficient.
- Prefer interacting with the page's existing controls.
- Avoid excessively aggressive request rates.
- Warn the user that site markup may change and break selectors.
- The user should review any console code before pasting it into DevTools.

## Recommended script

The script is `publix-clip-all.js`, in this skill's folder. Read it and give it to the user
in a `js` code block, unchanged, so they can review it before pasting. It is the only copy:
fix selectors and tuning values there, not in a pasted version.

## User instructions

1. Open the Publix Digital Coupons page.
2. Sign in to the user's Publix account.
3. Open browser DevTools:
   - Chrome / Edge: `F12` or `Ctrl+Shift+J`
   - macOS Chrome: `Cmd+Option+J`
4. Open the **Console** tab.
5. Paste the contents of `publix-clip-all.js`.
6. Press Enter.
7. Keep the tab open until the console prints `DONE`.

If Chrome blocks pasting into DevTools, explain the self-XSS warning and tell the user to follow Chrome's on-screen instructions only after reviewing the code.

## Troubleshooting

### Load More is detected but does not load

Inspect the current button:

```js
const b = [...document.querySelectorAll("button")]
  .find(x => x.innerText.toLowerCase().includes("load more"));

console.log(b);
console.log(b?.outerHTML);
console.log("Parent:", b?.parentElement?.outerHTML);
```

The selector known to work at the time this skill was created is:

```css
button[data-qa-automation="button-Load more"]
```

### Too many coupons fail to clip

Reduce:

```js
const BATCH_SIZE = 10;
```

to:

```js
const BATCH_SIZE = 5;
```

Or increase:

```js
const BATCH_DELAY_MS = 1400;
```

to `2000` or `2500`.

### Make it faster

If Publix is processing clicks reliably, increase `BATCH_SIZE` to `15` or `20`.

Avoid firing every coupon simultaneously because some requests may be dropped or throttled.

## Notes for maintainers

Publix may change its HTML, Vue components, visible button labels, or `data-qa-automation` attributes at any time.

If the script stops working:

1. Inspect the current Clip Coupon button.
2. Inspect the current Load More button.
3. Prefer stable `data-*` automation attributes where available.
4. Update the selectors in `publix-clip-all.js`, and the one quoted under Troubleshooting.
