import { cli } from "cleye";
import { exampleMessage } from "../lib/example/core.ts";
import { ExitCode } from "../lib/shared/exit-codes.ts";
import { die } from "../lib/shared/format.ts";

cli({
  name: "example",
  version: "1.0.0",
  parameters: ["<name>"],
});

async function main(): Promise<void> {
  const name = process.argv[2];

  if (!name) {
    die(
      "Error: no name provided. Usage: bun run --cwd scripts/node example -- <name>",
      ExitCode.INVALID_INPUT,
    );
  }

  const greeting = exampleMessage(name);
  console.log(greeting);
}

await main();
