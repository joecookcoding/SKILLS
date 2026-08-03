# Node and artifact contracts

Use these shapes exactly. Store one artifact per node attempt so workers and verifiers exchange bounded data rather than chat history.

Unknown top-level or nested fields are rejected. This prevents a producer from smuggling unvalidated data into fan-in under a superficially valid schema.

## Split

```json
{
  "tasks": [
    {
      "worker_id": "worker-01",
      "task": "One bounded assignment",
      "inputs": ["Explicit file, URL, or prior artifact"],
      "acceptance_criteria": ["Observable condition"],
      "permitted_writes": []
    }
  ],
  "coverage_notes": "Why these tasks cover the goal without fake dependencies"
}
```

Return exactly one task for every worker ID in `graph.json`. Use disjoint writes. If two workers must edit the same file, return proposals from both and appoint the consolidation node as the single writer.

## Worker

```json
{
  "worker_id": "worker-01",
  "task_result": "completed",
  "summary": "Bounded result",
  "evidence": [
    {"claim": "What is supported", "pointer": "file:line, command output, or source URL"}
  ],
  "deliverables": ["Artifact path or proposed change"],
  "acceptance_checks": [
    {"criterion": "Copied from task", "passed": true, "evidence": "Pointer"}
  ],
  "open_questions": []
}
```

Set `task_result` to `completed`, `partial`, or `blocked`. Do not hide a partial result behind confident prose.

## Verifier

```json
{
  "worker_id": "worker-01",
  "verdict": "pass",
  "score": 0.92,
  "checks": [
    {"lens": "correctness", "passed": true, "evidence": "Independent check"},
    {"lens": "completeness", "passed": true, "evidence": "Criteria coverage"},
    {"lens": "evidence", "passed": true, "evidence": "Pointers resolve"}
  ],
  "feedback": [],
  "residual_risks": []
}
```

Use `pass` or `revise` for a verification judgment. A verifier must independently run checks where tools permit. “The worker says it passed” is not evidence. Keep feedback actionable and scoped to the paired worker. If the verifier itself cannot execute, record `--result fail` with the separate execution-failure contract below.

## Consolidate

```json
{
  "included_workers": ["worker-01", "worker-02"],
  "excluded_workers": [],
  "coverage": [{"criterion": "Goal criterion", "status": "covered", "evidence": "Pointer"}],
  "conflicts": [],
  "synthesis": "The verified combined result",
  "final_answer_plan": ["Ordered point to include"]
}
```

Include only verifier-passed workers. `included_workers` must match all expected workers unless `excluded_workers` names the gap and the goal explicitly permits partial success. The runner rejects silent partial fan-in.

## Final

Use Markdown. Lead with the outcome, cite the verified evidence, disclose gaps, and keep operational details proportional to the user request. The final draft must not introduce new factual claims that were absent from the accepted artifacts.

Send the draft to a fresh `verify-final` node using the Verifier contract with `worker_id: "final"`. It must check traceability to accepted artifacts, goal coverage, and unsupported new claims. A `revise` verdict returns bounded feedback to the final-draft node. After `verify-final` passes, release the exact verified draft without another generative rewrite.

## Execution failure

`--result fail` means the node could not produce its normal success artifact. It uses a separate exact JSON contract for every node kind:

```json
{
  "error": "Bounded description of what failed",
  "evidence": "Exit code, tool output, or other reproducible pointer",
  "retryable": true
}
```

Set `retryable` to `false` when retrying the same node cannot help. Do not put partial success data in this envelope; record a normal worker artifact with `task_result: "partial"` when structured partial evidence exists.

## Prompt packet

Pass a node only:

1. The exact goal and success criteria.
2. Its bounded assignment and permitted inputs/writes.
3. Its artifact schema.
4. Active policies and the explicitly applied experiment from the run memory snapshot.
5. Retry feedback, if this is a retry.

Do not pass sibling chats, hidden chain-of-thought, or an ever-growing transcript.

`graphctl ready` emits this packet for each ready node. The goal and graph come from immutable run snapshots, so edits to live project files apply only to the next run.
