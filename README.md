# Research Project OS

Research Project OS is a lightweight, Git-managed operating model for research projects and AI collaboration.

It keeps the project purpose, current state, tasks, decisions, provenance, validation evidence, logs, handoffs, and execution environments in human-readable Markdown/YAML. Raw experimental data, credentials, and generated build artifacts remain outside ordinary Git history.

## Included

- `SKILL.md`: operating instructions for Codex/agent collaboration
- `scripts/bootstrap_project.py`: create a new project skeleton
- `scripts/validate_project.py`: check project invariants
- `scripts/context_pack.py`: build a purpose-limited agent context pack
- `scripts/register_environment.py`: register local/remote execution environments
- `scripts/record_execution.py`: bind a Task run to an environment, commit, and evidence
- `templates/`: decision, evidence, handoff, source, artifact, environment, execution, and failure records
- `profiles/`: compatibility mappings for existing project layouts
- `references/`: schema, workflow, and design philosophy

## Quick start

```bash
python3 scripts/bootstrap_project.py /path/to/project \\
  --name my-project \\
  --title "My Research Project" \\
  --kind analysis

python3 scripts/validate_project.py /path/to/project

python3 scripts/register_environment.py /path/to/project \\
  --id analysis-server-01 \\
  --name "Analysis server" \\
  --kind remote \\
  --host HOST_ID \\
  --repository /path/to/project \\
  --workdir /path/to/project \\
  --capability Python \\
  --restriction no-hardware-programming \\
  --tool Python=UNBOUND

python3 scripts/record_execution.py /path/to/project \\
  --id EXE-001 \\
  --task PLAN-001 \\
  --environment analysis-server-01 \\
  --role analysis \\
  --commit abc123 \\
  --command "python scripts/analyze.py" \\
  --validation docs/validation/EVD-001.yaml

python3 scripts/context_pack.py /path/to/project \\
  --task PLAN-001 \\
  --purpose "initial agent briefing"
```

For an existing project with custom paths, run the audit first and pass a profile:

```bash
python3 scripts/audit_project.py /path/to/existing-project
python3 scripts/context_pack.py /path/to/existing-project \\
  --profile profiles/amaneq-receiver.yaml \\
  --task TASK-001 \\
  --purpose "compatibility pilot"
```

## Design boundary

This repository manages one research project at a time. A future Portfolio OS may manage priorities across multiple projects, but is intentionally outside the current scope.
