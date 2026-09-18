#!/usr/bin/env python3
"""Validate SKILL.md frontmatter and structural conventions from write-skill.

Checks, per skill directory (one with a SKILL.md):
  - frontmatter has `name` and `description`
  - `name` is lowercase letters/numbers/hyphens, <=64 chars, matches the
    directory name, and doesn't contain the reserved words "claude" or
    "anthropic"
  - `description` is non-empty and <=1024 chars
  - the body (everything after the closing `---`) is under 500 lines
  - any references/*.md file over 100 lines has a "Contents"/"Table of
    Contents" heading in its first 30 lines

No third-party dependencies: frontmatter is a small YAML subset (scalar and
`>-`/`|-` block-scalar values for `name`/`description` only), parsed by hand
rather than pulled in via PyYAML.
"""
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("claude", "anthropic")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_BODY_LINES = 500
TOC_SCAN_LINES = 30
REFERENCE_FILE_MIN_LINES = 100
TOC_HEADING_RE = re.compile(r"^#+\s*(table of )?contents\b", re.IGNORECASE)

REPO_ROOT = Path(__file__).resolve().parents[2]


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: file must start with a '---' frontmatter marker")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    raise ValueError(f"{path}: frontmatter opened with '---' but never closed")


def parse_scalar_field(frontmatter_lines: list[str], field: str) -> str | None:
    for i, line in enumerate(frontmatter_lines):
        m = re.match(rf"^{field}:\s*(.*)$", line)
        if not m:
            continue
        value = m.group(1).strip()
        if value in (">-", ">", "|-", "|"):
            collected = []
            for cont in frontmatter_lines[i + 1 :]:
                if cont.strip() == "" or cont.startswith((" ", "\t")):
                    if cont.strip():
                        collected.append(cont.strip())
                    continue
                break
            return " ".join(collected)
        return value.strip('"').strip("'")
    return None


def validate_skill(skill_md: Path) -> list[str]:
    errors = []
    text = skill_md.read_text(encoding="utf-8")
    try:
        frontmatter, body = split_frontmatter(text, skill_md)
    except ValueError as e:
        return [str(e)]

    fm_lines = frontmatter.splitlines()
    name = parse_scalar_field(fm_lines, "name")
    description = parse_scalar_field(fm_lines, "description")
    dir_name = skill_md.parent.name

    if not name:
        errors.append(f"{skill_md}: missing 'name' in frontmatter")
    else:
        if not NAME_RE.match(name):
            errors.append(
                f"{skill_md}: name '{name}' must be lowercase letters/numbers/hyphens only"
            )
        if len(name) > MAX_NAME_LEN:
            errors.append(f"{skill_md}: name '{name}' exceeds {MAX_NAME_LEN} chars")
        if name != dir_name:
            errors.append(
                f"{skill_md}: name '{name}' does not match directory name '{dir_name}'"
            )
        for word in RESERVED_WORDS:
            if word in name:
                errors.append(f"{skill_md}: name '{name}' contains reserved word '{word}'")

    if not description:
        errors.append(f"{skill_md}: missing or empty 'description' in frontmatter")
    elif len(description) > MAX_DESCRIPTION_LEN:
        errors.append(
            f"{skill_md}: description is {len(description)} chars, "
            f"exceeds {MAX_DESCRIPTION_LEN}"
        )

    body_lines = [l for l in body.splitlines() if l.strip()]
    body_line_count = len(body.splitlines())
    if body_line_count > MAX_BODY_LINES:
        errors.append(
            f"{skill_md}: body is {body_line_count} lines, exceeds {MAX_BODY_LINES}"
        )
    del body_lines

    return errors


def validate_reference_file(ref_md: Path) -> list[str]:
    lines = ref_md.read_text(encoding="utf-8").splitlines()
    if len(lines) <= REFERENCE_FILE_MIN_LINES:
        return []
    head = lines[:TOC_SCAN_LINES]
    if any(TOC_HEADING_RE.match(l.strip()) for l in head):
        return []
    return [
        f"{ref_md}: {len(lines)} lines but no Contents/Table of Contents heading "
        f"in the first {TOC_SCAN_LINES} lines"
    ]


def main() -> int:
    errors: list[str] = []

    for skill_md in sorted(REPO_ROOT.glob("*/SKILL.md")):
        errors.extend(validate_skill(skill_md))

    for ref_md in sorted(REPO_ROOT.glob("*/references/*.md")):
        errors.extend(validate_reference_file(ref_md))

    if errors:
        print("Skill validation failed:\n")
        for e in errors:
            print(f"  - {e}")
        print(f"\n{len(errors)} error(s).")
        return 1

    skill_count = len(list(REPO_ROOT.glob("*/SKILL.md")))
    print(f"OK: {skill_count} skill(s) validated, no errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
