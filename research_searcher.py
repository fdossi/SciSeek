#!/usr/bin/env python3
"""Compat wrapper for legacy command usage.

Supported legacy patterns:
- python research_searcher.py
- python research_searcher.py --root ... --formats ... --terms ...
- python research_searcher.py --quick
- python research_searcher.py --config ...
"""

from __future__ import annotations

import argparse
import sys

from sciseek.cli import main as sciseek_main


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root")
    parser.add_argument("--formats")
    parser.add_argument("--terms")
    parser.add_argument("--groups")
    parser.add_argument("--mode")
    parser.add_argument("--output")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--max-pages", type=int)

    # Parse only known legacy args; keep unknown for forward compatibility.
    known, unknown = parser.parse_known_args(sys.argv[1:])

    if known.quick:
        return sciseek_main(["--quick"])

    # Legacy default behavior without args: run wizard.
    if len(sys.argv) == 1:
        return sciseek_main([])

    # Legacy search mode.
    argv = ["search"]
    if known.root:
        argv.extend(["--root", known.root])
    if known.formats:
        argv.extend(["--formats", known.formats])
    if known.terms:
        argv.extend(["--terms", known.terms])
    if known.groups:
        argv.extend(["--groups", known.groups])
    if known.mode:
        argv.extend(["--mode", known.mode])
    if known.output:
        argv.extend(["--output", known.output])
    if known.no_cache:
        argv.append("--no-cache")
    if known.max_pages is not None:
        argv.extend(["--max-pages", str(known.max_pages)])

    # Map --config legacy to --config-file in new CLI.
    if known.config:
        argv.extend(["--config-file", known.config])

    argv.extend(unknown)
    return sciseek_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
