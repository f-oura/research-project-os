# Agent handoff workflow

Use a bounded handoff rather than relying on chat history.

```text
goal -> allowed scope -> inputs and source revisions -> commands/tests -> expected evidence -> stop conditions -> next action
```

At session start, read:

1. `README.md`
2. `docs/project/current-state.yaml`
3. `docs/project/task-board.yaml`
4. the task's linked handoff, decision, specification, and validation records

When the task runs on a remote node, also confirm the registered environment, role, capabilities, restrictions, repository commit, and data access policy. A server-local path or cache is not a project fact until its locator and provenance are recorded.

At session end, record:

- files changed and why;
- commands/tests run and their result;
- evidence artifact paths and source commit;
- unresolved questions or newly discovered blockers;
- exact next action and whether human approval is required.
- execution environment, tool versions, and source commit when work ran outside the controller's checkout;

Do not claim hardware or production validation from simulation/build results. Do not access an unrelated board, port, dataset, or external account merely because it is visible in the environment.
