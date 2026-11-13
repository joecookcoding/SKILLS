---
name: optimize-claude-memory
description: Audit and restructure a repository's agent instructions into an AGENTS.md-only layout (lean root AGENTS.md, per-directory AGENTS.md files, procedures moved into skills, no CLAUDE.md) to cut per-turn tokens and stay portable across Claude Code, Copilot, Cursor and Cody. Use when the user wants to "optimize CLAUDE.md", "migrate CLAUDE.md to AGENTS.md", "add AGENTS.md", "support multiple agents", "make docs portable across Copilot/Cursor/Cody", "reduce token usage", "speed up Claude", "shrink memory", "audit AGENTS.md", "fix the claude setup", "make this repo ready for Claude", "add an AGENTS file for each service", "full docs on every service", "port the optimization pattern to another project", "remove the CLAUDE.md files", "Claude reads AGENTS.md now", "move rules into skills", or mentions CLAUDE.md being too long / hard to follow / slow / duplicated, or AGENTS.md not loading. Also triggers on "Claude Code memory", "context window", "skill migration", "@AGENTS.md pattern", "sibling CLAUDE.md", "nested CLAUDE.md", "directory-scoped rules", "monorepo docs", or "claude.md best practices". Not for auditing skills (skill-optimizer).
---

# Optimize Claude Memory

Restructure a repo's memory layout so that **always-true facts live in the root `AGENTS.md`** (portable across every coding agent — Claude Code, Copilot, Cursor, Cody), **procedures move into skills** (free until triggered), **area-specific rules live in per-subdirectory `AGENTS.md` files**, and **the repo has no `CLAUDE.md` at all**: Claude Code reads `AGENTS.md` itself, like every other agent.

Reference mechanics: see `references/memory-mechanics.md`. Official source: [Claude Code memory docs](https://code.claude.com/docs/en/memory#agents-md).

## The pattern at a glance

```
repo/
├── AGENTS.md          ← source of truth; Claude Code reads it at launch
├── .claude/rules/     ← optional: Claude-only rules (load alongside AGENTS.md)
└── services/
    └── x/
        ├── AGENTS.md  ← loads on demand when Claude opens a file in services/x/
        └── README.md  ← human-facing overview (untouched)
```

**Why no `CLAUDE.md`, anywhere:** with the default **Project instructions** setting (`claude-md-or-agents-md`), Claude Code reads `AGENTS.md` only while there is **no** `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it. One such file on that path switches Claude to CLAUDE.md-only, and every `AGENTS.md` silently stops loading. So it is all or nothing: none in the repo, none in a parent directory, no `CLAUDE.local.md`. `~/.claude/CLAUDE.md`, managed policy files and `.claude/rules/` don't count and keep loading.

**Why AGENTS.md is the content file:** a single file serves every agent. Claude Code, Copilot, Cursor, Cody, and future agents all read `AGENTS.md` directly. One source of truth, no second file to keep in sync.

**Where Claude-only content goes:** `.claude/rules/*.md`, which loads alongside `AGENTS.md` and can be path-scoped with `paths:` frontmatter. Personal, uncommitted notes go in `~/.claude/CLAUDE.md`, not a `CLAUDE.local.md` (that one counts, and switches `AGENTS.md` off).

**Never propose a `CLAUDE.md`.** The old bridge, a one-line `CLAUDE.md` holding `@AGENTS.md` beside every `AGENTS.md`, existed because Claude Code before v2.1.277 read only `CLAUDE.md`. It is now something to delete. If a session can't read `AGENTS.md`, the fix is to update Claude Code, re-enable the built-in plugin or change the setting (`references/memory-mechanics.md` lists the cases), not to add files to the repo. Keep a bridge only when the user asks for one by name.

## Rules that hold for the whole run

One line each; the full text with the reasons is in `references/anti-patterns.md`. Read the matching entry there before acting on anything it covers.

1. Never `@import` a subdirectory `AGENTS.md` from an ancestor file. It loads the subtree at every startup.
2. Leave no `CLAUDE.md` behind, and delete them all in one change. Half-removed is the worst state.
3. No vague skill descriptions. See `references/skill-writing.md`.
4. Don't delete content you don't understand. Ask.
5. Move content verbatim. Rewrite only to fix a stale command or a broken reference, and say so in the plan.
6. Don't merge `AGENTS.md` and `README.md`. Agents read one, people the other.
7. Work low-risk to high-risk: new `AGENTS.md` files, then the deletions, then command fixes.
8. Never skip the plan approval.
9. A block pinned by a "keep in sync" or "source of truth" convention is the user's decision, not yours.
10. No per-directory file counts in navigation tables. Strip the ones you find.

**Git:** never commit, stash, or push. The user manages git manually. Every project tested so far has this rule — honor it universally.

**After a context compaction, invoke this skill again before continuing.** A run is long, and the summary keeps only the top of this file; the later phases would be gone.

---

## What success looks like

- Root `AGENTS.md` under **200 lines** (target 120–150), per official guidance — holds only always-true facts
- **No `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the repo or any parent directory** (`~/.claude/CLAUDE.md` is fine)
- Root `AGENTS.md` carries a one-line note that there is no `CLAUDE.md` on purpose, so `/init` or another agent doesn't recreate one
- Every subdirectory with substantive rules has its own `AGENTS.md` — it loads on demand when Claude opens a file there
- Every service/package in a monorepo has its own `AGENTS.md` and a human-facing `README.md` — users frequently ask for "docs for every service," so make this a default
- Procedures and reference material moved into `.claude/skills/` with tight trigger-focused descriptions
- `MEMORY.md` (if the repo uses auto-memory) trimmed to current state — no completed migration history
- Duplicate task/todo files consolidated
- Broken doc references fixed
- Stale commands reconciled across AGENTS.md / README.md (common: deprecated CLIs lingering in one but fixed in another)
- **No per-directory file counts in navigation tables** — steer by complexity/purpose labels instead (rule 10)
- Build, type-check, and lint still pass (if the repo has any — docs-only repos skip this)

Expected savings: **~2,000–2,600 tokens per turn** from root-file reduction; additional **~300–400 tokens** if MEMORY.md is trimmed. Accuracy improves because tight skill descriptions match intent better than a monolithic rules file.

---

## Workflow

Follow these phases in order. Phase 3 (plan approval) is the only mandatory user checkpoint — everything before it is read-only, everything after it executes the approved plan.

### Phase 1 — Audit (read-only)

Goal: understand the current state before proposing changes, AND establish a baseline so post-change verification is unambiguous.

**Run `scripts/audit-memory-tree.ps1 -Root <repo>` for the deterministic measurements** (true root line counts, every `CLAUDE.md`-family file in the repo and its parent directories with a delete/migrate label, the Claude Code version, downward `@import` hits, broken `.md` references in the root instruction file); **never eyeball-count.**

**Triage — which starting point? (do this first).** The audit script prints the verdict. Three starting points:
- **On the pattern** — an `AGENTS.md` tree, no `CLAUDE.md`-family file anywhere, root `AGENTS.md` under ~200 lines. Produce a **Touch-up plan** (gap-fixes only: a missing service doc, a stale reference, a line-budget trim). A full audit of an already-optimized repo just manufactures busywork.
- **Old sibling pattern** — an `AGENTS.md` tree plus one-line `@AGENTS.md` `CLAUDE.md` files. Also a touch-up: its main item is deleting every one-liner, root included, in one change.
- **Migration** — a monolithic root `CLAUDE.md` (or `CLAUDE.md` files holding real content), few or no `AGENTS.md` files. The full workflow below applies.

  For either touch-up, the win is *deltas*, not a restructure. Make the plan a **minimal diff** and state plainly that the repo is already on (or one deletion away from) the pattern — otherwise a big-sounding six-phase workflow reads as alarming on a repo that's 95% done, and you risk manufacturing a restructure it doesn't need. Most steps below still apply; you'll just be confirming compliance rather than building from scratch.

  When a touch-up's root file is over its line budget: **line count only drops when you remove whole lines — trimming prose inside a table row saves tokens, not lines** (canonical explanation: `references/verification.md` §1). If the only big block left to cut is one *pinned* by a "keep in sync" convention (rule 9), you usually can't reach the budget without either finding other whole-line cuts or dropping real content: say that to the user as a decision rather than quietly condensing the pinned block.

**Then read `references/audit-steps.md` and work through its steps 0–14.** In short: prior-run report, build/lint baseline (only when a root build exists), root file measurements, parent-directory `CLAUDE.md` check, the memory-tree inventory including user-level skills, the version and setting check, stack and shell detection, a full read of the root instruction files, `MEMORY.md`, the broken-reference sweep, style conventions, the per-service docs gap scan, and the command-consistency sweep.

**Do not edit anything yet.** Produce a written audit for yourself summarizing: baseline state (or "no root build, skipping baseline"), line counts, the `CLAUDE.md`-family files found and their labels, what's duplicated, what's stale, broken references found, services missing docs, obvious skills that emerge.

### Phase 2 — Categorize

For each section of the root instruction file (`CLAUDE.md` in a migration, `AGENTS.md` in a touch-up), bucket it into one of five destinations. See `references/content-categorization.md` for the full decision framework with examples. Quick version:

| Bucket | Stays in root AGENTS.md? | Test |
|---|---|---|
| **Always-true fact** | Yes | "Do I need to know this *every* turn, regardless of what I'm doing?" |
| **Procedure / reference** | No → skill | "Is this steps-to-do-X, or a lookup table I only need for specific tasks?" |
| **Area-specific rule** | No → nested AGENTS.md | "Does this only matter when editing files under `src/X/`?" |
| **Dead / stale** | No → delete | "Is this describing a pattern we no longer use, or a file that no longer exists?" |
| **Redundant** | No → pointer | "Is this already stated in another AGENTS.md / section? Collapse to a one-line pointer — unless a documented 'keep in sync' convention pins it." |

Also inventory what nested `AGENTS.md` files are missing for directories that have substantive rules. Use the project's own convention if present — many repos use "AGENTS.md for 20+ file directories, README.md for 5–19, no doc for fewer."

### Phase 3 — Plan (REQUIRED user approval)

Write a plan to `C:\Users\<user>\.claude\plans\` (Windows) or `~/.claude/plans/` (macOS/Linux), or to the user's own plans location if their instructions name one, using the structure in `assets/plan-structure.template.md`. The plan must include:

- **Context** — why this change is happening (current line count, token cost)
- **Target pattern** — state explicitly: "AGENTS.md holds content at every level; no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` remains in the repo or above it."
- **Content migration map** — a table mapping every existing CLAUDE.md / AGENTS.md section to its destination. When moving existing content between files, the default is **verbatim** — preserve the team's prior wording unless a specific issue requires rewriting (stale command, broken reference, bad structure). Note any rewrites explicitly.
- **New skills to create** — each with its name, one-sentence purpose, and a draft description
- **New/updated AGENTS.md files** — each with a one-line purpose. Include every service/package that lacks one (from Phase 1 step 13).
- **CLAUDE.md files to delete** — the full list (repo and parent directories), each labelled one-liner (delete) or content (migrate first, then delete)
- **Collateral fixes** — broken references, duplicate files to merge, MEMORY.md trims, stale commands to reconcile (from Phase 1 step 14)
- **Expected outcome** — target root AGENTS.md line count, estimated token savings, lint/build impact ("none" for markdown-only; "none expected" if there IS a build)
- **Verification checklist** — from `references/verification.md`

Get explicit user approval before proceeding. If you're in plan mode, call `ExitPlanMode`. If you're not in plan mode (common when the skill is invoked directly), just write the plan file, summarize it in chat, and ask for approval conversationally — don't block on a tool that isn't available. **Do not proceed past this checkpoint without explicit approval.**

If the user rejects or requests changes, revise the plan and re-submit — don't start executing partial pieces.

### Phase 4 — Execute (after plan approval)

**Read `references/execute-steps.md` now, even if you read it earlier in the session,** and follow its nine steps. They run low-risk changes first: new skills (only after checking `~/.claude/skills/` for one that already covers it), every `AGENTS.md` written or updated with content moved verbatim, all `CLAUDE.md`-family files deleted in one change, no downward `@import`, stale commands reconciled, `MEMORY.md` trimmed, duplicate task files merged, broken references fixed, the lessons file updated.

### Phase 5 — Verify

Run the checks from `references/verification.md`. Short version:

1. **Line count** — root `AGENTS.md` ≤ 200 (target 150)
2. **No `CLAUDE.md` left** — no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the repo (outside skill dirs, `node_modules/`, `.venv/`, `vendor/`) or its parent directories. Every service/package flagged in Phase 1 step 13 now has `AGENTS.md` + `README.md`.
3. **No downward `@import`** — grep root `AGENTS.md` for any `@` path containing a slash (e.g., `@services/`). There should be none.
4. **Diff against Phase 1 baseline** — only if you took one. Run `npm run lint`, `npm run type-check`, etc. and **diff** against your baseline files. Markdown-only changes cannot cause build/lint/type-check failures, so any error present now that was present in the baseline is pre-existing. Flag only NEW failures as regressions. **Report pre-existing errors transparently in the final report** — don't pretend they're yours, don't hide them either. Skip this step if Phase 1 step 1 determined there's no root build.
5. **Broken reference sweep** — grep for any remaining references to files that were deleted or renamed.
6. **Stale-command sweep** — grep for the deprecated commands you identified in Phase 1 step 14 (e.g., `tctl`, `huggingface-cli`). Any remaining occurrences should be in deliberate deprecation notices, not as live instructions.
7. **Fresh-session check** (ask the user) — in a new Claude Code session in the repo, `/memory` lists the root `AGENTS.md` (an interactive session also prints `no CLAUDE.md found; AGENTS.md loaded: <path>`); after Claude opens a file in a subdirectory, that directory's `AGENTS.md` appears. Then ask 2–3 representative questions and confirm the right skill triggers. The first session after upgrading from v2.1.276 or earlier may still read `CLAUDE.md` only; the next one reads `AGENTS.md`.

### Phase 6 — Report

Write a before/after report using `assets/report.template.md`. Include:

- Line count reduction table (root CLAUDE.md → root AGENTS.md, MEMORY.md if trimmed)
- New skill count + their trigger keywords
- `CLAUDE.md` files removed
- Estimated per-turn token savings (2,000–2,500 typical + 300–400 if MEMORY trimmed)
- What the user should do next (the fresh-session check, porting the skill to other repos)

Put the report in the same directory as the plan file, named `<plan-file-name>-report.md`.

---

## Detection-driven adaptation

The skill must **not hardcode any project specifics**. The workflow is identical across repos, but the content of new skills depends on the stack:

- **React/Vue/Svelte** → likely need skills for component patterns, accessibility, design system, form validation
- **Python** → likely need skills for type-checking (mypy/pyright), test runners (pytest), linting (ruff)
- **Go** → likely need skills for test patterns, build tags, `go generate` workflows
- **Rust** → likely need skills for `cargo` workflows, async patterns, trait conventions
- **Monorepo** → consider workspace-level skills + per-package AGENTS.md

Let the project's existing patterns guide you. If the repo already has a skill for X, don't duplicate it — update its description if it's not triggering well, otherwise leave it alone.

---

## Shell detection

Windows repos typically use PowerShell — never assume bash. Check the instruction files for an explicit shell declaration first. Fall back to detecting from CI scripts (`*.ps1` vs `*.sh`). When running verification commands, use the correct syntax:

- Line count: PowerShell `(Get-Content file).Count` vs bash `wc -l file` (avoid `Measure-Object -Line` — it skips blank lines)
- Directory walk: PowerShell `Get-ChildItem -Recurse` vs bash `find`
- Preferred: use the Glob, Grep, Read, Write, Edit tools which are cross-platform.

---

## When NOT to use this skill

- **Checking instruction files for stale or conflicting content only** — the built-in `/doctor prompt-audit` does that and proposes edits. Use this skill when the goal is the portable AGENTS.md-only layout, nested directory rules, skill migration, or per-turn token reduction.
- **Greenfield projects with no instruction file yet** — just write a good root `AGENTS.md` from scratch using the target structure directly (not `/init`, which writes a `CLAUDE.md`).
- **Root instruction file already under 200 lines and no `CLAUDE.md` to retire** — unless there's a specific pain point (broken references, stale content), don't churn.
- **The user is in active feature work** — wait for a clean checkpoint. This skill touches many files and makes review difficult mid-feature.
- **Monorepos where the instruction files are split across workspaces** — the skill handles a single-repo run cleanly, and monorepo sub-packages work too (it auto-detects a parent CLAUDE.md). But if the user wants the whole monorepo optimized in one pass, brainstorm the scope first.

---

## References

- `references/audit-steps.md` — the fifteen Phase 1 audit steps, in order
- `references/anti-patterns.md` — the ten rules above with their reasons and the cases behind them
- `references/execute-steps.md` — the nine Phase 4 execution steps, in order
- `references/memory-mechanics.md` — How Claude Code discovers and loads AGENTS.md / imports, when AGENTS.md support is unavailable, and how to retire the old sibling pattern
- `references/content-categorization.md` — Decision framework for facts vs procedures vs area-rules
- `references/skill-writing.md` — How to write trigger-focused skill descriptions that actually match user intent
- `references/verification.md` — Full post-change verification checklist

## Scripts

- `scripts/audit-memory-tree.ps1` — deterministic Phase 1 measurements (true root line counts, every `CLAUDE.md`-family file in the repo and its parent directories labelled delete or migrate, the triage verdict, the Claude Code version, downward `@import` hits, broken `.md` references in the root instruction file). PowerShell 5.1-compatible; read-only.

## Assets

- `assets/plan-structure.template.md` — Plan file skeleton
- `assets/report.template.md` — Before/after report template
