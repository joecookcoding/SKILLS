---
name: engineer-agent-graphs
description: Design and run persistent agent execution graphs that fan a goal out to isolated workers, verify each result in fresh context, consolidate only accepted work, and measure an improvement experiment across runs. Use for graph engineering, multi-agent workflows, agent swarms, parallel workers, maker-checker or Ralph loops, goal-to-task orchestration, long-running agent tasks, self-improving agent harnesses, reusable research or code-review pipelines, or requests shaped like Goal → Split → Workers → Verify → Consolidate → Final.
---

# Engineer Agent Graphs

Build the graph as the execution system. Treat `GOAL.md` as the compact PRD, `graph.json` as topology and limits, `TODO.md` as a generated run view, and `.graph/` as the event ledger and memory. Do not use the HTML dashboard as the source of truth.

## Route the request

Use a graph only when the work has at least two genuinely independent branches, benefits from isolated context, or must survive retries/runs. Use one agent for a small task whose steps all depend on the complete prior result.

Ask of every proposed edge: “Does the downstream node consume data produced by the upstream node?” Remove edges that exist only because the prompt said “then.”

Use the default topology:

`Goal -> Split -> Worker 1..N -> Verifier 1..N -> Consolidate -> Final draft -> Fresh final verifier -> Retrospective`

Each verifier pairs with one worker. A failed verification edge returns bounded feedback to that worker. The retrospective writes one experiment for the next run; it never edits model weights or silently rewrites policy.

Read [references/contracts.md](references/contracts.md) before authoring node prompts or artifacts. Read [references/improvement-loop.md](references/improvement-loop.md) before closing a run or claiming improvement. Read [references/design-notes.md](references/design-notes.md) when changing the topology, adding a memory backend, or deciding whether a graph is warranted.

## Initialize the control plane

Run:

```bash
python3 <skill-dir>/scripts/graphctl.py init <project-dir> \
  --name "<graph name>" \
  --goal "<one measurable outcome>" \
  --workers <2-8>
```

Then refine `GOAL.md` before beginning. Put the objective, observable done criteria, constraints, non-goals, permitted writes, and human approval gates there. Keep a long product PRD elsewhere and link it from `GOAL.md`; do not pour it into every worker context.

Validate and begin:

```bash
python3 <skill-dir>/scripts/graphctl.py doctor <project-dir>
python3 <skill-dir>/scripts/graphctl.py begin <project-dir>
python3 <skill-dir>/scripts/graphctl.py ready <project-dir>
```

Use `TODO.md` and `.graph/dashboard.html` to inspect status. They are regenerated after every state change.

## Execute the graph

1. Read only the snapshotted goal/graph, the current run's memory snapshot, and the ready-node packet. The runner makes every packet self-contained with the goal, task, artifact contract, active policies, applied experiment, and retry feedback.
2. Run the split node first. Make tasks mutually exclusive where practical, collectively sufficient, and bound to one worker ID each.
3. Record the split artifact. The control plane releases all workers together.
4. Dispatch ready workers concurrently when an isolated subagent mechanism is available. Give each worker only the goal contract, its task, permitted inputs, its output schema, and relevant active policies. Do not give it another worker's reasoning.
5. Prevent concurrent writers from editing the same file. Use separate worktrees/sandboxes for parallel writes, or make workers return proposed patches/artifacts and appoint a single writer after consolidation.
6. Record every worker artifact, including failures. Never synthesize silently from a partial fan-in.
7. Dispatch each verifier in fresh context with only the goal, worker artifact, acceptance criteria, and verification lenses. Never pass the worker's chat transcript.
8. On `revise`, send only the verifier's bounded feedback back to its paired worker. Respect retry and round caps.
9. Consolidate only worker artifacts whose verifiers passed. Resolve conflicts explicitly; deterministic flattening, counting, sorting, and deduplication belong in code, not an agent prompt.
10. Produce the final draft from the consolidated artifact and record it.
11. Dispatch `verify-final` in a fresh context. Return `revise` if any material claim lacks support, the answer misses the goal, or residual gaps are hidden. The verifier-passed draft is the final answer; do not rewrite it afterward.

Record nodes with:

```bash
python3 <skill-dir>/scripts/graphctl.py record <project-dir> <node-id> \
  --result pass --artifact <artifact.json-or-md>
```

For a verifier requesting repair:

```bash
python3 <skill-dir>/scripts/graphctl.py record <project-dir> verify-01 \
  --result revise --artifact verifier-01.json
```

Use `--result fail` for an execution failure and provide the separate exact JSON failure contract from [references/contracts.md](references/contracts.md). Set `retryable` false for a terminal failure; otherwise the runner retries within caps and blocks when a cap is exhausted.

If native subagents are unavailable, execute nodes sequentially in isolated passes: clear task-local reasoning between worker and verifier, persist only the contracted artifact, and preserve the same state transitions. This loses latency benefits but keeps the trust boundary.

## Close the outer improvement loop

After `verify-final` passes, create metrics and an experiment using the schemas in [references/improvement-loop.md](references/improvement-loop.md), then run:

```bash
python3 <skill-dir>/scripts/graphctl.py close <project-dir> \
  --metrics metrics.json \
  --experiment experiment.json
```

Every run must produce a testable next-run experiment. On the next close, the control plane compares the target metric against its saved baseline and checks guardrails:

- Promote the change to active policy only when the target improves by the declared minimum and guardrails hold.
- Reject and remember regressions so the graph does not rediscover them.
- Preserve the raw run, verifier decisions, and metrics as append-only evidence.

When the next run begins, explicitly mark the pending experiment as applied and explain how it is active:

```bash
python3 <skill-dir>/scripts/graphctl.py begin <project-dir> \
  --apply-experiment <experiment-id> \
  --application-note "<where the exact change was applied>"
```

The runner refuses promotion without this treatment marker and refuses cross-run comparison when `GOAL.md` changed. If the goal changed intentionally, begin with `--abandon-pending "<reason>"` to retain the rejected lesson and establish a new baseline.

Say the system “learned” after every closed run. Say it “improved” only when the comparison promoted a candidate. Never claim recursive self-improvement from self-review alone.

## Operate safely

- Cap workers, attempts, rounds, and context passed into fan-in.
- Use a stronger model or greater reasoning effort at split, verification, and synthesis when available; use cheaper settings for bounded mechanical workers.
- Count expected versus received artifacts at every fan-in.
- Keep the event ledger append-only. Use the CLI rather than hand-editing `.graph/state.json` or `.graph/memory.json`.
- Let only the orchestrator call mutating CLI commands. The runner serializes concurrent mutations, but central recording keeps worker responsibilities narrow and audit order clear.
- Require human approval before destructive writes, production changes, external messages, purchases, credential use, or irreversible consolidation.
- Stop a graph that lacks measurable done criteria; more agents will not repair an undefined goal.

## Inspect and recover

```bash
python3 <skill-dir>/scripts/graphctl.py status <project-dir>
python3 <skill-dir>/scripts/graphctl.py history <project-dir>
python3 <skill-dir>/scripts/graphctl.py render <project-dir>
python3 <skill-dir>/scripts/graphctl.py doctor <project-dir>
```

If an interrupted mutation leaves the event ledger missing or malformed, preserve the current state and create an auditable recovery checkpoint:

```bash
python3 <skill-dir>/scripts/graphctl.py recover <project-dir> \
  --reason "<what failed and what was independently checked>"
python3 <skill-dir>/scripts/graphctl.py doctor <project-dir>
```

Recovery never blesses a mismatched graph hash. It quarantines a malformed ledger instead of deleting it and seals only legacy snapshots that had no hash. If a run blocks normally, inspect the failed node, its attempt artifacts, and verifier feedback. Repair the scoped input or contract, then begin a new run. Do not erase the failed run; it is training evidence for the harness.
