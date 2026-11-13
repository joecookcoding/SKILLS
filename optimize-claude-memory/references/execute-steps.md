# Phase 4 Execution Steps

Run only after the user approved the plan. Low-risk changes first, so a stop midway never
leaves the repo half-migrated. Never commit, stash or push: the user manages git.

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
