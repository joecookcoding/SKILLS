# Evidence-driven improvement loop

“Improves every run” must be an evaluation protocol, not a motivational phrase. A closed run always creates knowledge; only a successful next-run comparison earns an improvement claim.

## Two loops

- Inner maker-checker loop: `worker -> fresh verifier -> bounded feedback -> worker`, capped by `max_attempts_per_node` and `max_rounds`.
- Outer run loop: `run -> metrics -> proposed experiment -> next run -> compare -> promote or reject`.

This is Ralph-style persistence with explicit exit conditions. It does not modify model weights.

## Metrics artifact

Create JSON:

```json
{
  "objective_score": 82.5,
  "quality_gate_passed": true,
  "worker_success_rate": 1.0,
  "rework_count": 1,
  "wall_time_seconds": 184.2,
  "cost_units": 12.4,
  "notes": "How the objective score was calculated"
}
```

Requirements:

- `objective_score`: 0-100, defined by the goal's observable rubric.
- `quality_gate_passed`: the final acceptance gate, not agent confidence.
- `worker_success_rate`: completed expected workers divided by expected workers.
- `rework_count`: verifier-driven revision cycles.
- `wall_time_seconds` and `cost_units`: optional but non-negative when present. `cost_units` may be tokens, dollars, or another stable unit; keep the unit consistent across compared runs.
- `notes`: explain the measurement, especially when a human scored it.

## Experiment artifact

Create JSON:

```json
{
  "observation": "Workers repeated the same repository scan.",
  "hypothesis": "Passing a shared read-only file map will reduce wall time without lowering quality.",
  "change": "Generate one deterministic file map before fan-out and include its path in every worker packet.",
  "target_metric": "wall_time_seconds",
  "expected_direction": "decrease",
  "minimum_delta": 5.0,
  "guardrails": [
    {"metric": "objective_score", "rule": "not_decrease", "tolerance": 0.0},
    {"metric": "quality_gate_passed", "rule": "must_equal", "value": true}
  ]
}
```

Choose one bounded process, prompt, routing, tool, or context change. Do not propose “use a smarter model” without a cost/latency guardrail. The target metric must exist in the metrics artifact.

Supported directions: `increase`, `decrease`. Supported guardrail rules: `not_decrease`, `not_increase`, `must_equal`.

## Promotion

At close, the runner evaluates experiments that were pending when the run began:

1. Require the run to name the pending experiment at `begin` and record how the exact treatment is active.
2. Require the goal-contract hash to match the baseline so objective scores remain comparable.
3. Compare the current target against the saved baseline.
4. Require the declared `minimum_delta` in the expected direction.
5. Require every guardrail.
6. Promote the change into active policy only if all checks pass.
7. Otherwise move it to rejected memory with the observed deltas.

The same close creates a new pending experiment from the current metrics. The next run receives a snapshot of active policies plus that candidate.

The runner fingerprints changes across active, pending, and rejected memory. It refuses a duplicate change so a dry loop cannot spend runs rediscovering the same accepted or rejected policy.

## Claims language

- First run: “The graph established a baseline and queued an experiment.”
- Candidate rejected: “The graph learned that the change did not beat baseline; it was not promoted.”
- Candidate promoted: “The graph improved on `<metric>` by `<delta>` while guardrails held; the change is now active policy.”

Never say that a single self-review made the underlying model permanently smarter.
