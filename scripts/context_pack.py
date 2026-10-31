#!/usr/bin/env python3
"""Build a small, purpose-limited context pack from canonical project records."""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

from record_utils import git_revision, load_profile, referenced_values, resolve_path, task_blocks, parse_tasks


def read(path: Path, limit: int | None = None, *, root: Path) -> str:
    path = resolve_path(root, {}, "context source", str(path))
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
    return text if limit is None else text[:limit] + ("\n[truncated]" if len(text) > limit else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=Path("."))
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--task", help="task ID to include as the primary work item")
    parser.add_argument("--profile", type=Path, help="project profile YAML for legacy/custom paths")
    parser.add_argument("--max-chars", type=int, default=24000)
    parser.add_argument("--max-task-chars", type=int, default=10000)
    args = parser.parse_args()
    if args.max_chars <= 0 or args.max_task_chars <= 0:
        parser.error("character budgets must be positive")
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
    board_text = read(board_path, root=root)
    parse_tasks(board_text)
    project_commit = git_revision(root)
    tool_commit = git_revision(Path(__file__).resolve().parents[1])
    if args.task:
        selected = next((block for task_id, block in task_blocks(board_text) if task_id == args.task), None)
        if selected is None:
            parser.error(f"task is not registered: {args.task}")
        task_text = selected
        if len(task_text) > args.max_task_chars:
            parser.error("target task exceeds --max-task-chars; increase the budget; no pack emitted")
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
    core = [
        f"# Context Pack\n\nGenerated: {date.today().isoformat()}\nPurpose: {args.purpose}\nProject source commit: {project_commit}\nTool revision: {tool_commit}\nSource task board: {board_path.relative_to(root)}\nRedaction policy: best-effort filtering only; review before sharing.\n",
        "## Current state\n\n" + read(state_path, root=root),
        "## Execution environments\n\n" + read(env_path, root=root),
        "## Agent policy\n\n" + read(project_path("agent_policy", "AGENTS.md"), root=root),
        task_heading,
    ]
    sections = ["## Charter\n\n" + read(charter_path, 5000, root=root)]
    if args.task:
        for path in sorted(executions_path.glob("*.yaml")):
            if path.name.startswith("_") or "template" in path.name:
                continue
            path = resolve_path(root, {}, "execution record", str(path))
            execution_text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(rf"(?m)^task_id:\s*{re.escape(args.task)}\s*$", execution_text):
                sections.append(f"## Execution record: {path.name}\n\n" + read(path, 3000, root=root))
        referenced = re.findall(r"(?:docs|logs|manifests|tests|src|software|firmware)/[^\s,\])]+", task_text)
        for relative in dict.fromkeys(referenced):
            candidate = resolve_path(root, {}, "task reference", relative.rstrip(".\"\'"))
            if candidate.is_file():
                sections.append(f"## Referenced record: {relative}\n\n" + read(candidate, 3000, root=root))
    else:
        decisions = project_path("decisions", "docs/project/decisions")
        for path in sorted(decisions.glob("*.md")):
            sections.append(f"## Decision: {path.name}\n\n" + read(path, 2500, root=root))
    log_files = [path for path in sorted(logs_path.glob("*.md")) if "template" not in path.name]
    for path in log_files[-5:]:
        sections.append(f"## Topic log: {path.name}\n\n" + read(path, 1800, root=root))
    # Never truncate provenance, policy, target task, state or environments.
    output = "\n\n".join(core)
    if len(output) > args.max_chars:
        parser.error(f"mandatory context requires {len(output)} characters; increase --max-chars; no pack emitted")
    omitted = []
    for section in sections:
        candidate = output + "\n\n" + section
        # Reserve space for a complete omission marker, not a partial YAML record.
        if len(candidate) + 100 <= args.max_chars:
            output = candidate
        else:
            omitted.append(section.splitlines()[0])
    if omitted:
        marker = f"\n\n[omitted {len(omitted)} optional sections; consult canonical records before acting]"
        if len(output) + len(marker) > args.max_chars:
            parser.error("budget cannot fit mandatory context and omission notice; no pack emitted")
        output += marker
    print(output)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
