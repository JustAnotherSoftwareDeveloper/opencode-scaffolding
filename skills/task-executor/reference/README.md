# Task Execution Contract

This reference summarizes how to execute one approved task inline; it does not authorize replanning, reassignment, or delegation.

- Accept exactly one canonical `TaskPacket` object; its top-level `verification` field is optional.
- Load only the task-declared skills, in listed order, as inline context.
- Follow the task's read, write, execution, verification, and output boundaries.
- Do not invoke the `task` tool or delegate to a worker.
