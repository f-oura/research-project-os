#!/usr/bin/env python3
"""Create a lightweight, agent-ready research project skeleton."""
from __future__ import annotations

import argparse
import re
import json

from plotting import MARKER, git, install
from datetime import date
from pathlib import Path


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip().lower())
    return value.strip("-") or "research-project"


def write_new(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def copy_template(root: Path, skill_root: Path, name: str, relative: str) -> None:
    source = skill_root / "templates" / name
    if source.exists():
        write_new(root, relative, source.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument(
        "--kind",
        default="research",
        choices=["research", "analysis", "calculation", "detector", "daq-firmware", "simulation", "paper"],
    )
    parser.add_argument("--owner", default="UNBOUND")
    parser.add_argument("--without-plotting", action="store_true", help="create records only; skip Git/submodule integration")
    parser.add_argument("--plot-revision", help="full pinned custom-plot SHA; default: bundled pin")
    args = parser.parse_args()

    root = args.path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    revision = None
    integration_root = root
    if not args.without_plotting:
        revision = args.plot_revision or json.loads((Path(__file__).resolve().parents[1] / "config/plotting.json").read_text())["revision"]
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            parser.error("custom-plot requires a full pinned SHA")
        try:
            git_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
        except ValueError:
            if any(root.iterdir()):
                parser.error("existing non-Git target: initialize Git explicitly or use --without-plotting")
            git(root, "init")
            git_root = root
        integration_root = git_root
    today = date.today().isoformat()
    project_id = slug(args.name)
    files = {
        "project.yaml": f"schema_version: 1\nproject_id: {project_id}\ntitle: {args.title}\nkind: {args.kind}\nowner: {args.owner}\ncreated: {today}\nphase: PLANNING\nstatus: ACTIVE\n",
        "README.md": f"# {args.title}\n\nProject ID: `{project_id}`\n\nStart here:\n\n- [charter](docs/project/charter.md)\n- [current state](docs/project/current-state.yaml)\n- [task board](docs/project/task-board.yaml)\n- [provenance](docs/provenance/README.md)\n- [validation](docs/validation/README.md)\n- [results and figures](docs/validation/results-index.md)\n- [topic logs](logs/README.md)\n\nUnknown values remain `UNBOUND` until bound to evidence or a human decision.\n",
        "docs/project/charter.md": f"# Project charter\n\n- Project: `{project_id}`\n- Created: {today}\n- Status: draft\n\n## Primary question\n\nWhat decision-changing question will this project answer?\n\n## Claim and competing explanations\n\n- Target claim: UNBOUND\n- Null or competing explanation: UNBOUND\n- Discriminator/observable: UNBOUND\n\n## Scope\n\n- In scope: UNBOUND\n- Out of scope: UNBOUND\n\n## Completion\n\n- Minimum defensible completion: UNBOUND\n- Strong completion: UNBOUND\n- Stop/pivot criteria: UNBOUND\n",
        "docs/project/current-state.yaml": f"schema_version: 1\nupdated: {today}\nproject: {project_id}\nphase: PLANNING\nnext_action: Fill the charter and bind the first task to evidence.\nlast_validated_commit: UNBOUND\ngates:\n  external_inputs: UNBOUND\n  human_approval: NOT_REQUIRED_YET\n  release: NOT_READY\n",
        "docs/project/task-board.yaml": "schema_version: 1\nupdated: UNBOUND\nstatuses: [READY, RUNNING, REVIEW, BLOCKED, DONE]\ntasks:\n  - id: PLAN-001\n    title: Define the project charter and first evidence gate\n    owner_role: owner\n    status: READY\n    depends_on: []\n    scope:\n      in: [research question, competing explanation, first validation]\n      out: [unapproved implementation]\n    completion_evidence: [docs/project/charter.md, docs/project/current-state.yaml]\n    human_approval_required: false\n",
        "docs/provenance/README.md": "# Provenance\n\nRecord source identity, locator, version/hash, authority, license or reuse status, and access restrictions. Keep credentials out of this directory.\n",
        "docs/validation/README.md": "# Validation evidence\n\nKeep expected behavior, observed behavior, method, validation stage, input versions, result, and review state together. Do not promote simulation or build results to hardware validation.\n",
        "logs/README.md": "# Topic logs\n\nUse one file per subject under `topics/`. Append dated `discussion`, `development`, `test`, or `blocker` entries. Do not store secrets, raw data, or large generated output.\n",
        "logs/topics/project-start.md": f"---\ntopic: project-start\ntitle: Project start\ncreated: {today}\nupdated: {today}\nstatus: active\n---\n\n## {today} — discussion\n\nProject skeleton created. Charter, first gate, and source inventory remain to be completed.\n",
        "docs/project/decisions/.gitkeep": "",
        "docs/project/handoffs/.gitkeep": "",
        "docs/coordination/nodes/README.md": "# Execution nodes\n\nRegister local or remote machines here. Record stable identity, role, capabilities, restrictions, repository location, and data access policy.\n",
        "docs/coordination/roles/README.md": "# Roles\n\nDefine what a role may change, what it may execute, and what requires human approval.\n",
        "docs/validation/executions/.gitkeep": "",
        "manifests/environments.yaml": "schema_version: 1\nenvironments: []\n",
        "manifests/.gitkeep": "",
        "tests/.gitkeep": "",
        "data/README.md": "# Data\n\nKeep raw experimental data outside ordinary Git. Record metadata, locator, hash, and access policy here.\n",
    }
    for relative, content in files.items():
        write_new(root, relative, content)
    skill_root = Path(__file__).resolve().parents[1]
    copy_template(root, skill_root, "decision.md", "docs/project/decisions/_template.md")
    copy_template(root, skill_root, "agent-instructions.md", "AGENTS.md")
    copy_template(root, skill_root, "evidence.yaml", "docs/validation/_template.yaml")
    copy_template(root, skill_root, "handoff.yaml", "docs/project/handoffs/_template.yaml")
    copy_template(root, skill_root, "source.yaml", "docs/provenance/source-template.yaml")
    copy_template(root, skill_root, "artifact.yaml", "docs/validation/artifact-template.yaml")
    copy_template(root, skill_root, "failure.md", "logs/topics/failure-template.md")
    copy_template(root, skill_root, "environment.yaml", "docs/coordination/nodes/_template.yaml")
    copy_template(root, skill_root, "execution.yaml", "docs/validation/executions/_template.yaml")
    copy_template(root, skill_root, "figure.md", "docs/validation/figure-template.md")
    copy_template(root, skill_root, "results-index.md", "docs/validation/results-index.md")
    copy_template(root, skill_root, "study-log.md", "logs/topics/study-template.md")
    write_new(root, "docs/project/reporting-policy.md",
              (skill_root / "references/reporting-policy.md").read_text(encoding="utf-8"))
    if revision:
        try:
            result = install(integration_root, revision)
            if result["status"] != "PASS":
                parser.error("; ".join(result["issues"]))
            if integration_root != root:
                policy = root / "AGENTS.md"
                text = policy.read_text()
                if MARKER not in text:
                    text += "\n" + MARKER + "\n## Research figures\n\nResolve plotting from the containing Git repository root. Read `.agents/skills/research-plot/SKILL.md` there; its pinned dependency and manifest are shared with this nested project. Preserve this project's calculation and provenance conventions.\n"
                    policy.write_text(text)
        except ValueError as exc:
            parser.error(str(exc))
    print(f"Initialized {project_id} at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
