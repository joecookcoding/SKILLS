---
name: verify
description: "Boot, drive and inspect <APP> to confirm a change works before committing. Use before every commit that touches <APP_PATHS>, and for \"verify this\", \"smoke test\", \"does it work\", \"try it in the app\"."
---

# Verify <APP>

Run this before every commit that touches <APP_PATHS>. Report what you ran and what you
saw; include the screenshot or output path.

## Start

<!-- The exact commands, in order, with the port and the ready signal. -->
1. `<install command, only if lockfile changed>`
2. `<start command>`. Ready when the log shows `<ready line>` (usually under <N> s).
3. Seed data: `<seed command>`, or sign in as `<test account from env var NAME>`.

## Drive

<!-- How the agent reaches the app: browser tool, simulator MCP, curl, CLI. -->
- Open `<url or entry point>` with <tool>.
- Feature map: `<path to feature map>` lists each flow, its path and expected result.
  Run the flows the diff touches, plus <the one flow that must always work>.

## Inspect

- Logs: `<where>`. Fail on any `ERROR` line the change introduced.
- Data: `<query or command>` to confirm the write landed.
- Screenshot each flow's final screen to `<dir>`.

## Stop

`<stop command>`; free port <PORT>.

## Known wobbles

<!-- Every time this skill fails for a reason other than the change, add the cause and the fix here. -->
