---
name: python-source-style-guide
description: "Use when a request needs passive guidance on general Python source-style conventions."
selection:
  role: reference
  tags:
    actions: [reference, explain]
    inputs: [Python source-convention question]
    outputs: [source-style guidance]
    topics: [Python names, imports, expressions, docstrings, annotation idioms]
    constraints: [passive reference, preserve project conventions]
  use_when:
    - a developer or reviewer needs general Python source-writing conventions for new or existing code
  not_for:
    - a Python path alone or a question about project kind, supported runtimes, or source-tree placement
    - formatter, linter, type-checker setup or results; public API and typed-interface promises; or an implementation workflow
class: documentation
---

# Using This Reference

Use this passive reference when a developer or reviewer needs general Python
source-style guidance. The [compatibility hub](reference/python-source-style-guide.md)
defines the scope and shared decision context; the [index](reference/README.md) routes
readers to five substantial topics.

Read one topical document for the immediate question rather than treating the index or
hub as a substitute for its examples. When a decision crosses into project constraints,
load the specific neighboring reference identified in that topic. A cross-skill route
does not load another skill or transfer the consuming operation's workflow, permissions,
validation, or completion evidence.

## Docs

See the [Documentation Files](reference/README.md) index for reader questions and page
boundaries.
