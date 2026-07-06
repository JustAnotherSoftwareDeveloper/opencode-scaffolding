import { cli } from "cleye";
import { DEFAULT_MODELS, runBreakdownModelEval } from "../lib/eval-breakdown-models/core.ts";
import { ExitCode } from "../lib/shared/exit-codes.ts";
import { die } from "../lib/shared/format.ts";

cli({
  name: "eval-breakdown-models",
  version: "1.0.0",
});

interface CliOptions {
  endpoint?: string;
  models?: string[];
  output?: string;
  pull?: boolean;
  timeoutMs?: number;
}

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2));
  try {
    const results = await runBreakdownModelEval(options);
    const passed = results.filter((result) => result.pass).length;
    process.stdout.write(
      `${JSON.stringify({ output: options.output ?? "/tmp/opencode/breakdown-model-eval.json", passed, total: results.length }, null, 2)}\n`,
    );
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    die(`Error: eval failed: ${message}`, ExitCode.CONFIG_ERROR);
  }
}

function parseArgs(args: string[]): CliOptions {
  const options: CliOptions = {};
  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];
    if (arg === "--help" || arg === "-h") {
      process.stdout.write(helpText());
      process.exit(ExitCode.CLEAN);
    }
    if (arg === "--pull") {
      options.pull = true;
      continue;
    }
    const next = args[index + 1];
    if (!next) die(`Error: missing value for ${arg}`, ExitCode.INVALID_INPUT);
    if (arg === "--endpoint") options.endpoint = next;
    else if (arg === "--models")
      options.models = next
        .split(",")
        .map((model) => model.trim())
        .filter(Boolean);
    else if (arg === "--output") options.output = next;
    else if (arg === "--timeout-ms") options.timeoutMs = Number(next);
    else die(`Error: unknown option ${arg}`, ExitCode.INVALID_INPUT);
    index += 1;
  }
  if (
    options.timeoutMs !== undefined &&
    (!Number.isInteger(options.timeoutMs) || options.timeoutMs <= 0)
  ) {
    die("Error: --timeout-ms must be a positive integer", ExitCode.INVALID_INPUT);
  }
  return options;
}

function helpText(): string {
  return `Usage: bun run --cwd scripts/node eval:breakdown-models -- [options]

Options:
  --models <csv>       Comma-separated Ollama model names. Defaults to: ${DEFAULT_MODELS.join(",")}
  --output <path>      Results JSON path. Defaults to /tmp/opencode/breakdown-model-eval.json
  --endpoint <url>     Chat completions endpoint. Defaults to http://localhost:11434/v1/chat/completions
  --timeout-ms <ms>    Per-request timeout. Defaults to 900000
  --pull              Pull each model before testing
  --help              Show this help
`;
}

await main();
