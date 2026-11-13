---
name: skill-optimizer
description: Audit and upgrade existing Claude Code skills against Anthropic's skill-authoring guidance. Use for "optimize my skills", "enhance this skill", "audit my skills", "skill health check", "improve this skill", "why didn't skill X trigger", "skill descriptions are cut short", "trim skill descriptions", "review my SKILL.md", or right after authoring a new skill. Not for creating skills (skill-creator) or repo AGENTS.md memory (optimize-claude-memory).
---

# Skill Optimizer

Audit existing skills against Anthropic's published skill-authoring lessons and upgrade them without breaking what already works. The companion to `skill-creator` (which builds and evals *new* skills) — this tool measures, scores, and restructures *existing* ones.

## Why this exists

Four facts make skill quality a budget problem, not just a style problem:

1. **Every skill's name + description is loaded into context every session.** A 1,000-char description costs ~250 tokens per session whether the skill triggers or not.
2. **The listing has a hard budget: 1% of the context window.** Over it, Claude Code drops *whole descriptions*, least-invoked skills first. A skill that lost its description can no longer trigger on intent, so a bloated fleet silences its own rarely-used skills.
3. **Skills are folders, not markdown files.** The folder structure itself is a context-engineering tool — content Claude needs only in specific situations belongs in `references/` behind an explicit pointer, not inline. A loaded SKILL.md stays in context for the rest of the session, and after compaction only its first ~5,000 tokens survive.
4. **Skills are invoked across wildly varied situations.** Overly rigid instructions that work for the authoring session break on the hundredth invocation. The fix is explaining *why*, not adding more MUSTs.

## Workflow

Run these steps in order. Steps 1–3 are read-only; step 4 is the first that edits skills.

1. **Inventory** — read the latest `optimization-log.md` entry, then run `scripts/audit-skills.ps1` (pass `-Root` for a repo's `.claude/skills` or a source repo of skills). It emits per-skill measurements, threshold flags, and file-level findings: orphan candidates, dangling pointers, paths that point outside the skill, and frontmatter only Claude Code accepts. When the skills are authored in one place and installed in another, add `-CompareRoot <other root>` for the drift report. Never eyeball-count what the script measures — deterministic measurement is what scripts are for.
2. **Score** — read each flagged skill and score it A–K against `references/rubric.md`. Read SKILL.md fully; confirm the script's orphan candidates during the read (files referenced only via a glob pattern show up as false orphans). If a skill cites platform behaviour (how something loads, a model alias, a tool name, another skill), check it against `references/platform-facts.md` and the live docs before scoring the rest. For 3+ skills, fan out parallel read-only subagents with the rubric embedded in the prompt when the session allows subagents; otherwise read them in turn in the main session.
3. **Report** — write the scorecard using `assets/audit-report.template.md`. Order proposed changes by impact: description trims first (always-on cost), structural splits second, content enhancements third. Get user approval before touching anything. If the user already asked for the skills to be *changed*, not only audited, give the report and carry on, but still stop for two things: deleting a skill or a bundled file, and a description change that drops or rewords a trigger phrase.
4. **Apply** — make the approved changes. Two hard rules:
   - Moving content into `references/` means *moving*, not rewriting — silent rewrites lose hard-won wording.
   - Every moved block gets an explicit pointer in SKILL.md: "Read <references file> when <condition>."
5. **Verify** — re-run the inventory script and confirm the deltas, with no new `DANGLING`, `ORPHANS` or `YAML-RISK` flag. For any **description** change that removes or rewords text, prove triggering didn't regress: build a ~20-query trigger eval set (should-trigger + tricky near-misses) and run `skill-creator`'s description-optimization loop against it. A description trim that saves 100 tokens but loses a trigger costs more than it saves. For a change to what a skill *does*, compare a fresh session with the skill on against one with it set to `"off"` in `skillOverrides`: the authoring session's leftover context hides gaps in the written instructions.
6. **Sync** — only when step 1 used `-CompareRoot`. Copy each changed skill from the authoring root over its installed copy, then re-run with `-CompareRoot` and expect no drift. Before copying, read the diff of any file the report marks as modified later on the installed side: someone fixed something there, and the fix belongs in the source first.
7. **Log** — append an entry to `optimization-log.md` (this skill's memory): date, measurements, actions taken, and what was deliberately not done. The next audit diffs against this entry instead of starting cold, and the log reveals which past changes actually stuck.

## Which reference to read when

| Situation | Read |
|---|---|
| Scoring a skill, deciding pass/gap | `references/rubric.md` |
| A skill cites platform behaviour, or a flag needs explaining (listing budget, 1,536-char cap, compaction, portable frontmatter, `/doctor`, `skillOverrides`) | `references/platform-facts.md` |
| Rewriting a description (trim or trigger fix) | `references/description-patterns.md` |
| A SKILL.md body is >400 lines or >5,000 tokens, or deciding whether to split at all | `references/restructuring.md` |
| User wants usage data / suspects undertriggering | `references/measuring-usage.md` |

## When NOT to use this skill

- **Creating a new skill from scratch** → use `skill-creator` (it owns the draft→eval→iterate loop). Come back here afterward for a rubric pass.
- **Repo memory files** (AGENTS.md, MEMORY.md, a leftover CLAUDE.md) → use `optimize-claude-memory`. Same philosophy, different artifact.
- **A skill that just shipped and works** — don't churn a skill that triggers correctly and stays under thresholds. The rubric finds problems; it isn't a quota.
- **A quick check for stale or conflicting instructions** → the built-in `/doctor prompt-audit <path>` reports those with proposed edits. It does not measure cost, structure or triggering; this skill does.

## Gotchas

- **Long ≠ wrong for descriptions.** Trigger-dense descriptions fight undertriggering, which is the more common failure. Cut *workflow narration* from descriptions, never trigger phrases — and verify with evals when in doubt.
- **Splitting small skills backfires.** Each `references/` file costs a Read round-trip at invocation time. For a 120-line skill (especially a cheap model-pinned utility), the split costs more than the always-loaded lines it saves. Threshold guidance lives in `references/restructuring.md`.
- **A 1-line bundled file isn't automatically a bug.** Check intent before flagging (e.g., a template whose entire correct content is a single import line).
- **A skill can outlive the platform fact it encodes.** When Claude Code changes how it loads something, skills built on the old behavior keep prescribing it. Two real cases: Claude Code v2.1.277 began reading `AGENTS.md` itself, so `optimize-claude-memory`'s "sibling `CLAUDE.md` containing `@AGENTS.md`" pattern became the thing to remove; and a `commit` skill pinned `model: claude-sonnet-4-6` to dodge a 1M-context alias, then stayed on that model after `sonnet` moved two versions on.
- **A handoff to a skill that isn't installed is a dead end.** "Then `superpowers:systematic-debugging` takes over" tells the model to invoke something that may not exist. Check every skill a SKILL.md names against the session's skill list. Keep the handoff if the companion ships in the same repo; otherwise say what to do in plain words and name the skill as optional.
- **A source repo and its installed copy drift in both directions.** Fixes get made in `~/.claude/skills` during real use and never reach the repo, while the repo gains work the install lacks. Auditing one side alone re-proposes problems the other side already solved. Run `-CompareRoot`, and don't trust "modified later" on its own: a git checkout resets timestamps.
- **`description` with `: ` in it must be quoted.** `description: Use for X. Skip for: Y` is invalid YAML. Claude Code's parser reads it anyway, so nothing looks wrong, but PyYAML rejects the whole frontmatter (`package_skill.py`, a claude.ai upload, other agents). The script flags it as `YAML-RISK`; wrap the value in double quotes and escape inner quotes.
- **Hardcoded "use a subagent" steps fail where subagents are off.** Some users and some sessions deny the Agent tool. Write "if subagents are available, …; otherwise do it inline" so the skill degrades instead of stalling.
- **Skill-level memory can duplicate repo-level tracking.** If the data has a canonical home in a repo (an INDEX.md, a tasks file), adding a parallel log in the skill creates drift, not memory. Memory belongs in the skill only when no better home exists.
- **Duplicate skill names across scopes** (user `~/.claude/skills` vs repo `.claude/skills`) double the always-on cost, and the personal copy wins over the project one. The inventory script sees one root per run — when auditing inside a repo, run it against both roots and compare names.
- **`claude plugin validate` wants a `.claude/skills` directory.** Pointed at a bare folder of skills (a source repo's root) it fails with "No manifest found" and validates nothing. It also passes the unquoted `: ` case above, so it does not replace the script's check.

## Memory

`optimization-log.md` in this skill's folder is an append-only record of every audit and optimization run. Read it at the start of every audit; append at the end of every run. When the skill is installed from a source repo, append to the source copy and let step 6 carry it over, or the next sync overwrites the entry.

## Composition

- `skill-creator` — owns trigger-eval tooling (`run_loop`) and the full output-eval harness. This skill defines *what* to verify; skill-creator provides *how*.
- `optimize-claude-memory` — the repo-scope sibling for AGENTS.md trees.
- `update-config` — writes `skillOverrides` and the usage hook into `settings.json` when the report recommends them.
