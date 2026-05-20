---
name: adversarial-review
description: A structured adversarial review workflow that splits review work across narrow agent roles (Orchestrator, Investigator, Devil's Advocate, Impact Tracer, Fix Planner, Triage Lead, Final Decision) to catch what a single pass would miss. Use whenever the user asks for a "thorough review", "adversarial review", "second opinion", "red team", "devil's advocate", "steelman / strongest case against", "pre-merge review", "ship/no-ship call", "production-readiness review", or wants to validate a code change, pull request, architecture decision, database migration, auth/permissions change, refactor plan, AI agent design, vendor selection, hiring decision, roadmap call, or any high-stakes engineering or business decision before they commit. Also triggers on phrases like "is this safe to ship", "what am I missing", "talk me out of this", "poke holes in", "what could go wrong", "challenge my plan", "stress test this decision", "find what I'm not seeing", and on requests to review PRs, route handlers, schema changes, infra changes, monorepo migrations, framework swaps, or agent workflows. Walks through scope-narrowing → evidence-based claims → independent adversarial challenge → impact tracing → smallest-safe-fix planning → triage → final decision, with explicit human-approval gates on high-impact actions. Skip for: simple one-shot answers, throwaway scripts, or tasks where the user already knows the answer and just wants execution.
---

# Adversarial Review

## Purpose

Use multiple agent roles — not one — to review code, architecture, and decisions. One model playing builder, reviewer, skeptic, and decider at the same time misses things. Splitting the work into narrow roles makes the harness, not the model, the safety system.

## Why this matters

A single agent reviewing its own thinking tends to:

- Confirm rather than challenge its first read.
- Treat plausible language as evidence.
- Conflate "I see no problem" with "there is no problem."
- Recommend big actions to look decisive.

Separate roles fix this. The Investigator's job is to find. The Devil's Advocate's job is to disprove. The Impact Tracer asks whether anything actually matters. The Fix Planner picks the smallest safe step. The Triage Lead kills duplicates. The Final Decision Agent commits to one call. Each role has narrow scope and a fixed output, so it's harder for one weak link to fool the whole chain.

## When to use

Use this skill when the user is about to make a decision they can't easily reverse, or when they ask for a *thorough* review (not a quick look). Common triggers:

- Pull requests, route handlers, schema changes, infra changes
- Auth / authz / permissions logic
- Production release plans
- Architecture and stack decisions, monorepo migrations, framework swaps
- AI agent workflows (especially anything with tool access or autonomy)
- Vendor / dependency decisions
- Large refactors
- Hiring / roadmap / process decisions with meaningful risk

**Don't use this skill when:** the user just wants a quick answer, the change is trivial and reversible, or they've already decided and just want help executing.

## Modes

Pick one mode based on what's being reviewed. Each mode keeps the same workflow but tunes the questions.

### Code Review
Pull requests, changed files, APIs, services, components, database migrations, infra changes.
Primary questions: Is it correct? Is it safe? Is it maintainable? What could break? What tests are missing?

### Architecture Review
System design, stack decisions, service boundaries, data flow, scaling plans, monorepo / framework changes.
Primary questions: Is this the right design? What tradeoffs are we accepting? What does this make easier — and harder? What's the smallest reversible step?

### Decision Review
Product, business, vendor, roadmap, staffing, prioritization, or process decisions.
Primary questions: Strongest case for? Strongest case against? What happens if we're wrong? Cost of waiting? Smallest safe next step?

## Workflow

The skill always runs in this order. Skip a step only if the Orchestrator explicitly justifies why it doesn't apply.

1. **Narrow the scope.** One target, one risk category, one decision area. Reject vague "review this repo" framings.
2. **Investigate.** Find concrete claims with evidence. Stay inside scope.
3. **Challenge.** A separate adversarial pass that may not create new findings — only disprove, weaken, validate, or revise existing ones.
4. **Trace impact.** Is the finding reachable / does the decision actually matter? Practical vs. theoretical.
5. **Plan the smallest safe fix.** Prefer minimal changes. Include tests. Include rollback notes. Mark approval gates.
6. **Triage.** Merge duplicates. Reject unsupported claims. Prioritize what's left.
7. **Decide.** One call: Approve · Approve with follow-up · Block until fixed · Needs more evidence · Rework approach · Run a smaller experiment · Escalate to human review.

For the full responsibility list per role, see `references/agent-roles.md`. Individual agent prompts live in `prompts/00-orchestrator.md` through `prompts/06-final-decision.md`. Configuration knobs (modes, agents, safety) are in `config/`.

## Core Principles

### Narrow scope beats broad review

Bad: *"Review this repo and find issues."*
Better: *"Review `src/app/api/users/route.ts` for authorization mistakes around whether one user can access or modify another user's data."*

Every agent should receive: one target, one risk category or decision area, clear boundaries, relevant context, required output format.

### Separate finder from critic

The Investigator finds. The Devil's Advocate challenges. They are not the same agent, and the Devil's Advocate may not invent unrelated findings. This separation is the whole point.

### Split reasoning chains

Don't ask "is this a problem and is it impactful and what's the fix" in one breath. Ask them separately:

- Is there a problem?
- Is there evidence?
- Is it reachable?
- Is it impactful?
- What would disprove it?
- What's the smallest safe fix?
- What needs human approval?

Combined, these produce mush. Separated, they produce sharp answers.

### Track claims, not vibes

Every finding is a claim with: ID, title, evidence, scope, confidence, impact, status, disproof condition, recommended action. Vague claims get rejected.

Bad: *"This may have security issues."*
Good: *"The route checks for an authenticated user but does not verify ownership of the requested record before returning it."*

### Prefer evidence over confidence

High confidence without evidence is useless. Low confidence with a clear test is still useful. Reward specific files, functions, flows, tests, reproduction conditions, and disproof conditions.

### Require human approval for high-impact actions

Agents recommend; humans approve. Don't auto-apply production changes, auth changes, data migrations, deletes, public disclosures, large refactors, or anything touching secrets/credentials/customer data. Full gate list: `references/severity-and-safety.md`.

## Claim Format

Every claim — from Investigator, Devil's Advocate, or Impact Tracer — uses this structure:

```md
## Claim {ID}
Title:
Source Agent:
Scope:
Claim:
Evidence:
Confidence: High | Medium | Low
Impact: Critical | High | Medium | Low | None | Unknown
Status: Accepted | Rejected | Revised | Needs Evidence
What would disprove this:
Recommended next action:
Human approval required: Yes | No
```

Severity rubric and anti-noise rules: `references/severity-and-safety.md`.

## Final Output Format

The Final Decision Agent emits exactly this report (omit empty sections):

```md
# Multi-Agent Review Report

## Review Mode
## Scope
## Executive Summary
## Claim Ledger
## Accepted Findings
## Rejected Findings
## Revised Findings
## Findings Needing More Evidence
## Impact Analysis
## Recommended Actions
## Human Approval Gates
## Tests or Validation Steps
## Risks of the Recommended Action
## Risks of Doing Nothing
## Final Decision
```

A filled template is in `templates/review-report.md`; the claim ledger template is in `templates/claim-ledger.md`; a starter Review Packet is in `templates/review-packet.md`.

## How to invoke

**Single-shot (recommended for chat):** see `references/one-shot-prompt.md`. Paste it, then paste the Review Packet and target.

**Multi-step (rigorous reviews):** run `prompts/00-orchestrator.md` through `prompts/06-final-decision.md` in sequence, threading prior outputs forward.

**Worked examples** (one per mode) are in `examples/`.

## Final Rule

A good review system shouldn't depend on one model being careful. Assume every model can miss things, overstate things, forget things, or become inconsistent. The harness — narrow roles, separate finder from critic, claims with evidence, human approval gates — is the safety system.
