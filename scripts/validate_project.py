#!/usr/bin/env python3
"""Check the minimum invariant set for an agent-ready project."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from record_utils import load_profile, resolve_path

REQUIRED = ["README.md", "AGENTS.md", "project.yaml", "docs/project/charter.md", "docs/project/current-state.yaml", "docs/project/task-board.yaml", "docs/provenance", "docs/validation", "docs/validation/executions", "docs/coordination/nodes", "docs/coordination/roles", "manifests/environments.yaml", "logs", "logs/topics"]


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
        mapped_required = {
            label: mapping for label, mapping in mapped_required.items()
            if mapping[0] in profile
        }
    else:
        mapped_required["project.yaml"] = ("project", "project.yaml")
    for label, (role, default) in mapped_required.items():
        try:
            candidate = project_path(role, default)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not candidate.exists():
            errors.append(f"missing {role}: {candidate.relative_to(root)}")
    state = project_path("current_state", "docs/project/current-state.yaml")
    if state.exists():
        text = state.read_text(encoding="utf-8")
        for key in ("phase:", "next_action:", "gates:"):
            if key not in text:
                errors.append(f"current-state missing key: {key}")
    board = project_path("task_board", "docs/project/task-board.yaml")
    board_text = board.read_text(encoding="utf-8") if board.exists() else ""
    if board.exists() and "tasks:" not in board_text:
        errors.append("task-board missing tasks:")
    task_ids = re.findall(r"(?m)^\s*- id:\s*([^\s#]+)", board_text)
    duplicates = sorted({item for item in task_ids if task_ids.count(item) > 1})
    errors.extend(f"duplicate task id: {item}" for item in duplicates)
    known_ids = set(task_ids)
    for dependency_line in re.findall(r"(?m)^\s*depends_on:\s*\[([^]]*)\]", board_text):
        for dependency in (x.strip() for x in dependency_line.split(",")):
            if dependency and dependency not in known_ids:
                errors.append(f"unknown task dependency: {dependency}")
    valid_statuses = {"READY", "RUNNING", "REVIEW", "BLOCKED", "DONE"}
    for status in re.findall(r"(?m)^\s*status:\s*([^\s#]+)", board_text):
        if status not in valid_statuses:
            errors.append(f"invalid task status: {status}")
    validation_dir = project_path("validation", "docs/validation")
    for path in validation_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("evidence_id:", "claim:", "stage:", "verdict:"):
            if key not in text:
                errors.append(f"evidence missing {key}: {path.relative_to(root)}")
    handoffs_dir = project_path("handoffs", "docs/project/handoffs")
    for path in handoffs_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("handoff_id:", "task_id:", "one_next_action:"):
            if key not in text:
                errors.append(f"handoff missing {key}: {path.relative_to(root)}")
    executions_dir = project_path("executions", "docs/validation/executions")
    for path in executions_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("execution_id:", "task_id:", "environment_id:", "source_commit:"):
            if key not in text:
                errors.append(f"execution missing {key}: {path.relative_to(root)}")
    environment_manifest = project_path("environments", "manifests/environments.yaml")
    environment_text = environment_manifest.read_text(encoding="utf-8") if environment_manifest.exists() else ""
    environment_ids = set(re.findall(r"(?m)^\s*- environment_id:\s*([^\s#]+)", environment_text))
    execution_ids: set[str] = set()
    for path in executions_dir.glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        execution_id = re.search(r"(?m)^execution_id:\s*([^\s#]+)", text)
        task_id = re.search(r"(?m)^task_id:\s*([^\s#]+)", text)
        environment_id = re.search(r"(?m)^environment_id:\s*([^\s#]+)", text)
        if execution_id:
            if execution_id.group(1) in execution_ids:
                errors.append(f"duplicate execution id: {execution_id.group(1)}")
            execution_ids.add(execution_id.group(1))
        if task_id and task_id.group(1) not in known_ids:
            errors.append(f"execution references unknown task: {task_id.group(1)}")
        if environment_id and environment_id.group(1) not in environment_ids:
            errors.append(f"execution references unknown environment: {environment_id.group(1)}")
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
    raise SystemExit(main())
