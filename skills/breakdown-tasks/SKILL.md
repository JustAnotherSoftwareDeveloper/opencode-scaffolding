---
name: breakdown-tasks
description: Use when decomposing a request into the smallest possible task-delegation work items.
class: delegated
---

# Breakdown Tasks

Decompose a request into atomic work items suitable for serial worker delegation.

## Input Contract

Incoming standard delegation packet with the following sections:

- **`## PURPOSE`** — The decomposition goal: what must be broken down.
- **`## DETAILS`** — The clarified user request and all relevant context to decompose. This is the primary input for splitting into atomic tasks.
- **`## FILES TO READ`** — Constrains which files are relevant to the request.
- **`## FILES TO WRITE`** — Should normally be `None`; this skill decomposes rather than writes output files.
- Malformed or missing `## DETAILS` is **`BLOCKED:`** — the skill cannot proceed without a clear request to decompose.

## Output Contract

The output is a single plaintext string — no JSON, no Markdown code fences, no preamble, no postscript.
It consists of one or more delegation packets separated by `---` on its own line.
The consumer splits the output on the `---` delimiter before forwarding each packet to a worker.
Each packet uses the exact header names from the Packet Template below.

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
<comma-separated skill names to load>

## EXECUTION INSTRUCTIONS
<step-by-step instructions for execution>

## VERIFICATION
<how to check work completed correctly>

## EXPECTED OUTPUT
<what the worker should produce>
```

Delimit multiple packets with `---` on its own line between them.

## Atomic Task Unit

An atomic task is the smallest useful unit of work that can be delegated, executed, and verified independently.

Core Rules and Anti-Patterns governing atomic task decomposition are defined in [./REFERENCE.md](./REFERENCE.md). All decomposition must conform to those rules.

## Execution Steps

1. **Parse incoming packet** — Read the delegation packet's `## PURPOSE` and `## DETAILS` sections to understand the decomposition goal and the request to decompose.
2. **Extract request from `## DETAILS`** — Treat the content of `## DETAILS` as the primary input for decomposition. If `## DETAILS` is missing or malformed, report `BLOCKED: ## DETAILS is missing or malformed — cannot decompose without a clear request.`
3. **Decompose per ./REFERENCE.md** — Split the request into atomic tasks following Core Rules (single unit of work, single output artifact, logical step pipeline, dependent work serialization) and avoiding Anti-Patterns.
4. **Order tasks by prerequisites** — Arrange tasks so that each task's dependencies are satisfied by earlier tasks. Independent tasks may be ordered arbitrarily (use a stable heuristic such as alphabetical).
5. **Format each downstream packet** — For every atomic task, produce a complete delegation packet using the Packet Template (## PURPOSE, ## DETAILS, ## FILES TO READ, ## FILES TO WRITE, ## SKILLS, ## EXECUTION INSTRUCTIONS, ## VERIFICATION, ## EXPECTED OUTPUT).
6. **Join packets with `---`** — Concatenate all formatted packets with `---` on its own line between consecutive packets.
7. **Return plaintext** — Output the joined string with no JSON, no Markdown code fences, no preamble, and no postscript.

## Verification

After decomposition, verify the output against these checks. If any check fails, rework the affected packet(s) before returning.

- **Eight headers present** — Every downstream packet must contain exactly these eight headers: `## PURPOSE`, `## DETAILS`, `## FILES TO READ`, `## FILES TO WRITE`, `## SKILLS`, `## EXECUTION INSTRUCTIONS`, `## VERIFICATION`, `## EXPECTED OUTPUT`. Missing or misspelled headers are a blocker.
- **No combined tasks** — Each packet must represent exactly one atomic unit of work. Verify no packet bundles independent or logically separable steps under a single PURPOSE.
- **Dependencies ordered** — Confirm that every task's prerequisites (files it reads, skills it needs, context it depends on) are satisfied by an earlier packet in the sequence. If not, reorder or split.
- **Delimiter is `---`** — Between consecutive packets the separator must be exactly `---` on its own line, with no surrounding whitespace or additional characters.
- **No wrapping prose, fences, or JSON** — The entire output is a raw concatenation of packets. Reject any leading/trailing explanations, Markdown code fences, or JSON wrappers.

## Guardrails

- Preserve original intent and context.
- Include only information necessary for a worker to execute the task; omit background and rationale.
- Do not bundle dependent changes into a single task.
- **Do not execute the decomposed work** — This skill produces delegation packets only. Do not attempt to run the tasks, read files beyond scanning for dependency ordering, or produce any artifact other than packets.
- **Do not write files** — `## FILES TO WRITE` in the output packets belongs to the downstream worker, not this skill. This skill writes nothing to disk.
- **Produce only delegation packets** — The output is a sequence of packets and `---` delimiters with no surrounding text, fences, or JSON. Any non-packet content (status messages, summaries, questions) is a violation.
- **Return `BLOCKED:` for malformed input** — If `## DETAILS` is missing, empty, or cannot be parsed as a decomposable request, return `BLOCKED: <reason>` immediately. Do not attempt to decompose an underspecified request.