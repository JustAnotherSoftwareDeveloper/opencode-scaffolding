---
name: ask-question
description: Use when resolving ambiguity in a user request by asking only necessary clarifying questions through the question tool.
schema_version: "1.0"
cues:
  - {facet: operation, value: clarify-request, primary: true}
  - {facet: subject, value: user-request}
relationships:
  - {role: owner}
class: inline
---
# ask-question

Ask clarifying questions to resolve ambiguity in user requests.
