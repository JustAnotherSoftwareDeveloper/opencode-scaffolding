"""Core logic for resolve-script-root — global vs project-local script root resolution.

Resolution order:
1. $OPENCODE_SCRIPTS_PYTHON (or OPENCODE_SCRIPTS_NODE / OPENCODE_SCRIPTS_SHELL)
2. <project-root>/.opencode/scripts/<runtime>
3. ~/.config/opencode/scripts/<runtime>
"""

from __future__ import annotations

import os
from pathlib import Path


def resolve_script_root(
    runtime: str = "python",
    project_root: Path | None = None,
) -> tuple[Path, str]:
    """Resolve the script root directory for *runtime*.

    Returns a ``(path, source)`` tuple where *source* is one of:
    ``"env-var"``, ``"project-local"``, or ``"global"``.

    Parameters
    ----------
    runtime:
        One of ``"python"``, ``"node"``, or ``"shell"``.
    project_root:
        Optional explicit project root.
        Defaults to ``Path.cwd()`` when *None*.

    Returns
    -------
    tuple[Path, str]
        The resolved path and its source label.
    """
    # 1. Environment variable override
    env_var = f"OPENCODE_SCRIPTS_{runtime.upper()}"
    env_path_str = os.environ.get(env_var)
    if env_path_str:
        resolved = Path(env_path_str).resolve()
        return resolved, "env-var"

    # 2. Project-local root
    pr = project_root or Path.cwd()
    project_local = pr.resolve() / ".opencode" / "scripts" / runtime
    if project_local.is_dir():
        return project_local.resolve(), "project-local"

    # 3. Global fallback
    global_path = Path.home() / ".config" / "opencode" / "scripts" / runtime
    return global_path.resolve(), "global"
