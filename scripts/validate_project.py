#!/usr/bin/env python3
"""Check the minimum invariant set for an agent-ready project."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from record_utils import load_profile, resolve_path, load_yaml, parse_tasks



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--profile", type=Path, help="compatibility profile with canonical role mappings")
    args = parser.parse_args()
    root = args.path.resolve()
    profile = load_profile(args.profile.resolve()) if args.profile else {}
    def project_path(role: str, default: str) -> Path:
        return resolve_path(root, profile, role, default)
    errors: list[str] = []
    mapped_required = {
        "README.md": ("entrypoint", "README.md"),
        "AGENTS.md": ("agent_policy", "AGENTS.md"),
        "docs/project/charter.md": ("charter", "docs/project/charter.md"),
        "docs/project/current-state.yaml": ("current_state", "docs/project/current-state.yaml"),
        "docs/project/task-board.yaml": ("task_board", "docs/project/task-board.yaml"),
        "docs/provenance": ("provenance", "docs/provenance"),
        "docs/validation": ("validation", "docs/validation"),
        "docs/validation/executions": ("executions", "docs/validation/executions"),
        "docs/coordination/nodes": ("nodes", "docs/coordination/nodes"),
        "docs/coordination/roles": ("roles", "docs/coordination/roles"),
        "manifests/environments.yaml": ("environments", "manifests/environments.yaml"),
        "logs": ("logs_root", "logs"),
        "logs/topics": ("logs", "logs/topics"),
    }
    if args.profile:
        # Custom layouts may omit optional roles, never the state and work queue.
        mapped_required = {
            label: mapping for label, mapping in mapped_required.items()
            if mapping[0] in profile or mapping[0] in {"current_state", "task_board"}
        }
    else:
        mapped_required["project.yaml"] = ("project", "project.yaml")
    for label, (role, default) in mapped_required.items():
        try:
            candidate = project_path(role, default)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        directory_roles = {"provenance", "validation", "executions", "nodes", "roles", "logs_root", "logs"}
        if not (candidate.is_dir() if role in directory_roles else candidate.is_file()):
            errors.append(f"missing {role}: {candidate.relative_to(root)}")
    state = project_path("current_state", "docs/project/current-state.yaml")
    if state.is_file():
        data = load_yaml(state)
        for key in ("phase", "next_action", "gates"):
            if key not in data:
                errors.append(f"current-state missing key: {key}")
    project_manifest = project_path("project", "project.yaml")
    if project_manifest.is_file():
        load_yaml(project_manifest)
    board = project_path("task_board", "docs/project/task-board.yaml")
    tasks = parse_tasks(board.read_text(encoding="utf-8")) if board.is_file() else []
    known_ids = {task["id"] for task in tasks}
    valid_statuses = {"READY", "RUNNING", "REVIEW", "BLOCKED", "DONE"}
    for task in tasks:
        status = task.get("status")
        if not isinstance(status, str) or status not in valid_statuses:
            errors.append(f"invalid task status: {task['id']}: {status}")
        dependencies = task.get("depends_on", [])
        if not isinstance(dependencies, list):
            errors.append(f"depends_on must be a list: {task['id']}")
        else:
            for dependency in dependencies:
                if not isinstance(dependency, str) or dependency not in known_ids:
                    errors.append(f"unknown task dependency: {dependency}")
        if status == "DONE":
            evidence = task.get("completion_evidence")
            if (not isinstance(evidence, list) or not evidence or
                    any(not isinstance(item, str) or not item.strip() or item == "UNBOUND" for item in evidence)):
                errors.append(f"DONE task needs completion_evidence references: {task['id']}")
    validation_dir = project_path("validation", "docs/validation")
    for path in validation_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        data = load_yaml(path)
        for key in ("evidence_id:", "claim:", "stage:", "verdict:"):
            if key.rstrip(":") not in data:
                errors.append(f"evidence missing {key}: {path.relative_to(root)}")
    handoffs_dir = project_path("handoffs", "docs/project/handoffs")
    for path in handoffs_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        data = load_yaml(path)
        for key in ("handoff_id:", "task_id:", "one_next_action:"):
            if key.rstrip(":") not in data:
                errors.append(f"handoff missing {key}: {path.relative_to(root)}")
    executions_dir = project_path("executions", "docs/validation/executions")
    for path in executions_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        data = load_yaml(path)
        for key in ("execution_id:", "task_id:", "environment_id:", "source_commit:"):
            if key.rstrip(":") not in data:
                errors.append(f"execution missing {key}: {path.relative_to(root)}")
    environment_manifest = project_path("environments", "manifests/environments.yaml")
    environment_data = load_yaml(environment_manifest) if environment_manifest.is_file() else {}
    environments = environment_data.get("environments", [])
    if not isinstance(environments, list):
        raise ValueError("environments must be a list")
    environment_ids = set()
    for environment in environments:
        if not isinstance(environment, dict) or not isinstance(environment.get("environment_id"), str):
            raise ValueError("each environment needs a string environment_id")
        identity = environment["environment_id"]
        if identity in environment_ids:
            errors.append(f"duplicate environment id: {identity}")
        environment_ids.add(identity)
    execution_ids: set[str] = set()
    for path in executions_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        data = load_yaml(path)
        execution_id = data.get("execution_id")
        if not isinstance(execution_id, str):
            errors.append(f"execution_id must be a string: {path.name}")
        elif execution_id in execution_ids:
            errors.append(f"duplicate execution id: {execution_id}")
        else:
            execution_ids.add(execution_id)
        for key, known in (("task_id", known_ids), ("environment_id", environment_ids)):
            value = data.get(key)
            if not isinstance(value, str) or value not in known:
                errors.append(f"execution references unknown {key}: {value}")
    logs_dir = project_path("logs", "logs/topics")
    if logs_dir.name != "topics" and (logs_dir / "topics").is_dir():
        logs_dir = logs_dir / "topics"
    for path in logs_dir.glob("*.md"):
        if "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or not re.search(r"(?m)^topic:\s*\S+", text):
            errors.append(f"topic log missing metadata: {path.relative_to(root)}")
    if errors:
        print("FAIL")
        print("\n".join(f"- {item}" for item in errors))
        return 1
    print(f"PASS: {root}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
