#!/usr/bin/env python3
"""Structural and consistency checks for Markdown docs. Standard library only.

Usage: check_docs.py PATH [PATH ...]   (files or directories; scans *.md)

Errors (exit 1): heading-level jumps, code fences with no language, broken
relative links. Warnings (exit 0): sentences over MAX_WORDS, positional
references, filler words.
"""
import re
import sys
from pathlib import Path

# Google's guide asks for short sentences; 35 is the point where a sentence is
# nearly always worth splitting, so it works as a warning threshold.
MAX_WORDS = 35
POSITIONAL = re.compile(r"\b(as (shown|described|mentioned) (above|below|earlier)|"
                        r"the (above|below) (example|code|section)|see (above|below))\b", re.I)
FILLER = re.compile(r"\b(simply|just|easily|obviously|of course|it is worth noting|"
                    r"it's worth noting|let's dive in|in this section we will)\b", re.I)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(\s*)(```+|~~~+)(.*)$")


def check_file(path: Path):
    errors, warnings = [], []
    lines = path.read_text(encoding="utf-8").splitlines()
    in_fence, last_level, fence_marker, fence_len = False, 0, "", 0
    for n, line in enumerate(lines, 1):
        m = FENCE.match(line)
        if m:
            if not in_fence:
                in_fence, fence_marker, fence_len = True, m.group(2)[0], len(m.group(2))
                if not m.group(3).strip():
                    errors.append((n, "code fence has no language (use ```text for output)"))
            elif m.group(2)[0] == fence_marker and len(m.group(2)) >= fence_len and not m.group(3).strip():
                in_fence = False
            continue
        if in_fence:
            continue
        h = re.match(r"^(#{1,6})\s+\S", line)
        if h:
            level = len(h.group(1))
            if last_level and level > last_level + 1:
                errors.append((n, f"heading jumps from h{last_level} to h{level}"))
            last_level = level
            continue
        for target in LINK.findall(re.sub(r"`[^`]*`", "", line)):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            rel = target.split("#")[0].split("?")[0]
            # Only links to source files can be verified. Root-absolute and
            # extensionless (directory-style) links are resolved by the site
            # generator, so checking them here would give false errors.
            if rel and not rel.startswith("/") and Path(rel).suffix and not (path.parent / rel).exists():
                errors.append((n, f"broken relative link: {target}"))
        if line.lstrip().startswith("|") or line.lstrip().startswith(">"):
            continue
        prose = re.sub(r"`[^`]*`", "code", line)
        for sentence in re.split(r"(?<=[.!?])\s+", prose):
            if len(sentence.split()) > MAX_WORDS:
                warnings.append((n, f"sentence over {MAX_WORDS} words"))
        if POSITIONAL.search(prose):
            warnings.append((n, "positional reference; name the section instead"))
        f = FILLER.search(prose)
        if f:
            warnings.append((n, f"filler: '{f.group(0)}'"))
    return errors, warnings


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    files = []
    for arg in argv:
        p = Path(arg)
        if not p.exists():
            print(f"error: {arg} does not exist", file=sys.stderr)
            return 2
        files += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    n_err = 0
    for f in files:
        errors, warnings = check_file(f)
        for n, msg in errors:
            print(f"{f}:{n}: error: {msg}")
        for n, msg in warnings:
            print(f"{f}:{n}: warning: {msg}")
        n_err += len(errors)
    print(f"{len(files)} file(s), {n_err} error(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
