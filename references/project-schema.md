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

Classify records during a staged migration:

- `native`: follows the Research Project OS schema directly;
- `mapped`: an explicit profile maps the existing record to the role;
- `legacy`: human-readable but only partially machine-validated.

Do not create a second copy of a `mapped` record. Profile-aware validation may report a `legacy` schema warning without treating it as a reason to rewrite the existing record.

## Machine validation boundaries

YAML is parsed with PyYAML's safe loader and duplicate mapping keys are rejected.
Tasks must be a list of mappings with unique string IDs and valid statuses.
`depends_on` accepts flow or block lists and every referenced ID must exist.
`DONE` requires a non-empty list of non-placeholder `completion_evidence` references.
This is a structural requirement, not proof of the evidence contents or a scientific
completion verdict. Existing human review and domain-specific gates still apply.

Profiles are explicit contracts: a requested missing, malformed or empty profile
fails. Quoted paths and YAML comments are supported. Even a partial profile must
resolve an existing current state and task board, using defaults for omitted roles.
Context Pack file resolution rejects traversal and symlinks leaving the project.

## Reporting records

[Reporting policy](reporting-policy.md) defines figure explanation/provenance,
meaningful work records and commits, and master's-level explanations with defined
terms. New scaffolds include `docs/project/reporting-policy.md`,
`docs/validation/figure-template.md` and `logs/topics/study-template.md`.
Figure records may reuse Artifact/Evidence/Execution references. Existing projects
can use equivalent records at established paths; no bulk migration is required.
New explanatory fields are additive; old records remain valid. Readability and
scientific interpretation require content review rather than string checks.

Calculations and figures must have the information necessary and sufficient for
reproduction from inputs. The generated `docs/validation/results-index.md`, linked
from the project README, connects question/Task context, studies, executions,
evidence and artifacts. Existing projects may keep an equivalent index at their
established entrypoint. Procedure documentation and verified reproduction are
separate states; unresolved prerequisites remain explicit.
