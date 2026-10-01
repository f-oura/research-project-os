#!/usr/bin/env python3
"""Read-only audit of an existing repository against Research Project OS roles."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from plotting import inspect as inspect_plotting
from record_utils import load_profile, resolve_path

ROLE_CANDIDATES = {
    "entrypoint": ["README.md", "README.rst"],
    "agent_policy": ["AGENTS.md", "CONTRIBUTING.md"],
    "plan": ["docs/project/development-plan.md", "docs/project/plan.md", "docs/project/amaneq-receiver-development-plan.md"],
    "charter": ["docs/project/charter.md"],
    "current_state": ["docs/project/current-state.yaml", "docs/coordination/current-state.yaml"],
    "task_board": ["docs/project/task-board.yaml", "docs/coordination/task-board.yaml"],
    "handoffs": ["docs/project/handoffs", "docs/coordination/handoffs"],
    "approvals": ["docs/project/approvals", "docs/coordination/approvals"],
    "validation": ["docs/validation", "test", "tests"],
    "provenance": ["docs/provenance", "manifests"],
    "logs": ["logs/topics", "logs"],
    "environments": ["manifests/environments.yaml", "docs/coordination/environments.yaml"],
}


def extract_value(path: Path, key: str) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip()
    if value not in {">", "|"}:
        return value
    lines = text[match.end():].splitlines()
    parts: list[str] = []
    for line in lines:
        if line and not line.startswith(" "):
            break
        if line.strip():
            parts.append(line.strip())
    return " ".join(parts) or value


def audit(root: Path, profile_path: Path | None = None) -> dict:
    profile = load_profile(profile_path.resolve()) if profile_path else {}
    records: dict[str, str | None] = {}
    warnings: list[str] = []
    for role, candidates in ROLE_CANDIDATES.items():
        if role in profile:
            try:
                mapped = resolve_path(root, profile, role, candidates[0])
                found = str(mapped.relative_to(root)) if mapped.exists() else None
            except ValueError as exc:
                found = None
                warnings.append(str(exc))
        else:
            found = next((item for item in candidates if (root / item).exists()), None)
        records[role] = found
        if found is None:
            warnings.append(f"missing: {role}")
        elif role in {"current_state", "task_board", "plan"} and not found.startswith("docs/project/"):
            warnings.append(f"legacy path for {role}: {found}")

    current = root / records["current_state"] if records["current_state"] else None
    task_board = root / records["task_board"] if records["task_board"] else None
    task_text = task_board.read_text(encoding="utf-8", errors="replace") if task_board and task_board.is_file() else ""
    task_ids = re.findall(r"(?m)^\s*- id:\s*([^\s#]+)", task_text)
    statuses = re.findall(r"(?m)^\s*status:\s*([^\s#]+)", task_text)
    summary = {
        "project_id": extract_value(root / "project.yaml", "project_id") or root.name,
        "phase": extract_value(current, "phase") if current else None,
        "next_action": extract_value(current, "next_action") if current else None,
        "task_count": len(task_ids),
        "task_statuses": sorted(set(statuses)),
    }
    standard = {"current_state": "docs/project/current-state.yaml", "task_board": "docs/project/task-board.yaml", "environments": "manifests/environments.yaml"}
    plotting = inspect_plotting(root, profile)
    warnings.extend(plotting["issues"])
    compatibility = "PASS" if not warnings else "PARTIAL"
    return {"project_root": str(root), "compatibility": compatibility, "records": records, "summary": summary, "warnings": warnings, "standard_paths": standard, "plotting": plotting}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--profile", type=Path, help="compatibility profile with canonical role mappings")
    args = parser.parse_args()
    result = audit(args.path.resolve(), args.profile)
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Project: {result['summary']['project_id']}")
        print(f"Compatibility: {result['compatibility']}")
        print("\nCanonical records:")
        for role, path in result["records"].items():
            print(f"  {role}: {path or '[missing]'}")
        print(f"\nTasks: {result['summary']['task_count']}")
        if result["summary"]["phase"]:
            print(f"Phase: {result['summary']['phase']}")
        if result["summary"]["next_action"]:
            print(f"Next action: {result['summary']['next_action']}")
        if result["warnings"]:
            print("\nWarnings:")
            for warning in result["warnings"]:
                print(f"  - {warning}")
    return 0 if result["compatibility"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
