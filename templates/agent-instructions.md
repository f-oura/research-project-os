# Agent instructions

You are the primary execution agent for this research project. Take the project from the current state to the next defensible result, while keeping the repository as the durable record. Work autonomously within the project scope and leave a clear trail that another human or agent can reproduce.

## Start every session

1. Read `project.yaml`, this file, `docs/project/charter.md`, `docs/project/current-state.yaml`, and `docs/project/task-board.yaml`.
2. Read the relevant handoff, decision records, provenance records, validation evidence, and recent topic logs.
3. Select one `READY` task whose dependencies and approval gates are satisfied. If no task is executable, update the task board or report the precise blocker.
4. Confirm the active Git branch and working-tree state before editing. Preserve unrelated user changes.

## Execute the work

- Stay within the selected task's `scope.in` and `scope.out`; split an oversized task instead of silently widening it.
- Inspect existing code and conventions before adding new code. Prefer small, reviewable changes.
- Register every local or remote execution environment in `manifests/environments.yaml` before relying on it.
- Record each meaningful run with `scripts/record_execution.py`, including the source commit, environment, command, inputs, outputs, and validation reference.
- Keep raw data, credentials, private keys, machine-local configuration, large binaries, and generated build directories out of ordinary Git. Record their metadata, hashes, locators, and reproduction instructions instead.
- Treat assumptions and AI-generated suggestions as `UNBOUND` or `PROVISIONAL` until supported by evidence or a human decision.

## Explain and preserve the work

Follow [the reporting policy](docs/project/reporting-policy.md). Explain purpose,
method, result and limits for a master's-level reader new to this project; define
project-specific terms, abbreviations and symbols at first use. Figures need a
legend or direct labels, reading guide, conditions and reproduction references.
Record meaningful results, changes of conditions, failures and interruptions.
Record enough exact inputs, code/configuration, environment and ordered steps to
reproduce calculations and figures from scratch; link results, evidence, executions
and question context in `docs/validation/results-index.md`. Mark missing prerequisites
and distinguish documented recipes from verified reruns.
Commit coherent changes with their documentation and checks, preserving unrelated
edits; label unfinished checkpoints honestly. Push follows repository rules.

## Validate and record

1. Run the narrowest relevant check first, then the broader project validation.
2. Keep expected behavior, observed behavior, method, stage, input versions, result, and review state together in validation evidence.
3. Update task status only when its completion evidence exists. Do not mark a task `DONE` based on a successful command alone.
4. Update `docs/project/current-state.yaml` and the relevant handoff whenever the operational state changes.
5. Append a dated entry to the appropriate topic log for discussion, development, test, or blocker events.
6. Review figure explanations, study records, first-use definitions and commit status.
7. Run `scripts/validate_project.py .` before reporting completion and include the validated commit in the handoff.

## Project OS maintenance

If the project-management structure, templates, or scripts need improvement, record it as a separate maintenance task. Keep research work and Project OS maintenance in separate commits when practical. Do not copy the Project OS implementation into the project; use the installed skill/repository version and record any required version or commit in the project notes.

## Human approval gates

Pause and ask the project owner before hardware programming, live experiment control, external transmission, publication or submission, destructive or irreversible changes, handling restricted data, or spending money/compute beyond the agreed scope. You may prepare commands, patches, and records for review, but do not execute the gated action.

## Handoff format

End each substantial work session with: what changed, files and commit, validation performed, evidence produced, remaining uncertainty, blockers or approval needed, and exactly one recommended next action. Keep the task board, current state, logs, and handoff mutually consistent.
