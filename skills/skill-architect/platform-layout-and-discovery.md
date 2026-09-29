# Platform Layout and Discovery

## Purpose

Describe the canonical platform layout and discovery context for skill entries,
passive documentation stores, bounded operation entries, and script roots.

## Applicability

Applies when interpreting the skill-authoring family inventory and its indexes without
turning locations into execution instructions.

## Non-Goals

This document does not create, move, refresh, scan, or write files, and does not
authorize tools, delegation, loading, or completion. It does not specify or claim
host-level skill discovery, skill loading, or runtime enforcement behavior.

## Authority

This is the canonical current authority for platform layout and script placement within
the `skill-architect` reference scope, as indexed by [`SKILL.md`](SKILL.md). The
[platform layout context](platform-layout-context.md) is historical supporting
material only; it does not establish or override current policy. This documentation
authority does not imply host-level enforcement.

## Scope

- Skills use a directory entry point named `SKILL.md`.
- The planning authority keeps its six concern documents beside that entry point.
- Authoring, template/schema, and maintenance material remains in the three passive
  documentation stores.
- Operation entries retain their own bounded contracts.

These locations describe inventory structure and discovery context; they do not imply
that target-state files, indexes, or migrations are already complete.

## Script roots

The following root-selection behavior is the checked-in behavior of the script-root
resolver, not a claim about how the host discovers or loads skills. The Python paths
and precedence match `scripts/python/src/lib/resolve_script_root/core.py` and its
tests.

### Python

1. A non-empty `OPENCODE_SCRIPTS_PYTHON` environment variable overrides the defaults.
2. Otherwise, the resolver checks `<project-root>/opencode/scripts/python` (that is,
   `./opencode/scripts/python` relative to the project root). The project root is the
   explicit `project_root` argument when supplied, or the current working directory;
   this local root is selected only when it is a directory.
3. Otherwise, resolution falls back to the global root
   `~/.config/opencode/scripts/python`. The resolver returns this fallback path without
   checking whether the directory exists.

The resolver returns the selected path with source `env-var`, `project-local`, or
`global`, respectively. The environment override remains first, project-local
selection second, and global fallback last.

### Node and shell

Node and shell use their existing runtime-specific roots; the Python `opencode/`
project segment does not apply to them:

1. `OPENCODE_SCRIPTS_NODE` or `OPENCODE_SCRIPTS_SHELL` overrides the defaults for the
   corresponding runtime when non-empty.
2. The project-local roots are `<project-root>/.opencode/scripts/node` and
   `<project-root>/.opencode/scripts/shell`, respectively, selected only when the
   corresponding directory exists.
3. The global fallback roots are `~/.config/opencode/scripts/node` and
   `~/.config/opencode/scripts/shell`, respectively.

These Node and shell paths are recorded separately and are not changed by the Python
root rule.

## Evidence Status

The Python root order and paths above are verified against the checked-in resolver and
its tests. This evidence concerns that utility only; it does not establish host-level
skill discovery or loading behavior. Target-state publication status is limited to the
indexed six-document scope represented here.

## Shared Passive-Contract Verification

This concern is coupled to the indexed scope and contains reference context only.
It grants no execution authority, implicit or transitive loading, tool use, file
change, delegation, or completion authority. Cross-references identify context only;
they do not create an automatic load chain.
