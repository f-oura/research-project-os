#!/usr/bin/env python3
"""Check the minimum invariant set for an agent-ready project."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REQUIRED = ["README.md", "AGENTS.md", "project.yaml", "docs/project/charter.md", "docs/project/current-state.yaml", "docs/project/task-board.yaml", "docs/provenance", "docs/validation", "docs/validation/executions", "docs/coordination/nodes", "docs/coordination/roles", "manifests/environments.yaml", "logs", "logs/topics"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    root = args.path.resolve()
    errors: list[str] = []
    for item in REQUIRED:
        if not (root / item).exists():
            errors.append(f"missing: {item}")
    state = root / "docs/project/current-state.yaml"
    if state.exists():
        text = state.read_text(encoding="utf-8")
        for key in ("phase:", "next_action:", "gates:"):
            if key not in text:
                errors.append(f"current-state missing key: {key}")
    board = root / "docs/project/task-board.yaml"
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
    for path in (root / "docs/validation").glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("evidence_id:", "claim:", "stage:", "verdict:"):
            if key not in text:
                errors.append(f"evidence missing {key}: {path.relative_to(root)}")
    for path in (root / "docs/project/handoffs").glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("handoff_id:", "task_id:", "one_next_action:"):
            if key not in text:
                errors.append(f"handoff missing {key}: {path.relative_to(root)}")
    for path in (root / "docs/validation/executions").glob("*.yaml"):
        if path.name.startswith("_") or "template" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        for key in ("execution_id:", "task_id:", "environment_id:", "source_commit:"):
            if key not in text:
                errors.append(f"execution missing {key}: {path.relative_to(root)}")
    for path in (root / "logs/topics").glob("*.md"):
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
