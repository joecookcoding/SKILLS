#!/usr/bin/env python3
"""End-to-end smoke test for graphctl using only temporary files."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


SCRIPT = Path(__file__).resolve().with_name("graphctl.py")
LENSES = ["correctness", "completeness", "evidence"]


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            attributes = dict(attrs)
            if attributes.get("href"):
                self.links.append(attributes["href"] or "")


def write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


class GraphCtlEndToEndTest(unittest.TestCase):
    def run_cli(self, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, args)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            expected,
            msg=f"command failed: {args}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def artifact(self, root: Path, name: str, data: dict) -> Path:
        return write_json(root / "fixtures" / name, data)

    def split_artifact(self, root: Path) -> Path:
        return self.artifact(
            root,
            "split.json",
            {
                "tasks": [
                    {
                        "worker_id": "worker-01",
                        "task": "Analyze correctness",
                        "inputs": ["GOAL.md"],
                        "acceptance_criteria": ["Return one evidenced finding"],
                        "permitted_writes": [],
                    },
                    {
                        "worker_id": "worker-02",
                        "task": "Analyze completeness",
                        "inputs": ["GOAL.md"],
                        "acceptance_criteria": ["Return one evidenced finding"],
                        "permitted_writes": [],
                    },
                ],
                "coverage_notes": "The two independent lenses cover the example goal.",
            },
        )

    def worker_artifact(self, root: Path, worker_id: str, revision: int = 0) -> Path:
        return self.artifact(
            root,
            f"{worker_id}-{revision}.json",
            {
                "worker_id": worker_id,
                "task_result": "completed",
                "summary": f"Verified result from {worker_id}, revision {revision}",
                "evidence": [{"claim": "Fixture is present", "pointer": "GOAL.md"}],
                "deliverables": [],
                "acceptance_checks": [
                    {"criterion": "Return one evidenced finding", "passed": True, "evidence": "GOAL.md"}
                ],
                "open_questions": [],
            },
        )

    def verifier_artifact(self, root: Path, worker_id: str, verdict: str, score: float) -> Path:
        passed = verdict == "pass"
        return self.artifact(
            root,
            f"verify-{worker_id}-{verdict}.json",
            {
                "worker_id": worker_id,
                "verdict": verdict,
                "score": score,
                "checks": [
                    {"lens": lens, "passed": passed, "evidence": f"Independent {lens} check"}
                    for lens in LENSES
                ],
                "feedback": [] if passed else ["Add direct evidence for the fixture claim."],
                "residual_risks": [],
            },
        )

    def complete_run(self, project: Path, score: float, rework: bool, wall_time: float) -> dict:
        memory = json.loads((project / ".graph" / "memory.json").read_text(encoding="utf-8"))
        begin_args = ["begin", project]
        if memory["pending_experiments"]:
            begin_args.extend(
                [
                    "--apply-experiment",
                    memory["pending_experiments"][0]["id"],
                    "--application-note",
                    "The worker prompt packet includes the exact pending policy change for this fixture run.",
                ]
            )
        self.run_cli(*begin_args)
        self.run_cli("record", project, "split", "--result", "pass", "--artifact", self.split_artifact(project))
        for worker_id in ("worker-01", "worker-02"):
            self.run_cli(
                "record",
                project,
                worker_id,
                "--result",
                "pass",
                "--artifact",
                self.worker_artifact(project, worker_id),
            )
        if rework:
            self.run_cli(
                "record",
                project,
                "verify-01",
                "--result",
                "revise",
                "--artifact",
                self.verifier_artifact(project, "worker-01", "revise", 0.55),
            )
            self.run_cli(
                "record",
                project,
                "worker-01",
                "--result",
                "pass",
                "--artifact",
                self.worker_artifact(project, "worker-01", revision=1),
            )
        for verifier_id, worker_id in (("verify-01", "worker-01"), ("verify-02", "worker-02")):
            self.run_cli(
                "record",
                project,
                verifier_id,
                "--result",
                "pass",
                "--artifact",
                self.verifier_artifact(project, worker_id, "pass", 0.95),
            )
        consolidate = self.artifact(
            project,
            "consolidate.json",
            {
                "included_workers": ["worker-01", "worker-02"],
                "excluded_workers": [],
                "coverage": [{"criterion": "Example goal", "status": "covered", "evidence": "worker artifacts"}],
                "conflicts": [],
                "synthesis": "Both verified results are consistent.",
                "final_answer_plan": ["Report the verified outcome"],
            },
        )
        self.run_cli("record", project, "consolidate", "--result", "pass", "--artifact", consolidate)
        final = project / "fixtures" / "final.md"
        final.write_text("# Final answer\n\nThe two verified branches agree.\n", encoding="utf-8")
        self.run_cli("record", project, "final", "--result", "pass", "--artifact", final)
        self.run_cli(
            "record",
            project,
            "verify-final",
            "--result",
            "pass",
            "--artifact",
            self.verifier_artifact(project, "final", "pass", 0.96),
        )
        metrics = self.artifact(
            project,
            f"metrics-{score}.json",
            {
                "objective_score": score,
                "quality_gate_passed": True,
                "worker_success_rate": 1.0,
                "rework_count": 1 if rework else 0,
                "wall_time_seconds": wall_time,
                "cost_units": 4.0,
                "notes": "Fixture rubric scored the two independently verified branches.",
            },
        )
        experiment = self.artifact(
            project,
            f"experiment-{score}.json",
            {
                "observation": "Worker packets can be made more specific.",
                "hypothesis": "Specific evidence requirements will increase objective score.",
                "change": f"Require a direct evidence pointer in each worker packet after score {score}.",
                "target_metric": "objective_score",
                "expected_direction": "increase",
                "minimum_delta": 5.0,
                "guardrails": [{"metric": "quality_gate_passed", "rule": "must_equal", "value": True}],
            },
        )
        result = self.run_cli("close", project, "--metrics", metrics, "--experiment", experiment)
        return json.loads(result.stdout)

    def test_two_runs_promote_measured_improvement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="graphctl-test-") as temp:
            project = Path(temp) / "project"
            self.run_cli(
                "init",
                project,
                "--name",
                "Fixture Graph",
                "--goal",
                "Produce two independently verified findings.",
                "--workers",
                "2",
            )
            goal = project / "GOAL.md"
            goal.write_text(
                goal.read_text(encoding="utf-8").replace(
                    "Define a 0-100 rubric before the first run. Prefer checks a verifier can reproduce.",
                    "Score 50 points for each worker result that passes every independent verification lens.",
                ),
                encoding="utf-8",
            )
            self.run_cli("doctor", project)
            first = self.complete_run(project, score=70.0, rework=True, wall_time=20.0)
            self.assertEqual(first["promoted_count"], 0)
            missing_application = self.run_cli("begin", project, expected=2)
            self.assertIn("must be explicitly applied", missing_application.stderr)
            second = self.complete_run(project, score=80.0, rework=False, wall_time=16.0)
            self.assertEqual(second["promoted_count"], 1)
            third = self.complete_run(project, score=75.0, rework=False, wall_time=17.0)
            self.assertEqual(third["promoted_count"], 0)
            memory = json.loads((project / ".graph" / "memory.json").read_text(encoding="utf-8"))
            self.assertEqual(len(memory["active_policies"]), 1)
            self.assertEqual(len(memory["pending_experiments"]), 1)
            self.assertEqual(len(memory["rejected_experiments"]), 1)
            dashboard = (project / ".graph" / "dashboard.html").read_text(encoding="utf-8")
            self.assertIn("Active policies", dashboard)
            self.assertIn("Current TODO", dashboard)
            self.assertIn("Fresh verifiers", dashboard)
            self.assertIn("Final verifier", dashboard)
            collector = LinkCollector()
            collector.feed(dashboard)
            for link in collector.links:
                if "://" not in link and not link.startswith("#"):
                    self.assertTrue(((project / ".graph") / link).resolve().is_file(), msg=f"broken dashboard link: {link}")
            self.run_cli("doctor", project)

    def test_concurrent_records_are_serialized_and_doctor_catches_corruption(self) -> None:
        with tempfile.TemporaryDirectory(prefix="graphctl-concurrency-") as temp:
            project = Path(temp) / "project"
            self.run_cli(
                "init",
                project,
                "--name",
                "Concurrency Graph",
                "--goal",
                "Collect eight independently recorded results.",
                "--workers",
                "8",
            )
            goal = project / "GOAL.md"
            goal.write_text(
                goal.read_text(encoding="utf-8").replace(
                    "Define a 0-100 rubric before the first run. Prefer checks a verifier can reproduce.",
                    "Award 12.5 points for each independently recorded worker artifact.",
                ),
                encoding="utf-8",
            )
            self.run_cli("begin", project)
            tasks = []
            for index in range(1, 9):
                worker_id = f"worker-{index:02d}"
                tasks.append(
                    {
                        "worker_id": worker_id,
                        "task": f"Return result {index}",
                        "inputs": ["GOAL.md"],
                        "acceptance_criteria": ["Return one evidenced result"],
                        "permitted_writes": [str(project / "fixtures" / f"{worker_id}.json")],
                    }
                )
            split = self.artifact(
                project,
                "split-eight.json",
                {"tasks": tasks, "coverage_notes": "Eight disjoint tasks cover the eight requested results."},
            )
            self.run_cli("record", project, "split", "--result", "pass", "--artifact", split)
            commands = []
            for index in range(1, 9):
                worker_id = f"worker-{index:02d}"
                artifact = self.artifact(
                    project,
                    f"parallel-{worker_id}.json",
                    {
                        "worker_id": worker_id,
                        "task_result": "completed",
                        "summary": f"Result {index}",
                        "evidence": [{"claim": f"Result {index} exists", "pointer": str(split)}],
                        "deliverables": [],
                        "acceptance_checks": [
                            {"criterion": "Return one evidenced result", "passed": True, "evidence": str(split)}
                        ],
                        "open_questions": [],
                    },
                )
                commands.append(
                    subprocess.Popen(
                        [
                            sys.executable,
                            str(SCRIPT),
                            "record",
                            str(project),
                            worker_id,
                            "--result",
                            "pass",
                            "--artifact",
                            str(artifact),
                        ],
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                )
            results = [process.communicate(timeout=30) + (process.returncode,) for process in commands]
            self.assertTrue(all(returncode == 0 for _, _, returncode in results), msg=str(results))
            state_path = project / ".graph" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(all(state["nodes"][f"worker-{index:02d}"]["status"] == "passed" for index in range(1, 9)))
            self.run_cli("doctor", project)
            state["nodes"]["worker-01"]["attempts"] = 99
            write_json(state_path, state)
            corrupted = self.run_cli("doctor", project, expected=2)
            self.assertIn("exceed valid range", corrupted.stdout)

    def test_active_run_uses_immutable_graph_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="graphctl-snapshot-") as temp:
            project = Path(temp) / "project"
            self.run_cli(
                "init",
                project,
                "--name",
                "Snapshot Graph",
                "--goal",
                "Verify one result against the snapshotted threshold.",
                "--workers",
                "2",
            )
            goal = project / "GOAL.md"
            goal.write_text(
                goal.read_text(encoding="utf-8").replace(
                    "Define a 0-100 rubric before the first run. Prefer checks a verifier can reproduce.",
                    "Award 100 points when a verifier score at or above the run threshold passes.",
                ),
                encoding="utf-8",
            )
            self.run_cli("begin", project)
            self.run_cli("record", project, "split", "--result", "pass", "--artifact", self.split_artifact(project))
            self.run_cli(
                "record",
                project,
                "worker-01",
                "--result",
                "pass",
                "--artifact",
                self.worker_artifact(project, "worker-01"),
            )
            live_graph_path = project / "graph.json"
            live_graph = json.loads(live_graph_path.read_text(encoding="utf-8"))
            live_graph["quality_threshold"] = 0.99
            write_json(live_graph_path, live_graph)
            self.run_cli(
                "record",
                project,
                "verify-01",
                "--result",
                "pass",
                "--artifact",
                self.verifier_artifact(project, "worker-01", "pass", 0.95),
            )
            self.run_cli("doctor", project)

    def test_exact_contracts_and_recovery_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory(prefix="graphctl-recovery-") as temp:
            project = Path(temp) / "project"
            self.run_cli(
                "init",
                project,
                "--name",
                "Recovery Graph",
                "--goal",
                "Recover one recorded branch without accepting ambiguous artifacts.",
                "--workers",
                "2",
            )
            goal = project / "GOAL.md"
            goal.write_text(
                goal.read_text(encoding="utf-8").replace(
                    "Define a 0-100 rubric before the first run. Prefer checks a verifier can reproduce.",
                    "Award 100 points when every exact artifact contract and recovery check passes.",
                ),
                encoding="utf-8",
            )
            self.run_cli("begin", project)

            invalid_split_data = json.loads(self.split_artifact(project).read_text(encoding="utf-8"))
            invalid_split_data["unexpected"] = "must be rejected"
            invalid_split = self.artifact(project, "split-unexpected.json", invalid_split_data)
            rejected = self.run_cli(
                "record", project, "split", "--result", "pass", "--artifact", invalid_split, expected=2
            )
            self.assertIn("unexpected", rejected.stderr)
            self.run_cli("record", project, "split", "--result", "pass", "--artifact", self.split_artifact(project))

            plain_failure = project / "fixtures" / "plain-failure.txt"
            plain_failure.write_text("something failed", encoding="utf-8")
            rejected_failure = self.run_cli(
                "record", project, "worker-01", "--result", "fail", "--artifact", plain_failure, expected=2
            )
            self.assertIn("Invalid JSON", rejected_failure.stderr)
            valid_failure = self.artifact(
                project,
                "failure.json",
                {"error": "Transient tool error", "evidence": "Command exited 75", "retryable": True},
            )
            self.run_cli("record", project, "worker-01", "--result", "fail", "--artifact", valid_failure)

            ledger = next((project / ".graph" / "runs").glob("run-*/events.jsonl"))
            ledger.unlink()
            missing_ledger = self.run_cli("doctor", project, expected=2)
            self.assertIn("event ledger is missing", missing_ledger.stdout)
            recovered = self.run_cli(
                "recover", project, "--reason", "Rebuild checkpoint after an injected post-state ledger failure."
            )
            recovery_output = json.loads(recovered.stdout)
            self.assertIsNone(recovery_output["quarantined_ledger"])
            events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(events[-1]["type"], "recovery_checkpoint")
            self.assertEqual(events[-1]["reason"], "Rebuild checkpoint after an injected post-state ledger failure.")
            self.run_cli("doctor", project)

            manifest_path = next((project / ".graph" / "runs").glob("run-*/manifest.json"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["graph_snapshot"]["quality_threshold"] = 0.91
            write_json(manifest_path, manifest)
            tampered = self.run_cli("doctor", project, expected=2)
            self.assertIn("snapshot hash differs", tampered.stdout)
            refused = self.run_cli(
                "recover", project, "--reason", "Attempt to reseal tampered graph", expected=2
            )
            self.assertIn("Refusing recovery", refused.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
