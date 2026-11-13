# Phase 1 Audit Steps

The full read-only audit, in order. Run `scripts/audit-memory-tree.ps1 -Root <repo>` first: it
answers the measuring parts of steps 2, 3, 4, 5 and 11, and prints the triage verdict. In a
touch-up most steps only confirm compliance; do them anyway, briefly.

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
   - Flag it in the plan: its content moves to the parent's `AGENTS.md` (or `~/.claude/CLAUDE.md` if it is personal) and the file goes. It sits outside the repo, so the user deletes it; list it for them
4. **Inventory the memory tree:**
   - `Glob` for all `AGENTS.md` files (exclude `node_modules/**`, `vendor/**`, `.venv/**`, `target/**`)
   - **List every `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md`** in the repo and in each parent directory (the audit script does both). Label each: a one-line `@AGENTS.md` import (delete), or a file with real content (migrate its content, then delete)
   - `Glob` for all `README.md` files that function as agent guidance (skip library READMEs in sub-packages unless they exist in `src/`)
   - `Glob` for existing skills at `.claude/skills/*/SKILL.md`
   - **Also glob user-level skills at `~/.claude/skills/*/SKILL.md`** — many will already cover content that would otherwise seem to need a new skill. Read their descriptions. This is the cross-repo reuse check — skip duplicating what already exists at user level.
5. **Check that Claude can read `AGENTS.md` here.** `claude --version` must be v2.1.277 or later (the script prints it). Check **Project instructions** (`/config`, or `pluginConfigs` → `cc-plugin-agents-md@builtin` → `options.instructionFiles` in `~/.claude/settings.json`) is not `claude-md` or `managed-only`. If either check fails, the plan's first item is the fix (update Claude Code, change the setting, re-enable the built-in plugin), not a `CLAUDE.md`. `references/memory-mechanics.md` lists every case where `AGENTS.md` support is unavailable.
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
