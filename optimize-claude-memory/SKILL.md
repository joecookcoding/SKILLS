---
name: optimize-claude-memory
description: Audit and restructure a repository's agent memory system (CLAUDE.md, AGENTS.md, skills, MEMORY.md) to minimize per-turn token usage, enable multi-agent portability (Claude Code + Copilot + Cursor + Cody all reading the same AGENTS.md), and preserve context accuracy. Use when the user wants to "optimize CLAUDE.md", "add AGENTS.md", "support multiple agents", "make docs portable across Copilot/Cursor/Cody", "reduce token usage", "speed up Claude", "shrink memory", "audit AGENTS.md", "fix the claude setup", "make this repo ready for Claude", "add a CLAUDE/AGENTS file for each service", "full docs on every service", "port the optimization pattern to another project", "add nested CLAUDE.md files", "move rules into skills", or mentions CLAUDE.md being too long / hard to follow / slow / duplicated. Also triggers on "Claude Code memory", "context window", "skill migration", "@AGENTS.md pattern", "sibling CLAUDE.md", "directory-scoped rules", "monorepo docs", or "claude.md best practices". Works in any repo (React, Vue, Python, Go, Rust, monorepo, docker-compose, etc.) — detects stack and shell, adapts recommendations. Always produces a plan file for user approval before editing; never commits. Expected result: 2,000–2,600 tokens saved per turn, docs usable by any coding agent, plus improved skill triggering accuracy.
---

# Optimize Claude Memory

Restructure a repo's memory layout so that **always-true facts live in `AGENTS.md`** (portable across every coding agent — Claude Code, Copilot, Cursor, Cody), **procedures move into skills** (free until triggered), **area-specific rules live in per-subdirectory `AGENTS.md` files**, and **every `AGENTS.md` gets a sibling `CLAUDE.md` containing only `@AGENTS.md`** so Claude Code picks it up automatically.

Reference mechanics: see `references/memory-mechanics.md`. Official source: [Claude Code memory docs](https://code.claude.com/docs/en/memory).

## The pattern at a glance

```
repo/
├── AGENTS.md          ← source of truth (agent-agnostic)
├── CLAUDE.md          ← one line: @AGENTS.md
└── services/
    └── x/
        ├── AGENTS.md  ← subdirectory source of truth
        ├── CLAUDE.md  ← one line: @AGENTS.md
        └── README.md  ← human-facing overview (untouched)
```

**Why AGENTS.md is the content file, not CLAUDE.md:** a single file serves every agent. Claude Code picks it up via the sibling `CLAUDE.md` (which `@import`s it). Copilot, Cursor, Cody, and future agents read `AGENTS.md` directly. One source of truth, zero duplication, zero ongoing maintenance burden from keeping two files in sync.

**Why sibling `@AGENTS.md` is safe even at root:** `@import` at the *same* directory level just resolves to content-that-would-have-loaded-anyway. The anti-pattern is reaching *down* from root into subdirectory `AGENTS.md` files (see "Anti-patterns" below).

---

## What success looks like

- Root `AGENTS.md` under **200 lines** (target 120–150), per official guidance — holds only always-true facts
- Root `CLAUDE.md` is one line: `@AGENTS.md`
- Every subdirectory with substantive rules has an `AGENTS.md` + sibling `CLAUDE.md` (one line: `@AGENTS.md`) — subdir content loads on demand when Claude works there
- Every service/package in a monorepo has its own `AGENTS.md` (+ sibling `CLAUDE.md`) and a human-facing `README.md` — users frequently ask for "docs for every service," so make this a default
- Procedures and reference material moved into `.claude/skills/` with tight trigger-focused descriptions
- `MEMORY.md` (if the repo uses auto-memory) trimmed to current state — no completed migration history
- Duplicate task/todo files consolidated
- Broken doc references fixed
- Stale commands reconciled across CLAUDE.md / AGENTS.md / README.md (common: deprecated CLIs lingering in one but fixed in another)
- Build, type-check, and lint still pass (if the repo has any — docs-only repos skip this)

Expected savings: **~2,000–2,600 tokens per turn** from CLAUDE.md reduction; additional **~300–400 tokens** if MEMORY.md is trimmed. Accuracy improves because tight skill descriptions match intent better than a monolithic rules file.

---

## Workflow

Follow these phases in order. Phase 3 (plan approval) is the only mandatory user checkpoint — everything before it is read-only, everything after it executes the approved plan.

### Phase 1 — Audit (read-only)

Goal: understand the current state before proposing changes, AND establish a baseline so post-change verification is unambiguous.

1. **Baseline build/lint/type-check BEFORE editing anything (when there IS a root build).** Run the stack-appropriate commands and save their output — in Phase 5 you'll diff against these to distinguish pre-existing issues from regressions.
   ```
   npm run type-check 2>&1 | tee /tmp/baseline-typecheck.txt
   npm run lint 2>&1 | tee /tmp/baseline-lint.txt
   ```
   **Skip the baseline entirely when the repo has no root-level build/lint** (e.g., docker-compose monorepos where each service has its own tooling, or pure-docs repos). Markdown-only changes cannot regress a build that doesn't exist. Detect this by looking for a root `package.json` / `pyproject.toml` / `Cargo.toml` with runnable `lint`/`check`/`test` scripts. If all you find is `docker-compose.yml` and `k8s/` manifests, skip and say so in the plan.
2. **Measure root `CLAUDE.md`:**
   - `wc -l CLAUDE.md` (bash) or `(Get-Content CLAUDE.md | Measure-Object -Line).Lines` (PowerShell)
   - Note line count and identify section boundaries
3. **Detect monorepo context.** If the repo sits inside a parent that has its own `CLAUDE.md` (e.g., `cid-main/cids-frontend/` with `cid-main/CLAUDE.md`):
   - Note that the parent `CLAUDE.md` auto-loads at startup too — it counts against the token budget
   - Read the parent briefly; check for overlap with the current repo's CLAUDE.md
   - Flag if the parent has area-specific rules that should be moved to sub-repo level instead
4. **Inventory the memory tree:**
   - `Glob` for all `AGENTS.md` files (exclude `node_modules/**`, `vendor/**`, `.venv/**`, `target/**`)
   - `Glob` for all `README.md` files that function as agent guidance (skip library READMEs in sub-packages unless they exist in `src/`)
   - `Glob` for existing skills at `.claude/skills/*/SKILL.md`
   - **Also glob user-level skills at `~/.claude/skills/*/SKILL.md`** — many will already cover content that would otherwise seem to need a new skill. Read their descriptions. This is the cross-repo reuse check — skip duplicating what already exists at user level.
   - Note every directory that has AGENTS.md but no sibling CLAUDE.md
5. **Detect the stack** (affects which skills to suggest):
   - Check `package.json` → React/Vue/Svelte/Angular/Node
   - Check `pyproject.toml` or `requirements.txt` → Python
   - Check `go.mod` → Go / `Cargo.toml` → Rust / `composer.json` → PHP / `Gemfile` → Ruby
   - Check for Vite/Webpack/Turborepo config
6. **Detect the shell/OS** from existing CLAUDE.md declarations, `.gitignore`, CI configs:
   - Windows/PowerShell, Windows/Bash (Claude Code default), macOS/zsh, Linux/bash
   - The existing CLAUDE.md's environment block wins — honor it
7. **Read the root `CLAUDE.md`** in full — categorize mentally as you read (Phase 2).
8. **Read the root `AGENTS.md`** if present — identify overlap with CLAUDE.md.
9. **Check for `MEMORY.md`** at `~/.claude/projects/<project-slug>/memory/MEMORY.md` if it exists. If the directory doesn't exist, that's fine — user may not be using file-based memory — skip MEMORY.md steps in execution.
10. **Sweep for broken internal references.** Don't limit this to `.claude/instructions/` — check EVERY file reference in the root CLAUDE.md. Real cases seen in the wild:
   - CLAUDE.md references `AGENTS.md` (root) but `AGENTS.md` doesn't exist
   - CLAUDE.md references `tasks/lessons.md` but it doesn't exist
   - CLAUDE.md references `../CLAUDE.md` (parent) that doesn't exist
   - CLAUDE.md references removed instruction files

   Tactic: `Grep` for any `*.md` path or `src/**` path in CLAUDE.md, then verify each file exists. Track the list — these are fixes for Phase 4.
11. **Scan existing AGENTS.md files for style conventions** — heading style (`# Title` vs `# Title — Subtitle`), table formats, emoji use, callout style. Preserve these in any new AGENTS.md you write, so the tree stays consistent.
12. **Monorepo gap scan — per-service/per-package docs.** For every service/package directory (`services/*/`, `packages/*/`, `apps/*/`, etc.), check whether it has:
    - `AGENTS.md` — source of truth for that service
    - `CLAUDE.md` — should be one line (`@AGENTS.md`) for Claude-Code pickup
    - `README.md` — human-facing overview

    Users commonly ask for "docs on every service." Flag any missing files here — creating them is a primary output of this skill, not an afterthought. In Phase 3 the plan should enumerate every gap explicitly.
13. **Command-consistency sweep.** When both `CLAUDE.md` / `AGENTS.md` AND a `README.md` describe the same commands, they often drift. The newer one usually wins. Common examples: `tctl` → `temporal operator namespace`, `huggingface-cli` → `hf`, `pip` → `uv pip`, deprecated npm scripts. `Grep` for commands that appear in one file but not the other, and flag the divergence — Phase 4 will reconcile.

**Do not edit anything yet.** Produce a written audit for yourself summarizing: baseline state (or "no root build, skipping baseline"), line counts, what's duplicated, what's stale, broken references found, services missing docs, obvious skills that emerge.

### Phase 2 — Categorize

For each section of the root `CLAUDE.md`, bucket it into one of four destinations. See `references/content-categorization.md` for the full decision framework with examples. Quick version:

| Bucket | Stays in root CLAUDE.md? | Test |
|---|---|---|
| **Always-true fact** | Yes | "Do I need to know this *every* turn, regardless of what I'm doing?" |
| **Procedure / reference** | No → skill | "Is this steps-to-do-X, or a lookup table I only need for specific tasks?" |
| **Area-specific rule** | No → nested AGENTS.md | "Does this only matter when editing files under `src/X/`?" |
| **Dead / stale** | No → delete | "Is this describing a pattern we no longer use, or a file that no longer exists?" |

Also inventory what nested `AGENTS.md` files are missing for directories that have substantive rules. Use the project's own convention if present — many repos use "AGENTS.md for 20+ file directories, README.md for 5–19, no doc for fewer."

### Phase 3 — Plan (REQUIRED user approval)

Write a plan to `C:\Users\<user>\.claude\plans\` (Windows) or `~/.claude/plans/` (macOS/Linux) using the structure in `assets/plan-structure.template.md`. The plan must include:

- **Context** — why this change is happening (current line count, token cost)
- **Target pattern** — state explicitly: "AGENTS.md holds content at every level; each gets a sibling `CLAUDE.md` containing `@AGENTS.md`." This is the default for multi-agent portability. Only deviate if the user explicitly prefers Claude-only.
- **Content migration map** — a table mapping every existing CLAUDE.md / AGENTS.md section to its destination. When moving existing content between files, the default is **verbatim** — preserve the team's prior wording unless a specific issue requires rewriting (stale command, broken reference, bad structure). Note any rewrites explicitly.
- **New skills to create** — each with its name, one-sentence purpose, and a draft description
- **New/updated AGENTS.md files** — each with a one-line purpose. Include every service/package that lacks one (from Phase 1 step 12).
- **Sibling CLAUDE.md files** — full list of directories needing `@AGENTS.md` siblings (root + every subdirectory with an AGENTS.md)
- **Collateral fixes** — broken references, duplicate files to merge, MEMORY.md trims, stale commands to reconcile (from Phase 1 step 13)
- **Expected outcome** — target root AGENTS.md line count, estimated token savings, lint/build impact ("none" for markdown-only; "none expected" if there IS a build)
- **Verification checklist** — from `references/verification.md`

Get explicit user approval before proceeding. If you're in plan mode, call `ExitPlanMode`. If you're not in plan mode (common when the skill is invoked directly), just write the plan file, summarize it in chat, and ask for approval conversationally — don't block on a tool that isn't available. **Do not proceed past this checkpoint without explicit approval.**

If the user rejects or requests changes, revise the plan and re-submit — don't start executing partial pieces.

### Phase 4 — Execute (after plan approval)

Work through the plan in this order (low-risk changes first):

1. **Create new skills — but ONLY after checking user-level skills first.** For every candidate new skill:
   - Did Phase 1 find a matching skill at `~/.claude/skills/` already? If yes, **don't duplicate** — remove the content from CLAUDE.md and replace with a pointer (`"/skill-name"`). The cross-repo reuse is the whole point.
   - Only create net-new skills for content that's genuinely unique to this repo (e.g., `cid-auth-flow` for CID — auth flow is CID-specific).
   - Location choice:
     - **`~/.claude/skills/`** if the skill applies across repos (stack-agnostic or applies to every project using a common framework)
     - **`.claude/skills/` (repo-local)** if the skill is genuinely specific to this project
   - YAML frontmatter with `name` and `description` (≤1,536 chars)
   - Descriptions MUST include explicit trigger keywords — see `references/skill-writing.md` for the craft
   - Skill body contains the actual procedure/reference content extracted from CLAUDE.md
2. **Write or update every `AGENTS.md`** (this is where the content lives):
   - **Root `AGENTS.md`** — the trimmed, facts-only version: environment, project one-liner + stack, commands table, 10–15 critical rules, service-docs pointer table (points at each subdirectory's AGENTS.md), skill pointers, core workflow line. Target 120–150 lines.
   - **Subdirectory `AGENTS.md` files** — one per service/package/area with substantive rules. When moving content from a pre-existing `CLAUDE.md`, **default to verbatim** — preserve the team's wording, just change the H1 header to reflect the new filename. Only rewrite to fix stale commands or broken references.
   - Preserve any project-specific conventions already present (don't overwrite — merge)
3. **Create sibling `CLAUDE.md` files** next to every `AGENTS.md` (including root):
   - Content is ONLY `@AGENTS.md` (or `@README.md` if that's what holds the rules)
   - Use `assets/nested-claude-md.template.md` as the exact content
   - At root, the sibling `@AGENTS.md` is fine and recommended — it just resolves to content that would load at startup anyway, and makes the source of truth a portable `AGENTS.md`.
   - **Skip directories inside an existing skill** (e.g., `.claude/skills/<name>/AGENTS.md`) — skills have their own discovery mechanism
   - **Skip `node_modules/`**, `.venv/`, `vendor/`, and other dependency directories
4. **Do NOT rewrite root `CLAUDE.md` separately** — with the sibling pattern it becomes a one-liner (`@AGENTS.md`). The writing work happens in step 2 (root `AGENTS.md`).
5. **CRITICAL — NEVER `@import` *subdirectory* AGENTS.md from the root CLAUDE.md / AGENTS.md.** `@import` expands at launch, so reaching down from root (e.g., `@services/x/AGENTS.md`) forces every session to load subtree content at startup — defeating the on-demand optimization. What IS fine: `@AGENTS.md` at the same directory level (root CLAUDE.md → root AGENTS.md, or subdir CLAUDE.md → subdir AGENTS.md). That's the sibling pattern working as designed. The rule is: **never import downward into the tree from an ancestor file**.
6. **Reconcile stale commands** across the files that describe the same commands (from Phase 1 step 13). If `tctl` lingers in one file and `temporal operator namespace` is in another, the newer CLI wins. Fix everywhere (AGENTS.md, README.md). Keep a one-line deprecation notice where it helps future readers.
7. **Trim `MEMORY.md`** if accessible:
   - Remove COMPLETE migration blocks (they're in git history / lessons files now)
   - Remove stale references to deleted files
   - Keep current state, active patterns, all active project/feedback memories
8. **Consolidate duplicate task files** (common pattern: `todo.md` + `ACTION_ITEMS.md` or similar):
   - Merge into the primary file with a clear divider section
   - Delete the redundant file
   - Update any README/AGENTS.md that referenced it
9. **Fix broken references** (the full list you built in Phase 1 step 10):
   - If CLAUDE.md referenced a missing root `AGENTS.md`, either create one (navigation-focused, facts already moved to CLAUDE.md) or remove the pointer
   - If CLAUDE.md referenced a missing `tasks/lessons.md`, create it with the standard two-rule header (CLAUDE.md is facts-only, sibling-CLAUDE.md pattern) — it's easier than deleting the reference because future sessions genuinely benefit from this file
   - If CLAUDE.md referenced deleted instruction files, replace with skill pointers (`/skill-name`) or correct paths to their replacements
   - Preserve existing AGENTS.md formatting conventions you noted in Phase 1 (heading style, tables, callouts)
10. **Update the lessons file** (if the project has one like `tasks/lessons.md`):
    - Add an entry documenting the CLAUDE.md-as-facts-only principle
    - Add an entry documenting the sibling-CLAUDE.md pattern
    - This helps future maintainers understand the structure

**Git:** Never commit, stash, or push. The user manages git manually. Every project tested so far has this rule — honor it universally.

### Phase 5 — Verify

Run the checks from `references/verification.md`. Short version:

1. **Line count** — root `AGENTS.md` ≤ 200 (target 150); root `CLAUDE.md` is exactly 1 line (`@AGENTS.md`)
2. **Pattern coverage** — every `AGENTS.md` (outside skill dirs, `node_modules/`, `.venv/`, `vendor/`) has a sibling `CLAUDE.md` containing only `@AGENTS.md`. Every service/package flagged in Phase 1 step 12 now has all three: AGENTS.md + CLAUDE.md + README.md.
3. **No downward `@import`** — grep root `AGENTS.md` and root `CLAUDE.md` for any `@` path containing a slash (e.g., `@services/`). There should be none. Only `@AGENTS.md` and `@README.md` (same directory) are valid.
4. **Diff against Phase 1 baseline** — only if you took one. Run `npm run lint`, `npm run type-check`, etc. and **diff** against your baseline files. Markdown-only changes cannot cause build/lint/type-check failures, so any error present now that was present in the baseline is pre-existing. Flag only NEW failures as regressions. **Report pre-existing errors transparently in the final report** — don't pretend they're yours, don't hide them either. Skip this step if Phase 1 step 1 determined there's no root build.
5. **Broken reference sweep** — grep for any remaining references to files that were deleted or renamed.
6. **Stale-command sweep** — grep for the deprecated commands you identified in Phase 1 step 13 (e.g., `tctl`, `huggingface-cli`). Any remaining occurrences should be in deliberate deprecation notices, not as live instructions.
7. **Smoke test** (optional, ask user) — in a fresh Claude Code session, ask 2–3 representative questions and confirm the right skill / nested AGENTS.md triggers.

### Phase 6 — Report

Write a before/after report using `assets/report.template.md`. Include:

- Line count reduction table (CLAUDE.md, AGENTS.md, MEMORY.md if trimmed)
- New skill count + their trigger keywords
- Sibling CLAUDE.md count
- Estimated per-turn token savings (2,000–2,500 typical + 300–400 if MEMORY trimmed)
- What the user should do next (install the skill on other repos, smoke-test in a fresh session)

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

Windows repos typically use PowerShell — never assume bash. Check CLAUDE.md for an explicit shell declaration first. Fall back to detecting from CI scripts (`*.ps1` vs `*.sh`). When running verification commands, use the correct syntax:

- Line count: PowerShell `(Get-Content file | Measure-Object -Line).Lines` vs bash `wc -l file`
- Directory walk: PowerShell `Get-ChildItem -Recurse` vs bash `find`
- Preferred: use the Glob, Grep, Read, Write, Edit tools which are cross-platform.

---

## Anti-patterns to avoid

1. **Reaching *down* from root via `@import`.** Writing `@services/x/AGENTS.md` in root CLAUDE.md or root AGENTS.md forces every session to load subtree content at startup — it nullifies the on-demand optimization. Sibling `@AGENTS.md` (same directory) is always fine, including at root.
2. **Keeping content in CLAUDE.md instead of AGENTS.md.** If content lives in CLAUDE.md, only Claude Code reads it. Moving it to AGENTS.md (with a `@AGENTS.md` sibling CLAUDE.md) makes it work for Copilot, Cursor, Cody, and any future agent at zero extra cost. The sibling is the trick.
3. **Creating skills with vague descriptions.** A skill whose description is "Use for UI work" won't trigger reliably. See `references/skill-writing.md`.
4. **Deleting content you don't understand.** If a section seems obscure, ask the user before removing it — might be load-bearing for some rare workflow.
5. **Rewriting existing content when moving it.** When migrating a team's prior CLAUDE.md into AGENTS.md, default to verbatim copy. They wrote it carefully; don't silently reword. Only rewrite to fix stale commands or broken references, and note those rewrites in the plan.
6. **Merging AGENTS.md and README.md.** They serve different audiences. AGENTS.md = agent-facing rules; README.md = human-facing overview. Respect the existing split if it's there.
7. **Rewriting everything at once.** Work low-risk to high-risk: new AGENTS.md files first, then sibling CLAUDE.md redirects, then stale-command fixes. If something breaks mid-execute, you can stop without leaving the repo half-migrated.
8. **Skipping the plan approval.** Plan mode is the user's safety net. Even if the plan seems obvious, write it and get approval.

---

## When NOT to use this skill

- **Greenfield projects with no CLAUDE.md yet** — just write a good one from scratch using the target structure directly.
- **CLAUDE.md already under 200 lines** — unless there's a specific pain point (broken references, stale content), don't churn.
- **The user is in active feature work** — wait for a clean checkpoint. This skill touches many files and makes review difficult mid-feature.
- **Monorepos where CLAUDE.md is split across workspaces** — the skill handles a single-repo run cleanly, and monorepo sub-packages work too (it auto-detects parent CLAUDE.md). But if the user wants the whole monorepo optimized in one pass, brainstorm the scope first.

---

## References

- `references/memory-mechanics.md` — How Claude Code discovers and loads CLAUDE.md / AGENTS.md / imports
- `references/content-categorization.md` — Decision framework for facts vs procedures vs area-rules
- `references/skill-writing.md` — How to write trigger-focused skill descriptions that actually match user intent
- `references/verification.md` — Full post-change verification checklist

## Assets

- `assets/nested-claude-md.template.md` — The one-line `@AGENTS.md` content
- `assets/plan-structure.template.md` — Plan file skeleton
- `assets/report.template.md` — Before/after report template
