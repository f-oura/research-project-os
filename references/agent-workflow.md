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

## Meaningful checkpoints

Apply [the reporting policy](reporting-policy.md) at results, changes of conditions,
failures and interruptions. Use `templates/study-log.md` or equivalent topic records;
link execution details instead of duplicating them. Commit a coherent change with
its records and checks, or record the concrete reason a checkpoint cannot be made.
Report unrun checks and remaining changes explicitly. Commit and push are distinct.

At handoff, review figure captions/conditions, study records and first-use term
definitions. A reader with relevant master's-level fundamentals should be able to
follow the reasoning without prior project knowledge. Content review complements
structural validation; it is not certified by a validator's PASS result.
