"""Run the complete Nixie Rev2 schematic through KiCad and ngspice."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from common.project_cli import ProjectResult, execute

SIM = Path(__file__).resolve().parent
PROJECT = SIM.parents[1]
REPO = PROJECT
HARDWARE = PROJECT / "hardware" / SIM.name
SCHEMATIC = HARDWARE / "nixie_rev2.kicad_sch"
BUILD = SIM / "build" / "release"
PLACEHOLDER = re.compile(r"^\S+\s+__\S+", re.MULTILINE)
MEASUREMENT = re.compile(
    r"^\s*(?P<name>[a-z][a-z0-9_]*)\s*=\s*(?P<value>[+-]?[0-9.]+(?:e[+-]?[0-9]+)?)",
    re.IGNORECASE | re.MULTILINE,
)
NOMINAL_MID_SCALE_VOUT = 1.25 * (1 + 3e6 / 29.4e3) + (
    3e6 * (1.65 * 5.1e3 / (62e3 + 5.1e3)) / 14.7e3
)
# R10-R12, R13, R3, R4, and R7 in the current schematic set this target.
# The 5 V regulation window and 15 V peak allowance detect a changed circuit
# or startup overshoot while allowing the documented behavioral-model error.
LIMITS = {
    "vout_final": (NOMINAL_MID_SCALE_VOUT - 5.0, NOMINAL_MID_SCALE_VOUT + 5.0, "V"),
    "vout_ripple": (0.0, 1.0, "Vpp"),
    "vout_max": (0.0, NOMINAL_MID_SCALE_VOUT + 15.0, "V"),
    # User-approved 5 V simulation allowance above the XL6007's 60 V rating.
    # This is specific to the assumed clamp model, not physical stress sign-off.
    "sw_max": (0.0, 65.0, "V"),
}


def finding(identifier: str, message: str, remediation: str) -> dict[str, Any]:
    return {
        "id": f"SIM-NIXIE-REV2-{identifier}",
        "severity": "error",
        "category": "simulation",
        "message": message,
        "remediation": remediation,
    }


def command(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=HARDWARE,
        check=False,
        text=True,
        capture_output=True,
    )


def run() -> ProjectResult:
    BUILD.mkdir(parents=True, exist_ok=True)
    kicad_cli = shutil.which("kicad-cli")
    ngspice = shutil.which("ngspice")
    if kicad_cli is None or ngspice is None:
        raise RuntimeError("kicad-cli and ngspice are required")

    deck = BUILD / "nixie_rev2.cir"
    log = BUILD / "nixie_rev2-ngspice.log"
    summary = BUILD / "nixie_rev2-simulation.json"
    exported = command(
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
        ]
    )
    if exported.returncode:
        detail = (exported.stderr or exported.stdout).strip()
        raise RuntimeError(f"KiCad SPICE export failed: {detail}")

    placeholders = sorted(
        {
            line.split()[0]
            for line in PLACEHOLDER.findall(deck.read_text(encoding="utf-8"))
        }
    )
    if placeholders:
        return ProjectResult(
            data={
                "artifacts": [deck.relative_to(REPO).as_posix()],
                "unmodeled_components": placeholders,
            },
            findings=(
                finding(
                    "UNMODELED",
                    f"The complete netlist contains {len(placeholders)} unmodeled components.",
                    "Assign verified models or exclude nonsimulated devices explicitly.",
                ),
            ),
            exit_code=1,
        )

    simulated = command([ngspice, "-b", "-o", str(log), str(deck)])
    if simulated.returncode:
        detail = log.read_text(encoding="utf-8") if log.exists() else simulated.stderr
        raise RuntimeError(f"ngspice failed: {detail.strip()[-1200:]}")

    values = {
        match.group("name").lower(): float(match.group("value"))
        for match in MEASUREMENT.finditer(log.read_text(encoding="utf-8"))
    }
    missing = sorted(set(LIMITS) - values.keys())
    if missing:
        raise RuntimeError(
            f"ngspice omitted required measurements: {', '.join(missing)}"
        )
    findings = tuple(
        finding(
            name.upper().replace("_", "-"),
            f"{name} is {values[name]:.6g} {unit}; expected {low:g}–{high:g} {unit}.",
            (
                "Measure the physical switch waveform and verify the protection/clamp design; "
                "the model's assumed 60 V clamp cannot establish device stress."
                if name == "sw_max"
                else "Inspect the generated netlist, models, and simulation log."
            ),
        )
        for name, (low, high, unit) in LIMITS.items()
        if not low <= values[name] <= high
    )
    artifacts = [deck, log, summary]
    report = {
        "project": "nixie_rev2",
        "status": "FAIL" if findings else "PASS",
        "nominal_mid_scale_vout": NOMINAL_MID_SCALE_VOUT,
        "measurements": values,
        "limits": {
            name: {"minimum": low, "maximum": high, "unit": unit}
            for name, (low, high, unit) in LIMITS.items()
        },
        "artifacts": [path.relative_to(REPO).as_posix() for path in artifacts],
    }
    summary.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return ProjectResult(data=report, findings=findings, exit_code=1 if findings else 0)


def main() -> None:
    raise SystemExit(
        execute("simulate", run, description=__doc__ or "Run project simulation")
    )


if __name__ == "__main__":
    main()
