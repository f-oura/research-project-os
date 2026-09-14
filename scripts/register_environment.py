#!/usr/bin/env python3
"""Register an execution environment in a project's YAML manifest."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_pairs(values: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"--tool must use KEY=VALUE: {value}")
        key, item = value.split("=", 1)
        if not key or not item:
            raise ValueError(f"--tool must use non-empty KEY=VALUE: {value}")
        pairs.append((key, item))
    return pairs


def render(environment_id: str, name: str, kind: str, host: str, repository: str, workdir: str, tools: list[tuple[str, str]], capabilities: list[str], restrictions: list[str], data_mounts: list[str]) -> str:
    lines = [
        f"  - environment_id: {environment_id}", f"    name: {name}", f"    kind: {kind}",
        f"    host_identity: {host}", f"    repository_locator: {repository}", f"    working_directory: {workdir}",
        "    tool_versions:",
    ]
    lines.extend(f"      {key}: {value}" for key, value in tools)
    if not tools:
        lines.append("      {}")
    for key, values in (("capabilities", capabilities), ("restrictions", restrictions), ("data_mounts", data_mounts)):
        lines.append(f"    {key}:")
        lines.extend(f"      - {value}" for value in values)
        if not values:
            lines.append("      []")
    lines.extend(["    verified_at: UNBOUND", "    verified_by: UNBOUND"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--id", required=True, dest="environment_id")
    parser.add_argument("--name", required=True)
    parser.add_argument("--kind", choices=["local", "remote", "container", "cluster"], default="remote")
    parser.add_argument("--host", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--workdir", required=True)
    parser.add_argument("--tool", action="append", default=[])
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--restriction", action="append", default=[])
    parser.add_argument("--data-mount", action="append", default=[])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", args.environment_id):
        parser.error("--id must contain only letters, digits, '.', '_' or '-'")
    try:
        tools = parse_pairs(args.tool)
    except ValueError as error:
        parser.error(str(error))
    root = args.project.resolve()
    manifest = (args.manifest or root / "manifests/environments.yaml").resolve()
    if not manifest.exists():
        parser.error(f"manifest does not exist: {manifest}")
    text = manifest.read_text(encoding="utf-8")
    if re.search(rf"(?m)^\s*- environment_id:\s*{re.escape(args.environment_id)}\s*$", text):
        parser.error(f"environment already exists: {args.environment_id}")
    if "environments:" not in text:
        parser.error("manifest must contain an environments: key")
    entry = render(args.environment_id, args.name, args.kind, args.host, args.repository, args.workdir, tools, args.capability, args.restriction, args.data_mount)
    if re.search(r"(?m)^environments:\s*\[\]\s*$", text):
        updated = re.sub(r"(?m)^environments:\s*\[\]\s*$", "environments:\n" + entry.rstrip("\n"), text)
    else:
        updated = text.rstrip() + "\n" + entry
    if args.dry_run:
        print(updated)
    else:
        manifest.write_text(updated.rstrip() + "\n", encoding="utf-8")
        print(f"Registered {args.environment_id} in {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
