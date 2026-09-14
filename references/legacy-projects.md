# Existing project compatibility

Use the compatibility workflow when a repository already has useful plans, logs, task boards, validation records, or coordination files.

1. Run `scripts/audit_project.py PROJECT` in read-only mode.
2. Review detected canonical records and warnings.
3. Create a profile from `templates/project-profile.yaml` if paths differ from the default layout.
4. Generate a Task-specific pack with `scripts/context_pack.py PROJECT --profile PROFILE --task TASK-ID --purpose PURPOSE`.
5. Migrate or rename files only after the profile-based workflow has been tested and the change is explicitly accepted.

The audit exit status is `0` for a fully standard layout and `2` for a usable but partial/legacy layout. A partial result is not a project failure; it is a migration or mapping signal.
