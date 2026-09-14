# Research Project OS

Research Project OS is a lightweight, Git-managed operating model for research projects and AI collaboration.

It keeps the project purpose, current state, tasks, decisions, provenance, validation evidence, logs, handoffs, and execution environments in human-readable Markdown/YAML. Raw experimental data, credentials, and generated build artifacts remain outside ordinary Git history.

## Included

- `SKILL.md`: operating instructions for Codex/agent collaboration
- `scripts/bootstrap_project.py`: create a new project skeleton
- `scripts/validate_project.py`: check project invariants
- `scripts/context_pack.py`: build a purpose-limited agent context pack
- `templates/`: decision, evidence, handoff, source, artifact, environment, execution, and failure records
- `references/`: schema, workflow, and design philosophy

## Quick start

```bash
python3 scripts/bootstrap_project.py /path/to/project \\
  --name my-project \\
  --title "My Research Project" \\
  --kind analysis

python3 scripts/validate_project.py /path/to/project

python3 scripts/context_pack.py /path/to/project \\
  --task PLAN-001 \\
  --purpose "initial agent briefing"
```

## Design boundary

This repository manages one research project at a time. A future Portfolio OS may manage priorities across multiple projects, but is intentionally outside the current scope.
