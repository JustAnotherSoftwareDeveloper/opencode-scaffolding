---
name: breakdown-tasks
description: "Use when decomposing a request into the smallest possible task-delegation work items."
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.
See `./REFERENCE.md` for atomic task definition and decomposition rules.

## Input Contract

Incoming packet is a standard delegation packet.

## Execution Steps

1. Parse the delegation packet's `## PURPOSE` and `## DETAILS` sections to understand the decomposition goal and the request to decompose.
2. Extract the request from `## DETAILS`.
   Treat `## DETAILS` as the primary input for decomposition.
3. Discover available skills.
   Run `uv run --directory ~/.config/opencode/scripts/python collect-skills`, capture stdout, and parse the JSON array into a list of skill objects (`name`, `description`, `class`, `location`, `source`).
   Hold the list in working memory for the remainder of execution.
   If the command fails (non-zero exit), report `BLOCKED: Unable to discover available skills — collect-skills invocation failed.`
   If the output is an empty array, proceed with an empty skill index.
4. Decompose per `./REFERENCE.md`.
   Split the request into atomic tasks following Core Rules (single unit of work, single output artifact, logical step pipeline, dependent work serialization) and avoiding Anti-Patterns.
   The available skill list informs decomposition choices, but atomicity rules take precedence over skill availability.
5. Order tasks by prerequisites.
   Arrange tasks so that each task's dependencies are satisfied by earlier tasks.
   Independent tasks are ordered arbitrarily using a stable heuristic such as alphabetical.
6. Format each downstream packet.
   For every atomic task, produce a complete delegation packet using the Packet Template (`## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`).
   Populate each `## SKILLS` header by cross-referencing the task's PURPOSE and DETAILS against the discovered skill list.
   Assign the best-matching skill name(s) based on description alignment.
   If no match exists, leave the field empty.
7. Join packets with `---`.
   Concatenate all formatted packets with `---` on its own line between consecutive packets.
8. Return plaintext.

## Output Contract

Return a single plaintext string — no JSON, no Markdown code fences, no preamble, no postscript.
Join one or more delegation packets separated by `---` on its own line.
The consumer splits the output on the `---` delimiter before forwarding each packet to a worker.
Use the exact header names from the Packet Template below.

### Packet Template

```
## PURPOSE
<single sentence: what must be done>

## DETAILS
<full task description, constraints, and context>

## FILES TO READ
<comma-separated file paths to read>

## FILES TO WRITE
<single file path or "None">

## SKILLS
<comma-separated skill names to load — advisory, populated via skill-to-task matching>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

Delimit multiple packets with `---` on its own line between them.

## Verification

After decomposition, verify the output against these checks.
If any check fails, rework the affected packet(s) before returning.

- **Eight headers present** — Every downstream packet must contain exactly these eight headers: `## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`.
  Missing or misspelled headers are a blocker.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work.
  Verify no packet bundles independent or logically separable steps under a single PURPOSE.
- **Dependencies ordered** — Confirm that every task's prerequisites (files it reads, skills it needs, context it depends on) are satisfied by an earlier packet in the sequence.
  If not, reorder or split.
- **Delimiter is `---`** — Between consecutive packets the separator must be exactly `---` on its own line, with no surrounding whitespace or additional characters.
- **Output format matches contract** — Confirm the output satisfies the Output Contract's single-plaintext-string format rule.
- **Skill-name reasonableness** — Each `## SKILLS` entry must be appropriate for the task's PURPOSE and DETAILS.
  This is a reasonableness check, not a strict cross-reference — tasks may reference skills outside the discovered list.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task.
  Omit background and rationale.
- Do not bundle dependent changes into a single task.
- **Do not execute the decomposed work** — This skill produces delegation packets only.
  Do not attempt to run the tasks, read files beyond scanning for dependency ordering, or produce any artifact other than packets.
- **Do not write files** — `## FILES TO WRITE` in the output packets belongs to the downstream worker, not this skill.
  This skill writes nothing to disk.
- **Return `BLOCKED:` for malformed input** — If `## DETAILS` is missing, empty, or cannot be parsed as a decomposable request, return `BLOCKED: <reason>` immediately.
  Do not attempt to decompose an underspecified request.
- **Skill assignment is advisory, not mandatory** — Do not force-assign skills.
  Leave `## SKILLS` empty when no match exists.
- **Task atomicity over skill availability** — Do not merge or split tasks to match skill scope.