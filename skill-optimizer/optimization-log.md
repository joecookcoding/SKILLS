# Optimization Log (append-only)

Memory for the skill-optimizer skill. Each audit/optimization run appends an entry at the
bottom. At the start of every audit, read the latest entry and diff current measurements
against it instead of starting cold.

Entry format (one `## <date> — <summary>` heading per run): baseline measurements, the
decisions made, the actions taken, and anything deliberately *not* done so the next run
doesn't re-propose it.

---

## 2026-11-01 — optimize-claude-memory: sibling CLAUDE.md pattern retired

Targeted update, not a full audit (no A–K scorecard was run).

- **Trigger:** Claude Code v2.1.277+ reads `AGENTS.md` natively (docs: code.claude.com/docs/en/memory#agents-md, checked on v2.1.316). With the default Project instructions value, any `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it switches Claude to CLAUDE.md-only.
- **optimize-claude-memory:** target pattern is now AGENTS.md-only with no `CLAUDE.md` in the repo or its parents; the sibling `@AGENTS.md` pattern is kept only as a fallback for sessions that can't read `AGENTS.md`. Rewrote `SKILL.md` (triage has three starting points: on the pattern / legacy sibling / migration; Phase 1 step 5 checks the version and setting), `references/memory-mechanics.md`, and the sibling sections of `verification.md`, `content-categorization.md`, both templates and `evals.json`. Deleted `assets/nested-claude-md.template.md`.
- **audit-memory-tree.ps1:** section (b) now lists CLAUDE.md-family files in the repo and parent directories (one-liner vs content) instead of sibling coverage, and flags the mixed state; new (c) prints the Claude Code version and the setting. Fixed two pre-existing defects found while testing on tvmenus: the downward-`@import` check matched npm scopes in code spans (`@repo/ui`), and `Get-Content` without `-Encoding UTF8` garbled UTF-8 in PS 5.1. Walk switched to .NET enumeration with pruning: 253 s → 29 s on tvmenus (~8,400 directories).
- **Measurements:** description 1,220 → 1,292 chars; SKILL.md 283 → 295 lines.
- **Not done:** the description-trigger eval loop (`run_loop`) was not run; trigger phrases were only added ("remove the CLAUDE.md files", "Claude reads AGENTS.md now", "AGENTS.md not loading", "nested CLAUDE.md"), none removed. The eval fixtures live on another machine (`C:\Users\jcook\…`), so `evals.json` assertions were updated but not executed.
- **skill-optimizer:** gotcha example no longer cites the deleted template; added a gotcha about skills outliving the platform facts they encode.
