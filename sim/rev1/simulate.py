"""Run and validate the Nixie Rev1 release simulation."""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from common.project_cli import ProjectResult, execute

SIMULATION = Path(__file__).resolve().parent
PROJECT = SIMULATION.parents[1]
SCHEMATIC = PROJECT / "hardware" / SIMULATION.name / "nixie_rev1.kicad_sch"
MEASUREMENT_RE = re.compile(
    r"^\s*(?P<name>[a-z][a-z0-9_]*)\s*=\s*(?P<value>[+-]?[0-9.]+(?:e[+-]?[0-9]+)?)",
    re.IGNORECASE | re.MULTILINE,
)
LIMITS = {
    "vout_final": (190.0, 210.0, "V"),
    "vout_ripple": (0.0, 1.0, "Vpp"),
    "vout_max": (0.0, 215.0, "V"),
    "sw_max": (0.0, 65.0, "V"),
    "secondary_max": (0.0, 220.0, "V"),
}
MEASUREMENTS = {*LIMITS, "fb_final", "iusb_final"}


def run(arguments: list[str], *, cwd: Path) -> None:
    completed = subprocess.run(
        arguments,
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(
            f"command failed with exit code {completed.returncode}: {' '.join(arguments)}"
            + (f"\n{detail}" if detail else "")
        )


def measurements(log: Path) -> dict[str, float]:
    parsed = {
        match.group("name").lower(): float(match.group("value"))
        for match in MEASUREMENT_RE.finditer(log.read_text(encoding="utf-8"))
    }
    missing = sorted(MEASUREMENTS - parsed.keys())
    if missing:
        raise ValueError(f"ngspice log is missing measurements: {', '.join(missing)}")
    values = {name: parsed[name] for name in sorted(MEASUREMENTS)}
    if any(not math.isfinite(value) for value in values.values()):
        raise ValueError("ngspice returned a non-finite measurement")
    return values


def finding(
    name: str, value: float, minimum: float, maximum: float, unit: str
) -> dict[str, Any]:
    return {
        "id": f"SIM-NIXIE-REV1-{name.upper().replace('_', '-')}",
        "severity": "error",
        "category": "simulation",
        "message": f"{name} is {value:.6g} {unit}; expected {minimum:g}–{maximum:g} {unit}.",
        "remediation": "Inspect the generated SPICE deck, log, and waveform before release.",
    }


def simulate() -> ProjectResult:
    destination = SIMULATION / "build" / "release"
    destination.mkdir(parents=True, exist_ok=True)
    kicad_cli = shutil.which("kicad-cli")
    ngspice = shutil.which("ngspice")
    if kicad_cli is None:
        raise RuntimeError("kicad-cli is required")
    if ngspice is None:
        raise RuntimeError("ngspice is required")

    deck = destination / "nixie_rev1.cir"
    log = destination / "nixie_rev1-ngspice.log"
    summary = destination / "nixie_rev1-simulation.json"
    run(
        [
            kicad_cli,
            "sch",
            "export",
            "netlist",
            "--format",
            "spice",
            "-o",
            str(deck),
            str(SCHEMATIC),
        ],
        cwd=SCHEMATIC.parent,
    )
    run([ngspice, "-b", "-o", str(log), str(deck)], cwd=SCHEMATIC.parent)

    values = measurements(log)
    findings = tuple(
        finding(name, values[name], minimum, maximum, unit)
        for name, (minimum, maximum, unit) in LIMITS.items()
        if not minimum <= values[name] <= maximum
    )
    artifact_paths = (deck, log, summary)
    repo = PROJECT
    report = {
        "project": "nixie_rev1",
        "status": "FAIL" if findings else "PASS",
        "measurements": values,
        "limits": {
            name: {"minimum": minimum, "maximum": maximum, "unit": unit}
            for name, (minimum, maximum, unit) in LIMITS.items()
        },
        "artifacts": [
            path.resolve().relative_to(repo).as_posix() for path in artifact_paths
        ],
    }
    summary.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return ProjectResult(data=report, findings=findings, exit_code=1 if findings else 0)


def main() -> None:
    raise SystemExit(
        execute(
            "simulate",
            simulate,
            description=__doc__ or "Run project simulation",
        )
    )


if __name__ == "__main__":
    main()
