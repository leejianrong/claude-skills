#!/usr/bin/env python3
"""Redact known-sensitive keys from a JSON blob (stdin -> stdout).

Recursively walks the JSON structure and replaces the value of any key whose
name matches a sensitive pattern (case-insensitive substring) with the
literal string "[REDACTED]". Non-matching keys, including their nested
values, are left untouched. Run this on any API/tool response before
displaying it -- many create/update endpoints echo the request back,
including secret fields you just sent.

Usage:
    curl ... | python3 redact_secrets.py
    python3 redact_secrets.py < response.json
    python3 redact_secrets.py --extra internal_id session_id < response.json
"""

from __future__ import annotations

import argparse
import json
import sys

DEFAULT_PATTERNS = (
    "key",
    "token",
    "secret",
    "password",
    "passwd",
    "auth",
    "credential",
    "cookie",
)


def _is_sensitive(key: str, patterns: tuple[str, ...]) -> bool:
    lowered = key.lower()
    return any(pattern in lowered for pattern in patterns)


def redact(value: object, patterns: tuple[str, ...]) -> object:
    if isinstance(value, dict):
        return {
            key: ("[REDACTED]" if _is_sensitive(key, patterns) else redact(val, patterns))
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [redact(item, patterns) for item in value]
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--extra",
        nargs="*",
        default=(),
        help="additional case-insensitive substrings to treat as sensitive key names",
    )
    args = parser.parse_args()
    patterns = DEFAULT_PATTERNS + tuple(args.extra)

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"redact_secrets: input is not valid JSON: {exc}", file=sys.stderr)
        return 1

    json.dump(redact(data, patterns), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
