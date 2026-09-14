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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--task", help="task ID to include as the primary work item")
    parser.add_argument("--max-chars", type=int, default=24000)
    args = parser.parse_args()
    root = args.path.resolve()
    board_text = read(root / "docs/project/task-board.yaml", 12000)
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
        "## Charter\n\n" + read(root / "docs/project/charter.md", 5000),
        "## Current state\n\n" + read(root / "docs/project/current-state.yaml", 6000),
        "## Execution environments\n\n" + read(root / "manifests/environments.yaml", 5000),
        task_heading,
    ]
    if args.task:
        referenced = re.findall(r"(?:docs|logs|manifests|tests|src|software|firmware)/[^\s,\])]+", task_text)
        for relative in dict.fromkeys(referenced):
            candidate = root / relative.rstrip(".")
            if candidate.is_file():
                sections.append(f"## Referenced record: {relative}\n\n" + read(candidate, 3000))
    else:
        decisions = root / "docs/project/decisions"
        for path in sorted(decisions.glob("*.md")):
            sections.append(f"## Decision: {path.name}\n\n" + read(path, 2500))
    for path in sorted((root / "logs/topics").glob("*.md"))[-5:]:
        sections.append(f"## Topic log: {path.name}\n\n" + read(path, 1800))
    output = "\n\n".join(sections)
    if len(output) > args.max_chars:
        output = output[: args.max_chars] + "\n\n[pack truncated; consult canonical records before acting]"
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
