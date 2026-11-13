# Claude Code Memory Mechanics

Authoritative behavior of Claude Code's memory system, extracted from https://code.claude.com/docs/en/memory (checked 2026-11-12, Claude Code v2.1.323). Understanding these mechanics is the difference between an effective optimization and a pointless churn.

## What Claude Code reads: AGENTS.md or CLAUDE.md

Since **v2.1.277**, Claude Code reads `AGENTS.md` as project instructions through a built-in plugin (`cc-plugin-agents-md@builtin`; `agents-md@builtin` before v2.1.285). Which files it reads depends on the **Project instructions** setting (`/config`), default `claude-md-or-agents-md`:

| The repo has | Claude reads (default) |
|---|---|
| An `AGENTS.md`, and no `CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it | The `AGENTS.md` files |
| An `AGENTS.md` and a `CLAUDE.md` or `CLAUDE.local.md` in the working directory or above it | The `CLAUDE.md` files only |
| A `CLAUDE.md` that imports `@AGENTS.md` | The `CLAUDE.md`, with `AGENTS.md` included through the import |

- **What counts** (and so switches `AGENTS.md` off): a `CLAUDE.md`, `.claude/CLAUDE.md` or `CLAUDE.local.md` in the working directory or **any directory above it**.
- **What doesn't count** (keeps loading alongside `AGENTS.md`): `~/.claude/CLAUDE.md`, the organization's managed `CLAUDE.md`, and `.claude/rules/` files.
- **At session start** Claude reads every `AGENTS.md` and `.claude/AGENTS.md` in the working directory and the directories above it. An interactive session prints a line such as `no CLAUDE.md found; AGENTS.md loaded: /home/you/repo/AGENTS.md`, and `/memory` lists the file (v2.1.280+).
- **On demand:** a subdirectory's `AGENTS.md` loads when Claude opens a file in that subdirectory **with the Read tool**, provided that subdirectory has no `CLAUDE.md` of its own. (A subdirectory `CLAUDE.md` also loads on a write, an edit, or a Bash `cat`/`head` of a file there; the docs name only the Read tool for `AGENTS.md`.)
- **Inside each `AGENTS.md`:** `@path` imports expand, `claudeMdExcludes` patterns apply, and subagents that start without project instructions start without these files too.
- **Never read:** `AGENTS.local.md`, `AGENTS.override.md`, anything under `.agents/`.

Setting values:

| Value | Claude reads |
|---|---|
| `claude-md-or-agents-md` (default) | `CLAUDE.md` files, or `AGENTS.md` files when there is no `CLAUDE.md`/`CLAUDE.local.md` on the path |
| `claude-md-and-agents-md` | Both, each directory's `CLAUDE.md` first; an `AGENTS.md` already imported is not read twice |
| `claude-md` | `CLAUDE.md` files only |
| `managed-only` | Only the managed `CLAUDE.md` and auto memory at launch |

In a settings file: `pluginConfigs` → `cc-plugin-agents-md@builtin` → `options.instructionFiles`, read from `~/.claude/settings.json`, a `--settings` file or managed settings, and **ignored in project and local settings**. So a repo cannot set this for its contributors; it can only avoid having a `CLAUDE.md`.

### Where a directly-read AGENTS.md differs from CLAUDE.md

| | `CLAUDE.md` | `AGENTS.md` read directly |
|---|---|---|
| `InstructionsLoaded` hooks | Fire | Don't fire (they do for an `AGENTS.md` a `CLAUDE.md` imports) |
| `--add-dir` with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | The added directory's `CLAUDE.md` loads | Its `AGENTS.md` doesn't |
| `@path` import of a file outside the working directory | Claude asks to approve | Loads only if external imports were already approved, no prompt |

### When AGENTS.md support is unavailable

Claude reads `CLAUDE.md` files only, and Project instructions is missing from `/config`, when:
- Claude Code is older than v2.1.277 (or older than v2.1.281 on Amazon Bedrock or with telemetry disabled);
- the built-in plugin was disabled with `/plugin`;
- in some cases, it is the first session after upgrading from v2.1.276 or earlier (the next one reads `AGENTS.md`).

The fix in each case is on the machine, not in the repo: update Claude Code, re-enable the plugin, or start a second session. Don't add `CLAUDE.md` files to a repo to work around one person's setup; every other session then reads `CLAUDE.md` only.

The docs still describe an import bridge (a `CLAUDE.md` holding `@AGENTS.md`) for a repo that must serve such sessions, that relies on `InstructionsLoaded` hooks, or that is added with `--add-dir` while `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` is set. This skill never proposes it. If the user asks for one by name, it has to exist beside **every** `AGENTS.md`, root included, or the subdirectories without one stop loading.

## The `@path/to/file.md` import syntax

- Works anywhere inside a `CLAUDE.md` or a directly-read `AGENTS.md`
- Relative paths resolve **relative to the file containing the import**, not the working directory
- **Recursive** with a max depth of 5 hops
- **Imports expand at the moment the containing file loads.** This is the critical detail:
  - A `@foo.md` inside your ROOT `AGENTS.md` loads `foo.md` at session start (every turn)
  - A `@foo.md` inside a *nested* `AGENTS.md` loads `foo.md` only when that nested file loads (i.e., only when Claude reads files in that subdirectory)
- First import in a project shows an approval dialog; if declined, imports stay disabled and the dialog doesn't reappear

## Retiring the old sibling-CLAUDE.md pattern

Before v2.1.277 only `CLAUDE.md` was auto-discovered, so the multi-agent convention needed a bridge, and many repos still carry it:

```
src/api/AGENTS.md          ← canonical content (edited here, read by all agents)
src/api/CLAUDE.md          ← one line: `@AGENTS.md`
```

Delete every one of them, root included, in one change. A root `CLAUDE.md` with sibling-less subdirectory `AGENTS.md` files is the broken middle state: the root `CLAUDE.md` puts Claude in CLAUDE.md-only mode, so those subdirectories' rules never load.

What to do with each leftover: a `CLAUDE.md` whose whole content is `@AGENTS.md` is deleted (it has nothing to migrate). A `CLAUDE.md` that only *tells* Claude in words to read `AGENTS.md` should be deleted (Claude sees `AGENTS.md` only if it decides to open it). A `CLAUDE.md` symlinked to `AGENTS.md` is read once either way; delete it so the repo has one layout. A `SessionStart` hook that prints `AGENTS.md` must go, or Claude gets a second copy.

## Why NOT `@import` nested AGENTS.md from the root

This is the single most important anti-pattern to avoid:

```markdown
# DO NOT DO THIS in the root AGENTS.md (or a root CLAUDE.md)

@src/api/AGENTS.md
@src/components/AGENTS.md
@src/pages/AGENTS.md
# ... etc
```

The root `AGENTS.md` is read at every session start. `@import` expands at load time. So each imported AGENTS.md now loads at *startup*, on *every* turn — which is exactly what we were trying to avoid. You've just recreated the 478-line mega-file problem with more steps.

On-demand loading works precisely *because* the nested files are not in any startup-loaded ancestor chain. Keep them nested.

## Recommended root file size

- **Target: under 200 lines** for the root instruction file
- **Ideal: 120–150 lines**
- **Why:** Longer files consume more context AND reduce how reliably Claude follows them. Monolithic rule files become noise.
- On-demand files (subdirectory `CLAUDE.md` and its imports, on-demand rules) are cut at a per-file limit since v2.1.309: 40,000 characters on a 200K context window, 150,000 on a 1M window with current models. Claude gets the start and a note to read the rest. The docs don't say whether the limit covers a directly-read subdirectory `AGENTS.md`; keep those under it anyway.

## What belongs where

| Content type | Location | Why |
|---|---|---|
| Always-true facts (build commands, aliases, "never do X" rules) | Root `AGENTS.md` | Needed every session, by every agent |
| Multi-step procedures (workflows, API reference lookups, checklists) | Skill in `.claude/skills/` | Load only when triggered |
| Area-specific rules ("when editing queries, do X") | Nested `AGENTS.md` | Load only when working in that area |
| Claude-only rules | `.claude/rules/*.md` (optionally `paths:`-scoped) | Load alongside `AGENTS.md` without switching it off |
| Personal preferences | `~/.claude/CLAUDE.md` | Doesn't count against `AGENTS.md`; a `CLAUDE.local.md` would |
| Completed migration history | `lessons.md`, git log, docs/migrations/ | Don't include in MEMORY.md |

## Skill activation mechanics

- Skills appear in the startup listing with their `name` + `description` — `description` + `when_to_use` is cut at **1,536 characters per skill**, and the whole listing gets **1% of the context window** (roughly 8,000 characters on a 200K window). Over that budget Claude Code drops whole descriptions, least-invoked skills first, so a skill moved out of `AGENTS.md` only triggers if its description fits
- Full skill body (`SKILL.md` contents + referenced files) loads **only when the skill is invoked** — either by user (`/skill-name`) or by Claude auto-triggering on description match
- Unused skills cost only their description line in startup. `/doctor` reports the listing's real cost
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
