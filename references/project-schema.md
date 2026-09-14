# Project record schema

The schema is intentionally file-based. YAML is used for small machine-readable state; Markdown is used for reasoning and records that need human review.

## Required records

```text
project.yaml                         identity, kind, owner, phase
README.md                            entry point and navigation
AGENTS.md                            project-specific agent rules
docs/project/charter.md              question, hypotheses, scope, completion
docs/project/current-state.yaml      phase, next action, gates, last validated commit
docs/project/task-board.yaml         dependency-aware tasks
docs/project/decisions/              approved or superseded decisions
docs/project/handoffs/               bounded transfer between agents/sessions
docs/provenance/                     source, version, license, locator records
docs/validation/                     expected/observed evidence
logs/topics/                         append-only topic history
manifests/                           environment and input versions
manifests/environments.yaml           registered execution environments
docs/coordination/nodes/              remote/local node records
docs/coordination/roles/              allowed responsibilities and restrictions
docs/validation/executions/           task execution records
tests/                               reproducible checks and reference vectors
```

## Project kinds

The bootstrap script accepts the following controlled vocabulary for `project.yaml:kind`:

- `research`: general research project
- `analysis`: analysis of existing data or measurements
- `calculation`: analytical or numerical theory calculation
- `detector`: detector development
- `daq-firmware`: DAQ or firmware development
- `simulation`: executable simulation or Monte Carlo workflow
- `paper`: paper-focused project

## Task minimum

Every task should define: `id`, `title`, `owner_role`, `status`, `depends_on`, `scope.in`, `scope.out`, `completion_evidence`, and `human_approval_required` when relevant.

Recommended statuses are `READY`, `RUNNING`, `REVIEW`, `BLOCKED`, and `DONE`. A task is not `DONE` without concrete completion evidence.

## Evidence minimum

Every evidence record should identify: the claim tested, input/source locator, source version or commit, method, validation stage, expected behavior, observed behavior, result, and whether it was human-reviewed.

## Decision minimum

Every decision should identify: the decision question, selected option, rejected alternatives, rationale, evidence IDs, owner/approver, date, scope, and any decision it supersedes.

## Execution environment minimum

An environment record should identify: stable environment ID, host identity, repository locator, working directory, tool versions, capabilities, restrictions, data mounts, and verification date. An execution record binds a Task to an environment, role, source commit, procedure, inputs, outputs, and validation evidence.

Create execution records with `scripts/record_execution.py`. The command verifies that the Task and environment are registered, but it does not change Task status; review and completion remain explicit.

## Uncertainty rules

Use `UNBOUND` for values not tied to an authoritative document, measurement, or human decision. Keep `PROVISIONAL` separate from `CONFIRMED`. A newer file does not automatically supersede an older decision; record an explicit supersession or contradiction.

## Existing project compatibility

Existing projects may keep their established paths. Use a project profile to map roles such as `current_state`, `task_board`, `handoffs`, and `logs` to those paths. Audit first, report differences, and only migrate files when the mapping is insufficient.
