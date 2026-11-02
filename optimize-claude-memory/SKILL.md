---
name: optimize-claude-memory
description: Audit and restructure a repository's agent memory system (AGENTS.md, CLAUDE.md, skills, MEMORY.md) to minimize per-turn token usage, enable multi-agent portability (Claude Code + Copilot + Cursor + Cody all reading the same AGENTS.md), and preserve context accuracy. Use when the user wants to "optimize CLAUDE.md", "add AGENTS.md", "support multiple agents", "make docs portable across Copilot/Cursor/Cody", "reduce token usage", "speed up Claude", "shrink memory", "audit AGENTS.md", "fix the claude setup", "make this repo ready for Claude", "add an AGENTS file for each service", "full docs on every service", "port the optimization pattern to another project", "remove the CLAUDE.md files", "Claude reads AGENTS.md now", "move rules into skills", or mentions CLAUDE.md being too long / hard to follow / slow / duplicated, or AGENTS.md not loading. Also triggers on "Claude Code memory", "context window", "skill migration", "@AGENTS.md pattern", "sibling CLAUDE.md", "nested CLAUDE.md", "directory-scoped rules", "monorepo docs", or "claude.md best practices". Any stack or monorepo; plan-first and approval-gated. (The claude-md-improver plugin covers template-based CLAUDE.md quality audits; this skill owns the AGENTS.md-only layout, retiring CLAUDE.md files, and token optimization.)
---

# Optimize Claude Memory

Restructure a repo's memory layout so that **always-true facts live in the root `AGENTS.md`** (portable across every coding agent — Claude Code, Copilot, Cursor, Cody), **procedures move into skills** (free until triggered), **area-specific rules live in per-subdirectory `AGENTS.md` files**, and **the repo has no `CLAUDE.md` at all**: Claude Code v2.1.277 and later reads `AGENTS.md` itself.

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

**Why no `CLAUDE.md`, anywhere:** with the default **Project instructions** setting (`claude-md-or-agents-md`), Claude Code reads `AGENTS.md` only while there is **no** `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or any directory above it. One such file on that path switches Claude to CLAUDE.md-only, and every `AGENTS.md` without an `@AGENTS.md` sibling silently stops loading. So it is all or nothing: none in the repo, none in a parent directory, no `CLAUDE.local.md`. `~/.claude/CLAUDE.md`, managed policy files and `.claude/rules/` don't count and keep loading.

**Why AGENTS.md is the content file:** a single file serves every agent. Claude Code, Copilot, Cursor, Cody, and future agents all read `AGENTS.md` directly. One source of truth, no second file to keep in sync.

**Where Claude-only content goes:** `.claude/rules/*.md`, which loads alongside `AGENTS.md` and can be path-scoped with `paths:` frontmatter. Personal, uncommitted notes go in `~/.claude/CLAUDE.md`, not a `CLAUDE.local.md` (that one counts, and switches `AGENTS.md` off unless Project instructions is `claude-md-and-agents-md`).

### Fallback: the legacy sibling pattern

Before v2.1.277 Claude Code read only `CLAUDE.md`, so this skill used to put a one-line `CLAUDE.md` (`@AGENTS.md`) beside every `AGENTS.md`. Keep that pattern only when some session on the team can't read `AGENTS.md` directly, and then keep it **complete, at every level including root**:

- someone runs Claude Code older than v2.1.277 (older than v2.1.281 on Amazon Bedrock or with telemetry disabled);
- the built-in `AGENTS.md` plugin is disabled, or Project instructions is set to `claude-md`;
- the repo relies on `InstructionsLoaded` hooks (they don't fire for an `AGENTS.md` read directly), or on `--add-dir` with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` (that loads an added directory's `CLAUDE.md`, never its `AGENTS.md`).

Ask the user before choosing the fallback; otherwise default to no `CLAUDE.md`. Never mix the two: a root `CLAUDE.md` over subdirectory `AGENTS.md` files that lack siblings loses those files for Claude.

---

## What success looks like

- Root `AGENTS.md` under **200 lines** (target 120–150), per official guidance — holds only always-true facts
- **No `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the repo or any parent directory** (`~/.claude/CLAUDE.md` is fine), unless the user chose the fallback
- Root `AGENTS.md` carries a one-line note that there is no `CLAUDE.md` on purpose, so `/init` or another agent doesn't recreate one
- Every subdirectory with substantive rules has its own `AGENTS.md` — it loads on demand when Claude opens a file there
- Every service/package in a monorepo has its own `AGENTS.md` and a human-facing `README.md` — users frequently ask for "docs for every service," so make this a default
- Procedures and reference material moved into `.claude/skills/` with tight trigger-focused descriptions
- `MEMORY.md` (if the repo uses auto-memory) trimmed to current state — no completed migration history
- Duplicate task/todo files consolidated
- Broken doc references fixed
- Stale commands reconciled across AGENTS.md / README.md (common: deprecated CLIs lingering in one but fixed in another)
- **No per-directory file counts in navigation tables** — steer by complexity/purpose labels instead; full rule and rationale in anti-pattern #10 below.
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
- **Legacy sibling pattern** — an `AGENTS.md` tree plus one-line `@AGENTS.md` `CLAUDE.md` files. Also a touch-up: its main item is deleting every one-liner, root included, in one change, once the user confirms no session needs the fallback.
- **Migration** — a monolithic root `CLAUDE.md` (or `CLAUDE.md` files holding real content), few or no `AGENTS.md` files. The full workflow below applies.

  For either touch-up, the win is *deltas*, not a restructure. Make the plan a **minimal diff** and state plainly that the repo is already on (or one deletion away from) the pattern — otherwise a big-sounding six-phase workflow reads as alarming on a repo that's 95% done, and you risk manufacturing a restructure it doesn't need. Most steps below still apply; you'll just be confirming compliance rather than building from scratch.

  When a touch-up's root file is over its line budget: **line count only drops when you remove whole lines — trimming prose inside a table row saves tokens, not lines** (canonical explanation: `references/verification.md` §1). If the only big block left to cut is one *pinned* by a "keep in sync" convention (anti-pattern #9), you usually can't reach the budget without either finding other whole-line cuts or dropping real content: say that to the user as a decision rather than quietly condensing the pinned block.

0. **Step 0 — prior-run memory.** Glob `~/.claude/plans/` for a prior plan and its `<plan>-report.md` for this repo (Phase 6 writes the report next to the plan). If found, read the report's "Deliberately NOT doing" / follow-up sections and **diff against it instead of cold-auditing** — run N must not re-propose changes run N−1 deliberately rejected; carry unresolved follow-ups into this run's plan.
1. **Baseline build/lint/type-check BEFORE editing anything (when there IS a root build).** Run the stack-appropriate commands and save their output — in Phase 5 you'll diff against these to distinguish pre-existing issues from regressions.
   ```
   npm run type-check 2>&1 | tee /tmp/baseline-typecheck.txt
   npm run lint 2>&1 | tee /tmp/baseline-lint.txt
   ```
   **Skip the baseline entirely when the repo has no root-level build/lint** (e.g., docker-compose monorepos where each service has its own tooling, or pure-docs repos). Markdown-only changes cannot regress a build that doesn't exist. Detect this by looking for a root `package.json` / `pyproject.toml` / `Cargo.toml` with runnable `lint`/`check`/`test` scripts. If all you find is `docker-compose.yml` and `k8s/` manifests, skip and say so in the plan.
2. **Measure the root instruction files** (`CLAUDE.md` if present, and `AGENTS.md`):
   - `wc -l AGENTS.md` (bash) or `(Get-Content AGENTS.md).Count` (PowerShell). Avoid PowerShell `Measure-Object -Line` — it skips blank lines and undercounts the real total (see `references/verification.md`).
   - Note line count and identify section boundaries
3. **Detect monorepo context.** If the repo sits inside a parent that has its own `CLAUDE.md` (e.g., `cid-main/cids-frontend/` with `cid-main/CLAUDE.md`):
   - Note that the parent `CLAUDE.md` auto-loads at startup — it counts against the token budget, **and its presence stops Claude reading this repo's `AGENTS.md` at all**
   - Read the parent briefly; check for overlap with the current repo's instruction files
   - Flag it in the plan: its content moves to the parent's `AGENTS.md` (or `~/.claude/CLAUDE.md` if it is personal) and the file goes, or the user picks the fallback
4. **Inventory the memory tree:**
   - `Glob` for all `AGENTS.md` files (exclude `node_modules/**`, `vendor/**`, `.venv/**`, `target/**`)
   - **List every `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md`** in the repo and in each parent directory (the audit script does both). Label each: a one-line `@AGENTS.md` import (delete), or a file with real content (migrate its content, then delete)
   - `Glob` for all `README.md` files that function as agent guidance (skip library READMEs in sub-packages unless they exist in `src/`)
   - `Glob` for existing skills at `.claude/skills/*/SKILL.md`
   - **Also glob user-level skills at `~/.claude/skills/*/SKILL.md`** — many will already cover content that would otherwise seem to need a new skill. Read their descriptions. This is the cross-repo reuse check — skip duplicating what already exists at user level.
5. **Check that Claude can read `AGENTS.md` here.** `claude --version` must be v2.1.277 or later (the script prints it). Check **Project instructions** (`/config`, or `pluginConfigs` → `cc-plugin-agents-md@builtin` → `options.instructionFiles` in `~/.claude/settings.json`) is not `claude-md`. Ask the user whether anyone on the team falls under the fallback list above; the answer decides the target pattern.
6. **Detect the stack** (affects which skills to suggest):
   - Check `package.json` → React/Vue/Svelte/Angular/Node
   - Check `pyproject.toml` or `requirements.txt` → Python
   - Check `go.mod` → Go / `Cargo.toml` → Rust / `composer.json` → PHP / `Gemfile` → Ruby
   - Check for Vite/Webpack/Turborepo config
7. **Detect the shell/OS** from existing instruction-file declarations, `.gitignore`, CI configs:
   - Windows/PowerShell, Windows/Bash (Claude Code default), macOS/zsh, Linux/bash
   - The existing instruction file's environment block wins — honor it
8. **Read the root `CLAUDE.md`** (if any) in full — categorize mentally as you read (Phase 2).
9. **Read the root `AGENTS.md`** if present — identify overlap with CLAUDE.md.
10. **Check for `MEMORY.md`** at `~/.claude/projects/<project-slug>/memory/MEMORY.md` if it exists. If the directory doesn't exist, that's fine — user may not be using file-based memory — skip MEMORY.md steps in execution.
11. **Sweep for broken internal references.** Check EVERY file reference in the root instruction file (`CLAUDE.md` while it exists, else `AGENTS.md`), not just `.claude/instructions/`. Real cases seen in the wild:
   - CLAUDE.md references `AGENTS.md` (root) but `AGENTS.md` doesn't exist
   - CLAUDE.md references `tasks/lessons.md` but it doesn't exist
   - CLAUDE.md references `../CLAUDE.md` (parent) that doesn't exist
   - CLAUDE.md references removed instruction files

   Tactic: `Grep` for any `*.md` path or `src/**` path in the file, then verify each file exists. Track the list — these are fixes for Phase 4.
12. **Scan existing AGENTS.md files for style conventions** — heading style (`# Title` vs `# Title — Subtitle`), table formats, emoji use, callout style. Preserve these in any new AGENTS.md you write, so the tree stays consistent.
13. **Monorepo gap scan — per-service/per-package docs.** For every service/package directory (`services/*/`, `packages/*/`, `apps/*/`, etc.), check whether it has:
    - `AGENTS.md` — source of truth for that service
    - `README.md` — human-facing overview

    Users commonly ask for "docs on every service." Flag any missing files here — creating them is a primary output of this skill, not an afterthought. In Phase 3 the plan should enumerate every gap explicitly.
14. **Command-consistency sweep.** When both `CLAUDE.md` / `AGENTS.md` AND a `README.md` describe the same commands, they often drift. The newer one usually wins. Common examples: `tctl` → `temporal operator namespace`, `huggingface-cli` → `hf`, `pip` → `uv pip`, deprecated npm scripts. `Grep` for commands that appear in one file but not the other, and flag the divergence — Phase 4 will reconcile.

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

Write a plan to `C:\Users\<user>\.claude\plans\` (Windows) or `~/.claude/plans/` (macOS/Linux) using the structure in `assets/plan-structure.template.md`. The plan must include:

- **Context** — why this change is happening (current line count, token cost)
- **Target pattern** — state explicitly: "AGENTS.md holds content at every level; no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` remains in the repo or above it." This is the default. Use the legacy sibling pattern only if Phase 1 step 5 found a session that needs it, and say which.
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

Work through the plan in this order (low-risk changes first):

1. **Create new skills — but ONLY after checking user-level skills first.** For every candidate new skill:
   - Did Phase 1 find a matching skill at `~/.claude/skills/` already? If yes, **don't duplicate** — remove the content from the instruction file and replace with a pointer (`"/skill-name"`). The cross-repo reuse is the whole point.
   - Only create net-new skills for content that's genuinely unique to this repo (e.g., a skill documenting this project's bespoke auth/SSO flow — something no other repo shares).
   - Location choice:
     - **`~/.claude/skills/`** if the skill applies across repos (stack-agnostic or applies to every project using a common framework)
     - **`.claude/skills/` (repo-local)** if the skill is genuinely specific to this project
   - YAML frontmatter with `name` and `description` (≤1,536 chars)
   - Descriptions MUST include explicit trigger keywords — see `references/skill-writing.md` for the craft
   - Skill body contains the actual procedure/reference content extracted from CLAUDE.md
   - For building or eval-testing a NEW skill, hand off to `skill-creator`; for auditing existing skills against best practices, `skill-optimizer`.
2. **Write or update every `AGENTS.md`** (this is where the content lives):
   - **Root `AGENTS.md`** — the trimmed, facts-only version: environment, project one-liner + stack, commands table, 10–15 critical rules, service-docs pointer table (points at each subdirectory's AGENTS.md), skill pointers, core workflow line, and one line saying there is no `CLAUDE.md` on purpose (what one would break, and that Claude-only rules go in `.claude/rules/`). Target 120–150 lines.
   - **Subdirectory `AGENTS.md` files** — one per service/package/area with substantive rules. When moving content from a pre-existing `CLAUDE.md`, **default to verbatim** — preserve the team's wording, just change the H1 header to reflect the new filename. Only rewrite to fix stale commands or broken references.
   - Preserve any project-specific conventions already present (don't overwrite — merge)
3. **Delete every `CLAUDE.md`-family file in one change** (repo and parent directories, from the Phase 3 list):
   - Only after step 2 has landed each file's content in an `AGENTS.md`, `.claude/rules/`, or `~/.claude/CLAUDE.md`. A one-liner `@AGENTS.md` has nothing to migrate.
   - All of them together. Deleting the subdirectory one-liners while a root `CLAUDE.md` (or a `CLAUDE.local.md`) remains makes those subdirectories' `AGENTS.md` vanish for Claude.
   - Use `git rm` inside the repo so the deletion is staged with the rest. A file in a parent directory is outside the repo: list it for the user rather than deleting it unasked.
   - **Skip files inside an existing skill** (e.g., `.claude/skills/<name>/…`) and dependency directories (`node_modules/`, `.venv/`, `vendor/`).
   - **Fallback only:** instead of deleting, make sure every `AGENTS.md`, root included, has a sibling `CLAUDE.md` whose whole content is `@AGENTS.md`.
4. **CRITICAL — NEVER `@import` *subdirectory* AGENTS.md from the root AGENTS.md.** `@path` imports inside an `AGENTS.md` expand when it loads, so reaching down from root (e.g., `@services/x/AGENTS.md`) forces every session to load subtree content at startup — defeating the on-demand loading. The rule is: **never import downward into the tree from an ancestor file.**
5. **Reconcile stale commands** across the files that describe the same commands (from Phase 1 step 14). If `tctl` lingers in one file and `temporal operator namespace` is in another, the newer CLI wins. Fix everywhere (AGENTS.md, README.md). Keep a one-line deprecation notice where it helps future readers.
6. **Trim `MEMORY.md`** if accessible:
   - Remove COMPLETE migration blocks (they're in git history / lessons files now)
   - Remove stale references to deleted files, including any memory that still describes sibling `CLAUDE.md` files as current
   - Keep current state, active patterns, all active project/feedback memories
7. **Consolidate duplicate task files** (common pattern: `todo.md` + `ACTION_ITEMS.md` or similar):
   - Merge into the primary file with a clear divider section
   - Delete the redundant file
   - Update any README/AGENTS.md that referenced it
8. **Fix broken references** (the full list you built in Phase 1 step 11):
   - If the old root CLAUDE.md referenced a missing `tasks/lessons.md`, create it with the standard two-rule header (AGENTS.md is facts-only; there is no CLAUDE.md) — it's easier than deleting the reference because future sessions genuinely benefit from this file
   - If it referenced deleted instruction files, replace with skill pointers (`/skill-name`) or correct paths to their replacements
   - Preserve existing AGENTS.md formatting conventions you noted in Phase 1 (heading style, tables, callouts)
9. **Update the lessons file** (if the project has one like `tasks/lessons.md`):
    - Add an entry documenting the AGENTS.md-as-facts-only principle
    - Add an entry saying there is no `CLAUDE.md`: Claude Code reads `AGENTS.md` itself, and a `CLAUDE.md` or `CLAUDE.local.md` would switch that off
    - This helps future maintainers understand the structure

**Git:** Never commit, stash, or push. The user manages git manually. Every project tested so far has this rule — honor it universally.

### Phase 5 — Verify

Run the checks from `references/verification.md`. Short version:

1. **Line count** — root `AGENTS.md` ≤ 200 (target 150)
2. **No `CLAUDE.md` left** — no `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the repo (outside skill dirs, `node_modules/`, `.venv/`, `vendor/`) or its parent directories. Under the fallback instead: every `AGENTS.md`, root included, has a sibling `CLAUDE.md` containing only `@AGENTS.md`. Every service/package flagged in Phase 1 step 13 now has `AGENTS.md` + `README.md`.
3. **No downward `@import`** — grep root `AGENTS.md` for any `@` path containing a slash (e.g., `@services/`). There should be none.
4. **Diff against Phase 1 baseline** — only if you took one. Run `npm run lint`, `npm run type-check`, etc. and **diff** against your baseline files. Markdown-only changes cannot cause build/lint/type-check failures, so any error present now that was present in the baseline is pre-existing. Flag only NEW failures as regressions. **Report pre-existing errors transparently in the final report** — don't pretend they're yours, don't hide them either. Skip this step if Phase 1 step 1 determined there's no root build.
5. **Broken reference sweep** — grep for any remaining references to files that were deleted or renamed.
6. **Stale-command sweep** — grep for the deprecated commands you identified in Phase 1 step 14 (e.g., `tctl`, `huggingface-cli`). Any remaining occurrences should be in deliberate deprecation notices, not as live instructions.
7. **Fresh-session check** (ask the user) — in a new Claude Code session in the repo, `/memory` lists the root `AGENTS.md` (an interactive session also prints `no CLAUDE.md found; AGENTS.md loaded: <path>`); after Claude opens a file in a subdirectory, that directory's `AGENTS.md` appears. Then ask 2–3 representative questions and confirm the right skill triggers. The first session after upgrading from v2.1.276 or earlier may still read `CLAUDE.md` only; the next one reads `AGENTS.md`.

### Phase 6 — Report

Write a before/after report using `assets/report.template.md`. Include:

- Line count reduction table (root CLAUDE.md → root AGENTS.md, MEMORY.md if trimmed)
- New skill count + their trigger keywords
- `CLAUDE.md` files removed (or, under the fallback, sibling coverage)
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

## Anti-patterns to avoid

1. **Reaching *down* from root via `@import`.** Writing `@services/x/AGENTS.md` in the root `AGENTS.md` forces every session to load subtree content at startup — it nullifies on-demand loading. Imports inside an `AGENTS.md` expand exactly like imports inside a `CLAUDE.md`.
2. **Leaving any `CLAUDE.md` behind.** Content in a `CLAUDE.md` is Claude-only, and the file's mere presence (repo root, a parent directory, or a `CLAUDE.local.md`) switches native `AGENTS.md` reading off below it. The worst state is half-removed: subdirectory one-liners deleted, root `CLAUDE.md` kept, so every subdirectory `AGENTS.md` silently stops loading. `/init` writes a root `CLAUDE.md`, which is why the root `AGENTS.md` says there is none on purpose.
3. **Creating skills with vague descriptions.** A skill whose description is "Use for UI work" won't trigger reliably. See `references/skill-writing.md`.
4. **Deleting content you don't understand.** If a section seems obscure, ask the user before removing it — might be load-bearing for some rare workflow.
5. **Rewriting existing content when moving it.** When migrating a team's prior CLAUDE.md into AGENTS.md, default to verbatim copy. They wrote it carefully; don't silently reword. Only rewrite to fix stale commands or broken references, and note those rewrites in the plan.
6. **Merging AGENTS.md and README.md.** They serve different audiences. AGENTS.md = agent-facing rules; README.md = human-facing overview. Respect the existing split if it's there.
7. **Rewriting everything at once.** Work low-risk to high-risk: new and updated AGENTS.md files first, then the `CLAUDE.md` deletions (all in one step), then stale-command fixes. If something breaks mid-execute, you can stop without leaving the repo half-migrated.
8. **Skipping the plan approval.** Plan mode is the user's safety net. Even if the plan seems obvious, write it and get approval.
9. **Moving a block that's deliberately duplicated.** Some repos keep the same content in two places on purpose and document it — an index that says "keep `adr/README.md` and root `AGENTS.md` in sync," a table marked "canonical" or "source of truth." Before relocating or collapsing any block, grep the tree near that content for `keep .* in sync`, `source of truth`, `canonical`. If a documented convention pins it, it's load-bearing: surface it to the user as a decision (keep / slim / re-point the convention) rather than moving it unilaterally and silently breaking the rule. The win on an already-optimized repo comes from collapsing *un*-pinned duplication (Bucket 5 in `references/content-categorization.md`), not from fighting an intentional one.
10. **Per-directory file counts baked into the docs.** A count cell in a multi-row navigation table is the worst possible home for a number that changes constantly — every file add invalidates a cell, so the table is always wrong somewhere, and nobody keeps dozens of cells current (they drift 50–250% in practice). Don't add them, and strip them when you find them. The complexity label (LOW/MEDIUM/HIGH) is what actually drives "should I read this first?" — the raw number was never doing that work. If a size signal genuinely helps, keep at most one approximate count in the area doc's *header*. A precise count is a one-line shell command (`find` / `Get-ChildItem`) when someone needs it. Also reconcile any "update the file count when you add a file" maintenance rule the repo documents — it mandates exactly the drift you're removing; reword it to "refresh the area header count only on material drift (≈25+ files)."

---

## When NOT to use this skill

- **Template-based CLAUDE.md quality audits** — that's the `claude-md-management:claude-md-improver` plugin's territory (scans CLAUDE.md files, scores them against templates, makes targeted quality updates). Use this skill when the goal is the portable AGENTS.md-only layout, nested directory rules, skill migration, or per-turn token reduction.
- **Greenfield projects with no instruction file yet** — just write a good root `AGENTS.md` from scratch using the target structure directly (not `/init`, which writes a `CLAUDE.md`).
- **Root instruction file already under 200 lines and no `CLAUDE.md` to retire** — unless there's a specific pain point (broken references, stale content), don't churn.
- **The user is in active feature work** — wait for a clean checkpoint. This skill touches many files and makes review difficult mid-feature.
- **Monorepos where the instruction files are split across workspaces** — the skill handles a single-repo run cleanly, and monorepo sub-packages work too (it auto-detects a parent CLAUDE.md). But if the user wants the whole monorepo optimized in one pass, brainstorm the scope first.

---

## References

- `references/memory-mechanics.md` — How Claude Code discovers and loads AGENTS.md / CLAUDE.md / imports, and the legacy sibling pattern
- `references/content-categorization.md` — Decision framework for facts vs procedures vs area-rules
- `references/skill-writing.md` — How to write trigger-focused skill descriptions that actually match user intent
- `references/verification.md` — Full post-change verification checklist

## Scripts

- `scripts/audit-memory-tree.ps1` — deterministic Phase 1 measurements (true root line counts, every `CLAUDE.md`-family file in the repo and its parent directories labelled delete or migrate, the triage verdict, the Claude Code version, downward `@import` hits, broken `.md` references in the root instruction file). PowerShell 5.1-compatible; read-only.

## Assets

- `assets/plan-structure.template.md` — Plan file skeleton
- `assets/report.template.md` — Before/after report template
