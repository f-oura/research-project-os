#!/usr/bin/env python3
"""Build a small, purpose-limited context pack from canonical project records."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import subprocess

from record_utils import git_revision, load_profile, referenced_values, resolve_path, task_blocks


def read(path: Path, limit: int) -> str:
    if not path.exists():
        return f"[missing: {path}]"
    text = path.read_text(encoding="utf-8")
    if re.search(r"(?im)^\s*(access|classification):\s*restricted\s*$", text):
        return "[excluded: restricted record]"
    text = re.sub(
        r"(?im)^(\s*(?:password|token|secret|private_key|credential|api_key)\s*:\s*).*$",
        r"\1[REDACTED]",
        text,
    )
    return text[:limit] + ("\n[truncated]" if len(text) > limit else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--task", help="task ID to include as the primary work item")
    parser.add_argument("--profile", type=Path, help="project profile YAML for legacy/custom paths")
    parser.add_argument("--max-chars", type=int, default=24000)
    parser.add_argument("--max-task-chars", type=int, default=10000)
    args = parser.parse_args()
    root = args.path.resolve()
    profile = load_profile(args.profile.resolve()) if args.profile else {}
    def project_path(role: str, default: str) -> Path:
        return resolve_path(root, profile, role, default)
    board_path = project_path("task_board", "docs/project/task-board.yaml")
    state_path = project_path("current_state", "docs/project/current-state.yaml")
    charter_path = project_path("charter", "docs/project/charter.md")
    logs_path = project_path("logs", "logs/topics")
    env_path = project_path("environments", "manifests/environments.yaml")
    executions_path = project_path("executions", "docs/validation/executions")
    board_text = read(board_path, 1_000_000)
    project_commit = git_revision(root)
    tool_commit = git_revision(Path(__file__).resolve().parents[1])
    if args.task:
        selected = next((block for task_id, block in task_blocks(board_text) if task_id == args.task), None)
        if selected is None:
            parser.error(f"task is not registered: {args.task}")
        task_text = selected
        if len(task_text) > args.max_task_chars:
            task_text = task_text[: args.max_task_chars] + "\n[task block truncated]"
        task_heading = f"## Target task: {args.task}\n\n{task_text}"
        refs = referenced_values(selected)
        reference_lines = ["## Task references"]
        for key, values in refs.items():
            reference_lines.append(f"- {key}: {', '.join(values) if values else '[]'}")
        if len(reference_lines) > 1:
            task_heading += "\n\n" + "\n".join(reference_lines)
    else:
        task_text = board_text
        task_heading = "## Task board\n\n" + board_text
    sections = [
        f"# Context Pack\n\nGenerated: {date.today().isoformat()}\nPurpose: {args.purpose}\nProject source commit: {project_commit}\nTool revision: {tool_commit}\nSource task board: {board_path.relative_to(root)}\nRedaction policy: credentials and restricted records are excluded or redacted.\n",
        "## Charter\n\n" + read(charter_path, 5000),
        "## Current state\n\n" + read(state_path, 12000),
        "## Execution environments\n\n" + read(env_path, 5000),
        task_heading,
    ]
    if args.task:
        for path in sorted(executions_path.glob("*.yaml")):
            if path.name.startswith("_") or "template" in path.name:
                continue
            execution_text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(rf"(?m)^task_id:\s*{re.escape(args.task)}\s*$", execution_text):
                sections.append(f"## Execution record: {path.name}\n\n" + read(path, 3000))
        referenced = re.findall(r"(?:docs|logs|manifests|tests|src|software|firmware)/[^\s,\])]+", task_text)
        for relative in dict.fromkeys(referenced):
            candidate = root / relative.rstrip(".")
            if candidate.is_file():
                sections.append(f"## Referenced record: {relative}\n\n" + read(candidate, 3000))
    else:
        decisions = root / "docs/project/decisions"
        for path in sorted(decisions.glob("*.md")):
            sections.append(f"## Decision: {path.name}\n\n" + read(path, 2500))
    log_files = [path for path in sorted(logs_path.glob("*.md")) if "template" not in path.name]
    for path in log_files[-5:]:
        sections.append(f"## Topic log: {path.name}\n\n" + read(path, 1800))
    if args.task:
        priority = ("## Target task:", "## Current state", "## Execution environments", "## Execution record:", "## Charter", "## Referenced record:", "## Topic log:")
        sections.sort(key=lambda section: next((index for index, prefix in enumerate(priority) if section.startswith(prefix)), len(priority)))
    output = "\n\n".join(sections)
    if len(output) > args.max_chars:
        output = output[: args.max_chars] + "\n\n[pack truncated; consult canonical records before acting]"
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
