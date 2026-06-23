# Writing Skill Descriptions for the Model

The description is the **only** thing Claude sees when deciding whether to invoke a skill. It is also **always-on context** — loaded into every session whether the skill triggers or not (~chars ÷ 4 tokens, every session, forever). Both facts must shape every word.

## The tension to manage

- **Undertriggering** is the dominant failure mode — Claude tends to skip skills it should use. Trigger-dense, even "pushy" descriptions fight this. Long is not automatically wrong.
- **Always-on cost** means each non-trigger word is a tax paid in every session.

Resolution: a description earns each clause by improving triggering. Trigger phrases, contexts, and exclusions earn their keep. **Workflow narration never does** — what the skill *does internally* belongs in the body, which loads only on invocation.

## Anatomy of a good description

1. **What it does** — one clause, so the model knows what problem it solves.
2. **Trigger phrases** — verbatim things users actually type, including casual/abbreviated forms ("BR for X", "babysit this PR"). The blog's example: including the word "babysit" in a PR-monitoring skill's description.
3. **Trigger contexts** — situations and file patterns ("when editing files importing `zod`", "any paste of a backend team's delivery email").
4. **Near-miss exclusions** — "Skip for: …" and disambiguation from sibling skills ("for repo memory use optimize-claude-memory instead"). These prevent both wrong-skill triggers and overtriggering.

That's it. No step lists, no implementation details, no guarantees ("never runs git commit") unless the guarantee itself drives the trigger decision.

## Worked example

**Before** (a migration-runner skill, ~1,000 chars): trigger section is excellent, but then narrates the entire playbook — "Drives a fixed playbook — read the pending migration files, detect and run the repo's migration tool, verify the schema changes landed, regenerate types… Never runs git commit / push / stash… Tool-agnostic by design: the migrate / generate commands are detected from package.json…" None of that narration changes whether the skill triggers.

**After** (~420 chars): keep every trigger — "/migrate", "run the pending migrations", "apply the new schema", "the migration is ready", migration-file pastes, multiple migration paths — plus one what-it-does clause and one exclusion. Move the playbook narration into the SKILL.md body verbatim (it's good content — it's just in the wrong layer).

## Rules for trimming an existing description

1. List every trigger phrase/context in the current description first. **All of them survive.**
2. Delete workflow narration, rationale essays, and feature lists.
3. Keep disambiguators ("not X — use /other-skill for that") — they're triggering logic.
4. Anything deleted that's still true and useful moves to the body — don't destroy content, relocate it.
5. **Verify**: for high-traffic or rewritten-heavily descriptions, run skill-creator's description-optimization loop (`scripts/run_loop.py`: 20 realistic queries, 60/40 train/test split, 3 runs per query). A trim that loses a trigger costs more than the tokens it saves. For mechanical narration-only cuts where every trigger survives verbatim, evals are optional.

## Eval-query design (for the verification step)

Should-trigger (8–10): different phrasings of the same intent, casual + formal, cases that don't name the skill, cases where a sibling skill competes but this one should win.
Should-NOT-trigger (8–10): genuine near-misses sharing keywords with the skill — not obviously-irrelevant filler. Realistic detail (file paths, names, typos) beats abstract prompts.
