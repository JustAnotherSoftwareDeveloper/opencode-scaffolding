# Script Invocation (Node)

**Script invocation (Node):**

```shell
bun run --cwd ~/.config/opencode/scripts/node <entry-point> [args]
```

- **CLI definition** uses `cleye` — import `cleye` and export a typed `argv` parser.
- **Exit codes** use the `ExitCode` enum from `@opencode/scripts` (e.g., `ExitCode.SUCCESS`, `ExitCode.BLOCKED`).
- **Die helper** — call `die(message, exitCode?)` for early termination with a non-zero exit.
- **Capture stdout** as structured output (JSON preferred).
- **Test file** — create a `.test.ts` sibling stubbing the CLI argv and asserting the exit code.
- **Python-primary / Node-secondary** — prefer Python scripts unless the toolchain or ecosystem (npm packages, bundlers, TypeScript) justifies Node.
