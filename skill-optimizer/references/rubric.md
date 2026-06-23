# Skill Audit Rubric

Source: Anthropic, "Lessons from building Claude Code: how we use skills" (June 2026).
Score each criterion **pass / gap / n-a** with one line of evidence (quote or line ref). n-a is legitimate — not every criterion applies to every skill; forcing it produces busywork.

## A — Don't state the obvious

> "Claude already knows how to code and can read your codebase. A skill that restates what Claude would do by default adds context without adding value."

- **Pass test:** every section either changes Claude's default behavior or explains a constraint Claude couldn't infer.
- **Gap signs:** generic workflow narration ("analyzes the changes, understands context"), restated tool documentation, advice true of all software everywhere.
- **Fix:** delete it, or replace with the *non-obvious why* hiding underneath it.

## B — Gotchas section

> "The highest-signal content in any skill is the Gotchas section."

- **Pass test:** a dedicated section of real failure points, concrete enough to act on. Blog-grade examples: "the `subscriptions` table is append-only — the row you want has the highest version, not the latest `created_at`"; "staging returns 200 even when the Stripe webhook didn't process — check `payment_events` for real state."
- **Gap signs:** no such section; or a section of platitudes ("be careful with edge cases").
- **Fix:** mine corrections the user has given, past misfires, and lessons files. Gotchas accrete — every correction received while using the skill should land here. Naming varies (Gotchas / Edge cases / Anti-patterns / Never) — substance matters, not the heading.

## C — File system + progressive disclosure

> Structure the entire folder as a context-engineering tool. "Tell Claude what files are in your skill, and it will read them at appropriate times."

- **Pass test:** SKILL.md stays lean; situational content lives in `references/`, `scripts/`, `assets/`; every bundled file has an explicit conditional pointer ("if a job is pending, read `stuck-jobs.md`").
- **Gap signs:** body >~400 lines; bundled files nothing points to (orphans); the highest-value section buried at the bottom of a monolith.
- **Fix:** see `restructuring.md`. Note the inverse gap too: splitting skills too small to benefit (also covered there).

## D — Avoid railroading

> "Claude will generally try to stick to your instructions, and because skills are so reusable you'll want to be careful of being too specific."

- **Pass test:** procedures explain *why* each step matters, so the model can adapt when the situation deviates; fixed pipelines offer a scaled-down path for low-stakes runs.
- **Gap signs:** ALWAYS/NEVER walls without rationale; one-size step sequences with no exit ("all 7 roles every time"); instructions that encode one authoring-session's specifics as law.
- **Fix:** keep the discipline, add the reasoning; add explicit "when this is overkill" / lightweight-mode guidance.

## E — Think through the setup

- **Pass test:** if the skill needs user/environment-specific values (channels, paths, team layouts), it discovers them, reads a `config.json`, or **prompts** (AskUserQuestion) when missing. Degrades gracefully when dependencies (network, VPN, services) fail.
- **Gap signs:** hardcoded environment assumptions; silent failure when a fetch 403s; "the user will know."
- **Fix:** add discovery order + a troubleshooting block for known failure modes.

## F — Descriptions for the model, not for humans

> "The description field is not a summary, it's a description of when to trigger this skill."

- **Pass test:** concrete trigger phrases users actually type, contexts/file patterns, near-miss exclusions — and nothing else.
- **Gap signs:** workflow narration inside the description (the body's job); marketing prose; >~400 chars of non-trigger content. Remember the cost model: name+description load **every session**, triggered or not (~chars/4 tokens).
- **Fix:** see `description-patterns.md`. Never trim without keeping every trigger phrase; verify risky rewrites with skill-creator trigger evals.

## G — Help Claude remember

- **Pass test (when applicable):** repeat-invocation skills keep state (append-only log, JSON, SQLite) so run N can diff against run N−1 — e.g., a standup skill reading `standups.log` to report only what changed.
- **n-a:** genuinely stateless one-shot skills.
- **Anti-fix:** don't add skill-level memory when the data has a canonical repo home (tracking INDEX, tasks file) — that's drift, not memory.

## H — Store scripts and generate code

- **Pass test:** deterministic, every-run-identical work (measurements, data fetching, format conversion) is a bundled script; Claude *composes* helpers instead of reconstructing boilerplate. Signal from the blog: if test-run transcripts show every invocation writing the same helper, bundle it.
- **n-a:** pure-guidance skills with no mechanical steps.

## I — On-demand hooks

- **Pass test (when applicable):** constraints too opinionated to be always-on are session-scoped hooks registered at invocation. Blog examples: `/careful` (PreToolUse on Bash blocking `rm -rf`, `DROP TABLE`, force-push, `kubectl delete`), `/freeze` (block Edit/Write outside a directory while debugging). "You only want this when you know you're touching prod."
- **n-a:** most skills. Don't invent hooks to fill the box.

## J — Composing skills

> "Reference other skills by name, and the model will invoke them if they are installed."

- **Pass test:** the skill names its companions at the natural handoff points instead of duplicating them (file → wire-up; review → verify; message → PR).
- **Gap signs:** re-implementing a sibling skill's behavior inline; an obvious before/after companion never mentioned.

## K — Measurable

- **Pass test (fleet-level, not per-skill):** usage is observable — e.g., a PreToolUse hook logging skill invocations — so undertriggering is detected with data, not vibes. See `measuring-usage.md`.

---

## Category weighting

Classify the skill into the blog's nine types; weight criteria accordingly:

| Category | Weighs heaviest |
|---|---|
| Library/API reference | A, B, E (fetch failures), C |
| Product verification | H (assertions, recordings), D — blog: verification skills had "the most measurable impact on output quality" |
| Data fetching & analysis | H (helper composition), E (credentials/IDs) |
| Business process automation | G (run-to-run memory), E (setup) |
| Scaffolding & templates | C (assets/), A |
| Code quality & review | A, B, D, J |
| CI/CD & deployment | E, I (guardrails), B |
| Runbooks | C (symptom → which file), B, structured report output |
| Infrastructure ops | I (destructive-action guardrails: propose → confirm → soak → execute), E |
