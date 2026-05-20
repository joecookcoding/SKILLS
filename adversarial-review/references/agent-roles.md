# Agent Roles — Detailed Responsibilities

Each role has a narrow job. Read this when you need the full responsibility list for a specific agent. The short version of each role lives in `SKILL.md`; individual prompt templates live in `prompts/`.

## 0. Orchestrator

Controls the review. Picks mode, enforces scope, decides which agents to run, holds the claim ledger, produces the final report.

**Does:** identify mode, confirm scope, split work, prevent scope creep, preserve the claim ledger, produce only the requested final format.

**Does not:** invent missing context, expand the review without permission, hide uncertainty, treat speculation as fact.

## 1. Investigator

Finds concrete issues, weaknesses, bugs, flaws, or improvement opportunities.

**Does:** stay inside scope, identify concrete claims, provide evidence, explain why each claim matters, state confidence, state what would disprove the claim, suggest a verification step.

**Does not:** review the whole repo unless explicitly scoped, generate exploit code, create vague findings, overstate severity, recommend risky action without approval.

## 2. Devil's Advocate

Challenges the Investigator. The Devil's Advocate may not create unrelated new findings — its job is to disprove, weaken, validate, or revise an existing claim.

**Does:** try to disprove the claim, look for missing context, identify false positives, challenge assumptions, reduce inflated severity, accept / reject / revise / request more evidence.

**Does not:** create unrelated findings, expand scope, automatically agree, make the finding sound stronger than the evidence supports.

## 3. Impact Tracer

Determines whether an accepted or revised claim matters in the real system.

**For code/security:** Is the behavior reachable? Who can reach it? What permissions are required? What data or workflow is affected? Is the impact practical, theoretical, or unknown?

**For architecture/decisions:** Who is affected? What breaks if this is wrong? What does this make harder? What is the cost of delay? What is the cost of reversal?

## 4. Fix Planner

Recommends the smallest safe next step.

**Does:** prefer small changes over rewrites, preserve existing behavior where possible, include tests, identify regression risk, include rollback notes, mark human approval gates.

## 5. Triage Lead

Merges duplicate findings and prioritizes action.

**Does:** merge duplicates, reject unsupported claims, mark unclear items "Needs Evidence," assign priority, identify owners or next actions, preserve nuance.

## 6. Final Decision Agent

Turns the review into a recommendation.

**Possible decisions:** Approve · Approve with follow-up · Block until fixed · Needs more evidence · Rework approach · Run a smaller experiment · Escalate to human review.

**The decision must include:** why this decision was chosen, what action should happen next, what should not happen yet, what requires approval.
