---
name: linux-cli-conventions
description: "Use when Linux shell, common-command, or OS-interface semantics materially affect a requested explanation or result."
selection:
  role: reference
  tags:
    actions: [interpret, explain]
    inputs: [Linux command text, CLI-dependent task]
    outputs: [source-qualified reference context]
    topics: [common commands, shell semantics, Linux OS context]
    environments: [Linux CLI]
    constraints: [material relevance, passive reference]
  use_when:
    - the request asks how Linux command or OS-interface semantics affect an explanation or result
    - a bounded task materially depends on common Linux CLI or OS context, even without an explanation request
  not_for:
    - Bash script creation or testing alone without a distinct Linux utility or OS-semantics concern
    - Linux application work or command execution where CLI semantics are incidental
class: documentation
---

# Linux CLI Task Reference

Use this passive reference when shell, utility, or Linux OS semantics materially affect an explanation or result. Start with the requested job outcome below; each job has one primary home, with supporting references linked from that page.

## Find A Job Reference

- **[Find and change project files](docs/find-and-change-project-files.md)** — “Find the project config that controls this path,” or “collect generated release files without losing unusual filenames.” Covers path discovery, filename boundaries, and common file-operation semantics; it does not supply an editor or configuration-format workflow for changing a setting.
- **[Extract, reshape, or package information](docs/extract-reshape-package-information.md)** — “Filter matching text lines,” “filter systemd journal records by unit or time,” “select a field from quoted CSV,” or “inspect which archive members would be extracted.” Covers line/field distinctions, systemd journal filtering, and archive operations; it does not cover complete log aggregation or general JSON/YAML parsing.
- **[Run and debug a command or job](docs/run-and-debug-command-or-job.md)** — “Explain why a pipeline reports the later command's status,” “debug why a value becomes multiple arguments,” “investigate a foreground/background job,” or “investigate a unit that fails to start.” Covers command interpretation, shell/terminal behavior, process views, and related evidence; it is not an application or service-repair playbook.
- **[Prepare the environment a job needs](docs/prepare-environment-for-a-job.md)** — “Check whether a dependency is installed or only available,” “understand the service and access context before a run,” or “work out whether a space report describes a directory, filesystem, or mount.” Covers prerequisite-state and system-view distinctions, not installation, repair, or cleanup procedures.
- **[Reach or work across a remote boundary](docs/reach-work-across-remote-boundary.md)** — “Run a read-only query remotely,” “forward a local connection,” “interpret route and socket reports for a failed connection,” or “bundle files for delivery to a remote host.” Covers network views and SSH scope, with archive semantics linked as supporting context for packaging; it does not provide file-transfer or end-to-end connection workflows.

Route by the requested result, not by a command name:

- Filtering systemd journal records belongs under **Extract**; using journal evidence to investigate a failed job or unit start belongs under **Run and debug**, even if the unit's process never launched.
- **Prepare** is supporting context for unit-file, enablement, and runtime-state distinctions. It owns prerequisite-readiness checks, not failure investigation.
- An explicit remote host or service boundary belongs under **Reach remotely**, including file delivery. **Extract** supplies supporting archive semantics, not transfer instructions.

Follow links for support without changing the primary route. The references distinguish unit state and journal filtering but do not interpret a failed unit's cause or provide file-transfer procedures.

A familiar command name does not identify its shell, implementation, version, data source, or scope; the references qualify those boundaries where they affect interpretation. Manuals describe documented behavior, not installed tools or live host state.

This skill is not selected merely because a request mentions Linux, Bash, or a path. Script creation and testing remain with their task owners unless a separate Linux CLI semantic question materially affects the result.

## Passive Scope

The references explain documented behavior; they do not run commands, inspect hosts, establish installed tools or live state, or grant execution or administration authority. Static fragments illustrate bounded behavior, not procedures to run.

## Docs

See [Find A Job Reference](#find-a-job-reference) for the local task index.
