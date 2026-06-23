---
name: skill-optimizer
description: Audit and upgrade existing Claude Code skills against Anthropic's skill-authoring best practices. Use for "optimize my skills", "audit my skills", "skill health check", "improve this skill", "why didn't skill X trigger", "trim skill descriptions", "review my SKILL.md", or right after authoring a new skill. Not for creating skills (skill-creator) or repo CLAUDE.md/AGENTS.md (optimize-claude-memory).
---

# Skill Optimizer

Audit existing skills against Anthropic's published skill-authoring lessons and upgrade them without breaking what already works. The companion to `skill-creator` (which builds and evals *new* skills) — this tool measures, scores, and restructures *existing* ones.

## Why this exists

Three facts make skill quality a budget problem, not just a style problem:

1. **Every skill's name + description is loaded into context every session.** A 1,000-char description costs ~200 tokens per session whether the skill triggers or not. Ten skills like that is a permanent 2k-token tax.
2. **Skills are folders, not markdown files.** The folder structure itself is a context-engineering tool — content Claude needs only in specific situations belongs in `references/` behind an explicit pointer, not inline.
3. **Skills are invoked across wildly varied situations.** Overly rigid instructions that work for the authoring session break on the hundredth invocation. The fix is explaining *why*, not adding more MUSTs.

## Workflow

Run these six steps in order. Steps 1–3 are read-only; step 4 is the only one that edits skills, and only after the user approves the report.

1. **Inventory** — run `scripts/audit-skills.ps1` (pass `-Root` for a repo's `.claude/skills`). It emits per-skill measurements, threshold flags, and file-level findings: orphan candidates (bundled files SKILL.md never mentions) and dangling pointers (paths that don't exist). Never eyeball-count what the script measures — deterministic measurement is what scripts are for.
2. **Score** — read each flagged skill and score it A–K against `references/rubric.md`. Read SKILL.md fully; confirm the script's orphan candidates during the read (files referenced only via a glob pattern show up as false orphans). For 3+ skills, fan out parallel read-only subagents with the rubric embedded in the prompt.
3. **Report** — write the scorecard using `assets/audit-report.template.md`. Order proposed changes by impact: description trims first (always-on cost), structural splits second, content enhancements third. Get user approval before touching anything.
4. **Apply** — make the approved changes. Two hard rules:
   - Moving content into `references/` means *moving*, not rewriting — silent rewrites lose hard-won wording.
   - Every moved block gets an explicit pointer in SKILL.md: "Read <references file> when <condition>."
5. **Verify** — for any **description** change, prove triggering didn't regress: build a ~20-query trigger eval set (should-trigger + tricky near-misses) and run `skill-creator`'s description-optimization loop against it. For **structure** changes, re-run the inventory script and confirm line/token deltas. A description trim that saves 100 tokens but loses a trigger costs more than it saves.
6. **Log** — append an entry to `optimization-log.md` (this skill's memory): date, measurements, actions taken. The next audit diffs against this entry instead of starting cold, and the log reveals which past changes actually stuck.

## Which reference to read when

| Situation | Read |
|---|---|
| Scoring a skill, deciding pass/gap | `references/rubric.md` |
| Rewriting a description (trim or trigger fix) | `references/description-patterns.md` |
| A SKILL.md body is >400 lines, or deciding whether to split at all | `references/restructuring.md` |
| User wants usage data / suspects undertriggering | `references/measuring-usage.md` |

## When NOT to use this skill

- **Creating a new skill from scratch** → use `skill-creator` (it owns the draft→eval→iterate loop). Come back here afterward for a rubric pass.
- **Repo memory files** (CLAUDE.md, AGENTS.md, MEMORY.md) → use `optimize-claude-memory`. Same philosophy, different artifact.
- **A skill that just shipped and works** — don't churn a skill that triggers correctly and stays under thresholds. The rubric finds problems; it isn't a quota.

## Gotchas

- **Long ≠ wrong for descriptions.** Trigger-dense descriptions fight undertriggering, which is the more common failure. Cut *workflow narration* from descriptions, never trigger phrases — and verify with evals when in doubt.
- **Splitting small skills backfires.** Each `references/` file costs a Read round-trip at invocation time. For a 120-line skill (especially a cheap model-pinned utility), the split costs more than the always-loaded lines it saves. Threshold guidance lives in `references/restructuring.md`.
- **A 1-line bundled file isn't automatically a bug.** Check intent before flagging (e.g., a template whose entire correct content is `@AGENTS.md`).
- **Skill-level memory can duplicate repo-level tracking.** If the data has a canonical home in a repo (an INDEX.md, a tasks file), adding a parallel log in the skill creates drift, not memory. Memory belongs in the skill only when no better home exists.
- **Duplicate skill names across scopes** (user `~/.claude/skills` vs repo `.claude/skills`) double the always-on cost and make triggering ambiguous. The inventory script only sees one root per run — when auditing inside a repo, run it against both roots and compare names.

## Memory

`optimization-log.md` in this skill's folder is an append-only record of every audit and optimization run. Read it at the start of every audit; append at the end of every run.

## Composition

- `skill-creator` — owns trigger-eval tooling (`run_loop`) and the full output-eval harness. This skill defines *what* to verify; skill-creator provides *how*.
- `optimize-claude-memory` — the repo-scope sibling for CLAUDE.md/AGENTS.md trees.
