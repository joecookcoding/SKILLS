# Post-Optimization Verification Checklist

After executing the approved plan, run through this list before reporting success. Every failure is fixable; shipping a half-migrated repo is not.

## 1. Line-count sanity

| File | Target | How to check |
|---|---|---|
| Root `CLAUDE.md` | ≤ 200 lines (aim 120–150) | `wc -l CLAUDE.md` or `(Get-Content CLAUDE.md \| Measure-Object -Line).Lines` |
| Root `AGENTS.md` (if deduped) | Depends on codebase size | — |
| `MEMORY.md` (if trimmed) | ≤ 200 lines (loaded chunk) | — |
| Each new skill `SKILL.md` | ≤ 500 lines (per skill-creator guidance) | — |

If root CLAUDE.md is over 200 lines, find what else can move out — usually a "reference" section or an over-detailed rule.

## 2. Sibling-CLAUDE.md coverage

Every `AGENTS.md` in the tree (outside exclusions) must have a sibling `CLAUDE.md`. Check with:

**Bash / macOS / Linux:**
```bash
find . -name "AGENTS.md" \
  -not -path "*/node_modules/*" \
  -not -path "*/.claude/skills/*" \
  -not -path "*/vendor/*" \
  | while read f; do
    dir=$(dirname "$f")
    if [ ! -f "$dir/CLAUDE.md" ]; then
      echo "MISSING: $f has no sibling CLAUDE.md"
    fi
  done
```

**PowerShell:**
```powershell
Get-ChildItem -Recurse -Filter AGENTS.md `
  | Where-Object { $_.FullName -notmatch 'node_modules|\.claude[\\/]skills|vendor' } `
  | ForEach-Object {
      $dir = $_.Directory.FullName
      if (-not (Test-Path "$dir\CLAUDE.md")) {
        Write-Host "MISSING: $($_.FullName) has no sibling CLAUDE.md"
      }
    }
```

**Expected exclusions:**
- `.claude/skills/*/AGENTS.md` — inside a skill, don't add sibling (skill has its own discovery)
- `node_modules/**` — dependencies
- `vendor/**`, `.venv/**`, `target/**`, etc. — build/dep dirs

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

Also verify EVERY file path referenced in the root CLAUDE.md actually exists:

```
# Extract paths, then verify
Grep pattern="\\b[\\w/\\.-]+\\.md\\b" path="CLAUDE.md" output_mode="content"
Grep pattern="\\bsrc/[\\w/-]+\\b" path="CLAUDE.md" output_mode="content"
```

Common breakage sources seen in the wild:
- Files deleted from `.claude/instructions/` (frequently referenced from hookify configs, CLAUDE.md pointers)
- Task files that got merged/deleted (e.g., `ACTION_ITEMS.md` → `todo.md`)
- Renamed skills
- **Root `AGENTS.md` referenced but never existed** — CLAUDE.md points at it, nothing there
- **`tasks/lessons.md` referenced but never existed** — common if the repo was set up from a template that included the rule but not the file
- Renamed directories (`src/api/queries/` → `src/queries/`, etc.)

Fix each reference to point at the new location, create the missing file, or at the appropriate skill slash-command (`/skill-name`).

## 5. Smoke test in a fresh session (recommended)

Ask the user to open a new Claude Code session and probe a few representative scenarios:

1. **Task needing a new skill:** E.g., for a React + TS project, ask "how do I build a form with validation?" — the `forms-validation` skill (or equivalent) should trigger.
2. **Task needing nested AGENTS.md:** Ask "let me edit a query hook in `src/api/queries/`" — Claude should read from there; the nested AGENTS.md should appear in context.
3. **Broad question about the project:** Ask "what's the build command?" — answer should come from root CLAUDE.md instantly.

If a skill doesn't trigger for case 1, tighten its description (see `skill-writing.md`). If nested rules don't surface for case 2, verify the sibling CLAUDE.md was created and contains `@AGENTS.md`.

## 6. MEMORY.md trim verification (if trimmed)

Confirm:
- Completed migration blocks are gone
- Current state references still point at real files
- The lessons index still links to every referenced memory file
- Line count ≤ 200 (the auto-loaded chunk)

## 7. Stale reference in hookify / CI configs

Repos that use hookify or similar often reference `.claude/instructions/*.md` files inside hook configs. Grep `.claude/hookify*.md` for references that might now be dead.

## 8. Dedupe check between root CLAUDE.md and root AGENTS.md

They should serve different purposes now:
- `CLAUDE.md` = facts + directory conventions + skill pointers
- `AGENTS.md` = navigation index + source code map + task-based lookup

Open both side by side. Any bullet that appears in both is duplication. Pick one home and remove from the other.

## 9. Lessons file updated (if project has one)

If the project has a `lessons.md` or equivalent self-improvement log, add entries for:
- "CLAUDE.md is facts-only — procedures go in skills, area rules go in nested AGENTS.md"
- "Every AGENTS.md has a sibling CLAUDE.md that is just `@AGENTS.md`"

These entries prevent future maintainers from accidentally rebuilding the 478-line CLAUDE.md.

## 10. Final token math (estimate for the report)

Rough estimate: **line × ~5 tokens** = per-turn cost of that file if it's auto-loaded at startup.

Example:
- CLAUDE.md: 478 lines → ~2,400 tokens startup. Trimmed to 142 → ~710 tokens. **Savings: ~1,700 tokens/turn.**
- MEMORY.md: 120 → 76 lines. **Savings: ~220 tokens/turn.**
- Total: **~1,900–2,500 tokens/turn** typical, depending on how much was padding vs dense rules.

Report this honestly. If the math is smaller than 1,500 tokens, the repo didn't have much to trim — still worth fixing structure, but don't oversell the win.

---

## If any check fails

- **Don't hide it.** Tell the user exactly what failed, what you tried, what's left.
- **Don't revert silently.** If something's broken and you can't fix it in the current session, leave a note in the report and keep the branch.
- **Do ask for help** on regressions that surprise you. Pre-existing flakes are one thing; a new break is a signal.
