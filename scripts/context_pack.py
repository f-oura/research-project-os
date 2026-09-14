#!/usr/bin/env python3
"""Build a small, purpose-limited context pack from canonical project records."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re


def read(path: Path, limit: int) -> str:
    if not path.exists():
        return f"[missing: {path}]"
    text = path.read_text(encoding="utf-8")
    return text[:limit] + ("\n[truncated]" if len(text) > limit else "")


def load_profile(path: Path) -> dict[str, str]:
    """Read the simple canonical mapping without requiring PyYAML."""
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    in_canonical = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "canonical:":
            in_canonical = True
            continue
        if in_canonical and line and not line.startswith("  "):
            break
        if in_canonical:
            match = re.match(r"^\s{2}([a-z_]+):\s*(\S+)\s*$", line)
            if match:
                result[match.group(1)] = match.group(2)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--task", help="task ID to include as the primary work item")
    parser.add_argument("--profile", type=Path, help="project profile YAML for legacy/custom paths")
    parser.add_argument("--max-chars", type=int, default=24000)
    args = parser.parse_args()
    root = args.path.resolve()
    profile = load_profile(args.profile.resolve()) if args.profile else {}
    def project_path(role: str, default: str) -> Path:
        return root / profile.get(role, default)
    board_path = project_path("task_board", "docs/project/task-board.yaml")
    state_path = project_path("current_state", "docs/project/current-state.yaml")
    charter_path = project_path("charter", "docs/project/charter.md")
    logs_path = project_path("logs", "logs/topics")
    env_path = project_path("environments", "manifests/environments.yaml")
    executions_path = project_path("executions", "docs/validation/executions")
    board_text = read(board_path, 12000)
    if args.task:
        blocks = re.split(r"(?m)(?=^\s*- id:\s*)", board_text)
        selected = next((block for block in blocks if re.search(rf"^\s*- id:\s*{re.escape(args.task)}\s*$", block, re.M)), None)
        task_text = selected or f"[task not found: {args.task}]"
        task_heading = f"## Target task: {args.task}\n\n{task_text}"
    else:
        task_text = board_text
        task_heading = "## Task board\n\n" + board_text
    sections = [
        f"# Context Pack\n\nGenerated: {date.today().isoformat()}\nPurpose: {args.purpose}\n",
        "## Charter\n\n" + read(charter_path, 5000),
        "## Current state\n\n" + read(state_path, 6000),
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
