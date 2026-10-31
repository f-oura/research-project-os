"""Shared YAML, path and provenance helpers for Project OS tools."""
from __future__ import annotations

import subprocess
from pathlib import Path


def parse_yaml(text: str, source: str = "record") -> dict:
    """Load a mapping, rejecting malformed YAML and duplicate mapping keys."""
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("PyYAML is required; install with python -m pip install -r requirements.txt") from exc

    class UniqueLoader(yaml.SafeLoader):
        pass

    def mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            try:
                if key in result:
                    raise ValueError(f"{source}: duplicate YAML key: {key}")
                result[key] = loader.construct_object(value_node, deep=deep)
            except TypeError as exc:
                raise ValueError(f"{source}: mapping keys must be scalar") from exc
        return result

    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        data = yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"{source}: invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{source}: expected a YAML mapping")
    return data


def load_yaml(path: Path) -> dict:
    return parse_yaml(path.read_text(encoding="utf-8"), str(path))


def load_profile(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"profile does not exist: {path}")
    canonical = load_yaml(path).get("canonical")
    if not isinstance(canonical, dict) or not canonical:
        raise ValueError(f"{path}: canonical must be a non-empty mapping")
    for key, value in canonical.items():
        if not isinstance(key, str) or not isinstance(value, str) or not value.strip() or value == "UNBOUND":
            raise ValueError(f"{path}: canonical roles must map to non-empty paths")
    return canonical


def resolve_path(root: Path, profile: dict[str, str], role: str, default: str) -> Path:
    root = root.resolve()
    relative = profile.get(role, default)
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes project root: {role}: {relative}")
    return candidate


def parse_tasks(text: str) -> list[dict]:
    tasks = parse_yaml(text, "task board").get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("task board: tasks must be a list")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str) or not task["id"].strip():
            raise ValueError("task board: each task must have a non-empty string id")
        if task["id"] in seen:
            raise ValueError(f"duplicate task id: {task['id']}")
        seen.add(task["id"])
    return tasks


def task_blocks(text: str) -> list[tuple[str, str]]:
    tasks = parse_tasks(text)
    import yaml
    return [(task["id"], yaml.safe_dump([task], sort_keys=False, allow_unicode=True).rstrip())
            for task in tasks]


def git_revision(path: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNBOUND"


def referenced_values(task_text: str) -> dict[str, list[str]]:
    task = parse_tasks("tasks:\n" + task_text)[0]
    result = {}
    for key in ("depends_on", "completion_evidence", "evidence", "handoff", "approval", "validation"):
        value = task.get(key)
        if isinstance(value, list):
            result[key] = [str(item) for item in value]
    return result
