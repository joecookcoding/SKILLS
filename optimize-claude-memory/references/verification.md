# Post-Optimization Verification Checklist

After executing the approved plan, run through this list before reporting success. Every failure is fixable; shipping a half-migrated repo is not.

## 1. Line-count sanity

| File | Target | How to check |
|---|---|---|
| Root `AGENTS.md` | ≤ 200 lines (aim 120–150) | bash `wc -l AGENTS.md`; PowerShell `(Get-Content AGENTS.md).Count` |
| Root `CLAUDE.md` | Absent | — |
| `MEMORY.md` (if trimmed) | ≤ 200 lines (loaded chunk) | — |
| Each new skill `SKILL.md` | ≤ 500 lines (per skill-creator guidance) | — |

If the root AGENTS.md is over 200 lines, find what else can move out — usually a "reference" section or an over-detailed rule.

> **PowerShell gotcha:** `Measure-Object -Line` counts only **non-blank** lines, so on a file with many blank separators it reports a number well below the real total — a 197-line file can report 151, which looks alarmingly like you over-cut by 46 lines when you didn't. Use `(Get-Content file).Count` for the true total (the number that matters for the per-turn budget). Bash `wc -l` counts every line and is fine.

> **Line count ≠ token count — they are different levers.** Removing whole lines (a redundant section, a duplicated fenced command, a multi-line prose block) lowers the *line* count. Tightening prose *inside* a line lowers *tokens* but not lines — and a markdown **table row is one line no matter how long its text is**, so you cannot shrink a table's line count by trimming row prose; you shrink it by removing rows or moving the whole table out. When the goal is "get under the line ceiling," target whole-line removals (especially Bucket-5 redundancy); when the goal is raw token reduction, prose density also counts.

## 2. No CLAUDE.md left

No `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` may remain in the repo (outside exclusions) or in any parent directory. Any one of them switches Claude to CLAUDE.md-only and stops it reading the `AGENTS.md` files below it. `~/.claude/CLAUDE.md` is fine. The audit script checks both the tree and the parents; by hand:

**Bash / macOS / Linux:**
```bash
find . \( -name node_modules -o -name vendor -o -name .venv -o -name target -o -name .git \) -prune \
  -o \( -name CLAUDE.md -o -name CLAUDE.local.md \) -not -path "*/.claude/skills/*" -print
d=$(cd .. && pwd); while [ "$d" != "/" ]; do
  for f in CLAUDE.md CLAUDE.local.md .claude/CLAUDE.md; do
    [ -e "$d/$f" ] && [ "$d/$f" != "$HOME/.claude/CLAUDE.md" ] && echo "PARENT: $d/$f"
  done; d=$(dirname "$d"); done
```

**PowerShell:**
```powershell
Get-ChildItem -Recurse -Include CLAUDE.md, CLAUDE.local.md -File `
  | Where-Object { $_.FullName -notmatch 'node_modules|\.claude[\\/]skills|vendor|\.venv|[\\/]target[\\/]' } `
  | ForEach-Object { Write-Host "FOUND: $($_.FullName)" }
```

Both should print nothing. `scripts/audit-memory-tree.ps1` runs the same check and also looks in the parent directories.

**Expected exclusions:**
- `.claude/skills/**` — inside a skill (skill has its own discovery)
- `node_modules/**` — dependencies
- `vendor/**`, `.venv/**`, `target/**`, etc. — build/dep dirs

Then confirm Claude Code can read `AGENTS.md` here: `claude --version` is v2.1.277 or later, and **Project instructions** is not `claude-md`.

## 3. Build / lint / type-check (diff against Phase 1 baseline)

Run whatever the project provides and **diff** against the baseline you captured in Phase 1 step 1. The diff is what matters — not the raw output.

| Stack | Commands |
|---|---|
| Node (TypeScript) | `npm run type-check`, `npm run lint`, `npm run build` |
| Node (JavaScript) | `npm run lint`, `npm run build` |
| Python | `ruff check`, `mypy .`, `pytest` |
| Go | `go vet ./...`, `go build ./...`, `go test ./...` |
| Rust | `cargo check`, `cargo clippy`, `cargo test` |
| Deno | `deno check`, `deno lint`, `deno test` |

### Three outcomes

1. **Pre-existing errors still present, no new ones** — not your fault, not your fix. Report these transparently in the final report under a clear "Pre-existing (not caused by this run)" heading. Don't silently gloss over them; don't claim them as regressions either.
2. **All errors gone** — rare with markdown-only changes; means the repo was clean before and is clean now.
3. **New errors present** — you broke something. **Investigate before reporting done.** Since markdown changes can't cause build/lint/type-check failures, this almost always means a stale reference you introduced (e.g., moved a file, didn't update a test fixture that imports it). Check your changes against the diff, fix the reference, re-run.

**Key principle: trust the baseline, not narrative.** If the baseline showed 3 TypeScript errors and the post-run output shows the same 3 TypeScript errors, that's a pass. Without the baseline, you're guessing.

## 4. Broken reference sweep

Grep for paths that may have been invalidated:

```
Grep pattern="\\.claude/instructions/" output_mode="content"
Grep pattern="tasks/ACTION_ITEMS" output_mode="files_with_matches"   # or whatever file you deleted
```

Also verify EVERY file path referenced in the root AGENTS.md actually exists:

```
# Extract paths, then verify
Grep pattern="\\b[\\w/\\.-]+\\.md\\b" path="AGENTS.md" output_mode="content"
Grep pattern="\\bsrc/[\\w/-]+\\b" path="AGENTS.md" output_mode="content"
```

And grep the tree for prose that still points at a deleted `CLAUDE.md` (for example "see `services/x/CLAUDE.md`", or a lessons entry describing sibling files as current).

Common breakage sources seen in the wild:
- Files deleted from `.claude/instructions/` (frequently referenced from hookify configs, CLAUDE.md pointers)
- Task files that got merged/deleted (e.g., `ACTION_ITEMS.md` → `todo.md`)
- Renamed skills
- **Root `AGENTS.md` referenced but never existed** — CLAUDE.md points at it, nothing there
- **`tasks/lessons.md` referenced but never existed** — common if the repo was set up from a template that included the rule but not the file
- Renamed directories (`src/api/queries/` → `src/queries/`, etc.)

Fix each reference to point at the new location, create the missing file, or at the appropriate skill slash-command (`/skill-name`).

## 5. Smoke test in a fresh session (recommended)

Ask the user to open a new Claude Code session in the repo. First, confirm the root file loaded: an interactive session prints `no CLAUDE.md found; AGENTS.md loaded: <path>`, and `/memory` lists the root `AGENTS.md`. (The first session after upgrading from v2.1.276 or earlier may still read `CLAUDE.md` only; check the next one.) Then probe a few representative scenarios:

1. **Task needing a new skill:** E.g., for a React + TS project, ask "how do I build a form with validation?" — the `forms-validation` skill (or equivalent) should trigger.
2. **Task needing nested AGENTS.md:** Ask "let me edit a query hook in `src/api/queries/`" — once Claude opens a file there with the Read tool, the nested AGENTS.md should appear in context (`/memory` lists it).
3. **Broad question about the project:** Ask "what's the build command?" — answer should come from the root AGENTS.md instantly.

If a skill doesn't trigger for case 1, tighten its description (see `skill-writing.md`). If nested rules don't surface for case 2, look for a `CLAUDE.md` or `CLAUDE.local.md` still on the path (root, a parent directory, or that subdirectory), then check the version and the **Project instructions** setting.

## 6. MEMORY.md trim verification (if trimmed)

Confirm:
- Completed migration blocks are gone
- Current state references still point at real files
- The lessons index still links to every referenced memory file
- Line count ≤ 200 (the auto-loaded chunk)

## 7. Stale reference in hookify / CI configs

Repos that use hookify or similar often reference `.claude/instructions/*.md` files inside hook configs. Grep `.claude/hookify*.md` for references that might now be dead.

## 8. Nothing lost in the CLAUDE.md deletions

For every `CLAUDE.md` that held more than `@AGENTS.md`, confirm each of its rules now lives in an `AGENTS.md`, in `.claude/rules/`, in `~/.claude/CLAUDE.md`, or was deliberately dropped (and the plan says so). Diff the deleted file (`git show HEAD:path/CLAUDE.md`) against its destination. Also check the root `AGENTS.md` carries the one-line "no `CLAUDE.md` on purpose" note.

## 9. Lessons file updated (if project has one)

If the project has a `lessons.md` or equivalent self-improvement log, add entries for:
- "AGENTS.md is facts-only — procedures go in skills, area rules go in nested AGENTS.md"
- "There is no CLAUDE.md: Claude Code reads AGENTS.md itself, and a CLAUDE.md or CLAUDE.local.md would switch that off"

These entries prevent future maintainers from accidentally rebuilding the 478-line CLAUDE.md, or re-adding one with `/init`.

## 10. Final token math (estimate for the report)

Rough estimate: **line × ~5 tokens** = per-turn cost of that file if it's auto-loaded at startup.

Example:
- Root instruction file: 478 lines → ~2,400 tokens startup. Trimmed to 142 → ~710 tokens. **Savings: ~1,700 tokens/turn.**
- MEMORY.md: 120 → 76 lines. **Savings: ~220 tokens/turn.**
- Total: **~1,900–2,500 tokens/turn** typical, depending on how much was padding vs dense rules.

Report this honestly. If the math is smaller than 1,500 tokens, the repo didn't have much to trim — still worth fixing structure, but don't oversell the win.

---

## If any check fails

- **Don't hide it.** Tell the user exactly what failed, what you tried, what's left.
- **Don't revert silently.** If something's broken and you can't fix it in the current session, leave a note in the report and keep the branch.
- **Do ask for help** on regressions that surprise you. Pre-existing flakes are one thing; a new break is a signal.
