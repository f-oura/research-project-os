"""Offline fixtures for pinned submodules and canonical plotting discovery."""
from __future__ import annotations
import functools
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import bootstrap_project
from plotting import REQUIRED, git, inspect, install, runtime


class PlottingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / 'upstream'
        self.source.mkdir()
        git(self.source, 'init')
        for relative in REQUIRED:
            p = self.source / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('fixture\n')
        git(self.source, 'add', '.')
        git(self.source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture')
        self.sha = git(self.source, 'rev-parse', 'HEAD')
        self.project = self.root / 'project'
        self.project.mkdir()
        git(self.project, 'init')
        (self.project / 'AGENTS.md').write_text('# Preserve policy\n')
        (self.project / 'human-note.txt').write_text('preserve human note\n')

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, profile=None):
        return install(self.project, self.sha, profile, str(self.source))

    def test_pin_discovery_and_idempotent_install(self):
        self.assertEqual(self.add()['status'], 'PASS')
        self.assertEqual(self.add()['status'], 'PASS')
        self.assertIn('160000 ' + self.sha, git(self.project, 'ls-files', '--stage', 'vendor/custom-plot'))
        self.assertIn('vendor/custom-plot/.agents/skills/research-plot/SKILL.md', (self.project / '.agents/skills/research-plot/SKILL.md').read_text())
        self.assertEqual((self.project / 'human-note.txt').read_text(), 'preserve human note\n')
        self.assertTrue((self.project / 'AGENTS.md').read_text().startswith('# Preserve policy\n'))
        self.assertNotIn('human-note', git(self.project, 'diff', '--cached', '--name-only'))

    def test_mapped_paths_preserve_canonical_records(self):
        profile = {'plot_dependency': 'third_party/custom-plot', 'plot_skill': '.agents/skills/research-plot/SKILL.md', 'plot_manifest': 'manifests/custom-plot.json', 'agent_policy': 'rules/AGENTS.md'}
        (self.project / 'rules').mkdir()
        (self.project / 'rules/AGENTS.md').write_text('canonical policy\n')
        self.assertEqual(self.add(profile)['status'], 'PASS')
        self.assertEqual((self.project / 'AGENTS.md').read_text(), '# Preserve policy\n')
        self.assertEqual(inspect(self.project, profile)['status'], 'PASS')

    def test_manifest_discovers_nondefault_dependency_without_duplicate_profile(self):
        self.add({'plot_dependency': 'third_party/custom-plot'})
        self.assertEqual(inspect(self.project)['status'], 'PASS')

    def test_escape_path_rejected_before_mutation(self):
        with self.assertRaisesRegex(ValueError, 'escapes project root'):
            self.add({'plot_dependency': '../outside'})
        self.assertFalse((self.project / '.gitmodules').exists())

    def test_missing_contract_rejected_before_mutation(self):
        p = self.source / 'python/plotstyle.py'
        p.unlink()
        git(self.source, 'add', '.')
        git(self.source, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'missing')
        self.sha = git(self.source, 'rev-parse', 'HEAD')
        with self.assertRaisesRegex(ValueError, 'missing: python/plotstyle.py'):
            self.add()
        self.assertFalse((self.project / '.gitmodules').exists())

    def test_uninitialized_submodule_has_actionable_error(self):
        self.add()
        shutil.rmtree(self.project / 'vendor/custom-plot')
        result = inspect(self.project)
        self.assertEqual(result['status'], 'MISSING')
        self.assertTrue(any('submodule update --init' in issue for issue in result['issues']))

    def test_mismatched_pin_is_reported(self):
        self.add()
        p = self.project / 'manifests/plotting.json'
        manifest = json.loads(p.read_text())
        manifest['revision'] = 'f' * 40
        p.write_text(json.dumps(manifest))
        self.assertEqual(inspect(self.project)['status'], 'MISSING')

    def test_missing_interpreter_has_actionable_error(self):
        self.add()
        result = inspect(self.project, python=str(self.root / 'missing-python'))
        self.assertEqual(result['status'], 'MISSING')
        self.assertTrue(result['runtime']['missing'])

    def test_dirty_gitmodules_preserved(self):
        (self.project / '.gitmodules').write_text('# human change\n')
        with self.assertRaisesRegex(ValueError, 'existing changes'):
            self.add()
        self.assertEqual((self.project / '.gitmodules').read_text(), '# human change\n')

    def test_bootstrap_generates_pinned_dependency(self):
        target = self.root / 'new-project'
        with patch.object(sys, 'argv', ['bootstrap_project.py', str(target), '--name', 'example', '--title', 'Example', '--plot-revision', self.sha]), patch.object(bootstrap_project, 'install', functools.partial(install, source=str(self.source))):
            self.assertEqual(bootstrap_project.main(), 0)
        self.assertEqual(inspect(target)['status'], 'PASS')
        self.assertTrue((target / 'docs/project/current-state.yaml').is_file())

    def test_nested_scaffold_uses_repository_dependency_without_duplication(self):
        target = self.project / 'projects/nested'
        with patch.object(sys, 'argv', ['bootstrap_project.py', str(target), '--name', 'nested', '--title', 'Nested', '--plot-revision', self.sha]), patch.object(bootstrap_project, 'install', functools.partial(install, source=str(self.source))):
            self.assertEqual(bootstrap_project.main(), 0)
        self.assertEqual(inspect(self.project)['status'], 'PASS')
        self.assertTrue((target / 'docs/project/current-state.yaml').is_file())
        self.assertFalse((target / 'vendor').exists())
        self.assertFalse((target / 'manifests/plotting.json').exists())
        self.assertIn('containing Git repository root', (target / 'AGENTS.md').read_text())

    def test_records_only_scaffold_preserves_previous_behavior(self):
        target = self.root / 'records'
        with patch.object(sys, 'argv', ['bootstrap_project.py', str(target), '--name', 'records', '--title', 'Records', '--without-plotting']):
            self.assertEqual(bootstrap_project.main(), 0)
        self.assertFalse((target / '.git').exists())
        self.assertFalse((target / '.gitmodules').exists())
