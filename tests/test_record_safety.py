"""Boundary regressions for validation and purpose-limited context packs."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RecordSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / "project"
        result = self.tool("bootstrap_project.py", "--name", "fixture", "--title", "Fixture", "--without-plotting")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.board = self.project / "docs/project/task-board.yaml"
        self.state = self.project / "docs/project/current-state.yaml"

    def tool(self, name, *args):
        return subprocess.run([sys.executable, str(ROOT / "scripts" / name), str(self.project), *map(str, args)], capture_output=True, text=True)

    def pack(self, *args):
        return self.tool("context_pack.py", "--task", "PLAN-001", "--purpose", "regression", *args)

    def test_bootstrapped_project_validates(self):
        r = self.tool("validate_project.py")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_missing_profile_rejected_by_all_consumers(self):
        for name, extra in [("validate_project.py", []), ("audit_project.py", []),
                            ("context_pack.py", ["--purpose", "test"]), ("install_plotting.py", ["--check"])]:
            with self.subTest(name=name):
                r = self.tool(name, "--profile", self.base / "missing.yaml", *extra)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn("profile does not exist", r.stdout + r.stderr)
                self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_invalid_and_empty_profiles_fail(self):
        profile = self.base / "profile.yaml"
        for text in ("canonical: {}", "canonical: [", "canonical: null", "canonical:\n  task_board: null"):
            profile.write_text(text)
            r = self.tool("validate_project.py", "--profile", profile)
            self.assertNotEqual(r.returncode, 0)

    def test_partial_profile_cannot_validate_empty_project(self):
        profile = self.base / "profile.yaml"
        profile.write_text("canonical:\n  entrypoint: README.md\n")
        self.board.unlink()
        r = self.tool("validate_project.py", "--profile", profile)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("missing task_board", r.stdout)

    def test_quoted_profile_paths_work(self):
        profile = self.base / "profile.yaml"
        profile.write_text('canonical:\n  task_board: "docs/project/task-board.yaml" # comment\n  current_state: "docs/project/current-state.yaml"\n')
        r = self.tool("validate_project.py", "--profile", profile)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_malformed_yaml_and_duplicate_keys_fail(self):
        for text in ("tasks: [", "tasks: []\ntasks: []\n", "tasks: null", "tasks: [null]"):
            self.board.write_text(text)
            for r in (self.tool("validate_project.py"), self.pack()):
                self.assertNotEqual(r.returncode, 0)

    def test_block_dependency_checked(self):
        self.board.write_text('tasks:\n  - id: "PLAN-001"\n    status: READY\n    depends_on:\n      - MISSING\n')
        r = self.tool("validate_project.py")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("unknown task dependency: MISSING", r.stdout)
        self.board.write_text(self.board.read_text().replace("MISSING", "PLAN-002") + '  - id: PLAN-002\n    status: READY\n')
        self.assertEqual(self.tool("validate_project.py").returncode, 0)

    def test_nested_ids_are_not_tasks(self):
        self.board.write_text('tasks:\n  - id: PLAN-001\n    status: READY\n    steps:\n      - id: NESTED\n        status: not-a-task-status\n')
        self.assertEqual(self.tool("validate_project.py").returncode, 0)
        r = self.tool("context_pack.py", "--purpose", "test", "--task", "NESTED")
        self.assertNotEqual(r.returncode, 0)

    def test_done_requires_nonplaceholder_evidence(self):
        for value in ("[]", "null", "[UNBOUND]", '"not a list"'):
            self.board.write_text(f'tasks:\n  - id: PLAN-001\n    status: DONE\n    completion_evidence: {value}\n')
            r = self.tool("validate_project.py")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("DONE task needs", r.stdout)
        self.board.write_text(self.board.read_text().replace('"not a list"', '[docs/project/charter.md]'))
        self.assertEqual(self.tool("validate_project.py").returncode, 0)

    def test_context_preserves_metadata_and_full_core_or_fails(self):
        self.state.write_text('phase: TEST\nnext_action: review\ngates: {}\n' + '# filler\n' * 1600 + '# END_STATE\n')
        r = self.pack("--max-chars", "1000")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")
        r = self.pack("--max-chars", "30000")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Project source commit:", r.stdout)
        self.assertIn("Tool revision:", r.stdout)
        self.assertIn("# END_STATE", r.stdout)
        self.assertLessEqual(len(r.stdout.rstrip('\n')), 30000)

    def test_task_budget_never_truncates(self):
        r = self.pack("--max-task-chars", "10")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")
        self.assertIn("no pack emitted", r.stderr)

    def test_project_escape_and_symlink_rejected(self):
        outside = self.base / "outside.txt"
        outside.write_text("OUTSIDE_SECRET_FIXTURE")
        (self.project / 'docs/escape.txt').symlink_to(outside)
        for ref in ('docs/../../outside.txt', 'docs/escape.txt'):
            self.board.write_text(f'tasks:\n  - id: PLAN-001\n    status: READY\n    evidence: [{ref}]\n')
            r = self.pack()
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("escapes project root", r.stderr)
            self.assertEqual(r.stdout, "")

    def test_optional_log_symlink_rejected(self):
        outside = self.base / "outside.md"
        outside.write_text("OUTSIDE_SECRET_FIXTURE")
        (self.project / 'logs/topics/zzzz.md').symlink_to(outside)
        r = self.pack()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "")

    def test_in_project_reference_included(self):
        (self.project / 'docs/evidence.md').write_text('IN_PROJECT_EVIDENCE')
        self.board.write_text('tasks:\n  - id: PLAN-001\n    status: READY\n    evidence:\n      - docs/evidence.md\n')
        r = self.pack()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('IN_PROJECT_EVIDENCE', r.stdout)

    def test_optional_sections_omitted_with_metadata_retained(self):
        for i in range(5):
            (self.project / f'logs/topics/zz{i}.md').write_text('x' * 5000)
        r = self.pack('--max-chars', '7000')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('[omitted ', r.stdout)
        self.assertIn('Tool revision:', r.stdout)
        self.assertIn('Project source commit:', r.stdout)
        self.assertLessEqual(len(r.stdout.rstrip('\n')), 7000)


if __name__ == '__main__':
    unittest.main()
