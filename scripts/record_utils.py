"""Small dependency-free helpers shared by Project OS command-line tools."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path


def load_profile(path: Path) -> dict[str, str]:
    """Read canonical role mappings without requiring PyYAML."""
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


def resolve_path(root: Path, profile: dict[str, str], role: str, default: str) -> Path:
    relative = profile.get(role, default)
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"profile path escapes project root: {role}: {relative}")
    return candidate


def task_blocks(text: str) -> list[tuple[str, str]]:
    """Return task ID and complete YAML-ish block, without truncating the board."""
    matches = list(re.finditer(r"(?m)^\s*- id:\s*([^\s#]+)\s*$", text))
    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append((match.group(1), text[match.start():end].rstrip()))
    return blocks


def git_revision(path: Path) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNBOUND"


def referenced_values(task_text: str) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for key in ("depends_on", "completion_evidence", "evidence", "handoff", "approval", "validation"):
        match = re.search(rf"(?m)^\s*{key}:\s*\[([^]]*)\]", task_text)
        if match:
            values[key] = [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]
    return values
