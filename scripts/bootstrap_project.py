#!/usr/bin/env python3
"""Create a lightweight, agent-ready research project skeleton."""
from __future__ import annotations

import argparse
import re
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
    args = parser.parse_args()

    root = args.path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    project_id = slug(args.name)
    files = {
        "project.yaml": f"schema_version: 1\nproject_id: {project_id}\ntitle: {args.title}\nkind: {args.kind}\nowner: {args.owner}\ncreated: {today}\nphase: PLANNING\nstatus: ACTIVE\n",
        "README.md": f"# {args.title}\n\nProject ID: `{project_id}`\n\nStart here:\n\n- [charter](docs/project/charter.md)\n- [current state](docs/project/current-state.yaml)\n- [task board](docs/project/task-board.yaml)\n- [provenance](docs/provenance/README.md)\n- [validation](docs/validation/README.md)\n- [topic logs](logs/README.md)\n\nUnknown values remain `UNBOUND` until bound to evidence or a human decision.\n",
        "AGENTS.md": "# Agent rules\n\nTreat this project as an evidence chain. Read the current state and task board before editing. Keep changes small and reviewable. Do not access hardware, send external data, publish results, or change irreversible state without explicit human approval. Keep secrets, raw data, and generated build directories out of Git. Record validation evidence and update the handoff when state changes.\n",
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
    copy_template(root, skill_root, "evidence.yaml", "docs/validation/_template.yaml")
    copy_template(root, skill_root, "handoff.yaml", "docs/project/handoffs/_template.yaml")
    copy_template(root, skill_root, "source.yaml", "docs/provenance/source-template.yaml")
    copy_template(root, skill_root, "artifact.yaml", "docs/validation/artifact-template.yaml")
    copy_template(root, skill_root, "failure.md", "logs/topics/failure-template.md")
    copy_template(root, skill_root, "environment.yaml", "docs/coordination/nodes/_template.yaml")
    copy_template(root, skill_root, "execution.yaml", "docs/validation/executions/_template.yaml")
    print(f"Initialized {project_id} at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
