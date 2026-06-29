# Exit Codes

Use standard exit codes matching Python and Node conventions:

- **0** — Success.
  Use when: Normal completion.
- **1** — Runtime error.
  Use when: File not found, command failed, unexpected condition.
- **2** — Usage error.
  Use when: Invalid arguments, missing required option, `--help` invoked.
- **3** — Environment error.
  Use when: Missing dependency, wrong bash version, unsupported OS.