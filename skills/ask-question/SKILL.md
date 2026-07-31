---
name: ask-question
description: Use when the user request is ambiguous in a way that would materially change execution output, and asking 2-5 clarifying questions would resolve the ambiguity.
schema_version: "1.0"
cues:
  - {facet: operation, value: "clarify-ambiguous-request", primary: true}
  - {facet: subject, value: "user request"}
  - {facet: constraint, value: "material ambiguity"}
  - {facet: outcome, value: "clarifying questions"}
relationships:
  - {role: owner, rationale: "owns ambiguity resolution through questions"}
class: inline
---

# Ask Question

This skill resolves ambiguity before work proceeds.
Ask only questions whose answers would materially change the next step.

## Input

Free-form prompt from caller containing a user request that may require clarification.

- **Request text**: What the user wants to accomplish.
- **Provided context**: Files, directories, constraints, or background already mentioned.
- **All provided context**: Preserve meaning; do not omit details.

## Output

Clarifying answers returned to the caller.
A question array of zero must never be returned.

### Question Tool Input Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "questions": {
      "type": "array",
      "minItems": 2,
      "maxItems": 5,
      "description": "Questions to ask the user via the question tool",
      "items": {
        "type": "object",
        "properties": {
          "question": {
            "type": "string",
            "minLength": 1,
            "description": "The actual question text"
          },
          "header": {
            "type": "string",
            "maxLength": 30,
            "description": "Short label (max 30 chars) for the question"
          },
          "options": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {
              "type": "object",
              "properties": {
                "label": {
                  "type": "string",
                  "description": "Display label for the option"
                },
                "description": {
                  "type": "string",
                  "description": "Explanation of the choice"
                }
              },
              "required": ["label", "description"]
            },
            "description": "Array of 1-5 {label, description} option objects"
          },
          "multiple": {
            "type": "boolean",
            "description": "Whether the user can select multiple options for this question"
          }
        },
        "required": ["question", "header", "options", "multiple"]
      }
    }
  },
  "required": ["questions"]
}
```

### Skill Output Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "answers": {
      "type": "array",
      "description": "Clarifying answers mapped to their originating question; empty when no clarification was needed",
      "items": {
        "type": "object",
        "properties": {
          "header": {
            "type": "string",
            "description": "Question header shown to the user"
          },
          "question": {
            "type": "string",
            "description": "Question text shown to the user"
          },
          "selected": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Selected labels or custom answer text returned by the user"
          }
        },
        "required": ["header", "question", "selected"]
      }
    }
  },
  "required": ["answers"]
}
```

## Question Guidelines

Formulate each question to resolve one decision point.
Ask about one file, test, behavior, constraint, or preference at a time.
Use clear choices with a useful custom-answer escape hatch.
Do not ask broad questions when a narrower question would decide the next step.

Cover these dimensions across the 2-5 questions:

- **Purpose**: what outcome is needed.
- **Scope**: what is included or excluded.
- **Constraints**: what limits the approach.
- **Preference**: what style or pattern to follow.

## Execution Plan

1. Analyze [Input](#input) for areas needing clarification.
2. Formulate 2-5 questions per [Question Guidelines](#question-guidelines).
   See [Guardrails](#guardrails) for mandatory question rules.
3. Invoke the `question` tool once with [Question Tool Input Schema](#question-tool-input-schema), passing all 2-5 questions in a single call.
4. Return results using [Skill Output Schema](#skill-output-schema).

This is a single-pass process.
Ask all clarifying questions in one invocation.
Do not perform follow-up rounds, multi-pass clarification, or iterative narrowing.

## Guardrails

- Always ask at least 2 questions and at most 5 questions.
- Do not skip questions because the request appears clear — ask confirmation, scope, assumption, constraint, or verification-preference questions instead.
- Ask only when the answer changes execution.
- Do not ask what the request already answers.
- Return answers without filtering.
