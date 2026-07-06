"""SkillClass enumeration — single source of truth for skill class labels.

Consumers: collect-skills, assign-skills.

All six valid skill classes as defined in the skill-architect taxonomy.
Used by ``collect-skills --class <value>`` for filtering and by
``assign-skills --skill-classes`` for candidate discovery.
"""

from __future__ import annotations

from enum import StrEnum


class SkillClass(StrEnum):
    """Six canonical skill classes from the OpenCode skill taxonomy.

    Members:
        OPERATION: Skills that perform direct work (script writers,
            test writers, skill factory, etc.).
        DELEGATED: Skills that delegate work to a sub-agent via the
            task tool (dispatch-decompose, task-delegation, etc.).
        INLINE: Skills loaded and executed in-process by the LLM
            (ask-question, generic-analysis, etc.).
        ORCHESTRATED: Skills that coordinate multiple agents or
            workers (breakdown-tasks, etc.).
        PLANNING: Skills used for planning and design decisions
            (skill-architect, etc.).
        DOCUMENTATION: Passive reference skills containing
            documentation, conventions, and guides (skill-authoring-guide,
            skill-bash-conventions, etc.).
    """

    OPERATION = "operation"
    DELEGATED = "delegated"
    INLINE = "inline"
    ORCHESTRATED = "orchestrated"
    PLANNING = "planning"
    DOCUMENTATION = "documentation"
