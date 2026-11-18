---
name: test-strategy
description: "Decide which tests a change needs, which to skip, and which existing tests to delete, so an agent proves its work with evidence instead of a green count. Use for \"what tests should I write\", \"add tests for this\", \"write a test plan\", \"how do I verify this change\", \"tests pass but it's broken\", \"is this test worth keeping\", \"review our test suite\", \"too many tests\", \"tests break every refactor\", \"should I mock this\", \"snapshot tests\", \"flaky test\", \"add a retry to this test\", \"E2E vs unit\", \"property-based tests\", \"fast-check\", \"Hypothesis\", \"differential test for a migration\", \"set up a verify skill\", \"commit gate\", \"reliability checklist\". Not for test-framework syntax alone, or for reviewing a diff for bugs (code-review)."
---

# Test Strategy

Less is more. A test earns its place only if it **can fail for a broken program and pass
for a working one**, and something other than the code's author decides the result.
Ten mocked unit tests can all pass while the feature is broken; one end-to-end run of the
real flow cannot. Write fewer checks that are hard to fool, run them often, and delete the
ones that only describe the code's current shape.

Sources: Addy Osmani, "How the Claude Code team thinks about verification" (claude.dev,
2026-11-16); Felix Rieseberg, "How to be more ambitious" (2026-10-13), for the outside
judge and the outcome-first framing; Google Testing on the Toilet, "Change-Detector Tests
Considered Harmful" (2015-01-27).

## Workflow

1. **Name "done" as an outcome a user could see.** Not "write a test for `applyCoupon`"
   but "a shopper with a valid code sees the discount at checkout and pays the lower
   total". Then answer: **what, other than you or me, would show this is right?** A
   running app, a property library's generator, the old system's output, a real
   database. If the answer is "my own test that I wrote from my own code", look again.
2. **Run the change before writing any test.** Boot the app and drive the flow: a
   browser for web, a simulator for mobile, the service and a real request for backend,
   the CLI with real arguments. If the project has no quick way to do this, building one
   is the first task: write a project `verify` skill from
   `assets/verify-skill.template.md`. This smoke run catches more than any test you are
   about to write.
3. **Pick the fewest tests that pin the outcome,** in this order. Read
   `references/test-types.md` for patterns and libraries.

   | Situation | Test | Why it is hard to fool |
   |---|---|---|
   | A user flow (sign up, check out, export) | **End-to-end** through the real UI or API | The whole feature works or it doesn't; a failure shows the broken step |
   | A rule that must always hold (round trip, never negative, idempotent, fast = naive) | **Property test** (fast-check, Hypothesis, proptest) | Generated inputs don't share the author's assumptions |
   | A rewrite, port or migration that must behave the same | **Differential test**: old and new on the same inputs | The old system is the oracle; no hand-written expectations |
   | Pure logic with many named cases (a parser, a tax table, date math) | **Table-driven unit test** on inputs and outputs | The table is the spec, not a copy of the code |
   | Code that talks to a database, queue or another service | **Integration test** against the real thing (or its official emulator) | Mocks of the ORM hide constraint, migration and query bugs |

   One good test per behaviour, at the highest layer that can see it. Don't repeat the
   same behaviour at three layers.
4. **Assert at a real boundary:** the returned value, the rendered screen, the row
   written, the request another system received. Never the order in which internal
   helpers were called.
5. **Watch it fail.** A test that went green on the first run was never seen red. Break
   the code on purpose (flip the condition, return early, drop the write), confirm the
   test goes red for the right reason, then restore. If it stays green, it tests
   nothing: fix it or delete it.
6. **Run cheap checks first, heavy ones before commit.** Type check, lint, unit and
   build in the inner loop; E2E and differential runs before committing or opening a
   PR. Run heavy suites where the project says they run (a build box, CI), not
   wherever is handy.
7. **Three rounds, then a person.** If a check is still red after three honest fix
   attempts, stop. Report the failing check, what you tried, and the evidence. Don't
   weaken the assertion, skip the test, or edit the check that judges your change to get
   to green.
8. **Report evidence, not adjectives.** Say what ran (command, flow, count of tests
   collected), what it showed (output, screenshot path, diff count), and what was **not**
   verified. "Tests pass" with no count is not a report.

## Tests to avoid

Each of these costs upkeep on every change and catches no real defect. Don't write them;
when one breaks during a refactor, delete it rather than updating it.

- **Change detectors.** Mock every collaborator, call the method, assert each mock was
  called, in order. That is the method body rewritten as assertions. It fails only when
  the code changes shape.
- **Expected values copied out of the source.** If the only way to get the expected
  value was to read the implementation, the test restates it.
- **Mocks asserting what the mock was told to return.** `stub.returns(5); expect(x()).toBe(5)`
  through one pass-through layer tests the stub.
- **Snapshots nobody reads.** A 400-line snapshot approved with `-u` pins everything and
  checks nothing. Keep a snapshot only when it is small and a person reads every diff.
- **Tests of the framework or language.** That a getter returns what the setter set, that
  React renders a `div`, that the ORM saves a field.
- **Coverage padding.** A test written to colour a line green, with no behaviour in mind.
- **Flaky tests kept alive with sleeps, retries or skips.** A flaky test trains everyone,
  agents included, to rerun instead of fixing. Find the root cause; if you can't, delete
  the test and write down why.
- **Slow tests in the inner loop.** If the suite takes minutes, the agent runs it less and
  failures arrive in batches nobody can untangle. Move the slow part to the pre-commit tier.
- **Tests the change rewrote to pass.** Editing an assertion in the same change that broke
  it hides the break. Say which was wrong, the test or the code, and why.

**Mocks are fine when the call is the behaviour** (the HTTP request sent, the email
dispatched, the card charged) or when the real thing is unavailable or random (the
clock, randomness, a paid third-party API). Prefer a fake with real behaviour over a mock
that records calls.

## Auditing an existing suite

When asked to review tests, trim a suite, or fix "tests break every refactor":

1. Find the suite's cost first: run time, how many tests, which files changed most often
   alongside production code (`git log --name-only`).
2. Sort each test or test file into **keep** (behaviour at a boundary, or it has caught a
   real bug), **rewrite** (right behaviour, wrong shape: move it up to a boundary), or
   **delete** (change detector, duplicate of a higher-layer test, can't fail).
3. For each delete, run step 5 above in reverse: does breaking the code it covers turn
   anything else red? If yes, the delete is safe.
4. Name the gaps: the user flows nothing covers end to end. One E2E for a gap is worth
   more than the deletes.
5. Present the table and the gaps; delete in bulk only after the owner agrees.

## Gotchas

- **Passing unit tests are not a working feature.** Both the code and its tests can carry
  the same misunderstanding of the task. Step 2 exists for this.
- **An agent's tests share the agent's blind spots.** Tests written right after the code,
  by the same session, check what it already believed. Property generators, the old
  system, and the running app are the outside judges.
- **"0 failed" can mean "0 collected".** A wrong file name or glob runs nothing and exits
  green. Check the count of tests that ran.
- **Type checks and lint are not verification.** They are the cheapest tier, not the proof.
- **A mocked database passes migrations that fail in production.** Constraints, indexes,
  NULL handling and transaction behaviour only show up against the real engine.
- **Review rules read from the PR can be weakened by the PR.** Gates must load their rules
  from the base branch. See `references/verification-layer.md`.
- **A passing check on an old commit means nothing.** Re-run after the last push.
- **Rules and suites only grow unless pruned.** Delete checks that haven't fired in a long
  time or whose code is gone.

## Hardening a repo's verification layer

For "set up a commit gate", "make the agent verify before committing", "turn this
incident into a rule", or running many agents in parallel: read
`references/verification-layer.md`. It covers the project `verify` skill, the
diff-triggered reliability checklist (`assets/reliability-checklist.template.md`),
gates in observe mode before enforce, commit stamps, turning misses into rules, and
grading the checks themselves.

## When this is overkill

A typo, a copy change, a config value with no logic: run the app or the build once and
say so. No new test.

## Composition

- `codebase-exploration`: before, to find the tests and test helpers that already exist.
- `adversarial-review` or `/code-review`: after, as the outside reviewer of the change.
- `run` (built-in): to launch and drive the app for step 2 when the project has no
  `verify` skill yet.
