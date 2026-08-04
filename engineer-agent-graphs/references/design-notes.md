# Graph design notes

## What to create first

Create all four layers, each with one job:

| Layer | Artifact | Authority |
|---|---|---|
| Goal contract | `GOAL.md` | What success and safety mean |
| Topology | `graph.json` | Dependencies, fan-out, verifier lenses, caps |
| Runtime state | `.graph/` | Attempts, artifacts, events, metrics, memory |
| Human view | `TODO.md`, `.graph/dashboard.html` | Generated inspection only |

A full product PRD is optional. Link it from `GOAL.md` when product scope needs it. The graph is not a PRD, the TODO is not a scheduler, and HTML must never become state.

## When a graph pays

Use it for independent source research, file-by-file review, competing proposals, broad discovery, repeated scheduled workflows, and tasks too wide for one context. Keep one agent for narrow bugs, tightly sequential reasoning, or tasks where coordination costs more than the work.

## Core invariants

- A node owns one bounded job, explicit input, validated output, and one writer scope.
- An edge carries named data.
- Model judgment lives in nodes; routing, counting, sorting, deduplication, caps, and retries live in code.
- Every expected input is counted at fan-in.
- Worker and verifier contexts are separate.
- A final draft receives its own fresh verifier and is released unchanged after passing.
- Loops deduplicate against everything seen, including rejected findings.
- Every loop has attempt, round, time, and cost caps appropriate to the environment.
- Large fan-in is layered: summarize batches before final synthesis.

## Execution graph versus knowledge graph

An execution graph coordinates work. A knowledge graph stores entities and time-qualified relationships. They solve different problems.

Start with the file-backed temporal ledger in this skill. It is inspectable, versionable, dependency-free, and sufficient to learn workflow policies. Add a graph database only when queries are truly relational or multi-hop across many runs, such as ownership, dependency blast radius, or changing decisions. Keep source pointers and `reference_time`; never ingest speculation as fact.

## Model routing

Use cheap/fast models for bounded extraction or classification. Use stronger judgment for decomposition, adversarial verification, conflict resolution, and final synthesis. Record the routing policy as an experiment before making it permanent.

The per-node-kind table lives in SKILL.md under "Route models to node kinds". Two properties make that table worth following rather than approximating:

**Verification is the load-bearing tier.** A worker on too weak a model produces a poor artifact that its verifier catches. A *verifier* on too weak a model produces a false `pass`, and nothing downstream re-checks it — the graph's entire trust boundary is the verifier's independence and judgment. Economizing on workers is recoverable; economizing on verifiers silently converts the graph into a single-agent pipeline that merely looks reviewed.

**A default model is a decision you did not make.** Harnesses inherit the orchestrator's model when none is passed, so "I did not choose" resolves to "everything runs on the most expensive tier." That is not a safe default: it multiplies cost by the fan-out width and makes rate-limit death the expected outcome of a wide graph. Cap concurrent strongest-tier agents and release in waves — an outage takes every in-flight node with it, including nodes that were one tool call from finishing, and their partial work is unrecoverable because artifacts are written at the end.

## Failure handling

- Missing worker result: flag the exact gap; do not call the report complete.
- Verifier revision: return scoped feedback only to its paired worker.
- Repeated failure: exhaust the node cap, mark the run blocked, preserve evidence.
- Parallel write collision: switch to isolated worktrees or proposal-only workers plus one consolidating writer.
- Context collapse: batch fan-in and synthesize summaries.
- Runaway discovery: stop after configured dry rounds and dedupe against all seen items.
- Concurrent recording: keep mutations in the orchestrator; the runner also uses a project lock and unique atomic-replacement files.
- Interrupted recording: use `recover` to write a state-hash checkpoint; malformed ledgers are quarantined, never overwritten.
- Live configuration drift: active runs read hashed manifest graph and goal snapshots; root edits apply to the next run, and hash mismatches stop execution.

## Research synthesis

The supplied research converged on the diamond topology, real-edge test, structured node contracts, fresh maker-checker contexts, deterministic reductions, isolated writes, bounded loops, model tiering, and persistent memory. Some threads instead described graph databases or adjacent deployment practices; those informed the temporal ledger, source discipline, evals, and measurable operational outcomes rather than the execution topology.

Source threads:

- https://x.com/AnatoliKopadze/status/2080668775796314331
- https://x.com/0x_rody/status/2081664256571810178
- https://x.com/cyrilXBT/status/2082304935547314254
- https://x.com/RohOnChain/status/2080296261576687751
- https://x.com/0xCodez/status/2082468167935308098
- https://x.com/zodchiii/status/2080219348338090198
- https://x.com/angeldot_/status/2081061068516798931
- https://x.com/eng_khairallah1/status/2047609433489035739
