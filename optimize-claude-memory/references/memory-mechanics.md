# Claude Code Memory Mechanics

Authoritative behavior of Claude Code's memory system, extracted from https://code.claude.com/docs/en/memory. Understanding these mechanics is the difference between an effective optimization and a pointless churn.

## What Claude Code auto-discovers

- **Upward walk:** From the current working directory, Claude Code walks *up* the filesystem and loads every `CLAUDE.md` and `CLAUDE.local.md` it finds, concatenating them into startup context. Within each directory, `CLAUDE.local.md` is appended after `CLAUDE.md`, so local notes take precedence.
- **Subdirectory discovery:** Claude Code also discovers `CLAUDE.md` files in subdirectories *under* the cwd, but these load **on-demand** (not at startup) — they're included when Claude reads or edits files in that subdirectory.
- **Filename specificity:** Only `CLAUDE.md` and `CLAUDE.local.md` are auto-discovered. `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, etc. are **NOT** auto-loaded by Claude Code. Other agent tools (Codex, Cursor, Aider) read `AGENTS.md` by convention, which is why the sibling-CLAUDE.md pattern matters.
- **No depth limit** documented; the walk is upward (ancestors) and sideways/downward (subdirectories of cwd).

## The `@path/to/file.md` import syntax

- Works anywhere inside a CLAUDE.md file
- Relative paths resolve **relative to the CLAUDE.md file containing the import**, not the working directory
- **Recursive** with a max depth of 5 hops
- **Imports expand at the moment the containing file loads.** This is the critical detail:
  - A `@foo.md` inside your ROOT CLAUDE.md loads `foo.md` at session start (every turn)
  - A `@foo.md` inside a *nested* CLAUDE.md loads `foo.md` only when that nested CLAUDE.md is auto-loaded (i.e., only when Claude reads files in that subdirectory)
- First import in a project shows an approval dialog; if declined, imports stay disabled and the dialog doesn't reappear

## The sibling-CLAUDE.md pattern (why it works)

Given that only `CLAUDE.md` is auto-discovered but the multi-agent convention uses `AGENTS.md`, the pairing pattern is:

```
src/api/AGENTS.md          ← canonical content (edited here, read by all agents)
src/api/CLAUDE.md          ← one line: `@AGENTS.md`
```

Behavior:
- **Session startup:** neither file is loaded (they're not in the cwd's ancestor chain — assuming cwd is the repo root)
- **Claude reads `src/api/client.ts`:** Claude Code auto-loads `src/api/CLAUDE.md` (on-demand subdirectory behavior); the `@AGENTS.md` import expands AGENTS.md into context at that moment
- **Codex / Cursor:** reads `AGENTS.md` directly (doesn't know about CLAUDE.md)
- **Edits only happen in AGENTS.md** — sibling CLAUDE.md is a symlink-in-markdown, zero maintenance

## Why NOT `@import` nested AGENTS.md from root CLAUDE.md

This is the single most important anti-pattern to avoid:

```markdown
# DO NOT DO THIS in root CLAUDE.md

@src/api/AGENTS.md
@src/components/AGENTS.md
@src/pages/AGENTS.md
# ... etc
```

Root `CLAUDE.md` is auto-loaded at every session start (it's in the cwd's ancestor chain). `@import` expands at load time. So each imported AGENTS.md now loads at *startup*, on *every* turn — which is exactly what we were trying to avoid. You've just recreated the 478-line mega-file problem with more steps.

The nested CLAUDE.md pattern works precisely *because* the nested files are not in any startup-loaded ancestor chain. Keep them nested.

## Recommended CLAUDE.md size

- **Target: under 200 lines** per CLAUDE.md file
- **Ideal: 120–150 lines** for the root file
- **Why:** Longer files consume more context AND reduce how reliably Claude follows them. Monolithic rule files become noise.

## What belongs where

| Content type | Location | Why |
|---|---|---|
| Always-true facts (build commands, aliases, "never do X" rules) | Root `CLAUDE.md` | Needed every session |
| Multi-step procedures (workflows, API reference lookups, checklists) | Skill in `.claude/skills/` | Load only when triggered |
| Area-specific rules ("when editing queries, do X") | Nested `AGENTS.md` + sibling `CLAUDE.md` | Load only when working in that area |
| Per-machine overrides (absolute paths, personal prefs) | `CLAUDE.local.md` | Typically gitignored |
| Completed migration history | `lessons.md`, git log, docs/migrations/ | Don't include in MEMORY.md |

## Skill activation mechanics

- Skills appear in the startup catalog with their `name` + `description` — the combined text is capped at **1,536 characters per skill**, with the total catalog capped around **8,000 characters** dynamically
- Full skill body (`SKILL.md` contents + referenced files) loads **only when the skill is invoked** — either by user (`/skill-name`) or by Claude auto-triggering on description match
- Unused skills cost only their description line in startup (~450 tokens total for a typical catalog)
- `disable-model-invocation: true` hides the skill from the catalog entirely — the description costs zero tokens; only reachable via `/skill-name`
  - Use this for user-only triggered skills where you're confident the user will invoke manually
  - DON'T use for skills you want Claude to trigger automatically on intent

## MEMORY.md (user auto-memory)

For users running with file-based memory at `~/.claude/projects/<project-slug>/memory/MEMORY.md`:

- The **first 200 lines or 25KB** load automatically into every turn
- Content after 200 lines is truncated from startup context
- The file is an **index** of pointers to detailed memory files
- Keep it focused on *current* state — move completed migrations, resolved incidents, and historical context to separate files (or delete)

## Settings and config

- **`outputStyle` setting** adds tokens at startup. For large projects, consider `Concise` over `Explanatory`.
- **`ENABLE_TOOL_SEARCH`** — default `auto` defers MCP tool schemas until needed. `false` loads all schemas upfront (heavier startup). Leave on `auto` unless the overhead of searching is measurably hurting UX.
