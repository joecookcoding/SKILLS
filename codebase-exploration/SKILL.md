---
name: codebase-exploration
description: Use whenever the user asks to fix a bug, add a feature, refactor code, extend a system, implement something new, or change how an existing piece of code behaves — including "fix this bug", "add support for X", "refactor Y", "where should I put this", "extend the auth flow", "implement Z", "wire up the new endpoint", "modify how the worker handles N", "the API is returning the wrong thing, fix it", or any task that involves writing or changing more than a one-line edit. Also trigger on questions like "where does X get called", "what existing function does this", "is there already a helper for Y", "how does this dispatch work" — those are the moments when investigation saves the most rework. The skill teaches an investigate-before-mutate discipline adapted from NVIDIA's TensorRT-LLM exploration playbook: search for the concept not just the symbol, read callers before the called function, check for existing helpers and dispatchers before writing new code, mirror existing test style, and use a structured three-pass file budget with the Explore subagent and TodoList to prevent "I've read 30 files and still don't know what's going on" spirals. The single most common failure mode in coding tasks is writing parallel code that duplicates an existing helper because the existing helper was never found — this skill prevents that, and the cost of running the discipline (a few extra reads) is always less than the cost of writing then deleting the duplicate. Skip only for: trivial one-line edits, typos, removing a print, or tasks where the user has already named the exact file + symbol + change.
metadata:
  version: "1.0.0"
  tags: [code, investigation, bug-fix, refactor, multi-step]
---

# Codebase Exploration

Read before you write. The bug is rarely where the symptom appears, the feature you're about to add usually has a sibling implementation somewhere, and the dispatcher above the function you opened often holds the real answer. The discipline below is what separates a change that lands cleanly from one the user rewrites in review.

Adapted from the post-mortem-driven exploration discipline in NVIDIA's [TensorRT-LLM codebase exploration skill](https://github.com/NVIDIA/skills/blob/main/skills/TensorRT-LLM/trtllm-codebase-exploration/SKILL.md), where they once wrote 250 lines of new attention code across four iterations before discovering a 10-line dispatch to an existing method would have done it. The shape repeats in every large codebase; this skill makes the discipline portable.

## When to use

Use this skill any time you're about to write or modify code beyond a one-line edit. The strongest triggers are:

- **Bug fixes** — the report names a symptom; the cause is usually elsewhere.
- **Adding features** — a sibling implementation often exists.
- **Refactors** — knowing every caller is the prerequisite.
- **"Where does X live"** — same skill, just stopping before the write step.

Skip for: typos, single-line edits where the user named the exact change, or trivial mechanical work (renaming a local variable, deleting a print statement).

## Rule of thumb

**If you're about to write code and can't name the existing function it would call into, the existing helper it would replace, or the dispatcher that would route to it, you haven't read enough yet.**

This is the test. If you can answer those three questions, you've done the work. If not, do one more pass.

## The investigation passes

Three passes with bounded read budgets. The budgets force synthesis between passes; they don't cap your total reading.

### Pass 1 — Orient (≤ 5 reads)

Goal: understand the *shape* of the area where the work lives.

- `Glob` the top-level layout of the directory most likely involved.
- `Read` the README or AGENTS.md if present in that area.
- `Read` 2-3 files that look like landmarks (the main entry point, the most-imported module, the file the user named).

End of Pass 1: write a one-sentence note to yourself (or a `TodoWrite` entry) describing the shape. *"Auth lives in `src/auth/`, has a middleware layer and a per-route guards layer; `verify_token` is in middleware/jwt.ts; routes import guards via `~/auth/guards`."*

### Pass 2 — Trace (≤ 8 reads / ≤ 12 greps)

Goal: find the *dispatch chain* — caller → router → called function. The bug or the right insertion point usually lives in this chain.

- **Search for the *concept*, not just the symbol.** Reports name specific symbols ("`verify_token` returns wrong result"); the bug usually lives a level above (caller's wrong assumption) or a level below (called function's silent default). `Grep` for `token`, `verify`, `auth` — concepts survive refactors that symbol names don't.
- **Read all callers before reading the called function.** When `Grep` finds the candidate file, find who calls into it first. Read 2-3 callers. *Then* read the called code, with the callers' assumptions in mind. The bug is often in the caller's contract assumption.
- **Check the dispatcher.** Many bugs are mis-routing — the right function exists, the request never reaches it.
- **Read existing tests as evidence.** `Glob` for `*test*` in the area; existing tests encode the team's expected behavior and the style a new test should mirror.

For wide searches that would dump hundreds of lines into your context (e.g. "find every caller of a widely-used utility"), **dispatch the Explore subagent**. Explore returns a digest, not raw output — your context stays clean while you still get the picture. Same for "what does this entire subsystem do" investigations.

End of Pass 2: a list of 1-3 candidate files for the change, with one-line annotations on each.

### Pass 3 — Confirm (≤ 5 reads)

Goal: verify before writing. Specifically:

- Read the existing-test file in full so the new test (if you're authoring one) matches the style and uses the same fixtures.
- Re-read the dispatcher / caller most likely to be affected, with the planned change in mind: does the change break any contract the caller depends on?
- If a sibling implementation exists, read it in full — your change should usually call it, mirror it, or extend it, not parallel it.

End of Pass 3: you can answer the three rule-of-thumb questions. Now write code.

## Manual compaction signal

If you've blown past a pass budget (15+ files read and you still don't know what's going on), **stop reading and synthesize**. Write a paragraph summarizing what you've found, what you don't know yet, and what the next read should clarify. Then continue.

This is the manual companion to harness-level context compaction. The signal that you need it: rereading the same file, forgetting what was in a file you read 6 reads ago, or finding yourself unable to articulate a hypothesis. Don't push through — synthesize, then continue.

For very long investigations (30+ reads), the Explore subagent is usually the right move from earlier: it does the wide read, you get a summary back, your context doesn't fill up.

## Common exploration mistakes

| Mistake | Consequence | Counter |
|---|---|---|
| Reading only the file the user / report named | Miss that the bug is in the caller or dispatcher | Grep for callers first, then read down |
| Searching only for the exact function name | Miss renamed-but-not-everywhere-updated equivalents and concept-level matches | Search the concept (`auth`, `token`, `validate`) before the symbol |
| Writing new code that parallels an existing helper | Two implementations diverge; reviewers ask "why not use X" | Pass 2 explicitly searches for sibling helpers — if one exists, your change calls it |
| Skipping existing tests | New test asserts the wrong invariant; reviewer pushes back on style | Read `*test*` in the area before authoring a new test |
| Treating one plausible file as definitive | The actual root cause is one level up; you patch the symptom | `root_files` is ordered by *root cause likelihood*. The symptom file is at best position #2 |
| Dumping wide grep output into your own context | Context fills, you re-read trying to remember earlier results | Dispatch the Explore subagent for wide searches; it returns a digest |
| "I'll just start writing and see what fits" | Half-written code shaped by incomplete understanding; rewrite cost > read cost | Apply the three rule-of-thumb questions before the first edit |
| Reading until you "feel like you understand" | No-progress spiral, context bloat | Per-pass file budget; synthesize between passes |
| Confidence without evidence | "This is the cause" with no caller trace, no test confirmation | Confidence is a function of evidence quality. State explicitly what evidence you have |

## Tooling

The Claude Code tools that pair with this discipline:

- **`Grep`** — concept-first search. Use `output_mode: "content"` with `-C 3` for short looks, `files_with_matches` for "where does this live."
- **`Glob`** — layout discovery. `**/*test*.{ts,py}` for existing tests, `**/AGENTS.md` for documented decisions.
- **`Read`** — focused file reads. Don't speculate about content; read it.
- **`Agent` with `subagent_type: "Explore"`** — wide-area investigation. Use when the search would put hundreds of lines in your context. Give Explore a specific question, not a vague one. *"Find every place that calls `verify_token` and report the 3-5 most interesting callsites with brief context"* beats *"explore the auth system."*
- **`TodoWrite`** — between-pass scratchpad. One todo per pass with the synthesis you wrote at the end of it. This survives context compression and gives the model a stable reference for what's been ruled out.

## Reading C / native code, generated code, vendored deps

Most repos are mostly one or two languages and the rules above apply directly. A few specific cases:

- **Generated code** — files with `# DO NOT EDIT`, `*_pb2.py`, `*.gen.ts`, `__generated__/`. The bug is upstream in the generator, not in the generated file.
- **Native bindings** — a Python function may resolve to a C entry point in `*.c` / `*.pyx` / `*.cc`. Grep both sides.
- **Vendored dependencies** — `node_modules/`, `.venv/`, `vendor/`. Skip unless the dependency itself is the suspect; in that case, read the version pinned in `package.json` / `pyproject.toml`, not master.

## When this discipline is overkill

It's a yellow flag if you find yourself running three passes on a task that was "remove this `console.log`" or "rename `foo` to `bar` in one file." Apply the rule-of-thumb test: if you can already name the existing function / helper / dispatcher, you've done enough. Don't pad reads to satisfy the structure.

The skill protects against under-investigation; it doesn't mandate over-investigation. Use the rhythm when the task is substantial; skip it when the task is small.

## What "investigate before mutate" is NOT

- Not a license to widen scope. The investigation locates the *smallest* change that solves the problem; it doesn't justify drive-by refactors.
- Not a substitute for running the code. After the change lands, run the test or the app — reading deeply doesn't prove the change works.
- Not a checklist to satisfy. If 4 files of reading is enough for high confidence, don't pad to 18 because the budget allows.
- Not bureaucracy. The point is fewer hours spent rewriting after review, not more hours spent reading before writing.

## Why this matters

Every codebase eventually grows a sibling helper for almost any task you'd want to add. Every bug usually has a cause one level removed from its symptom. Every refactor depends on understanding the full caller graph. The cost of the discipline is a few extra `Grep` and `Read` calls. The cost of skipping it is writing code that duplicates existing functionality, patches the wrong layer, or breaks a contract you didn't know existed — and then rewriting it after the user catches it in review.

A few reads up front beats a rewrite after the fact. Always.
