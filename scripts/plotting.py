"""Pinned plotting dependency shared by bootstrap, installer and read-only audit."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from record_utils import resolve_path

URL = "https://github.com/f-oura/custom-plot.git"
DEFAULTS = {
    "plot_dependency": "vendor/custom-plot",
    "plot_skill": ".agents/skills/research-plot/SKILL.md",
    "plot_manifest": "manifests/plotting.json",
    "agent_policy": "AGENTS.md",
}
REQUIRED = [".agents/skills/research-plot/SKILL.md", "python/plotstyle.py",
            "config/selection.json", "config/color_options.json", "config/styles.json"]
MARKER = "<!-- custom-plot -->"


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "Git command failed")
    return result.stdout.strip()


def paths(root: Path, profile: dict[str, str]) -> dict[str, Path]:
    mapped = dict(profile)
    manifest_path = resolve_path(root, mapped, "plot_manifest", DEFAULTS["plot_manifest"])
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text())
        mapped.setdefault("plot_dependency", manifest.get("path", DEFAULTS["plot_dependency"]))
        mapped.setdefault("plot_skill", manifest.get("skill", DEFAULTS["plot_skill"]))
    return {role: resolve_path(root, mapped, role, default) for role, default in DEFAULTS.items()}


def runtime(python: str) -> dict:
    code = "import sys,importlib.util,json; print(json.dumps({'version':list(sys.version_info[:3]),'missing':[m for m in ['numpy','matplotlib'] if importlib.util.find_spec(m) is None]}))"
    try:
        result = subprocess.run([python, "-c", code], capture_output=True, text=True, timeout=15)
        if result.returncode:
            raise ValueError(result.stderr.strip())
        info = json.loads(result.stdout)
        if info["version"] < [3, 10]:
            info["missing"].append("Python >=3.10")
        if not info["missing"]:
            probe = subprocess.run([python, "-c", "import numpy,matplotlib"], capture_output=True, text=True, timeout=15)
            if probe.returncode:
                info["missing"].append("NumPy/Matplotlib import failed: " + probe.stderr.strip())
        info["status"] = "MISSING" if info["missing"] else "PASS"
        return info
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        return {"status": "MISSING", "missing": [str(exc)]}


def inspect(root: Path, profile: dict[str, str] | None = None, python: str | None = None) -> dict:
    root = root.resolve()
    issues = []
    try:
        target = paths(root, profile or {})
        manifest = json.loads(target["plot_manifest"].read_text())
        dependency = target["plot_dependency"]
        relative = str(dependency.relative_to(root))
        if manifest.get("path") != relative or manifest.get("repository") != URL:
            issues.append("plotting manifest does not match canonical dependency path/URL")
        revision = manifest.get("revision", "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            issues.append("plotting revision must be a full pinned commit SHA")
        entries = git(root, "ls-files", "--stage", "--", relative).splitlines()
        if not any(line.startswith("160000 " + revision + " ") for line in entries):
            issues.append("plotting Git index is missing the pinned submodule gitlink")
        registered = git(root, "config", "-f", ".gitmodules", "--get", "submodule." + relative + ".url")
        if registered != URL:
            issues.append("plotting submodule URL differs from canonical URL")
        missing = [item for item in REQUIRED if not (dependency / item).is_file()]
        if missing:
            issues.append("uninitialized/incomplete plotting submodule; run git submodule update --init -- " + relative)
        elif git(dependency, "rev-parse", "HEAD") != revision:
            issues.append("plotting checkout differs from pinned revision")
        if not target["plot_skill"].is_file() or relative + "/.agents/skills/research-plot/SKILL.md" not in target["plot_skill"].read_text():
            issues.append("plotting trigger skill is missing its canonical reference")
        if not target["agent_policy"].is_file() or MARKER not in target["agent_policy"].read_text():
            issues.append("agent policy is missing plotting reference")
    except (OSError, ValueError, KeyError) as exc:
        issues.append("plotting dependency unavailable: " + str(exc))
    result = {"status": "PASS" if not issues else "MISSING", "issues": issues}
    if python:
        result["runtime"] = runtime(python)
        if result["runtime"]["status"] != "PASS":
            result["status"] = "MISSING"
            result["issues"].append("existing Python runtime is missing plotting dependencies; select a compatible existing interpreter")
    return result


def install(root: Path, revision: str, profile: dict[str, str] | None = None, source: str = URL) -> dict:
    root = root.resolve()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("custom-plot revision must be a full 40-character commit SHA")
    target = paths(root, profile or {})
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root:
        raise ValueError("target must be the Git repository root; initialize it explicitly first")
    relative = str(target["plot_dependency"].relative_to(root))
    if target["plot_manifest"].exists():
        result = inspect(root, profile)
        manifest = json.loads(target["plot_manifest"].read_text())
        if result["status"] == "PASS" and manifest.get("revision") == revision:
            return result
        raise ValueError("existing plotting integration differs or is incomplete; review it without overwriting")
    if target["plot_dependency"].exists() or target["plot_skill"].exists():
        raise ValueError("plotting destination already exists; review without overwriting")
    if git(root, "status", "--porcelain", "--", ".gitmodules"):
        raise ValueError(".gitmodules has existing changes; resolve ownership before adding a submodule")
    if target["agent_policy"].exists() and MARKER in target["agent_policy"].read_text():
        raise ValueError("agent policy already has a plotting integration; review without overwriting")
    # Verify the exact revision and file contract before touching the consuming repo.
    with tempfile.TemporaryDirectory(prefix="custom-plot-") as directory:
        checkout = Path(directory) / "source"
        git(Path(directory), "clone", "--no-checkout", "--", source, str(checkout))
        git(checkout, "checkout", "--detach", revision)
        missing = [item for item in REQUIRED if not (checkout / item).is_file()]
        if missing:
            raise ValueError("custom-plot pinned revision is missing: " + ", ".join(missing))
        git(root, "-c", "protocol.file.allow=always", "submodule", "add", "--name", relative, "--", str(checkout), relative)
        git(root, "config", "-f", ".gitmodules", "submodule." + relative + ".url", URL)
        git(root, "config", "submodule." + relative + ".url", URL)
        git(target["plot_dependency"], "remote", "set-url", "origin", URL)
        git(target["plot_dependency"], "checkout", "--detach", revision)
        git(root, "add", "--", ".gitmodules", relative)
    content = (Path(__file__).resolve().parents[1] / "templates/research-plot-skill.md").read_text().replace("@DEPENDENCY@", relative)
    target["plot_skill"].parent.mkdir(parents=True, exist_ok=True)
    target["plot_skill"].write_text(content)
    policy = target["agent_policy"].read_text() if target["agent_policy"].exists() else "# Agent instructions\n"
    policy += "\n" + MARKER + "\n## Research figures\n\nFor plotting, read `" + str(target["plot_skill"].relative_to(root)) + "` and the canonical workflow in `" + relative + "/.agents/skills/research-plot/SKILL.md`. Use the pinned submodule; initialize it with `git submodule update --init -- " + relative + "`. Preserve project calculation, provenance, and output rules.\n"
    target["agent_policy"].parent.mkdir(parents=True, exist_ok=True)
    target["agent_policy"].write_text(policy)
    target["plot_manifest"].parent.mkdir(parents=True, exist_ok=True)
    target["plot_manifest"].write_text(json.dumps({"schema_version": 1, "repository": URL, "path": relative, "revision": revision, "skill": str(target["plot_skill"].relative_to(root))}, indent=2) + "\n")
    return inspect(root, profile)
