# Source-Style Guide Compatibility Hub

This page keeps the former `reference/python-source-style-guide.md` route working for
existing readers. It is a hub, not a second copy of the detailed guide. Choose a topic
from the [index](README.md) for examples, edge cases, and source-level recommendations.

## Scope And Shared Decision Context

This reference owns general Python source conventions: names, imports, source
formatting, expressions, function and class form, comments, docstrings, and annotation
idioms. It does not decide a project's public API, runtime support, directory tree,
formatter/checker configuration, security or logging policy, concurrency model, package
distribution, or code-change procedure.

Read each statement according to its kind. Python documentation describes syntax and
runtime behavior for a named version; PEP 8 and PEP 257 publish conventions within their
stated scopes; Google and NumPy examples describe their own house or ecosystem choices;
topic pages label this guide's proposed defaults; project contracts and approved local
policy control their own decisions. PEP 8 explicitly scopes itself to the standard
library, gives project-specific guidance precedence in conflicts, and says not to break
backwards compatibility merely to satisfy the PEP ([PEP 8: Introduction and consistency](https://peps.python.org/pep-0008/#introduction)).

For an established project, preserve its documented conventions and compatibility
promises first, then follow applicable approved local policy. Consider a proposed
default only for a new or unconfigured project when the task permits a choice. A source
format preference does not authorize a public rename, mass reformat, syntax upgrade, or
policy migration.

Use the primary links beside each topic's examples to answer the relevant question:
Python's language/library references explain execution, PEP 8/257 explain conventions,
and Google or NumPy show concrete house-style alternatives. For version-sensitive
syntax or annotation evaluation, check the project's supported interpreters before
adopting an example; a style recommendation cannot make newer syntax compatible.

The source reads recorded on 2026-11-07 rendered Python 3.15.2 and NumPy v2.5. Those
versions describe the inspected documentation, not a target project's environment.
Google, Typing `/latest/`, and numpydoc `stable` pages are mutable and exposed no
numbered revision. Use PEPs 585/604 for feature introduction dates and current Python
documentation for semantics. None of these guides establishes one universally best
style or measured maintainability benefit; choose among conventions using the code's
meaning, reader needs, and existing project practice.

## Choose A Topic

- [Names and imports](names-and-imports.md) — naming roles, public/internal signals,
  import grouping, aliases, wildcard trade-offs, and module-level dunder ordering.
- [Readable layout and control flow](readable-layout-and-control-flow.md) — formatting,
  line wrapping, expression readability, and behavior-preserving rewrites.
- [Functions, classes, and state](functions-classes-and-state.md) — cohesive callable
  boundaries, decomposition, mutable defaults, instance/class state, and modules.
- [Comments and docstrings](comments-and-docstrings.md) — explanatory comments,
  docstring meaning, Google/NumPy format choices, and runtime-visible docstrings.
- [Annotations and typing idioms](annotations-and-typing-idioms.md) — type intent,
  supported syntax, checker/runtime distinctions, and annotation introspection.

## Neighboring Ownership

When a source-style question depends on a broader project contract, explicitly load only
the needed module. `python-project-reference -> reference/source-and-api.md` owns public
API promises and failure semantics; `python-project-reference -> reference/project-context-and-layout.md`
owns project kind, runtime support, and file placement; and
`python-project-reference -> reference/static-quality.md` owns formatter, linter, and
type-checker configuration and result interpretation. Those references supply context,
not a transitive load or permission to act. The operation that requested work retains
its workflow and evidence responsibilities.
