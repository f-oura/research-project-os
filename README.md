# Research Project OS

Research Project OS is a lightweight, Git-managed operating model for research projects and AI collaboration.

It keeps the project purpose, current state, tasks, decisions, provenance, validation evidence, logs, handoffs, and execution environments in human-readable Markdown/YAML. Raw experimental data, credentials, and generated build artifacts remain outside ordinary Git history.

`--kind` supports `research`, `analysis`, `calculation`, `detector`, `daq-firmware`, `simulation`, and `paper`. Use `calculation` for analytical or numerical theory work; reserve `simulation` for executable simulations or Monte Carlo workflows.

## Included

- `SKILL.md`: operating instructions for Codex/agent collaboration
- `scripts/bootstrap_project.py`: create a new project skeleton
- `templates/agent-instructions.md`: generated `AGENTS.md` for the project execution agent
- `scripts/validate_project.py`: check project invariants
- `scripts/context_pack.py`: build a purpose-limited agent context pack
- `scripts/register_environment.py`: register local/remote execution environments
- `scripts/record_execution.py`: bind a Task run to an environment, commit, and evidence
- `templates/`: decision, evidence, handoff, source, artifact, environment, execution, and failure records
- `profiles/`: compatibility mappings for existing project layouts
- `references/`: schema, workflow, and design philosophy

## Quick start

Use Python 3.10+ with the declared YAML dependency. Install into your chosen
virtual environment before running validation or profile/context tools:

```bash
python3 -m pip install -r requirements.txt
```

```bash
python3 scripts/bootstrap_project.py /path/to/project \\
  --name my-project \\
  --title "My Research Project" \\
  --kind analysis

python3 scripts/validate_project.py /path/to/project

# For an existing repository with mapped or legacy paths:
python3 scripts/validate_project.py /path/to/project \\
  --profile profiles/amaneq-receiver.yaml

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

python3 -m unittest discover -s tests -v
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

## Shared plotting

New scaffolds include the bundled full-SHA pin from `config/plotting.json` at
`vendor/custom-plot` and a discoverable `.agents/skills/research-plot/SKILL.md`
that reads the canonical submodule skill. Bootstrap initializes Git only for a
new empty target; existing non-Git targets require explicit initialization or
`--without-plotting`. Nested projects use one plotting integration at the containing
Git repository root and refer to its skill; they do not create another submodule. The dependency is cloned when bootstrapping, so GitHub
access is needed. A missing dependency fails with a clear error; no Python
environment is installed.

```bash
# Add to an existing Git project without moving its records:
python3 scripts/install_plotting.py PROJECT --profile PROFILE
# Read-only runtime check with an existing Python 3.10+ interpreter:
python3 scripts/install_plotting.py PROJECT --check --python /path/to/python
# Initialize the committed pin after a non-recursive clone:
git submodule update --init -- vendor/custom-plot
```

Profiles can map `plot_dependency`, `plot_skill`, and `plot_manifest` alongside
the existing canonical roles. This changes the dependency location rather than
creating duplicate project records. The installer refuses occupied destinations
and dirty `.gitmodules`; an identical integration is idempotent. It stages only
`.gitmodules` and the gitlink; review and commit the skill, manifest, and AGENTS
change together before using it as a durable project revision. Do not use
`submodule update --remote` in routine figure production. To adopt a new version,
review the source, update the gitlink and manifest revision together, and rerun
the check. Existing calculation and figure provenance conventions still apply.

## Validation and context boundaries

- An explicitly supplied profile must exist and contain a non-empty `canonical`
  mapping. Missing/invalid profiles fail; they never silently select defaults.
- Validation parses YAML and rejects duplicate keys, malformed records, duplicate
  Task IDs and unknown dependencies (both flow and block lists). State and task
  board remain required with partial profiles. A `DONE` Task must have non-empty,
  non-`UNBOUND` completion evidence references. `PASS` checks record structure; it
  does not certify the referenced evidence, scientific claim, or hardware approval.
- Context sources must resolve within the project, including symlink targets and
  references inside Tasks. Copying external materials into a pack requires a
  separately reviewed provenance/access workflow, not a traversal path.
- Source commit, tool revision, agent policy, full current state, environments,
  and target Task are mandatory context. Insufficient `--max-chars` or
  `--max-task-chars` fails without emitting a pack; increase the relevant budget.
  Optional sections may be omitted with a notice; individual optional excerpts
  can still be marked `[truncated]`. Consult their canonical records before acting.
- Task YAML is parsed and serialized; YAML comments are not part of the selected
  Task record. Put operational constraints in fields or the agent policy.
  Redaction is best effort, not a guarantee that arbitrary secrets are removed.

Run the regression suite with `python3 -m unittest discover -s tests -v` in the
same environment. Tests use temporary fixtures and do not contact hardware.
