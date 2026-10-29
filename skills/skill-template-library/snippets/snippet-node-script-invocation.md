# Script Invocation (Node)

**Script invocation (Node):**

```shell
bun run --cwd ~/.config/opencode/scripts/node <entry-point> [args]
```

- **Entry point** — Use the path, relative to `~/.config/opencode/scripts/node` (under `src/cli/`), of the Node CLI script selected by the containing skill as `<entry-point>`. Replace the placeholder with that concrete path when instantiating this snippet.
- **CLI definition** — Define the CLI with `cleye`: import it and export a typed `argv` parser.
- **Exit codes** use the `ExitCode` enum from `@opencode/scripts` (e.g., `ExitCode.SUCCESS`, `ExitCode.BLOCKED`).
- **Die helper** — call `die(message, exitCode?)` for early termination with a non-zero exit.
- **Capture stdout** as structured output (JSON preferred).
- **Test file** — Add a sibling `.test.ts` file that stubs the CLI argv and asserts the exit code.
- **Python-primary / Node-secondary** — prefer Python scripts unless the toolchain or ecosystem (npm packages, bundlers, TypeScript) justifies Node.
