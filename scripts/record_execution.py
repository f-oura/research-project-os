#!/usr/bin/env python3
"""Create a provenance record binding a task run to an environment and commit."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def items(label: str, values: list[str]) -> list[str]:
    lines = [f"{label}:"]
    lines.extend(f"  - {quote(value)}" for value in values)
    if not values:
        lines.append("  []")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--id", required=True, dest="execution_id")
    parser.add_argument("--task", required=True, dest="task_id")
    parser.add_argument("--environment", required=True, dest="environment_id")
    parser.add_argument("--role", required=True)
    parser.add_argument("--commit", required=True, dest="source_commit")
    parser.add_argument("--status", choices=["planned", "running", "completed", "failed", "aborted"], default="completed")
    parser.add_argument("--started", default="UNBOUND")
    parser.add_argument("--finished", default="UNBOUND")
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--input", action="append", default=[])
    parser.add_argument("--output", action="append", default=[])
    parser.add_argument("--validation", action="append", default=[])
    parser.add_argument("--notes", default="UNBOUND")
    parser.add_argument("--task-board", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.execution_id):
        parser.error("--id must contain only letters, digits, '.', '_' or '-'")
    root = args.project.resolve()
    board = (args.task_board or root / "docs/project/task-board.yaml").resolve()
    manifest = (args.manifest or root / "manifests/environments.yaml").resolve()
    output_dir = (args.output_dir or root / "docs/validation/executions").resolve()
    if not board.is_file():
        parser.error(f"task board does not exist: {board}")
    if not manifest.is_file():
        parser.error(f"environment manifest does not exist: {manifest}")
    board_text = board.read_text(encoding="utf-8")
    if not re.search(rf"(?m)^\s*- id:\s*{re.escape(args.task_id)}\s*$", board_text):
        parser.error(f"task is not registered: {args.task_id}")
    manifest_text = manifest.read_text(encoding="utf-8")
    if not re.search(rf"(?m)^\s*- environment_id:\s*{re.escape(args.environment_id)}\s*$", manifest_text):
        parser.error(f"environment is not registered: {args.environment_id}")
    target = output_dir / f"{args.execution_id}.yaml"
    if target.exists():
        parser.error(f"execution record already exists: {target}")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    started = args.started if args.started != "UNBOUND" else (now if args.status != "planned" else "UNBOUND")
    finished = args.finished if args.finished != "UNBOUND" else (now if args.status in {"completed", "failed", "aborted"} else "UNBOUND")
    lines = [
        f"execution_id: {args.execution_id}", f"task_id: {args.task_id}", f"environment_id: {args.environment_id}",
        f"role: {args.role}", f"source_commit: {args.source_commit}", f"started_at: {started}", f"finished_at: {finished}",
    ]
    lines += items("commands_or_procedure", args.command)
    lines += items("input_versions", args.input)
    lines += items("outputs", args.output)
    lines += items("validation_refs", args.validation)
    lines += [f"status: {args.status}", f"notes: {quote(args.notes)}"]
    content = "\n".join(lines) + "\n"
    if args.dry_run:
        print(content, end="")
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"Created {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
