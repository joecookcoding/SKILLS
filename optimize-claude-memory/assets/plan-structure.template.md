# Plan: Optimize Claude Memory — [repo name]

## Context

Current state:
- Root `CLAUDE.md`: **[N] lines / absent**
- Root `AGENTS.md`: **[N] lines / missing** (target: ≤200, ideally 120–150 per https://code.claude.com/docs/en/memory)
- `CLAUDE.md`-family files found: [N] in the repo, [N] in parent directories ([N] one-line `@AGENTS.md`, [N] with content)
- Claude Code version: [vX.Y.Z] (needs ≥ 2.1.277 to read AGENTS.md); Project instructions: [claude-md-or-agents-md / ...]; fix needed before AGENTS.md loads: [none / update Claude Code / change the setting]
- Existing skills: [count] at `.claude/skills/` + [count] at `~/.claude/skills/`
- Existing `AGENTS.md` files: [count] across the tree
- Services/packages missing `AGENTS.md`/`README.md`: [list from Phase 1 step 13]
- Stack: [React/Vue/Python/Go/docker-compose/etc.] + [TS/JS] + [Vite/Webpack/etc.]
- Root build: [yes — `npm run lint` etc. / no — docker-compose only / pure docs]
- Shell: [PowerShell/bash/zsh]
- Stale commands detected: [e.g., `tctl` in CLAUDE.md vs `temporal operator namespace` in README]

The root instruction file is above the guideline and mixes three content types that should live in different places. This plan redistributes content into the **AGENTS.md-only** pattern, with no `CLAUDE.md` left, so that all agents (Claude Code, Copilot, Cursor, Cody) read the same source of truth, while reducing per-turn token cost.

## Target pattern

```
AGENTS.md            ← source of truth; Claude Code (≥ v2.1.277) reads it at launch
.claude/rules/       ← optional: Claude-only rules
services/x/AGENTS.md ← subdirectory source of truth, loads on demand
```

No `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the repo or above it: any one of them makes Claude read only CLAUDE.md files and drop every `AGENTS.md`.

Never `@import` a subdirectory AGENTS.md from root — that forces subtree content into every startup.

## Constraints (encoded from CLAUDE.md / project conventions)

- [Shell constraint — PowerShell-only / bash / etc.]
- Never commit or push — user manages git manually
- [Any other per-project constraints observed during audit]

## Content migration map

When moving existing content between files, **default to verbatim** — preserve the team's wording. Only rewrite to fix stale commands, broken references, or bad structure. Call out any rewrites in the "Reason" column.

| Current CLAUDE.md section (line range) | Destination | Reason |
|---|---|---|
| [Section name] (L12–45) | Root `AGENTS.md` (facts) | Always-relevant |
| [Section name] (L60–120) | New skill `[skill-name]` | Multi-step reference |
| [Section name] (L130–180) | `services/x/AGENTS.md` (verbatim) | Area-specific |
| [Section name] (L200–220) | Delete (stale) | Describes deprecated flow |
| ... | ... | ... |

## New skills to create

For each:
- **Name:** skill name
- **Install location:** `.claude/skills/[name]/SKILL.md` (repo-scoped) or `~/.claude/skills/[name]/` (cross-repo)
- **Description draft:** [trigger-focused, ≤1,536 chars — see skill-writing.md]
- **Body source:** [which CLAUDE.md section or external doc]

Example:
- **Name:** `api-reference`
- **Install location:** `.claude/skills/api-reference/SKILL.md`
- **Description:** "Look up [project] API endpoints, schemas, tags. Use when need to find an endpoint, check request/response shapes, ..., or writing a new query hook and need to confirm the backend contract."
- **Body source:** current CLAUDE.md lines 432–440 + `public/docs/llms/` local files

## AGENTS.md updates

| Directory | Action | Content |
|---|---|---|
| `src/api/queries/` | Create new | TanStack Query direct-import rules + SSE coverage |
| `src/pages/` | Merge | Add New Page 5-step checklist (currently in root CLAUDE.md) |
| `src/constants/` | Verify | Status Model rules already present? |
| ... | ... | ... |

## CLAUDE.md files to delete

Every `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md` in the repo (except inside `.claude/skills/` and `node_modules/`), deleted together in one step:

| File | Content | Action |
|---|---|---|
| `CLAUDE.md` | [N] lines | Migrate per the map above, then delete |
| `src/api/CLAUDE.md` | `@AGENTS.md` | Delete |
| ... | ... | ... |

Parent directories: [`../CLAUDE.md` — the user removes or moves it; it is outside this repo]

**Total: [N] files.**

## Collateral

- [ ] Trim `MEMORY.md` at `~/.claude/projects/<slug>/memory/MEMORY.md` — remove completed migration blocks (list them)
- [ ] Add the one-line "no `CLAUDE.md` on purpose" note to the root `AGENTS.md`
- [ ] Merge duplicate task files (e.g., `ACTION_ITEMS.md` + `todo.md` → keep only `todo.md`); update `tasks/AGENTS.md` references
- [ ] Fix broken doc references: [list paths that point at deleted files]
- [ ] Add lesson entries to `tasks/lessons.md` (or project equivalent):
   - "AGENTS.md is facts-only"
   - "There is no CLAUDE.md: Claude Code reads AGENTS.md itself, and a CLAUDE.md or CLAUDE.local.md would switch that off"

## Execution order

Phase A (low risk — content lands in its new home before anything is removed):
1. Create new skills under `.claude/skills/` (or `~/.claude/skills/` if cross-repo)
2. Write each `AGENTS.md` — root + every subdirectory. For existing CLAUDE.md content being moved, copy **verbatim** (change only the H1 header) unless a specific section needs a stale-command fix.
3. `git rm` every `CLAUDE.md`-family file in the list, all in one step

Phase B (targeted fixes):
4. Reconcile stale commands flagged in Phase 1 (e.g., `tctl` → `temporal operator namespace`) across AGENTS.md and README.md
5. Fix broken references (missing linked files, deleted instruction docs)
6. Trim `MEMORY.md` (if applicable) — remove completed migration blocks
7. Merge duplicate task files

Phase C (verify):
8. Line count: root AGENTS.md ≤ 200
9. No `CLAUDE.md`-family file left in the repo or its parent directories (re-run the audit script)
10. Grep root AGENTS.md for any `@` path containing `/` — there should be none (no downward imports)
11. Run lint + type-check + build if the repo has a root build; skip if not (docker-compose monorepos, pure-docs)
12. Grep for broken references
13. Grep for deprecated commands flagged in Phase 1 — any remaining occurrences should be deliberate deprecation notices
14. Fresh session (ask user): `/memory` lists the root AGENTS.md; a subdirectory's AGENTS.md appears once Claude opens a file there

## Expected outcome

- Root instruction file: [N] → **~150 lines** (root AGENTS.md)
- New skills: [count] added
- AGENTS.md added: [count]
- CLAUDE.md files removed: [count]
- Broken references fixed: [count]
- Expected token savings per turn: **~[estimate] tokens**
- Build/lint/type-check: **no regressions expected** (markdown-only changes)

## Verification checklist (will apply after execution)

See `references/verification.md` in the skill directory. Summary:

- [ ] Root AGENTS.md ≤ 200 lines
- [ ] `npm run type-check` / stack equivalent passes
- [ ] `npm run lint` / stack equivalent passes
- [ ] No CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md in the repo or above it (outside skill dirs)
- [ ] No broken references remain
- [ ] Smoke test passes (optional)

## Files to modify

**New files:**
- `[list every new file path]`

**Modified files:**
- `[list every existing file being edited]`

**Deleted files:**
- `[list every file being removed — the CLAUDE.md files, merged duplicate task files]`

## Rollback plan

All changes are markdown + skill directories. No code changes, no dependency changes. Rollback = revert commits, or `git restore --staged --worktree` the touched files (that also brings back deleted `CLAUDE.md` files). If mid-execute something breaks, stop at the last completed phase and report state.
