# Shared Library Rules

Keep `src/cli/` adapters thin: they handle command input, wiring, and the established
CLI contract rather than owning reusable behavior. `src/lib/` is one internal library
root. Feature-specific behavior belongs to its cohesive feature or domain package, even
when multiple CLI adapters use it. Reserve `src/lib/shared/` for small, domain-neutral
primitives reused across domains; a second command consumer alone does not make
behavior shared.

## Five Shared Module Rules

Every shared module must follow these conventions:

- **No CLI entry points** — Shared modules are library code only.
  They are imported, never invoked via `uv run`.
  No entry point registration in `[project.scripts]`.

- **100% test coverage** — Shared modules must meet the existing `fail_under = 100`
  coverage requirement.
  Tests live under `tests/` using the `test_shared_*.py` naming convention.

- **Consumer documentation** — Each shared module must name its consuming feature or
  domain packages in a module-level docstring when those consumers are established:

  ```python
  """Small path primitives used by collection and rendering packages."""
  ```

- **Domain-based naming** — Package and module names describe the cohesive feature or
  primitive, not whichever CLI happens to call them. This keeps ownership with the
  behavior rather than its current consumers.

- **Canonical behavior and placement** — Before adding behavior, locate the canonical
  implementation and its tests, then check whether equivalent behavior already exists.
  Extend the canonical implementation rather than copying it. Keep feature-specific
  behavior in its cohesive feature/domain package. Use `src/lib/shared/` only for a
  small, domain-neutral primitive reused across domains; consumer count alone is not an
  extraction rule.

Preserve existing package and module names and paths unless an inventory-grounded
decision identifies a specific minimal change. Do not rename packages to match
illustrative examples or to follow a CLI consumer.

## File Layout

**PLACE-001 fixture annotation:** In this layout, `<feature_or_domain>` is the
`snake_case` package identifier for a cohesive capability. Replace it with that
identifier before using the example.

```text
scripts/python/
  src/
    cli/                          # thin Click command adapters
    lib/
      <feature_or_domain>/         # cohesive feature/domain behavior
        __init__.py
        core.py
      shared/                     # optional small domain-neutral primitives
        __init__.py               # empty or re-exports
  tests/
    test_<feature_or_domain>.py
```

CLI adapters and feature packages may import internal library modules using
package-qualified paths. For example:

```python
from lib.collect_skills import parser
from lib.skill_metadata import normalize_skill_metadata
```

These are internal project imports. A public `lib.*` API or separate library
distribution is not required, and this guidance does not guarantee external import
compatibility or direct-source invocation behavior.
