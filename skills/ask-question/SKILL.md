---
name: ask-question
description: Use when resolving ambiguity in a user request by asking only necessary clarifying questions through the question tool.
class: inline
---

# Ask Question

This skill resolves ambiguity before work proceeds. Ask only questions whose answers would materially change the next step.

## Input

Free-form prompt from caller containing a user request that may require clarification.

- **Request text**: What the user wants to accomplish
- **Any provided context**: Files, directories, constraints, or background info already mentioned
- **All provided context**: Preserve meaning; do not omit details

## Output

Clarifying answers returned to the caller. If there is no material ambiguity, return no questions and `answers: []`.

### Question Tool Input Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "questions": {
      "type": "array",
      "minItems": 1,
      "maxItems": 5,
      "description": "Questions to ask the user via the question tool",
      "items": {
        "type": "object",
        "properties": {
          "question": { "type": "string", "minLength": 1, "description": "The actual question text" },
          "header": { "type": "string", "maxLength": 30, "description": "Short label (max 30 chars) for the question" },
          "options": {
            "type": "array",
            "minItems": 1,
            "maxItems": 5,
            "items": {
              "type": "object",
              "properties": {
                "label": { "type": "string", "description": "Display label for the option" },
                "description": { "type": "string", "description": "Explanation of the choice" }
              },
              "required": ["label", "description"]
            },
            "description": "Array of 1-5 {label, description} option objects"
          },
          "multiple": { "type": "boolean", "description": "Whether the user can select multiple options for this question" }
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
          "header": { "type": "string", "description": "Question header shown to the user" },
          "question": { "type": "string", "description": "Question text shown to the user" },
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

## Question Granularity

Each question should resolve one decision point:

- Ask about one file, test, behavior, constraint, or preference at a time
- Prefer clear choices with a useful custom-answer escape hatch
- Do not ask broad questions when a narrower question would decide the next step

## Execution Plan

1. Analyze [Input](#input) for ambiguity that would change the next step
2. If no material ambiguity exists, return `answers: []`
3. Otherwise, formulate 1-5 questions using [Question Granularity](#question-granularity)
4. Invoke the `question` tool with [Question Tool Input Schema](#question-tool-input-schema)
5. Return results using [Skill Output Schema](#skill-output-schema)

## Question Formulation Guidelines

- Purpose: what outcome is needed?
- Scope: what is included or excluded?
- Constraints: what limits the approach?
- Preference: what style or pattern should be followed?

## Guardrails

- Ask only when the answer changes execution.
- Do not ask what the request already answers.
- Return answers without filtering.
