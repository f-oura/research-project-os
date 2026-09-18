#!/usr/bin/env python3
"""Regression tests for fail-closed task selection and profile-aware records."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTEXT = ROOT / "scripts/context_pack.py"
VALIDATE = ROOT / "scripts/validate_project.py"
AUDIT = ROOT / "scripts/audit_project.py"


class ToolingTests(unittest.TestCase):
    def run_tool(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    def test_context_pack_finds_task_after_old_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "docs/project").mkdir(parents=True)
            (project / "docs/validation/executions").mkdir(parents=True)
            (project / "manifests").mkdir()
            (project / "logs/topics").mkdir(parents=True)
            tasks = "tasks:\n" + "".join(
                f"  - id: TASK-{index:04d}\n    title: {'x' * 220}\n    status: READY\n"
                for index in range(80)
            )
            tasks += "  - id: TARGET-001\n    title: target task\n    status: READY\n    depends_on: []\n    completion_evidence: [EVD-001]\n"
            (project / "docs/project/task-board.yaml").write_text(tasks, encoding="utf-8")
            (project / "docs/project/current-state.yaml").write_text("phase: PLANNING\nnext_action: target\ngates: {}\n", encoding="utf-8")
            (project / "docs/project/charter.md").write_text("# Charter\n", encoding="utf-8")
            (project / "manifests/environments.yaml").write_text("environments: []\n", encoding="utf-8")
            result = self.run_tool(CONTEXT, str(project), "--purpose", "test", "--task", "TARGET-001")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Target task: TARGET-001", result.stdout)
            self.assertIn("EVD-001", result.stdout)

    def test_context_pack_unknown_task_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "docs/project").mkdir(parents=True)
            (project / "docs/project/task-board.yaml").write_text("tasks:\n  - id: KNOWN\n", encoding="utf-8")
            result = self.run_tool(CONTEXT, str(project), "--purpose", "test", "--task", "UNKNOWN")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("task is not registered", result.stderr)

    def test_profile_resolves_legacy_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "docs/coordination").mkdir(parents=True)
            (project / "logs/topics").mkdir(parents=True)
            (project / "manifests").mkdir()
            (project / "docs/coordination/task-board.yaml").write_text("tasks:\n  - id: TASK-001\n    status: READY\n    depends_on: []\n", encoding="utf-8")
            (project / "docs/coordination/current-state.yaml").write_text("phase: PLANNING\nnext_action: test\ngates: {}\n", encoding="utf-8")
            (project / "README.md").write_text("# Project\n", encoding="utf-8")
            (project / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            (project / "manifests/environments.yaml").write_text("environments: []\n", encoding="utf-8")
            profile = project / "profile.yaml"
            profile.write_text("canonical:\n  entrypoint: README.md\n  agent_policy: AGENTS.md\n  current_state: docs/coordination/current-state.yaml\n  task_board: docs/coordination/task-board.yaml\n  environments: manifests/environments.yaml\n  logs: logs/topics\n", encoding="utf-8")
            result = self.run_tool(VALIDATE, str(project), "--profile", str(profile))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_audit_profile_reports_mapped_paths(self) -> None:
        fixture = ROOT / "tests/fixtures/legacy-project"
        profile = ROOT / "profiles/amaneq-receiver.yaml"
        result = self.run_tool(AUDIT, str(fixture), "--profile", str(profile), "--format", "json")
        self.assertIn('"task_board": "docs/coordination/task-board.yaml"', result.stdout)


if __name__ == "__main__":
    unittest.main()
