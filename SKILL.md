---
name: research-project-os
description: Bootstrap and operate Git-managed research projects with structured plans, tasks, evidence, decisions, logs, handoffs, and AI-ready context packs. Use when starting a research, analysis, detector, DAQ/firmware, simulation, or paper project, or when standardizing an existing project for agent collaboration.
---

# Research Project OS

Use this skill to make a research project reconstructable by a human or a new AI agent. The project repository is the durable record; generated indexes and context packs are disposable.

## Operating model

- Keep the project self-contained in Git: purpose, current state, plan, tasks, decisions, provenance, validation, code, tests, manifests, logs, and handoffs.
- Treat `README.md` as the entry point, `docs/project/current-state.yaml` as the operational snapshot, and `docs/project/task-board.yaml` as the executable work queue.
- Record important claims with evidence and provenance. Never turn an AI summary, inference, or unverified external value into a confirmed fact.
- Use explicit states such as `CONFIRMED`, `MEASURED`, `REPRODUCED`, `PROVISIONAL`, `UNBOUND`, `BLOCKED`, and `SUPERSEDED`.
- Separate validation stages: simulation, analysis regression, synthesis/build, timing, integration, hardware, and production. Passing one stage does not prove another.
- Append discussion, development, test, and blocker entries to a topic log. Record decisions separately with rationale, alternatives, evidence, owner, and supersession links.
- Keep raw data, credentials, private keys, machine-local configuration, generated build directories, and large binary outputs outside ordinary Git history. Store metadata, hashes, locators, and reproduction instructions.
- Require explicit human approval before hardware programming, live experiment control, external transmission, publication, or irreversible changes.
- Treat remote servers as execution nodes, not separate project truths. Record node role, capabilities, restrictions, source commit, and tool versions.

## When starting a project

1. Ensure Python 3.10+ and the dependencies in `requirements.txt` are available in the chosen environment, then run `scripts/bootstrap_project.py` to create the standard structure and the pinned custom-plot submodule plus discoverable research-plot skill. A new empty target becomes a Git repository. Use `--without-plotting` only for a records-only scaffold. Check the existing plotting interpreter with `scripts/install_plotting.py PROJECT --check --python PYTHON`; report missing dependencies without installing an environment.
2. Fill `docs/project/charter.md` with one decision-changing research or engineering question, competing explanations, observable/discriminator, scope, and completion criteria.
3. Replace placeholders in `current-state.yaml` and `task-board.yaml`; keep unknown values as `UNBOUND`.
4. Define dependency-ordered work packages. Every task must have an owner, inputs, output artifact, validation, gate, and failure response.
5. Add source and version records before relying on external code, data, hardware, or literature.
6. Register relevant execution environments and roles when the project spans local and remote machines.
7. For an existing project, run `scripts/audit_project.py` first and use a project profile for legacy paths instead of moving files prematurely.
8. Add plotting to an existing Git project with `scripts/install_plotting.py PROJECT --profile PROFILE` after reviewing the read-only audit. Map `plot_dependency`, `plot_skill`, and `plot_manifest` in the same canonical profile when needed; preserve native/mapped/legacy asset classifications and source-of-truth records.
9. For a profiled project, pass the same profile to `scripts/validate_project.py`; do not duplicate canonical records just to satisfy the standard layout.
10. Register each execution environment with `scripts/register_environment.py`; do not infer host, tool, or data access facts.
11. Record completed or planned runs with `scripts/record_execution.py`; keep Task completion and execution recording as separate review steps.

## When continuing a project

1. Read the current state, task board, relevant handoff, decision records, and topic logs before editing.
2. Choose one task whose dependencies and gate are satisfied. Do not silently widen its scope.
3. Make the smallest reviewable change, run the narrowest applicable validation first, and record expected versus observed behavior.
4. Update task status, evidence, current state, and handoff in the same change when the project state changes.
5. Run `scripts/validate_project.py` before reporting completion. If context is needed for an agent, generate a purpose-limited pack with `scripts/context_pack.py`.
6. Context packs fail closed for unknown Task IDs, invalid profiles, out-of-project references, and insufficient mandatory-context budgets. They retain the full Task, current state, agent policy, environments, source project commit, and tool revision. Optional excerpts may be omitted or marked truncated; consult canonical records before acting. Redaction is best effort.

## References

- Read [project-schema.md](references/project-schema.md) when creating or reviewing project records.
- Read [agent-workflow.md](references/agent-workflow.md) when handing work between agents, machines, or sessions.
- Read [philosophy.md](references/philosophy.md) when deciding whether a proposed feature belongs in the Project OS or in a future Portfolio OS.
- Read [legacy-projects.md](references/legacy-projects.md) when adapting an existing repository without restructuring it.

## Scope boundary

This skill creates and governs project records. It does not choose among unrelated research programs, certify scientific claims, operate hardware, send external messages, or replace domain-specific planning/review skills. Use `physics-planner`, `physics-code`, `physics-skeptic`, `literature-investigator`, or `project-log` when their specialized workflow is needed.
