"""Unit tests for lib.shared.skill_class."""

from __future__ import annotations

import pytest

from lib.shared.skill_class import SkillClass


def test_all_five_members_present() -> None:
    """Verify all five canonical values exist."""
    assert len(SkillClass) == 5
    assert SkillClass.OPERATION == "operation"
    assert SkillClass.DELEGATED == "delegated"
    assert SkillClass.INLINE == "inline"
    assert SkillClass.PLANNING == "planning"
    assert SkillClass.DOCUMENTATION == "documentation"


@pytest.mark.parametrize(
    "value",
    [
        "operation",
        "delegated",
        "inline",
        "planning",
        "documentation",
    ],
)
def test_construct_from_string(value: str) -> None:
    """Verify each value can construct its enum member."""
    member = SkillClass(value)
    assert member.value == value


def test_construct_invalid_raises() -> None:
    """Verify invalid values raise ValueError."""
    with pytest.raises(ValueError):
        SkillClass("nonexistent")


def test_str_enum_string_behavior() -> None:
    """SkillClass is a StrEnum — comparison with str works."""
    assert SkillClass.OPERATION == "operation"
    assert SkillClass.OPERATION == "operation"
    assert str(SkillClass.OPERATION) == "operation"
