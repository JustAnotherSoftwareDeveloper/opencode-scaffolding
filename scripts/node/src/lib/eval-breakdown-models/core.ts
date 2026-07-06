import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

export const DEFAULT_MODELS = [
  "north-mini-code-1.0:q4_K_M",
  "laguna-xs-2.1:q4_K_M",
  "ornith:35b",
  "ornith:9b",
  "glm-4.7-flash:q4_K_M",
  "qwen3.6:35b",
  "gemma4:26b",
];

const DEFAULT_ENDPOINT = "http://localhost:11434/v1/chat/completions";
const DEFAULT_OUTPUT = "/tmp/opencode/breakdown-model-eval.json";
const DEFAULT_TIMEOUT_MS = 900_000;

const TESTS: EvalTest[] = [
  {
    name: "echo_three",
    request: "Break this request into atomic worker packets: run echo 1, echo 2, and echo 3.",
    check: (output) => {
      const errors: string[] = [];
      if (output.tasks.length !== 3) errors.push(`expected 3 tasks, got ${output.tasks.length}`);
      for (const [index, task] of output.tasks.entries()) {
        const expected = String(index + 1);
        const joined = `${task.purpose} ${task.context} ${task.expectedOutput} ${task.executionInstructions
          .map((step) => step.action)
          .join(" ")}`;
        if (!joined.includes(expected))
          errors.push(`task ${index} does not clearly target ${expected}`);
      }
      return errors;
    },
  },
  {
    name: "dark_mode_unknown_paths",
    request:
      "Break this request into atomic worker packets: add a dark mode toggle, persist the preference, update README docs, and add tests. No repository file tree has been provided, so do not invent specific file paths.",
    check: (output) => {
      const errors: string[] = [];
      if (
        output.tasks.some((task) => task.filesToRead.length > 0 || task.filesToWrite.length > 0)
      ) {
        errors.push("invented file paths when none were provided");
      }
      if (output.tasks.length < 3)
        errors.push(`expected at least 3 tasks, got ${output.tasks.length}`);
      return errors;
    },
  },
  {
    name: "skill_creation",
    request:
      "Break this request into atomic worker packets: create a new OpenCode skill named release-notes-writer that generates release notes from git history, with docs and validation.",
    check: (output) => {
      const skills = new Set(output.tasks.flatMap((task) => task.skills));
      const errors: string[] = [];
      if (!skills.has("skill-factory")) errors.push("missing skill-factory assignment");
      if (
        !output.tasks.some((task) =>
          task.filesToWrite.some((file) => file.includes("skills/release-notes-writer")),
        )
      ) {
        errors.push("missing expected skill path in filesToWrite");
      }
      return errors;
    },
  },
  {
    name: "script_task",
    request:
      "Break this request into atomic worker packets: create a TypeScript Node CLI script to validate task JSON files and add tests for it.",
    check: (output) => {
      const skills = new Set(output.tasks.flatMap((task) => task.skills));
      const errors: string[] = [];
      if (!skills.has("skill-script-node-writer"))
        errors.push("missing skill-script-node-writer assignment");
      if (!skills.has("skill-script-node-test-writer"))
        errors.push("missing skill-script-node-test-writer assignment");
      return errors;
    },
  },
];

export interface EvalOptions {
  endpoint?: string;
  models?: string[];
  output?: string;
  pull?: boolean;
  rootDir?: string;
  timeoutMs?: number;
}

export interface EvalResult {
  model: string;
  test: string;
  pass: boolean;
  parseError: string | null;
  schemaErrors: string[];
  semanticErrors: string[];
  finish: string | null;
  usage: unknown;
  seconds: number;
  contentPreview: string;
}

interface EvalTest {
  name: string;
  request: string;
  check: (output: BreakdownOutput) => string[];
}

interface BreakdownOutput {
  summary: string;
  tasks: TaskPacket[];
}

interface TaskPacket {
  purpose: string;
  context: string;
  filesToRead: string[];
  filesToWrite: string[];
  skills: string[];
  executionInstructions: ExecutionStep[];
  verification?: string[];
  expectedOutput: string;
}

interface ExecutionStep {
  step: number;
  action: string;
  verification?: string;
}

export async function runBreakdownModelEval(options: EvalOptions = {}): Promise<EvalResult[]> {
  const endpoint = options.endpoint ?? DEFAULT_ENDPOINT;
  const models = options.models?.length ? options.models : DEFAULT_MODELS;
  const output = options.output ?? DEFAULT_OUTPUT;
  const rootDir = resolve(options.rootDir ?? process.cwd(), "../..");
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const availableSkills = readAvailableSkills(rootDir);
  const results: EvalResult[] = [];

  for (const model of models) {
    if (options.pull) pullModel(model);
    for (const test of TESTS) {
      results.push(await runOneEval({ endpoint, model, test, availableSkills, timeoutMs }));
      writeJson(output, results);
    }
  }

  return results;
}

function readAvailableSkills(rootDir: string): Set<string> {
  const skillsDir = resolve(rootDir, "skills");
  if (!existsSync(skillsDir)) return new Set();
  return new Set(
    readdirSync(skillsDir, { withFileTypes: true })
      .filter(
        (entry) => entry.isDirectory() && existsSync(resolve(skillsDir, entry.name, "SKILL.md")),
      )
      .map((entry) => entry.name),
  );
}

function pullModel(model: string): void {
  const result = spawnSync("ollama", ["pull", model], { encoding: "utf8", stdio: "inherit" });
  if (result.status !== 0) {
    throw new Error(`ollama pull failed for ${model}`);
  }
}

async function runOneEval(input: {
  endpoint: string;
  model: string;
  test: EvalTest;
  availableSkills: Set<string>;
  timeoutMs: number;
}): Promise<EvalResult> {
  const started = Date.now();
  let content = "";
  let finish: string | null = null;
  let usage: unknown = null;
  let parseError: string | null = null;
  let schemaErrors: string[] = [];
  let semanticErrors: string[] = [];

  try {
    const response = await fetch(input.endpoint, {
      method: "POST",
      signal: AbortSignal.timeout(input.timeoutMs),
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        model: input.model,
        messages: [
          { role: "system", content: buildSystemPrompt(input.availableSkills) },
          { role: "user", content: input.test.request },
        ],
        temperature: 0.2,
        max_tokens: 4096,
        stream: false,
      }),
    });

    if (!response.ok) {
      parseError = `HTTP ${response.status}: ${await response.text()}`;
    } else {
      const body = (await response.json()) as ChatCompletionResponse;
      const choice = body.choices?.[0];
      content = choice?.message?.content ?? "";
      finish = choice?.finish_reason ?? null;
      usage = body.usage ?? null;

      try {
        const parsed = JSON.parse(content) as unknown;
        schemaErrors = validateBreakdownOutput(parsed, input.availableSkills);
        if (schemaErrors.length === 0) semanticErrors = input.test.check(parsed as BreakdownOutput);
      } catch (err) {
        parseError = err instanceof Error ? err.message : String(err);
      }
    }
  } catch (err) {
    parseError = err instanceof Error ? err.message : String(err);
  }

  return {
    model: input.model,
    test: input.test.name,
    pass: parseError == null && schemaErrors.length === 0 && semanticErrors.length === 0,
    parseError,
    schemaErrors,
    semanticErrors,
    finish,
    usage,
    seconds: Number(((Date.now() - started) / 1000).toFixed(2)),
    contentPreview: content.slice(0, 2000),
  };
}

interface ChatCompletionResponse {
  choices?: Array<{
    finish_reason?: string;
    message?: { content?: string };
  }>;
  usage?: unknown;
}

function buildSystemPrompt(availableSkills: Set<string>): string {
  return `You are the breakdown-tasks skill. Return only valid JSON, no markdown fences, no commentary.

Output shape:
{
  "summary": "one paragraph",
  "tasks": [{
    "purpose": "single atomic purpose",
    "context": "worker context",
    "filesToRead": [],
    "filesToWrite": [],
    "skills": ["one to three exact skill names"],
    "executionInstructions": [{"step": 1, "action": "concrete action", "verification": "optional check"}],
    "verification": ["optional top-level checks"],
    "expectedOutput": "precise deliverable"
  }]
}

Rules:
- Use only these available skills: ${Array.from(availableSkills).sort().join(", ")}.
- Do not invent file paths. If no repository files are supplied, leave filesToRead and filesToWrite empty unless the request names an exact path.
- Split independent work into atomic tasks.
- Step numbers inside each task must start at 1 and increase by 1.
- Do not include additional object fields.`;
}

function validateBreakdownOutput(value: unknown, availableSkills: Set<string>): string[] {
  const errors: string[] = [];
  if (!isObject(value)) return ["top-level output is not an object"];
  const keys = Object.keys(value);
  for (const key of keys) {
    if (!["summary", "tasks"].includes(key)) errors.push(`unknown top-level field ${key}`);
  }
  if (typeof value.summary !== "string") errors.push("summary must be string");
  if (!Array.isArray(value.tasks) || value.tasks.length === 0) {
    errors.push("tasks must be non-empty array");
    return errors;
  }

  for (const [index, task] of value.tasks.entries()) {
    validateTask(task, index, availableSkills, errors);
  }
  return errors;
}

function validateTask(
  value: unknown,
  index: number,
  availableSkills: Set<string>,
  errors: string[],
): void {
  if (!isObject(value)) {
    errors.push(`task ${index} is not an object`);
    return;
  }
  const allowed = [
    "purpose",
    "context",
    "filesToRead",
    "filesToWrite",
    "skills",
    "executionInstructions",
    "verification",
    "expectedOutput",
  ];
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) errors.push(`task ${index} unknown field ${key}`);
  }
  for (const key of ["purpose", "context", "expectedOutput"] as const) {
    if (typeof value[key] !== "string") errors.push(`task ${index} ${key} must be string`);
  }
  for (const key of ["filesToRead", "filesToWrite"] as const) {
    if (!isStringArray(value[key])) errors.push(`task ${index} ${key} must be string array`);
  }
  if (!isStringArray(value.skills) || value.skills.length < 1 || value.skills.length > 3) {
    errors.push(`task ${index} skills must contain 1 to 3 strings`);
  } else {
    for (const skill of value.skills) {
      if (!availableSkills.has(skill)) errors.push(`task ${index} unknown skill ${skill}`);
    }
  }
  if (value.verification !== undefined && !isStringArray(value.verification)) {
    errors.push(`task ${index} verification must be string array`);
  }
  validateSteps(value.executionInstructions, index, errors);
}

function validateSteps(value: unknown, taskIndex: number, errors: string[]): void {
  if (!Array.isArray(value) || value.length === 0) {
    errors.push(`task ${taskIndex} executionInstructions must be non-empty array`);
    return;
  }
  for (const [stepIndex, step] of value.entries()) {
    if (!isObject(step)) {
      errors.push(`task ${taskIndex} step ${stepIndex} is not an object`);
      continue;
    }
    for (const key of Object.keys(step)) {
      if (!["step", "action", "verification"].includes(key)) {
        errors.push(`task ${taskIndex} step ${stepIndex} unknown field ${key}`);
      }
    }
    if (step.step !== stepIndex + 1) errors.push(`task ${taskIndex} step numbering`);
    if (typeof step.action !== "string")
      errors.push(`task ${taskIndex} step ${stepIndex} action must be string`);
    if (step.verification !== undefined && typeof step.verification !== "string") {
      errors.push(`task ${taskIndex} step ${stepIndex} verification must be string`);
    }
  }
}

function writeJson(path: string, data: unknown): void {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(data, null, 2)}\n`);
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return (
    Array.isArray(value) &&
    value.every((item) => typeof item === "string") &&
    new Set(value).size === value.length
  );
}
