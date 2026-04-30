# Plan: Optimize Claude Memory — [repo name]

## Context

Current state:
- Root `CLAUDE.md`: **[N] lines** (target: ≤200, ideally 120–150 per https://code.claude.com/docs/en/memory)
- Root `AGENTS.md`: [exists / missing]
- Existing skills: [count] at `.claude/skills/` + [count] at `~/.claude/skills/`
- Existing `AGENTS.md` files: [count] across the tree
- Services/packages missing `CLAUDE.md`/`AGENTS.md`: [list from Phase 1 step 12]
- Stack: [React/Vue/Python/Go/docker-compose/etc.] + [TS/JS] + [Vite/Webpack/etc.]
- Root build: [yes — `npm run lint` etc. / no — docker-compose only / pure docs]
- Shell: [PowerShell/bash/zsh]
- Stale commands detected: [e.g., `tctl` in CLAUDE.md vs `temporal operator namespace` in README]

The root CLAUDE.md is above the guideline and mixes three content types that should live in different places. This plan redistributes content into the **AGENTS.md-first + sibling CLAUDE.md** pattern so that all agents (Claude Code, Copilot, Cursor, Cody) read the same source of truth, while reducing per-turn token cost.

## Target pattern

```
AGENTS.md            ← source of truth everywhere
CLAUDE.md            ← one line: @AGENTS.md  (picks up AGENTS.md for Claude Code)
services/x/AGENTS.md ← subdirectory source of truth, loads on demand
services/x/CLAUDE.md ← one line: @AGENTS.md
```

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

## Sibling CLAUDE.md files to create

For every directory with AGENTS.md (except inside `.claude/skills/` and `node_modules/`):

- `src/CLAUDE.md` → `@AGENTS.md`
- `src/api/CLAUDE.md` → `@AGENTS.md`
- `src/api/queries/CLAUDE.md` → `@AGENTS.md`
- ... (full list)

Each file contains only one line: `@AGENTS.md` (or `@README.md` if that's where the rules live).

**Total: [N] sibling CLAUDE.md files.**

## Collateral

- [ ] Trim `MEMORY.md` at `~/.claude/projects/<slug>/memory/MEMORY.md` — remove completed migration blocks (list them)
- [ ] Dedupe root `AGENTS.md` against new root `CLAUDE.md` (remove duplicated Critical Rules table, Skills listing)
- [ ] Merge duplicate task files (e.g., `ACTION_ITEMS.md` + `todo.md` → keep only `todo.md`); update `tasks/AGENTS.md` references
- [ ] Fix broken doc references: [list paths that point at deleted files]
- [ ] Add lesson entries to `tasks/lessons.md` (or project equivalent):
   - "CLAUDE.md is facts-only"
   - "Every AGENTS.md has a sibling CLAUDE.md that is just `@AGENTS.md`"

## Execution order

Phase A (low risk — new files only, nothing removed):
1. Create new skills under `.claude/skills/` (or `~/.claude/skills/` if cross-repo)
2. Write each `AGENTS.md` — root + every subdirectory. For existing CLAUDE.md content being moved, copy **verbatim** (change only the H1 header) unless a specific section needs a stale-command fix.
3. Create/overwrite every sibling `CLAUDE.md` as the one-liner `@AGENTS.md` (root + every subdirectory that has an AGENTS.md)

Phase B (targeted fixes):
4. Reconcile stale commands flagged in Phase 1 (e.g., `tctl` → `temporal operator namespace`) across AGENTS.md and README.md
5. Fix broken references (missing linked files, deleted instruction docs)
6. Trim `MEMORY.md` (if applicable) — remove completed migration blocks
7. Merge duplicate task files

Phase C (verify):
8. Line count: root AGENTS.md ≤ 200; root CLAUDE.md is 1 line (`@AGENTS.md`)
9. Verify every AGENTS.md has a sibling CLAUDE.md
10. Grep root AGENTS.md / CLAUDE.md for any `@` path containing `/` — there should be none (no downward imports)
11. Run lint + type-check + build if the repo has a root build; skip if not (docker-compose monorepos, pure-docs)
12. Grep for broken references
13. Grep for deprecated commands flagged in Phase 1 — any remaining occurrences should be deliberate deprecation notices
14. Smoke test in fresh session (optional, ask user)

## Expected outcome

- Root CLAUDE.md: [N] → **~150 lines**
- New skills: [count] added
- AGENTS.md added: [count]
- Sibling CLAUDE.md added: [count]
- Broken references fixed: [count]
- Expected token savings per turn: **~[estimate] tokens**
- Build/lint/type-check: **no regressions expected** (markdown-only changes)

## Verification checklist (will apply after execution)

See `references/verification.md` in the skill directory. Summary:

- [ ] Root CLAUDE.md ≤ 200 lines
- [ ] `npm run type-check` / stack equivalent passes
- [ ] `npm run lint` / stack equivalent passes
- [ ] Every AGENTS.md has sibling CLAUDE.md (outside skill dirs)
- [ ] No broken references remain
- [ ] Smoke test passes (optional)

## Files to modify

**New files:**
- `[list every new file path]`

**Modified files:**
- `[list every existing file being edited]`

**Deleted files:**
- `[list every file being removed — e.g., merged duplicate task files]`

## Rollback plan

All changes are markdown + skill directories. No code changes, no dependency changes. Rollback = revert commits or `git restore` touched files. If mid-execute something breaks, stop at the last completed phase and report state.
