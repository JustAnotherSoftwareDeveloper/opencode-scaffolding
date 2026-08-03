#!/usr/bin/env python3
"""Validate OpenCode skill framework artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import click
import yaml
from lxml import etree


CLASSES = ("operation", "delegated", "planning")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass
class CheckResult:
    ok: bool
    messages: list[str]


def _repo_path(path: Path) -> Path:
    return path if path.is_absolute() else REPO_ROOT / path


def parse_frontmatter(skill_file: Path) -> tuple[dict[str, object], str]:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter block")
    try:
        _, raw, body = text.split("---\n", 2)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter block") from exc
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, body


def validate_skill_file(skill_file: Path, *, require_class: bool = False) -> CheckResult:
    path = _repo_path(skill_file)
    messages: list[str] = []
    if not path.exists():
        return CheckResult(False, [f"{skill_file}: file not found"])
    try:
        frontmatter, body = parse_frontmatter(path)
    except Exception as exc:
        return CheckResult(False, [f"{skill_file}: {exc}"])

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    class_name = frontmatter.get("class")

    if not isinstance(name, str) or not name:
        messages.append(f"{skill_file}: frontmatter.name is required")
    elif not NAME_RE.match(name):
        messages.append(f"{skill_file}: frontmatter.name must be lowercase alphanumeric with single hyphen separators")
    elif path.parent.name != name:
        messages.append(f"{skill_file}: frontmatter.name '{name}' must match directory '{path.parent.name}'")

    if not isinstance(description, str) or not description.strip():
        messages.append(f"{skill_file}: frontmatter.description is required")
    elif len(description) > 1024:
        messages.append(f"{skill_file}: frontmatter.description must be <= 1024 characters")

    if require_class and not class_name:
        messages.append(f"{skill_file}: frontmatter.class is required for framework-authored skills")
    if class_name and class_name not in CLASSES:
        messages.append(f"{skill_file}: frontmatter.class must be one of {', '.join(CLASSES)}")
    if not body.strip():
        messages.append(f"{skill_file}: body must not be empty")

    return CheckResult(not messages, messages or [f"{skill_file}: ok"])


def validate_xml_against_xsd(xml_file: Path, xsd_file: Path) -> CheckResult:
    try:
        schema_doc = etree.parse(str(xsd_file))
        schema = etree.XMLSchema(schema_doc)
        xml_doc = etree.parse(str(xml_file))
        schema.assertValid(xml_doc)
    except Exception as exc:
        return CheckResult(False, [f"{xml_file}: failed against {xsd_file}: {exc}"])
    return CheckResult(True, [f"{xml_file}: ok"])


def validate_class_schemas(skill_dir: Path) -> CheckResult:
    root = _repo_path(skill_dir)
    messages: list[str] = []
    ok = True
    for class_name in CLASSES:
        xsd_file = root / "schemas" / f"{class_name}.xsd"
        if not xsd_file.exists():
            ok = False
            messages.append(f"{xsd_file}: missing canonical XSD template")
            continue
        try:
            etree.XMLSchema(etree.parse(str(xsd_file)))
        except Exception as exc:
            ok = False
            messages.append(f"{xsd_file}: invalid XSD template: {exc}")
            continue
        messages.append(f"{xsd_file}: ok")
        docs = schema_documentation(xsd_file)
        if not docs:
            ok = False
            messages.append(f"{xsd_file}: missing xs:documentation annotations for markdown rendering")
    return CheckResult(ok, messages)


def schema_documentation(xsd_file: Path) -> list[str]:
    doc = etree.parse(str(xsd_file))
    ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
    values: list[str] = []
    for node in doc.xpath("//xs:documentation", namespaces=ns):
        text = " ".join("".join(node.itertext()).split())
        if text:
            values.append(text)
    return values


def render_markdown(class_name: str, skill_dir: Path | None = None) -> CheckResult:
    if class_name not in CLASSES:
        return CheckResult(False, [f"unknown class '{class_name}'"])
    root = _repo_path(skill_dir or Path("skills/skill-hygiene"))
    xsd_file = root / "schemas" / f"{class_name}.xsd"
    if not xsd_file.exists():
        return CheckResult(False, [f"{xsd_file}: missing schema"])
    docs = schema_documentation(xsd_file)
    if not docs:
        return CheckResult(False, [f"{xsd_file}: no xs:documentation annotations found"])
    lines = [f"# {class_name.title()} Skill Guidance", "", f"Source: `{xsd_file.relative_to(REPO_ROOT)}`", ""]
    lines.extend(f"- {item}" for item in docs)
    return CheckResult(True, ["\n".join(lines)])


def validate_all() -> CheckResult:
    messages: list[str] = []
    ok = True
    for skill_file in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        require_class = skill_file.parent.name == "skill-hygiene"
        result = validate_skill_file(skill_file, require_class=require_class)
        ok = ok and result.ok
        messages.extend(result.messages)
    schema_result = validate_class_schemas(REPO_ROOT / "skills" / "skill-hygiene")
    ok = ok and schema_result.ok
    messages.extend(schema_result.messages)
    for class_name in CLASSES:
        render_result = render_markdown(class_name)
        ok = ok and render_result.ok
        if not render_result.ok:
            messages.extend(render_result.messages)
    return CheckResult(ok, messages)


@click.command(name="validate-skill-framework")
@click.argument(
    "skill_file",
    required=False,
    type=click.Path(exists=True, readable=True),
)
@click.option(
    "--all",
    "all_skills",
    is_flag=True,
    default=False,
    help="Validate all skills and skill-hygiene schemas",
)
@click.option(
    "--class-schemas",
    "class_schemas",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    default=None,
    help="Validate per-class canonical XSD templates in the given skill directory",
)
@click.option(
    "--render-markdown",
    "render_markdown_option",
    type=click.Choice(CLASSES, case_sensitive=False),
    default=None,
    help="Render markdown guidance from a class XSD annotation",
)
def cli(
    skill_file: str | None,
    all_skills: bool,
    class_schemas: str | None,
    render_markdown_option: str | None,
) -> None:
    """Validate OpenCode skill framework artifacts.

    Provide a SKILL_FILE to validate a single skill, or use one of the
    flags (--all, --class-schemas, --render-markdown) for batch operations.
    """
    if all_skills:
        result = validate_all()
    elif class_schemas:
        result = validate_class_schemas(Path(class_schemas))
    elif render_markdown_option:
        result = render_markdown(render_markdown_option)
    elif skill_file:
        path = Path(skill_file)
        result = validate_skill_file(path, require_class=path.parent.name == "skill-hygiene")
    else:
        click.echo("No validation target supplied. Use --help for usage.", err=True)
        raise SystemExit(2)

    for message in result.messages:
        click.echo(message)
    raise SystemExit(0 if result.ok else 1)


if __name__ == "__main__":
    cli()
