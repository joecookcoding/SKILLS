# Hardening a repo's verification layer

Read this when setting up gates, rules or checks that judge many changes, or before
running several agents at once. Source: "How the Claude Code team thinks about
verification" (claude.dev, 2026-11-16). Treat the checks as a system: keep them out of
reach of the changes they judge, grade them against bugs that mattered, and prune them.

## 1. A project `verify` skill

The smoke test the agent runs before every commit: how to boot, drive and inspect this
app. Write it from `assets/verify-skill.template.md` into `.claude/skills/verify/`,
as close to the code it covers as possible (one per app in a monorepo). Then make it
fast and reliable: ask the agent to run it ten times and fix whatever wobbles. A
smoke harness that fails at random teaches the agent to ignore it.

## 2. Cheap checks before shared ones

Tests, build and lint run locally before a PR opens, so CI and reviewers don't spend
time on what the agent could have caught. Enforce it with a Stop hook that runs the
quick suite, or by setting the goal as "the suite passes".

## 3. A reliability checklist keyed to the diff

Each item has a **trigger readable from a diff**, a **check**, and the **incident or PR
behind it**. The agent reads the diff and runs only the items whose trigger matches,
usually 3 to 10. Nobody has to remember past outages. Template:
`assets/reliability-checklist.template.md`.

Example: trigger "session storage or message types change"; check "older saved
sessions still load when the new field is missing"; why "the incident where resume broke
for every transcript older than the release".

## 4. Changes can't edit their own judges

- Review rules (`REVIEW.md`), CI config and gate scripts are read from the **base
  branch**, never from the PR.
- A review applies to one commit. A push during review voids it.
- A test changed in the same diff as the code it judges gets a sentence in the PR body
  saying why.

## 5. New gates start in observe mode

Give every gate off, observe and enforce modes. Observe logs what it would have blocked;
read those logs for false positives before you enforce. In enforce mode, let a commit
carry a written reason for skipping verification, and after two blocks in one session
let the next through, so a stuck agent doesn't loop.

Stamp each commit with how it was verified, for example a trailer
`Verified-by: verify, unit`, including `Verified-by: none`, so unverified commits can be
counted.

## 6. One tuned reviewer, rounds that build

A second, pricier reviewer stacked on the first usually does worse than tuning the first.
Write `REVIEW.md` to say what matters in this code. Point each round at the findings and
failures of earlier rounds instead of starting fresh. Tag findings Important, Nit or
Pre-existing, so the author isn't blamed for bugs that were already there.

## 7. Turn misses into rules, and prune them

- A pattern becomes a rule only when it shows up in **at least two PRs** and can be
  **spotted from a diff**. Try to disprove it before adding it; a person approves it.
- Replay a known incident's PR against the reviewer. If the bug was on a small diff and
  the reviewer missed it, that gap is worth a rule.
- Flaky tests: no skips, sleeps or retries. Root cause, or delete with a written reason.
- Prune on a schedule. Rules, checklists and suites only grow unless someone removes
  what no longer fires.

## 8. Grade the checks

Track merged changes later reverted, changes a maintainer rejected, and a size-matched set
that stayed clean. For a formal eval: rebuild the repo at the state of past incidents,
write a one-sentence answer key per bug, score only findings that name it, keep clean
changes as a control against over-flagging, and hold the tuning set apart from the test
set. Score raw findings, post-verification and final output separately so you see where
a found bug gets lost. Stop tuning when the next gain would only fit the eval.
