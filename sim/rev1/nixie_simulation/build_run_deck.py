"""Swap the analysis include in an exported KiCad SPICE deck."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=Path)
    parser.add_argument("profile", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    source = args.base.read_text(encoding="utf-8")
    profile = args.profile.as_posix()
    updated, count = re.subn(
        r"(?m)^\.include (?:\.\./\.\./sim/rev1/)?runs/[^\r\n]+$",
        f".include {profile}",
        source,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not replace the run-profile include")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(updated, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
