---
name: adversarial-review
description: A structured adversarial review workflow that splits review work across narrow agent roles (Investigator, Devil's Advocate, Impact Tracer, and more) to catch what a single pass would miss. Use for "thorough review", "adversarial review", "second opinion", "red team", "devil's advocate", "steelman / strongest case against", "pre-merge review", "ship/no-ship call", "production-readiness review", "is this safe to ship", "what am I missing", "talk me out of this", "poke holes in", "challenge my plan", "stress test this decision", "find what I'm not seeing" — or validating any high-stakes engineering or business decision before commitment: PRs, architecture, database migrations, auth/permissions changes, refactor plans, AI agent designs, vendor selection, hiring, roadmap calls. Skip for: simple one-shot answers, throwaway scripts, light cleanup reviews, or when the user already knows the answer and just wants execution.
metadata:
  version: "1.1.0"
  tags: [review, quality, safety, multi-agent]
---

# Adversarial Review

## Mode routing

Pick the mode by what's being reviewed; the workflow is the same — each mode just tunes the questions.

| Mode | When | Primary questions |
|---|---|---|
| **Code Review** | PRs, files, APIs, services, components, migrations, infra | Correct? Safe? Maintainable? What breaks? Tests missing? |
| **Architecture Review** | System design, stack, boundaries, data flow, scaling, monorepo / framework swaps | Right design? Tradeoffs accepted? Easier — and harder? Smallest reversible step? |
| **Decision Review** | Product, business, vendor, roadmap, staffing, prioritization, process | Strongest case for? Strongest case against? Cost if wrong? Cost of waiting? Smallest safe next step? |
| **Lightweight** | Low-stakes, easily-reversible targets: small PRs, internal scripts, throwaway changes | Correct? Anything obviously broken or unsafe? Easy to reverse if wrong? (Orchestrator → Investigator → Final Decision only) |

## Pre-flight

Before running any agent role, confirm all four. If any is missing, **stop and ask** — do not guess.

1. **One target.** A specific file path, PR URL, ADR, design doc, or decision statement. *"Review this repo"* is not a target.
2. **One risk category** *or* **one decision area**. *"Find issues"* is not a risk category. *"Authorization mistakes around cross-user record access"* is.
3. **Loaded context.** The diff, the design doc, the relevant ADRs, or the decision brief is in scope. If you'd have to guess what "the change" is, the input is incomplete.
4. **A mode picked** from the table above.

> **HARD STOP:** If the user says "review the codebase" or "look around and tell me what's wrong," refuse to run the workflow and ask for a narrowed target. Broad sweeps produce vibes, not findings.

## Why this matters

A single agent reviewing its own thinking tends to:

- Confirm rather than challenge its first read.
- Treat plausible language as evidence.
- Conflate "I see no problem" with "there is no problem."
- Recommend big actions to look decisive.

Separate roles fix this. The Investigator's job is to find. The Devil's Advocate's job is to disprove. The Impact Tracer asks whether anything actually matters. The Fix Planner picks the smallest safe step. The Triage Lead kills duplicates. The Final Decision Agent commits to one call. Each role has narrow scope and a fixed output, so it's harder for one weak link to fool the whole chain.

A good review system shouldn't depend on one model being careful. Assume every model can miss things, overstate things, forget things, or become inconsistent. The harness — narrow roles, separate finder from critic, claims with evidence, human approval gates — is the safety system.

## When to use

Use this skill when the user is about to make a decision they can't easily reverse, or when they ask for a *thorough* review (not a quick look). For AI agent workflows, anything with tool access or autonomy meets that bar. (Full trigger and skip lists live in the frontmatter description.)

## Routing & composition

- **no-glaze** is the register; this skill is the pipeline. If the user wants direct blunt feedback rather than a structured multi-role ship/no-ship process, use no-glaze alone.
- A plain correctness sweep on a diff → the **code-review** skill is cheaper.
- Auth/permissions-heavy targets → **security-review**.
- After an APPROVE verdict on code → the **verify** skill to confirm the behavior.

## Workflow

The skill always runs in this order. Skip a step only if the Orchestrator explicitly justifies why it doesn't apply.

The Orchestrator picks **Lightweight** when the stakes are low and reversal is cheap — it runs only Investigator → Final Decision, skipping the adversarial roles. The full 7-role pipeline is for high-stakes or hard-to-reverse decisions. Running it on a trivial change wastes the reviewers and trains people to skip reviews entirely; reserve the heavy machinery for where it earns its cost.

1. **Narrow the scope.** One target, one risk category, one decision area. Reject vague "review this repo" framings.
2. **Investigate.** Find concrete claims with evidence. Stay inside scope.
3. **Challenge.** A separate adversarial pass that may not create new findings — only disprove, weaken, validate, or revise existing ones.
4. **Trace impact.** Is the finding reachable / does the decision actually matter? Practical vs. theoretical.
5. **Plan the smallest safe fix.** Prefer minimal changes. Include tests. Include rollback notes. Mark approval gates.
6. **Triage.** Merge duplicates. Reject unsupported claims. Prioritize what's left.
7. **Decide.** One call: Approve · Approve with follow-up · Block until fixed · Needs more evidence · Rework approach · Run a smaller experiment · Escalate to human review.
8. **Persist the ledger.** At the end of a full run, write the final claim ledger to `.claude/reviews/<target-slug>.md` in the target repo. On re-invocation against the same target, read it first and instruct the Investigator and Triage Lead: claims rejected in the prior run may not be re-raised without new evidence, and previously ACCEPTED findings must be verified fixed. Exception: when the target is a GitHub PR, the PR thread is the canonical home — post the ledger there via `gh` instead of the local file.

For the full responsibility list per role, see `references/agent-roles.md`. The per-role prompt contracts are listed in "How to execute" below.

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

## Anti-patterns

Recurring failure modes. If you catch yourself in the left column, switch to the right.

| Failure mode | What it looks like | Counter |
|---|---|---|
| One agent plays all roles | Investigator and Devil's Advocate produce indistinguishable findings; the "challenge" pass agrees with everything | Run roles as separate prompts. Devil's Advocate may only disprove / weaken / validate / revise existing claims — never add new ones |
| Devil's Advocate invents unrelated findings | New claims appear in the challenge pass that weren't in Investigation; noise drowns real disagreements | Restrict Devil's Advocate output to operations on existing claims (disprove, weaken, validate, revise). New claims belong in a fresh Investigation pass |
| Unfalsifiable claims | "May have security issues", "could be a problem", "potentially unsafe" | Reject any claim without an evidence pointer *and* a disproof condition. If the claim can't be disproved, it can't be acted on |
| Decisive-looking big actions | "Refactor the auth layer", "rewrite the migration", "ban this library" | Default to the smallest safe fix. Big actions require an explicit human-approval gate AND a smaller-step alternative that was considered and rejected |
| Confidence without evidence | "High confidence" with no file:line, no repro, no test | Confidence is a function of evidence quality. No evidence = Low confidence at most |
| Scope creep mid-review | Investigation widens from "this route handler" to "the whole auth system" | Stop, finish the narrow review, document the wider concern as a separate proposed review |
| "Review the codebase" | The user gave a vague ask and you started reading anyway | Pre-flight HARD STOP — refuse and ask for a target |

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

## How to execute

This skill runs *in this session* — Claude executes the roles directly. Each role's prompt file is its contract — read it before running that pass and follow its rules and return format exactly:

- Orchestrator → `prompts/00-orchestrator.md`
- Investigator → `prompts/01-investigator.md`
- Devil's Advocate → `prompts/02-devils-advocate.md`
- Impact Tracer → `prompts/03-impact-tracer.md`
- Fix Planner → `prompts/04-fix-planner.md`
- Triage Lead → `prompts/05-triage-lead.md`
- Final Decision → `prompts/06-final-decision.md`

**Lightweight mode:** run the three roles (Orchestrator → Investigator → Final Decision) as one in-context pass, reading only those three prompt files.

**Full pipeline:** run each role as a sequential in-context pass under its prompt-file contract above. Emit the claim ledger after the Investigator pass and update it between every subsequent pass. For very large targets, roles MAY be dispatched as subagents instead of in-context passes — same contracts, same ledger threading.

`references/one-shot-prompt.md` is not an execution path for this skill; it is a paste-ready prompt for an external chat UI where the user drives the review manually.

For a worked example of a full run, read the one matching your target — `examples/architecture-review-example.md`, `examples/code-review-example.md`, or `examples/decision-review-example.md` — when you need to see the expected shape of intermediate or final outputs; skip them otherwise.
