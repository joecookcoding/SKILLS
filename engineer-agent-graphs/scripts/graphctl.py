#!/usr/bin/env python3
"""Dependency-free control plane for persistent, verified agent graphs."""

from __future__ import annotations

import argparse
import functools
import hashlib
import html
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
TOPOLOGY_ID = "goal-split-workers-verifiers-consolidate-final-final-verifier-retrospective"
TERMINAL_NODE_STATES = {"passed", "failed"}
METRIC_KEYS = {
    "objective_score",
    "quality_gate_passed",
    "worker_success_rate",
    "rework_count",
    "wall_time_seconds",
    "cost_units",
    "notes",
}


class GraphError(Exception):
    pass


class ProjectLock:
    """Cross-platform advisory lock for every read-modify-write command."""

    def __init__(self, project: Path) -> None:
        runtime = project_paths(project)["runtime"]
        runtime.mkdir(parents=True, exist_ok=True)
        self.path = runtime / ".mutation.lock"
        self.handle: Any = None

    def __enter__(self) -> "ProjectLock":
        self.handle = self.path.open("a+b")
        self.handle.seek(0, os.SEEK_END)
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self.handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.handle is None:
            return
        self.handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()


def locked_command(function: Any) -> Any:
    @functools.wraps(function)
    def wrapper(args: argparse.Namespace) -> Any:
        with ProjectLock(Path(args.project).resolve()):
            return function(args)

    return wrapper


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slug(value: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in cleaned.split("-") if part) or "agent-graph"


def project_paths(project: Path) -> dict[str, Path]:
    graph_dir = project / ".graph"
    return {
        "project": project,
        "goal": project / "GOAL.md",
        "graph": project / "graph.json",
        "todo": project / "TODO.md",
        "runtime": graph_dir,
        "state": graph_dir / "state.json",
        "memory": graph_dir / "memory.json",
        "runs": graph_dir / "runs",
        "dashboard": graph_dir / "dashboard.html",
        "templates": graph_dir / "templates",
    }


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GraphError(f"Missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GraphError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise GraphError(f"Expected a JSON object in {path}")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def canonical_json_hash(data: dict[str, Any]) -> str:
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def emit(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def load_graph(project: Path) -> dict[str, Any]:
    graph = read_json(project_paths(project)["graph"])
    validate_graph(graph)
    return graph


def load_state(project: Path, required: bool = True) -> dict[str, Any] | None:
    path = project_paths(project)["state"]
    if not path.exists():
        if required:
            raise GraphError("No run state found. Run `begin` first.")
        return None
    return read_json(path)


def load_memory(project: Path) -> dict[str, Any]:
    memory = read_json(project_paths(project)["memory"])
    for key in ("active_policies", "pending_experiments", "rejected_experiments", "evaluations"):
        if not isinstance(memory.get(key), list):
            raise GraphError(f"memory.json field `{key}` must be a list")
    return memory


def load_run_graph(project: Path, state: dict[str, Any]) -> dict[str, Any]:
    manifest = read_json(run_dir(project, state) / "manifest.json")
    if manifest.get("run_id") != state.get("run_id"):
        raise GraphError("Current run manifest ID differs from state")
    graph = manifest.get("graph_snapshot")
    if not isinstance(graph, dict):
        raise GraphError("Current run manifest has no valid graph snapshot")
    expected_hash = manifest.get("graph_sha256")
    if not isinstance(expected_hash, str) or not expected_hash:
        raise GraphError("Current run manifest has no graph snapshot hash; run `recover` to seal it")
    actual_hash = canonical_json_hash(graph)
    if actual_hash != expected_hash:
        raise GraphError("Current run graph snapshot hash differs from manifest")
    state_hash = state.get("graph_sha256")
    if not isinstance(state_hash, str) or not state_hash:
        raise GraphError("Current run state has no graph snapshot hash; run `recover` to seal it")
    if state_hash != expected_hash:
        raise GraphError("Current run graph snapshot hash differs between state and manifest")
    validate_graph(graph)
    return graph


def load_run_goal(project: Path, state: dict[str, Any]) -> str:
    directory = run_dir(project, state)
    manifest = read_json(directory / "manifest.json")
    goal_path = directory / "GOAL.md"
    try:
        goal_text = goal_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise GraphError("Current run GOAL.md snapshot is missing") from exc
    actual_hash = hashlib.sha256(goal_text.encode("utf-8")).hexdigest()
    manifest_hash = manifest.get("goal_sha256")
    if actual_hash != manifest_hash or actual_hash != state.get("goal_sha256"):
        raise GraphError("Current run GOAL.md snapshot hash differs from state or manifest")
    return goal_text


def validate_graph(graph: dict[str, Any]) -> None:
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise GraphError(f"Unsupported graph schema version: {graph.get('schema_version')}")
    if not isinstance(graph.get("name"), str) or not graph["name"].strip():
        raise GraphError("graph.json requires a non-empty `name`")
    topology = graph.get("topology")
    if not isinstance(topology, dict) or topology.get("id") != TOPOLOGY_ID:
        raise GraphError(f"graph.json topology.id must be `{TOPOLOGY_ID}`")
    expected_stages = [
        "goal",
        "split",
        "workers",
        "verifiers",
        "consolidate",
        "final",
        "final-verifier",
        "retrospective",
    ]
    if topology.get("stages") != expected_stages:
        raise GraphError(f"graph.json topology.stages must be {expected_stages}")
    workers = graph.get("workers")
    if not isinstance(workers, list) or not workers:
        raise GraphError("graph.json requires a non-empty `workers` list")
    ids = [worker.get("id") for worker in workers if isinstance(worker, dict)]
    if len(ids) != len(workers) or len(ids) != len(set(ids)):
        raise GraphError("Every worker requires a unique ID")
    expected_ids = [f"worker-{index:02d}" for index in range(1, len(workers) + 1)]
    if ids != expected_ids:
        raise GraphError(f"Worker IDs must be ordered as {expected_ids}")
    limits = graph.get("limits")
    if not isinstance(limits, dict):
        raise GraphError("graph.json requires `limits`")
    max_workers = limits.get("max_workers")
    if not isinstance(max_workers, int) or not 2 <= max_workers <= 64:
        raise GraphError("limits.max_workers must be an integer from 2 to 64")
    if not 2 <= len(workers) <= max_workers:
        raise GraphError(f"Worker count must be from 2 to {max_workers}")
    for key in ("max_attempts_per_node", "max_rounds"):
        if not isinstance(limits.get(key), int) or not 1 <= limits[key] <= 20:
            raise GraphError(f"limits.{key} must be an integer from 1 to 20")
    lenses = graph.get("verification_lenses")
    if not isinstance(lenses, list) or len(lenses) < 1 or not all(isinstance(item, str) and item for item in lenses):
        raise GraphError("verification_lenses must be a non-empty list of strings")
    threshold = graph.get("quality_threshold")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise GraphError("quality_threshold must be from 0 to 1")


def run_dir(project: Path, state: dict[str, Any]) -> Path:
    return project_paths(project)["runs"] / state["run_id"]


def event(project: Path, state: dict[str, Any], event_type: str, **payload: Any) -> None:
    append_event(
        run_dir(project, state) / "events.jsonl",
        {"at": utc_now(), "type": event_type, **payload},
    )


def build_nodes(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    max_attempts = graph["limits"]["max_attempts_per_node"]
    max_rounds = graph["limits"]["max_rounds"]

    def node(node_id: str, kind: str, label: str, dependencies: list[str], attempts: int) -> dict[str, Any]:
        return {
            "id": node_id,
            "kind": kind,
            "label": label,
            "dependencies": dependencies,
            "status": "blocked",
            "attempts": 0,
            "max_attempts": attempts,
            "artifacts": [],
            "feedback_artifact": None,
            "last_note": None,
        }

    nodes: dict[str, dict[str, Any]] = {
        "goal": node("goal", "goal", "Goal contract", [], 1),
        "split": node("split", "split", "Split the goal", ["goal"], max_attempts),
    }
    for worker in graph["workers"]:
        worker_id = worker["id"]
        nodes[worker_id] = node(worker_id, "worker", worker.get("label", worker_id), ["split"], max_attempts)
    for worker in graph["workers"]:
        suffix = worker["id"].split("-")[-1]
        verifier_id = f"verify-{suffix}"
        nodes[verifier_id] = node(
            verifier_id,
            "verifier",
            f"Verify {worker.get('label', worker['id'])}",
            [worker["id"]],
            max_rounds,
        )
    verifier_ids = [f"verify-{worker['id'].split('-')[-1]}" for worker in graph["workers"]]
    nodes["consolidate"] = node("consolidate", "consolidate", "Consolidate verified work", verifier_ids, max_attempts)
    nodes["final"] = node("final", "final", "Draft final answer", ["consolidate"], max_attempts)
    nodes["verify-final"] = node(
        "verify-final",
        "verifier",
        "Verify final answer",
        ["final"],
        max_rounds,
    )
    nodes["retrospective"] = node("retrospective", "retrospective", "Measure and learn", ["verify-final"], 1)
    nodes["goal"]["status"] = "passed"
    return nodes


def refresh_state(state: dict[str, Any]) -> None:
    nodes = state["nodes"]
    changed = True
    while changed:
        changed = False
        for node in nodes.values():
            if node["status"] != "blocked":
                continue
            dependency_states = [nodes[dep]["status"] for dep in node["dependencies"]]
            if dependency_states and all(status == "passed" for status in dependency_states):
                node["status"] = "ready"
                changed = True
    if nodes["retrospective"]["status"] == "passed":
        state["status"] = "closed"
    elif any(node["status"] == "failed" for node in nodes.values()):
        state["status"] = "blocked"
    elif nodes["verify-final"]["status"] == "passed":
        state["status"] = "awaiting_close"
    else:
        state["status"] = "running"


def artifact_contract(kind: str) -> dict[str, Any]:
    contracts = {
        "split": {
            "format": "json",
            "required": ["tasks", "coverage_notes"],
            "task_required": ["worker_id", "task", "inputs", "acceptance_criteria", "permitted_writes"],
        },
        "worker": {
            "format": "json",
            "required": [
                "worker_id",
                "task_result",
                "summary",
                "evidence",
                "deliverables",
                "acceptance_checks",
                "open_questions",
            ],
        },
        "verifier": {
            "format": "json",
            "required": ["worker_id", "verdict", "score", "checks", "feedback", "residual_risks"],
            "verdicts": ["pass", "revise"],
        },
        "consolidate": {
            "format": "json",
            "required": [
                "included_workers",
                "excluded_workers",
                "coverage",
                "conflicts",
                "synthesis",
                "final_answer_plan",
            ],
        },
        "final": {
            "format": "markdown",
            "rule": "Use only claims present in verifier-passed worker artifacts and the consolidation artifact.",
        },
        "retrospective": {
            "format": "generated",
            "rule": "Close the run with validated metrics and one unique experiment; do not record this node directly.",
        },
    }
    contract = contracts[kind]
    return {
        **contract,
        "failure_contract": {
            "format": "json",
            "required": ["error", "evidence", "retryable"],
            "rule": "Use this exact schema only when recording --result fail.",
        },
    }


def ready_packets(project: Path, graph: dict[str, Any], state: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    split_node = state["nodes"]["split"]
    if split_node["artifacts"]:
        split_artifact = project_paths(project)["runtime"] / split_node["artifacts"][-1]
        split_data = read_json(split_artifact)
        tasks = {task["worker_id"]: task for task in split_data["tasks"]}
    packets = []
    goal_contract = load_run_goal(project, state)
    for node in state["nodes"].values():
        if node["status"] != "ready":
            continue
        packet: dict[str, Any] = {
            "node_id": node["id"],
            "kind": node["kind"],
            "label": node["label"],
            "attempt": node["attempts"] + 1,
            "max_attempts": node["max_attempts"],
            "goal_contract": goal_contract,
            "artifact_contract": artifact_contract(node["kind"]),
            "active_policies": state["memory_snapshot"]["active_policies"],
            "applied_experiments": state.get("applied_experiments", []),
            "feedback_artifact": node.get("feedback_artifact"),
        }
        if node["kind"] == "worker":
            packet["task"] = tasks.get(node["id"])
            packet["feedback_artifact"] = node.get("feedback_artifact")
        if node["kind"] == "verifier":
            worker_id = node["dependencies"][0]
            worker_node = state["nodes"][worker_id]
            packet["worker_id"] = worker_id
            packet["worker_artifact"] = worker_node["artifacts"][-1] if worker_node["artifacts"] else None
            packet["task"] = tasks.get(worker_id) if worker_id != "final" else {
                "worker_id": "final",
                "task": "Independently verify that the final draft is supported by accepted artifacts and satisfies GOAL.md.",
                "inputs": [worker_node["artifacts"][-1] if worker_node["artifacts"] else None],
                "acceptance_criteria": [
                    "Every material claim is traceable to accepted artifacts",
                    "The answer satisfies the goal and discloses residual gaps",
                    "No new unsupported claim is introduced",
                ],
                "permitted_writes": [],
            }
            packet["verification_lenses"] = graph["verification_lenses"]
            packet["quality_threshold"] = graph["quality_threshold"]
        packets.append(packet)
    return packets


def store_artifact(project: Path, state: dict[str, Any], node: dict[str, Any], source: Path) -> str:
    if not source.is_file():
        raise GraphError(f"Artifact does not exist or is not a file: {source}")
    extension = source.suffix.lower() or ".txt"
    attempt_number = node["attempts"] + 1
    relative = Path("runs") / state["run_id"] / "artifacts" / node["id"] / f"attempt-{attempt_number:02d}{extension}"
    destination = project_paths(project)["runtime"] / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)
    return relative.as_posix()


def require_list(data: dict[str, Any], key: str, artifact: Path) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise GraphError(f"{artifact}: `{key}` must be a list")
    return value


def require_exact_keys(data: dict[str, Any], expected: set[str], artifact: Path, label: str) -> None:
    actual = set(data)
    missing = expected - actual
    unexpected = actual - expected
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing {sorted(missing)}")
        if unexpected:
            details.append(f"unexpected {sorted(unexpected)}")
        raise GraphError(f"{artifact}: {label} has " + " and ".join(details))


def validate_artifact(
    project: Path,
    graph: dict[str, Any],
    state: dict[str, Any],
    node: dict[str, Any],
    artifact: Path,
    result: str,
) -> None:
    kind = node["kind"]
    if result == "fail":
        data = read_json(artifact)
        require_exact_keys(data, {"error", "evidence", "retryable"}, artifact, "failure artifact")
        if not isinstance(data["error"], str) or not data["error"].strip():
            raise GraphError("Failure artifact requires a non-empty `error`")
        if not isinstance(data["evidence"], str) or not data["evidence"].strip():
            raise GraphError("Failure artifact requires non-empty `evidence`")
        if not isinstance(data["retryable"], bool):
            raise GraphError("Failure artifact `retryable` must be boolean")
        return
    if kind == "final":
        if not artifact.read_text(encoding="utf-8").strip():
            raise GraphError("Final artifact cannot be empty")
        return
    data = read_json(artifact)
    worker_ids = [worker["id"] for worker in graph["workers"]]
    if kind == "split":
        require_exact_keys(data, {"tasks", "coverage_notes"}, artifact, "split artifact")
        tasks = require_list(data, "tasks", artifact)
        task_ids = [task.get("worker_id") for task in tasks if isinstance(task, dict)]
        if task_ids != worker_ids:
            raise GraphError(f"Split artifact must contain exactly these ordered worker IDs: {worker_ids}")
        coverage_notes = data.get("coverage_notes")
        if not isinstance(coverage_notes, str) or not coverage_notes.strip():
            raise GraphError("Split artifact requires non-empty `coverage_notes`")
        write_owners: dict[str, str] = {}
        for task in tasks:
            if not isinstance(task, dict):
                raise GraphError("Every split task must be an object")
            require_exact_keys(
                task,
                {"worker_id", "task", "inputs", "acceptance_criteria", "permitted_writes"},
                artifact,
                "split task",
            )
            if not isinstance(task.get("task"), str) or not task["task"].strip():
                raise GraphError("Every split task requires a non-empty `task`")
            inputs = require_list(task, "inputs", artifact)
            criteria = require_list(task, "acceptance_criteria", artifact)
            writes = require_list(task, "permitted_writes", artifact)
            if not criteria or not all(isinstance(item, str) and item.strip() for item in criteria):
                raise GraphError("Every split task requires non-empty string acceptance criteria")
            if not all(isinstance(item, str) and item.strip() for item in inputs + writes):
                raise GraphError("Split inputs and permitted_writes must contain only non-empty strings")
            for target in writes:
                if target in write_owners:
                    raise GraphError(
                        f"Parallel write collision: {task['worker_id']} and {write_owners[target]} both own {target}"
                    )
                write_owners[target] = task["worker_id"]
        return
    if kind == "worker":
        require_exact_keys(
            data,
            {
                "worker_id",
                "task_result",
                "summary",
                "evidence",
                "deliverables",
                "acceptance_checks",
                "open_questions",
            },
            artifact,
            "worker artifact",
        )
        if data.get("worker_id") != node["id"]:
            raise GraphError(f"Worker artifact worker_id must be {node['id']}")
        if result == "pass" and data.get("task_result") != "completed":
            raise GraphError("A passing worker artifact requires task_result `completed`")
        if not isinstance(data.get("summary"), str) or not data["summary"].strip():
            raise GraphError("Worker artifact requires a non-empty `summary`")
        evidence = require_list(data, "evidence", artifact)
        if result == "pass" and not evidence:
            raise GraphError("A passing worker requires at least one evidence item")
        for item in evidence:
            if not isinstance(item, dict) or not isinstance(item.get("claim"), str) or not item["claim"].strip():
                raise GraphError("Every worker evidence item requires a non-empty `claim`")
            require_exact_keys(item, {"claim", "pointer"}, artifact, "worker evidence item")
            if not isinstance(item.get("pointer"), str) or not item["pointer"].strip():
                raise GraphError("Every worker evidence item requires a non-empty `pointer`")
        deliverables = require_list(data, "deliverables", artifact)
        if not all(isinstance(item, str) and item.strip() for item in deliverables):
            raise GraphError("Worker deliverables must contain only non-empty strings")
        checks = require_list(data, "acceptance_checks", artifact)
        if result == "pass" and (not checks or not all(isinstance(check, dict) and check.get("passed") is True for check in checks)):
            raise GraphError("A passing worker requires at least one passing acceptance check and no failed checks")
        split_artifact = project_paths(project)["runtime"] / state["nodes"]["split"]["artifacts"][-1]
        split_data = read_json(split_artifact)
        task = next(task for task in split_data["tasks"] if task["worker_id"] == node["id"])
        expected_criteria = task["acceptance_criteria"]
        actual_criteria = [check.get("criterion") for check in checks]
        if actual_criteria != expected_criteria:
            raise GraphError(f"Worker acceptance checks must exactly match assigned criteria: {expected_criteria}")
        for check in checks:
            if not isinstance(check, dict):
                raise GraphError("Every acceptance check must be an object")
            require_exact_keys(check, {"criterion", "passed", "evidence"}, artifact, "acceptance check")
            if not isinstance(check.get("passed"), bool):
                raise GraphError("Every acceptance check `passed` value must be boolean")
            if not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
                raise GraphError("Every acceptance check requires evidence")
        questions = require_list(data, "open_questions", artifact)
        if not all(isinstance(item, str) and item.strip() for item in questions):
            raise GraphError("Worker open_questions must contain only non-empty strings")
        return
    if kind == "verifier":
        require_exact_keys(
            data,
            {"worker_id", "verdict", "score", "checks", "feedback", "residual_risks"},
            artifact,
            "verifier artifact",
        )
        worker_id = node["dependencies"][0]
        if data.get("worker_id") != worker_id:
            raise GraphError(f"Verifier artifact worker_id must be {worker_id}")
        verdict = data.get("verdict")
        expected = {"pass": "pass", "revise": "revise", "fail": "fail"}[result]
        if verdict != expected:
            raise GraphError(f"Verifier verdict `{verdict}` does not match record result `{result}`")
        score = data.get("score")
        if not isinstance(score, (int, float)) or not 0 <= score <= 1:
            raise GraphError("Verifier score must be from 0 to 1")
        checks = require_list(data, "checks", artifact)
        check_lenses = [check.get("lens") for check in checks if isinstance(check, dict)]
        if len(check_lenses) != len(set(check_lenses)):
            raise GraphError("Verifier lenses must not be duplicated")
        missing = set(graph["verification_lenses"]) - set(check_lenses)
        if missing:
            raise GraphError(f"Verifier artifact is missing lenses: {sorted(missing)}")
        feedback = require_list(data, "feedback", artifact)
        residual_risks = require_list(data, "residual_risks", artifact)
        if not all(isinstance(item, str) and item.strip() for item in feedback + residual_risks):
            raise GraphError("Verifier feedback and residual_risks must contain only non-empty strings")
        for check in checks:
            if not isinstance(check, dict):
                raise GraphError("Every verifier check must be an object")
            require_exact_keys(check, {"lens", "passed", "evidence"}, artifact, "verifier check")
            if not isinstance(check.get("lens"), str) or not check["lens"].strip():
                raise GraphError("Every verifier check requires a non-empty lens")
            if not isinstance(check.get("passed"), bool):
                raise GraphError("Every verifier check `passed` value must be boolean")
            if not isinstance(check.get("evidence"), str) or not check["evidence"].strip():
                raise GraphError("Every verifier check requires independent evidence")
        if result == "revise" and not data["feedback"]:
            raise GraphError("A revise verdict requires actionable feedback")
        if result == "pass":
            if score < graph["quality_threshold"]:
                raise GraphError("Passing verifier score is below graph quality_threshold")
            if not all(check.get("passed") is True for check in checks if check.get("lens") in graph["verification_lenses"]):
                raise GraphError("Every required verification lens must pass")
        return
    if kind == "consolidate":
        require_exact_keys(
            data,
            {"included_workers", "excluded_workers", "coverage", "conflicts", "synthesis", "final_answer_plan"},
            artifact,
            "consolidation artifact",
        )
        included = require_list(data, "included_workers", artifact)
        excluded = require_list(data, "excluded_workers", artifact)
        if not all(isinstance(item, str) and item.strip() for item in included + excluded):
            raise GraphError("Consolidation worker IDs must contain only non-empty strings")
        if set(included) | set(excluded) != set(worker_ids) or set(included) & set(excluded):
            raise GraphError("Consolidation must account for every worker exactly once")
        if not graph.get("allow_partial", False) and (set(included) != set(worker_ids) or excluded):
            raise GraphError("This graph forbids partial fan-in; all workers must be included")
        for worker_id in included:
            verifier_id = f"verify-{worker_id.split('-')[-1]}"
            if state["nodes"][verifier_id]["status"] != "passed":
                raise GraphError(f"Cannot include {worker_id}; {verifier_id} has not passed")
        coverage = require_list(data, "coverage", artifact)
        if not coverage:
            raise GraphError("Consolidation requires non-empty coverage evidence")
        for item in coverage:
            if not isinstance(item, dict) or not all(
                isinstance(item.get(key), str) and item[key].strip() for key in ("criterion", "status", "evidence")
            ):
                raise GraphError("Every coverage item requires criterion, status, and evidence strings")
            require_exact_keys(item, {"criterion", "status", "evidence"}, artifact, "coverage item")
        conflicts = require_list(data, "conflicts", artifact)
        final_answer_plan = require_list(data, "final_answer_plan", artifact)
        if not all(isinstance(item, str) and item.strip() for item in conflicts + final_answer_plan):
            raise GraphError("Consolidation conflicts and final_answer_plan must contain only non-empty strings")
        if not isinstance(data.get("synthesis"), str) or not data["synthesis"].strip():
            raise GraphError("Consolidation requires a non-empty `synthesis`")
        return
    raise GraphError(f"Unsupported artifact kind: {kind}")


def save_state_and_views(project: Path, graph: dict[str, Any], state: dict[str, Any] | None) -> None:
    paths = project_paths(project)
    if state is not None:
        refresh_state(state)
        write_json(paths["state"], state)
    render_todo(project, graph, state)
    render_dashboard(project, graph, state)


def render_todo(project: Path, graph: dict[str, Any], state: dict[str, Any] | None) -> None:
    paths = project_paths(project)
    lines = [
        f"# {graph['name']} — task view",
        "",
        "> Generated by `graphctl.py`; do not hand-edit. State lives in `.graph/state.json`.",
        "",
        "[Open dashboard](.graph/dashboard.html) · [Goal contract](GOAL.md) · [Graph specification](graph.json)",
        "",
    ]
    if state is None:
        lines.extend(["No run has started.", "", "Run `graphctl.py begin <project-dir>`.", ""])
    else:
        lines.extend([f"Run: `{state['run_id']}` · Status: **{state['status']}**", "", "## Nodes", ""])
        for node in state["nodes"].values():
            mark = "x" if node["status"] == "passed" else " "
            lines.append(
                f"- [{mark}] `{node['id']}` — {node['label']} "
                f"(**{node['status']}**, attempts {node['attempts']}/{node['max_attempts']})"
            )
        packets = ready_packets(project, graph, state)
        lines.extend(["", "## Ready now", ""])
        if packets:
            for packet in packets:
                lines.append(f"- `{packet['node_id']}` — {packet['label']} (attempt {packet['attempt']})")
        else:
            lines.append("- Nothing is ready.")
        feedback_nodes = [node for node in state["nodes"].values() if node.get("feedback_artifact")]
        if feedback_nodes:
            lines.extend(["", "## Active verifier feedback", ""])
            for node in feedback_nodes:
                lines.append(f"- `{node['id']}`: `{node['feedback_artifact']}`")
        lines.append("")
    paths["todo"].write_text("\n".join(lines), encoding="utf-8")


def status_class(status: str) -> str:
    return status if status in {"passed", "ready", "blocked", "failed"} else "blocked"


def node_card(node: dict[str, Any]) -> str:
    artifact = node["artifacts"][-1] if node.get("artifacts") else None
    artifact_link = f'<a href="{html.escape(artifact)}">artifact</a>' if artifact else "no artifact"
    return (
        f'<article class="node {status_class(node["status"])}">'
        f'<div class="node-top"><code>{html.escape(node["id"])}</code><span>{html.escape(node["status"])}</span></div>'
        f'<h3>{html.escape(node["label"])}</h3>'
        f'<p>{node["attempts"]}/{node["max_attempts"]} attempts · {artifact_link}</p>'
        "</article>"
    )


def render_dashboard(project: Path, graph: dict[str, Any], state: dict[str, Any] | None) -> None:
    paths = project_paths(project)
    memory = load_memory(project)
    if state is None:
        node_html = '<div class="empty">No run yet. Begin a run to materialize the graph.</div>'
        run_id = "not started"
        run_status = "idle"
    else:
        nodes = state["nodes"]
        workers = [nodes[worker["id"]] for worker in graph["workers"]]
        verifiers = [nodes[f"verify-{worker['id'].split('-')[-1]}"] for worker in graph["workers"]]
        stages = [
            ("Define", [nodes["goal"]]),
            ("Split", [nodes["split"]]),
            ("Workers", workers),
            ("Fresh verifiers", verifiers),
            ("Consolidate", [nodes["consolidate"]]),
            ("Final draft", [nodes["final"]]),
            ("Final verifier", [nodes["verify-final"]]),
            ("Learn", [nodes["retrospective"]]),
        ]
        stage_parts = []
        for index, (label, stage_nodes) in enumerate(stages):
            if index:
                stage_parts.append('<div class="arrow" aria-hidden="true">→</div>')
            cards = "".join(node_card(node) for node in stage_nodes)
            stage_parts.append(f'<section class="stage"><h2>{html.escape(label)}</h2>{cards}</section>')
        node_html = "".join(stage_parts)
        run_id = state["run_id"]
        run_status = state["status"]

    def policy_items(items: list[dict[str, Any]], field: str) -> str:
        if not items:
            return "<li>None yet</li>"
        return "".join(f"<li>{html.escape(str(item.get(field, item.get('change', item.get('id', 'entry')))))}</li>" for item in items[-8:])

    history_rows = []
    if paths["runs"].exists():
        for directory in sorted((entry for entry in paths["runs"].iterdir() if entry.is_dir()), reverse=True)[:10]:
            manifest_path = directory / "manifest.json"
            if not manifest_path.exists():
                continue
            manifest = read_json(manifest_path)
            history_rows.append(
                f"<tr><td><code>{html.escape(directory.name)}</code></td>"
                f"<td>{html.escape(str(manifest.get('status', 'unknown')))}</td>"
                f"<td>{html.escape(str(manifest.get('started_at', '')))}</td></tr>"
            )
    rows = "".join(history_rows) or '<tr><td colspan="3">No completed history</td></tr>'
    goal_summary = html.escape(graph.get("goal_summary", "See GOAL.md"))
    generated = utc_now()
    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(graph['name'])} · Agent Graph</title>
<style>
:root {{ color-scheme: dark; --bg:#0b1020; --panel:#131a2c; --line:#2b3654; --ink:#eef3ff; --muted:#9ba9c7; --blue:#6ea8fe; --green:#54d39a; --amber:#f5c451; --red:#ff747d; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:Inter,ui-sans-serif,system-ui,sans-serif; background:radial-gradient(circle at 20% -10%,#203565 0,transparent 35%),var(--bg); color:var(--ink); }}
main {{ max-width:1600px; margin:auto; padding:32px; }} a {{ color:var(--blue); }} code {{ color:#c8d8ff; }}
.eyebrow {{ color:var(--blue); text-transform:uppercase; letter-spacing:.14em; font-size:.75rem; font-weight:800; }} h1 {{ margin:.35rem 0; font-size:clamp(2rem,5vw,4rem); }}
.lede {{ max-width:850px; color:var(--muted); font-size:1.05rem; }} .meta {{ display:flex; flex-wrap:wrap; gap:10px; margin:22px 0; }} .pill {{ background:#17223a; border:1px solid var(--line); border-radius:999px; padding:8px 12px; }}
.links {{ display:flex; gap:16px; flex-wrap:wrap; margin:20px 0 34px; }} .graph {{ display:flex; align-items:stretch; gap:12px; overflow-x:auto; padding:10px 2px 28px; }}
.stage {{ min-width:190px; flex:1; background:rgba(19,26,44,.82); border:1px solid var(--line); border-radius:18px; padding:14px; }} .stage h2 {{ margin:0 0 12px; color:var(--muted); font-size:.78rem; text-transform:uppercase; letter-spacing:.1em; }}
.arrow {{ align-self:center; color:var(--blue); font-size:1.8rem; }} .node {{ border:1px solid var(--line); border-left:4px solid var(--muted); border-radius:12px; padding:12px; background:#0f1628; margin-bottom:10px; }}
.node:last-child {{ margin-bottom:0; }} .node.passed {{ border-left-color:var(--green); }} .node.ready {{ border-left-color:var(--amber); box-shadow:0 0 0 1px rgba(245,196,81,.18); }} .node.failed {{ border-left-color:var(--red); }}
.node-top {{ display:flex; justify-content:space-between; gap:8px; color:var(--muted); font-size:.72rem; }} .node h3 {{ font-size:.95rem; margin:10px 0 6px; }} .node p {{ margin:0; color:var(--muted); font-size:.75rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; margin-top:22px; }} .panel {{ background:rgba(19,26,44,.82); border:1px solid var(--line); border-radius:18px; padding:18px; }} .panel h2 {{ margin-top:0; }} .panel li {{ margin:.55rem 0; color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; }} th,td {{ text-align:left; border-bottom:1px solid var(--line); padding:9px; color:var(--muted); }} .empty {{ padding:32px; border:1px dashed var(--line); border-radius:16px; color:var(--muted); }} footer {{ color:var(--muted); margin-top:26px; font-size:.8rem; }}
@media (max-width:760px) {{ main {{ padding:20px; }} .arrow {{ transform:rotate(90deg); }} .graph {{ flex-direction:column; }} }}
</style>
</head>
<body><main>
<div class="eyebrow">Persistent agent control plane</div>
<h1>{html.escape(graph['name'])}</h1>
<p class="lede">{goal_summary}</p>
<div class="meta"><span class="pill">Run <code>{html.escape(run_id)}</code></span><span class="pill">Status <strong>{html.escape(run_status)}</strong></span><span class="pill">Workers {len(graph['workers'])}</span><span class="pill">Quality ≥ {graph['quality_threshold']:.0%}</span></div>
<nav class="links"><a href="../GOAL.md">Goal contract</a><a href="../TODO.md">Current TODO</a><a href="../graph.json">Graph JSON</a><a href="templates/metrics.json">Metrics template</a><a href="templates/experiment.json">Experiment template</a></nav>
<div class="graph" aria-label="Agent execution graph">{node_html}</div>
<div class="grid">
<section class="panel"><h2>Active policies</h2><ul>{policy_items(memory['active_policies'], 'policy')}</ul></section>
<section class="panel"><h2>Pending experiments</h2><ul>{policy_items(memory['pending_experiments'], 'change')}</ul></section>
<section class="panel"><h2>Rejected experiments</h2><ul>{policy_items(memory['rejected_experiments'], 'change')}</ul></section>
</div>
<section class="panel" style="margin-top:16px"><h2>Run history</h2><table><thead><tr><th>Run</th><th>Status</th><th>Started</th></tr></thead><tbody>{rows}</tbody></table></section>
<footer>Generated {generated}. Views are disposable; JSON state and append-only events are authoritative.</footer>
</main></body></html>"""
    paths["dashboard"].write_text(document, encoding="utf-8")


@locked_command
def cmd_init(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    paths = project_paths(project)
    project.mkdir(parents=True, exist_ok=True)
    runtime_payload = paths["runtime"].exists() and any(
        child.name != ".mutation.lock" for child in paths["runtime"].iterdir()
    )
    protected = [paths["goal"], paths["graph"], paths["todo"]]
    if runtime_payload:
        protected.append(paths["runtime"])
    existing = [path for path in protected if path.exists()]
    if existing:
        raise GraphError(f"Refusing to overwrite an existing graph project: {', '.join(map(str, existing))}")
    if not 2 <= args.workers <= 8:
        raise GraphError("Initial worker count must be from 2 to 8")
    template_dir = Path(__file__).resolve().parent.parent / "assets" / "project-template"
    goal_template = (template_dir / "GOAL.md").read_text(encoding="utf-8")
    paths["goal"].write_text(goal_template.replace("{{NAME}}", args.name).replace("{{GOAL}}", args.goal), encoding="utf-8")
    graph = {
        "schema_version": SCHEMA_VERSION,
        "name": args.name,
        "goal_file": "GOAL.md",
        "goal_summary": args.goal,
        "topology": {
            "id": TOPOLOGY_ID,
            "stages": [
                "goal",
                "split",
                "workers",
                "verifiers",
                "consolidate",
                "final",
                "final-verifier",
                "retrospective",
            ],
            "feedback_edge": "verifier -> paired worker",
            "next_run_edge": "retrospective -> next goal",
        },
        "workers": [
            {"id": f"worker-{index:02d}", "label": f"Worker {index}"}
            for index in range(1, args.workers + 1)
        ],
        "verification_lenses": ["correctness", "completeness", "evidence"],
        "quality_threshold": 0.8,
        "allow_partial": False,
        "limits": {"max_workers": 8, "max_attempts_per_node": 3, "max_rounds": 3},
    }
    write_json(paths["graph"], graph)
    paths["runs"].mkdir(parents=True)
    paths["templates"].mkdir(parents=True)
    shutil.copy2(template_dir / "metrics.json", paths["templates"] / "metrics.json")
    shutil.copy2(template_dir / "experiment.json", paths["templates"] / "experiment.json")
    memory = {
        "schema_version": SCHEMA_VERSION,
        "project_name": args.name,
        "active_policies": [],
        "pending_experiments": [],
        "rejected_experiments": [],
        "evaluations": [],
        "updated_at": utc_now(),
    }
    write_json(paths["memory"], memory)
    save_state_and_views(project, graph, None)
    emit({"project": str(project), "status": "initialized", "next": "Refine GOAL.md, run doctor, then begin."})


def next_run_id(paths: dict[str, Path]) -> str:
    base = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    candidate = base
    counter = 2
    while (paths["runs"] / candidate).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


@locked_command
def cmd_begin(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    paths = project_paths(project)
    graph = load_graph(project)
    old_state = load_state(project, required=False)
    if old_state and old_state.get("status") in {"running", "awaiting_close"}:
        raise GraphError(f"Run {old_state['run_id']} is still {old_state['status']}")
    goal_text = paths["goal"].read_text(encoding="utf-8")
    if "Define a 0-100 rubric before the first run" in goal_text:
        raise GraphError("GOAL.md still contains the undefined objective-score instruction. Replace it with a concrete rubric before beginning.")
    memory = load_memory(project)
    goal_sha256 = hashlib.sha256(goal_text.encode("utf-8")).hexdigest()
    pending = memory["pending_experiments"]
    applied_experiments = []
    selected_pending = []
    if pending:
        if args.abandon_pending:
            abandoned_at = utc_now()
            for candidate in pending:
                memory["rejected_experiments"].append(
                    {
                        **candidate,
                        "abandoned_at": abandoned_at,
                        "evaluation": {"promoted": False, "reason": args.abandon_pending},
                    }
                )
            memory["pending_experiments"] = []
            memory["updated_at"] = abandoned_at
            write_json(paths["memory"], memory)
        else:
            if not args.apply_experiment:
                raise GraphError(
                    f"A pending experiment must be explicitly applied: use --apply-experiment {pending[0]['id']} "
                    "--application-note '<how the change is active>', or --abandon-pending '<reason>'"
                )
            candidate = next((item for item in pending if item["id"] == args.apply_experiment), None)
            if candidate is None:
                raise GraphError(f"Unknown pending experiment: {args.apply_experiment}")
            if not args.application_note or not args.application_note.strip():
                raise GraphError("--application-note is required when applying an experiment")
            baseline_goal = candidate.get("baseline_goal_sha256")
            if baseline_goal and baseline_goal != goal_sha256:
                raise GraphError(
                    "GOAL.md changed since the experiment baseline; comparability is broken. "
                    "Restore the goal or use --abandon-pending with a reason."
                )
            selected_pending = [candidate]
            applied_experiments = [
                {
                    "id": candidate["id"],
                    "change": candidate["experiment"]["change"],
                    "application_note": args.application_note.strip(),
                }
            ]
    elif args.apply_experiment or args.abandon_pending or args.application_note:
        raise GraphError("There is no pending experiment to apply or abandon")
    run_id = next_run_id(paths)
    nodes = build_nodes(graph)
    state = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": "running",
        "started_at": utc_now(),
        "closed_at": None,
        "nodes": nodes,
        "revision_count": 0,
        "goal_sha256": goal_sha256,
        "graph_sha256": canonical_json_hash(graph),
        "applied_experiments": applied_experiments,
        "memory_snapshot": {
            "active_policies": memory["active_policies"],
            "pending_experiments": selected_pending,
        },
    }
    refresh_state(state)
    directory = paths["runs"] / run_id
    (directory / "artifacts").mkdir(parents=True)
    (directory / "GOAL.md").write_text(goal_text, encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "status": "running",
        "started_at": state["started_at"],
        "closed_at": None,
        "goal_sha256": goal_sha256,
        "graph_sha256": state["graph_sha256"],
        "graph_snapshot": graph,
        "memory_snapshot": state["memory_snapshot"],
        "applied_experiments": applied_experiments,
    }
    write_json(directory / "manifest.json", manifest)
    save_state_and_views(project, graph, state)
    event(project, state, "run_started", goal_sha256=manifest["goal_sha256"])
    event(project, state, "node_passed", node_id="goal", attempt=1, artifact="GOAL.md")
    emit(
        {
            "run_id": run_id,
            "status": state["status"],
            "memory_snapshot": state["memory_snapshot"],
            "ready": ready_packets(project, graph, state),
        }
    )


def cmd_ready(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    state = load_state(project)
    graph = load_run_graph(project, state)
    emit(
        {
            "run_id": state["run_id"],
            "status": state["status"],
            "memory_snapshot": state["memory_snapshot"],
            "ready": ready_packets(project, graph, state),
        }
    )


@locked_command
def cmd_record(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    state = load_state(project)
    graph = load_run_graph(project, state)
    if state["status"] not in {"running", "awaiting_close"}:
        raise GraphError(f"Cannot record into a run with status {state['status']}")
    node = state["nodes"].get(args.node_id)
    if node is None:
        raise GraphError(f"Unknown node: {args.node_id}")
    if node["status"] != "ready":
        raise GraphError(f"Node {args.node_id} is {node['status']}, not ready")
    if args.result == "revise" and node["kind"] != "verifier":
        raise GraphError("Only verifier nodes may return `revise`")
    if not args.artifact:
        raise GraphError("Every recorded node result requires --artifact")
    artifact = Path(args.artifact).resolve()
    validate_artifact(project, graph, state, node, artifact, args.result)
    stored = store_artifact(project, state, node, artifact)
    node["attempts"] += 1
    node["artifacts"].append(stored)
    node["last_note"] = args.note

    if args.result == "pass":
        node["status"] = "passed"
        node["feedback_artifact"] = None
        event_type = "node_passed"
        event_payload = {"node_id": node["id"], "attempt": node["attempts"], "artifact": stored, "note": args.note}
    elif args.result == "revise":
        worker_id = node["dependencies"][0]
        worker = state["nodes"][worker_id]
        state["revision_count"] += 1
        if node["attempts"] >= node["max_attempts"] or worker["attempts"] >= worker["max_attempts"]:
            node["status"] = "failed"
            worker["status"] = "failed"
            event_type = "revision_cap_exhausted"
        else:
            node["status"] = "blocked"
            worker["status"] = "ready"
            worker["feedback_artifact"] = stored
            event_type = "revision_requested"
        event_payload = {"node_id": node["id"], "worker_id": worker_id, "artifact": stored}
    else:
        failure_data = read_json(artifact)
        if failure_data["retryable"] is False or node["attempts"] >= node["max_attempts"]:
            node["status"] = "failed"
            event_type = "node_failed_terminal"
        else:
            node["status"] = "ready"
            event_type = "node_failed_retryable"
        event_payload = {"node_id": node["id"], "attempt": node["attempts"], "artifact": stored, "note": args.note}

    save_state_and_views(project, graph, state)
    event(project, state, event_type, **event_payload)
    emit(
        {
            "run_id": state["run_id"],
            "node_id": node["id"],
            "node_status": node["status"],
            "run_status": state["status"],
            "artifact": stored,
            "ready": ready_packets(project, graph, state),
        }
    )


def validate_metrics(metrics: dict[str, Any], state: dict[str, Any], graph: dict[str, Any]) -> None:
    unknown = set(metrics) - METRIC_KEYS
    if unknown:
        raise GraphError(f"Unknown metrics fields: {sorted(unknown)}")
    for key in ("objective_score", "worker_success_rate", "rework_count", "quality_gate_passed", "notes"):
        if key not in metrics:
            raise GraphError(f"Metrics require `{key}`")
    if not isinstance(metrics["objective_score"], (int, float)) or not 0 <= metrics["objective_score"] <= 100:
        raise GraphError("objective_score must be from 0 to 100")
    if not isinstance(metrics["quality_gate_passed"], bool):
        raise GraphError("quality_gate_passed must be boolean")
    if metrics["quality_gate_passed"] is not True:
        raise GraphError("A run with a passed final node must close with quality_gate_passed true")
    if not isinstance(metrics["worker_success_rate"], (int, float)) or not 0 <= metrics["worker_success_rate"] <= 1:
        raise GraphError("worker_success_rate must be from 0 to 1")
    worker_ids = [worker["id"] for worker in graph["workers"]]
    computed_rate = sum(state["nodes"][worker_id]["status"] == "passed" for worker_id in worker_ids) / len(worker_ids)
    if abs(metrics["worker_success_rate"] - computed_rate) > 1e-9:
        raise GraphError(f"worker_success_rate must equal computed rate {computed_rate}")
    if not isinstance(metrics["rework_count"], int) or metrics["rework_count"] < 0:
        raise GraphError("rework_count must be a non-negative integer")
    if metrics["rework_count"] != state["revision_count"]:
        raise GraphError(f"rework_count must equal recorded revision count {state['revision_count']}")
    for key in ("wall_time_seconds", "cost_units"):
        if key in metrics and metrics[key] is not None and (
            not isinstance(metrics[key], (int, float)) or metrics[key] < 0
        ):
            raise GraphError(f"{key} must be non-negative when present")
    if not isinstance(metrics["notes"], str) or not metrics["notes"].strip():
        raise GraphError("metrics.notes must explain the measurement")


def validate_experiment(experiment: dict[str, Any], metrics: dict[str, Any]) -> None:
    required = {
        "observation",
        "hypothesis",
        "change",
        "target_metric",
        "expected_direction",
        "minimum_delta",
        "guardrails",
    }
    missing = required - set(experiment)
    if missing:
        raise GraphError(f"Experiment is missing fields: {sorted(missing)}")
    for key in ("observation", "hypothesis", "change"):
        if not isinstance(experiment[key], str) or not experiment[key].strip():
            raise GraphError(f"Experiment `{key}` must be a non-empty string")
    target = experiment["target_metric"]
    if target not in metrics or not isinstance(metrics[target], (int, float)) or isinstance(metrics[target], bool):
        raise GraphError("Experiment target_metric must name a numeric metric in metrics.json")
    if experiment["expected_direction"] not in {"increase", "decrease"}:
        raise GraphError("expected_direction must be `increase` or `decrease`")
    if not isinstance(experiment["minimum_delta"], (int, float)) or experiment["minimum_delta"] < 0:
        raise GraphError("minimum_delta must be non-negative")
    if not isinstance(experiment["guardrails"], list):
        raise GraphError("guardrails must be a list")
    for guardrail in experiment["guardrails"]:
        if not isinstance(guardrail, dict) or guardrail.get("metric") not in metrics:
            raise GraphError("Every guardrail must name a metric in metrics.json")
        if guardrail.get("rule") not in {"not_decrease", "not_increase", "must_equal"}:
            raise GraphError("Unsupported guardrail rule")
        if guardrail["rule"] == "must_equal" and "value" not in guardrail:
            raise GraphError("must_equal guardrails require `value`")
        tolerance = guardrail.get("tolerance", 0)
        if not isinstance(tolerance, (int, float)) or tolerance < 0:
            raise GraphError("Guardrail tolerance must be non-negative")


def change_fingerprint(change: str) -> str:
    normalized = " ".join(change.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def known_change_fingerprints(memory: dict[str, Any]) -> set[str]:
    fingerprints = set()
    for item in memory["active_policies"]:
        change = item.get("policy")
        if isinstance(change, str):
            fingerprints.add(item.get("fingerprint") or change_fingerprint(change))
    for key in ("pending_experiments", "rejected_experiments"):
        for item in memory[key]:
            change = item.get("change") or (item.get("experiment") or {}).get("change")
            if isinstance(change, str):
                fingerprints.add(item.get("fingerprint") or change_fingerprint(change))
    return fingerprints


def evaluate_candidate(
    candidate: dict[str, Any],
    current_metrics: dict[str, Any],
    current_run: str,
    current_goal_sha256: str,
    application_note: str,
) -> dict[str, Any]:
    experiment = candidate["experiment"]
    baseline = candidate["baseline_metrics"]
    target = experiment["target_metric"]
    if candidate.get("baseline_goal_sha256") != current_goal_sha256:
        return {
            "id": candidate["id"],
            "promoted": False,
            "reason": "GOAL.md changed; objective metrics are not comparable",
            "baseline_run": candidate["baseline_run"],
            "current_run": current_run,
            "application_note": application_note,
        }
    before = baseline[target]
    after = current_metrics.get(target)
    if not isinstance(after, (int, float)) or isinstance(after, bool):
        return {"id": candidate["id"], "promoted": False, "reason": f"Current metric `{target}` is unavailable"}
    direction = experiment["expected_direction"]
    observed_delta = after - before
    signed_gain = observed_delta if direction == "increase" else -observed_delta
    target_passed = signed_gain >= experiment["minimum_delta"]
    guardrail_results = []
    for guardrail in experiment["guardrails"]:
        metric = guardrail["metric"]
        rule = guardrail["rule"]
        tolerance = guardrail.get("tolerance", 0)
        old = baseline.get(metric)
        new = current_metrics.get(metric)
        if rule == "must_equal":
            passed = new == guardrail["value"]
        elif not isinstance(old, (int, float)) or not isinstance(new, (int, float)):
            passed = False
        elif rule == "not_decrease":
            passed = new + tolerance >= old
        else:
            passed = new - tolerance <= old
        guardrail_results.append({"metric": metric, "rule": rule, "before": old, "after": new, "passed": passed})
    promoted = target_passed and all(result["passed"] for result in guardrail_results)
    return {
        "id": candidate["id"],
        "promoted": promoted,
        "baseline_run": candidate["baseline_run"],
        "current_run": current_run,
        "target_metric": target,
        "expected_direction": direction,
        "before": before,
        "after": after,
        "observed_delta": observed_delta,
        "minimum_delta": experiment["minimum_delta"],
        "target_passed": target_passed,
        "guardrails": guardrail_results,
        "application_note": application_note,
    }


@locked_command
def cmd_close(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    paths = project_paths(project)
    state = load_state(project)
    graph = load_run_graph(project, state)
    if state["status"] != "awaiting_close" or state["nodes"]["verify-final"]["status"] != "passed":
        raise GraphError("The fresh final verifier must pass before closing the run")
    metrics = read_json(Path(args.metrics).resolve())
    experiment = read_json(Path(args.experiment).resolve())
    validate_metrics(metrics, state, graph)
    validate_experiment(experiment, metrics)
    memory = load_memory(project)
    new_fingerprint = change_fingerprint(experiment["change"])
    if new_fingerprint in known_change_fingerprints(memory):
        raise GraphError("This experiment change already exists in active, pending, or rejected memory; propose a new bounded change")
    evaluations = []
    snapshot_ids = {candidate["id"] for candidate in state["memory_snapshot"]["pending_experiments"]}
    applications = {item["id"]: item["application_note"] for item in state.get("applied_experiments", [])}
    remaining_pending = []
    for candidate in memory["pending_experiments"]:
        if candidate["id"] not in snapshot_ids:
            remaining_pending.append(candidate)
            continue
        if candidate["id"] not in applications:
            raise GraphError(f"Pending experiment {candidate['id']} was not marked applied for this run")
        evaluation = evaluate_candidate(
            candidate,
            metrics,
            state["run_id"],
            state["goal_sha256"],
            applications[candidate["id"]],
        )
        evaluations.append(evaluation)
        evaluated = {**candidate, "evaluation": evaluation, "evaluated_at": utc_now()}
        if evaluation["promoted"]:
            memory["active_policies"].append(
                {
                    "id": candidate["id"],
                    "policy": candidate["experiment"]["change"],
                    "hypothesis": candidate["experiment"]["hypothesis"],
                    "fingerprint": candidate.get("fingerprint") or change_fingerprint(candidate["experiment"]["change"]),
                    "promoted_at": utc_now(),
                    "evidence": evaluation,
                }
            )
        else:
            memory["rejected_experiments"].append(evaluated)
        memory["evaluations"].append(evaluation)
    memory["pending_experiments"] = remaining_pending
    candidate_id = f"experiment-{state['run_id']}"
    new_candidate = {
        "id": candidate_id,
        "baseline_run": state["run_id"],
        "baseline_metrics": metrics,
        "baseline_goal_sha256": state["goal_sha256"],
        "experiment": experiment,
        "change": experiment["change"],
        "fingerprint": new_fingerprint,
        "created_at": utc_now(),
    }
    memory["pending_experiments"].append(new_candidate)
    memory["updated_at"] = utc_now()
    write_json(paths["memory"], memory)

    directory = run_dir(project, state)
    write_json(directory / "metrics.json", metrics)
    write_json(directory / "experiment.json", experiment)
    retrospective = {
        "run_id": state["run_id"],
        "closed_at": utc_now(),
        "metrics": metrics,
        "evaluations": evaluations,
        "next_experiment_id": candidate_id,
    }
    write_json(directory / "retrospective.json", retrospective)
    retrospective_node = state["nodes"]["retrospective"]
    retrospective_node["attempts"] = 1
    retrospective_node["status"] = "passed"
    retrospective_node["artifacts"].append(
        (Path("runs") / state["run_id"] / "retrospective.json").as_posix()
    )
    state["closed_at"] = retrospective["closed_at"]
    refresh_state(state)
    manifest = read_json(directory / "manifest.json")
    manifest["status"] = "closed"
    manifest["closed_at"] = state["closed_at"]
    manifest["objective_score"] = metrics["objective_score"]
    manifest["improvements_promoted"] = sum(evaluation["promoted"] for evaluation in evaluations)
    write_json(directory / "manifest.json", manifest)
    save_state_and_views(project, graph, state)
    event(project, state, "run_closed", metrics=metrics, evaluations=evaluations, next_experiment_id=candidate_id)
    emit(
        {
            "run_id": state["run_id"],
            "status": state["status"],
            "evaluations": evaluations,
            "promoted_count": sum(evaluation["promoted"] for evaluation in evaluations),
            "next_experiment": new_candidate,
        }
    )


def cmd_status(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    state = load_state(project, required=False)
    memory = load_memory(project)
    if state is None:
        emit({"project": str(project), "status": "idle", "active_policies": len(memory["active_policies"])})
        return
    graph = load_run_graph(project, state)
    node_counts: dict[str, int] = {}
    for node in state["nodes"].values():
        node_counts[node["status"]] = node_counts.get(node["status"], 0) + 1
    emit(
        {
            "project": str(project),
            "graph": graph["name"],
            "run_id": state["run_id"],
            "status": state["status"],
            "nodes": node_counts,
            "revision_count": state["revision_count"],
            "ready": ready_packets(project, graph, state),
            "memory": {
                "active_policies": len(memory["active_policies"]),
                "pending_experiments": len(memory["pending_experiments"]),
                "rejected_experiments": len(memory["rejected_experiments"]),
            },
        }
    )


def cmd_history(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    paths = project_paths(project)
    load_graph(project)
    runs = []
    if paths["runs"].exists():
        for directory in sorted((entry for entry in paths["runs"].iterdir() if entry.is_dir())):
            manifest_path = directory / "manifest.json"
            if manifest_path.exists():
                manifest = read_json(manifest_path)
                runs.append(
                    {
                        "run_id": directory.name,
                        "status": manifest.get("status"),
                        "started_at": manifest.get("started_at"),
                        "closed_at": manifest.get("closed_at"),
                        "objective_score": manifest.get("objective_score"),
                        "improvements_promoted": manifest.get("improvements_promoted", 0),
                    }
                )
    emit({"project": str(project), "runs": runs})


@locked_command
def cmd_recover(args: argparse.Namespace) -> None:
    """Seal legacy snapshots and rebuild a trustworthy ledger checkpoint without discarding evidence."""

    project = Path(args.project).resolve()
    state = load_state(project)
    directory = run_dir(project, state)
    manifest_path = directory / "manifest.json"
    manifest = read_json(manifest_path)
    graph = manifest.get("graph_snapshot")
    if not isinstance(graph, dict):
        raise GraphError("Cannot recover a run without a valid graph snapshot")
    validate_graph(graph)
    actual_graph_hash = canonical_json_hash(graph)
    recorded_graph_hash = manifest.get("graph_sha256")
    sealed_legacy_snapshot = False
    if recorded_graph_hash is None:
        manifest["graph_sha256"] = actual_graph_hash
        manifest["graph_sealed_at"] = utc_now()
        manifest["graph_seal_reason"] = args.reason
        write_json(manifest_path, manifest)
        sealed_legacy_snapshot = True
    elif recorded_graph_hash != actual_graph_hash:
        raise GraphError("Refusing recovery because the graph snapshot hash does not match the manifest")
    state_graph_hash = state.get("graph_sha256")
    if state_graph_hash is None:
        state["graph_sha256"] = actual_graph_hash
        sealed_legacy_snapshot = True
    elif state_graph_hash != actual_graph_hash:
        raise GraphError("Refusing recovery because the graph snapshot hash does not match state")

    ledger = directory / "events.jsonl"
    quarantine = None
    malformed = False
    if ledger.exists():
        try:
            entries = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
            malformed = not all(isinstance(item, dict) and item.get("at") and item.get("type") for item in entries)
        except json.JSONDecodeError:
            malformed = True
    if malformed:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        quarantine = directory / f"events.corrupt-{stamp}.jsonl"
        os.replace(ledger, quarantine)

    save_state_and_views(project, graph, state)
    checkpoint = {
        "at": utc_now(),
        "type": "recovery_checkpoint",
        "run_id": state["run_id"],
        "reason": args.reason,
        "state_sha256": canonical_json_hash(state),
        "manifest_sha256": canonical_json_hash(read_json(manifest_path)),
        "sealed_legacy_snapshot": sealed_legacy_snapshot,
        "quarantined_ledger": quarantine.name if quarantine else None,
    }
    append_event(ledger, checkpoint)
    emit(
        {
            "run_id": state["run_id"],
            "status": state["status"],
            "recovery_checkpoint": str(ledger),
            "quarantined_ledger": str(quarantine) if quarantine else None,
            "sealed_legacy_snapshot": sealed_legacy_snapshot,
            "ready": ready_packets(project, graph, state),
        }
    )


def validate_state_consistency(project: Path, graph: dict[str, Any], state: dict[str, Any]) -> list[str]:
    errors = []
    expected = build_nodes(graph)
    expected_nodes = set(expected)
    actual_nodes = set(state.get("nodes", {}))
    if expected_nodes != actual_nodes:
        errors.append(f"State node set differs from graph: expected {sorted(expected_nodes)}, got {sorted(actual_nodes)}")
    for node_id, node in state.get("nodes", {}).items():
        expected_node = expected.get(node_id)
        if expected_node is None:
            continue
        if node.get("status") not in {"blocked", "ready", "passed", "failed"}:
            errors.append(f"{node_id} has invalid status {node.get('status')}")
        if node.get("dependencies") != expected_node["dependencies"]:
            errors.append(f"{node_id} dependencies differ from the run graph snapshot")
        attempts = node.get("attempts")
        maximum = node.get("max_attempts")
        if maximum != expected_node["max_attempts"]:
            errors.append(f"{node_id} max_attempts differs from the run graph snapshot")
        if not isinstance(attempts, int) or attempts < 0 or not isinstance(maximum, int) or attempts > maximum:
            errors.append(f"{node_id} attempts {attempts} exceed valid range 0..{maximum}")
        artifacts = node.get("artifacts")
        if not isinstance(artifacts, list):
            errors.append(f"{node_id} artifacts must be a list")
        else:
            for artifact in artifacts:
                if not isinstance(artifact, str) or not (project_paths(project)["runtime"] / artifact).is_file():
                    errors.append(f"{node_id} references missing artifact {artifact}")
            if node.get("status") == "passed" and node_id != "goal" and not artifacts:
                errors.append(f"{node_id} is passed but has no artifact")
        for dependency in node.get("dependencies", []):
            if dependency not in actual_nodes:
                errors.append(f"{node_id} references missing dependency {dependency}")
        dependency_states = [state["nodes"][dep]["status"] for dep in node.get("dependencies", []) if dep in actual_nodes]
        if node.get("status") == "ready" and dependency_states and not all(status == "passed" for status in dependency_states):
            errors.append(f"{node_id} is ready before all dependencies passed")
        if node.get("status") == "blocked" and dependency_states and all(status == "passed" for status in dependency_states):
            errors.append(f"{node_id} is blocked even though all dependencies passed")
    recorded_revisions = 0
    for node in state.get("nodes", {}).values():
        if node.get("kind") != "verifier":
            continue
        for artifact in node.get("artifacts", []):
            if not isinstance(artifact, str) or not artifact.endswith(".json"):
                continue
            try:
                if read_json(project_paths(project)["runtime"] / artifact).get("verdict") == "revise":
                    recorded_revisions += 1
            except GraphError:
                continue
    if state.get("revision_count") != recorded_revisions:
        errors.append("revision_count does not match stored verifier revision artifacts")
    expected_status = "running"
    if state.get("nodes", {}).get("retrospective", {}).get("status") == "passed":
        expected_status = "closed"
    elif any(node.get("status") == "failed" for node in state.get("nodes", {}).values()):
        expected_status = "blocked"
    elif state.get("nodes", {}).get("verify-final", {}).get("status") == "passed":
        expected_status = "awaiting_close"
    if state.get("status") != expected_status:
        errors.append(f"Run status {state.get('status')} should be {expected_status}")
    return errors


@locked_command
def cmd_doctor(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    paths = project_paths(project)
    checks = []
    errors = []
    try:
        graph = load_graph(project)
        checks.append("graph.json schema")
    except GraphError as exc:
        errors.append(str(exc))
        emit({"ok": False, "checks": checks, "errors": errors})
        raise GraphError("Doctor found errors")
    if paths["goal"].is_file():
        checks.append("GOAL.md exists")
    else:
        errors.append("GOAL.md is missing")
    try:
        load_memory(project)
        checks.append("memory.json schema")
    except GraphError as exc:
        errors.append(str(exc))
    state = load_state(project, required=False)
    if state:
        try:
            run_graph_snapshot = load_run_graph(project, state)
            checks.append("immutable run graph snapshot")
        except GraphError as exc:
            errors.append(str(exc))
            run_graph_snapshot = graph
        state_errors = validate_state_consistency(project, run_graph_snapshot, state)
        errors.extend(state_errors)
        if not state_errors:
            checks.append("state.json node consistency")
        directory = run_dir(project, state)
        manifest_path = directory / "manifest.json"
        goal_snapshot = directory / "GOAL.md"
        if manifest_path.is_file():
            manifest = read_json(manifest_path)
            if manifest.get("run_id") != state.get("run_id"):
                errors.append("Manifest run_id differs from state")
            expected_manifest_status = "closed" if state.get("status") == "closed" else "running"
            if manifest.get("status") != expected_manifest_status:
                errors.append(
                    f"Manifest status {manifest.get('status')} should be {expected_manifest_status} for state {state.get('status')}"
                )
            if not goal_snapshot.is_file():
                errors.append("Run GOAL.md snapshot is missing")
            elif hashlib.sha256(goal_snapshot.read_bytes()).hexdigest() != manifest.get("goal_sha256"):
                errors.append("Run GOAL.md snapshot hash differs from manifest")
        else:
            errors.append("Current run manifest is missing")
        ledger = directory / "events.jsonl"
        if directory.is_dir() and ledger.is_file():
            try:
                events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
                if not events or not all(isinstance(item, dict) and item.get("at") and item.get("type") for item in events):
                    errors.append("Current run ledger contains malformed events")
                else:
                    checks.append("current run ledger")
            except json.JSONDecodeError:
                errors.append("Current run ledger contains invalid JSON")
        else:
            errors.append("Current run directory or event ledger is missing")
        graph = run_graph_snapshot
    save_state_and_views(project, graph, state)
    if paths["todo"].is_file() and paths["dashboard"].is_file():
        checks.append("generated TODO and dashboard")
    emit({"ok": not errors, "checks": checks, "errors": errors})
    if errors:
        raise GraphError("Doctor found errors")


@locked_command
def cmd_render(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    state = load_state(project, required=False)
    graph = load_run_graph(project, state) if state else load_graph(project)
    save_state_and_views(project, graph, state)
    emit({"todo": str(project_paths(project)["todo"]), "dashboard": str(project_paths(project)["dashboard"])})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a graph project without overwriting existing state")
    init_parser.add_argument("project")
    init_parser.add_argument("--name", required=True)
    init_parser.add_argument("--goal", required=True)
    init_parser.add_argument("--workers", type=int, default=3)
    init_parser.set_defaults(func=cmd_init)

    command_parsers: dict[str, argparse.ArgumentParser] = {}
    for name, function, help_text in (
        ("begin", cmd_begin, "Begin a new run"),
        ("ready", cmd_ready, "Show nodes ready to dispatch"),
        ("status", cmd_status, "Show current state"),
        ("history", cmd_history, "List run history"),
        ("doctor", cmd_doctor, "Validate graph, state, and generated views"),
        ("render", cmd_render, "Regenerate TODO.md and dashboard.html"),
        ("recover", cmd_recover, "Seal a legacy snapshot or restore an event-ledger checkpoint"),
    ):
        command_parser = subparsers.add_parser(name, help=help_text)
        command_parser.add_argument("project")
        command_parser.set_defaults(func=function)
        command_parsers[name] = command_parser

    begin_modes = command_parsers["begin"].add_mutually_exclusive_group()
    begin_modes.add_argument("--apply-experiment")
    begin_modes.add_argument("--abandon-pending")
    command_parsers["begin"].add_argument("--application-note")
    command_parsers["recover"].add_argument("--reason", required=True)

    record_parser = subparsers.add_parser("record", help="Record one node attempt")
    record_parser.add_argument("project")
    record_parser.add_argument("node_id")
    record_parser.add_argument("--result", choices=("pass", "revise", "fail"), required=True)
    record_parser.add_argument("--artifact", required=True)
    record_parser.add_argument("--note")
    record_parser.set_defaults(func=cmd_record)

    close_parser = subparsers.add_parser("close", help="Close a successful run and update experiment memory")
    close_parser.add_argument("project")
    close_parser.add_argument("--metrics", required=True)
    close_parser.add_argument("--experiment", required=True)
    close_parser.set_defaults(func=cmd_close)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except GraphError as exc:
        print(f"graphctl: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
