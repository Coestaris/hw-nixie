# IN-8-2 Nixie Dock, revision 1

This two-layer adapter carries one wire-ended IN-8-2 tube and plugs into a Rev2 clock motherboard. The tube mounts on the front, with four 1×3, 2.54 mm female sockets on the back. The motherboard supplies the high-voltage drive and current limiting. Open [dock_rev1.kicad_pro](dock_rev1.kicad_pro) in KiCad 10.

The outline and pad centers come from `projects/legacy/nixie/hardware/nixie.kicad_pcb` in `Coestaris/hardware-legacy` at `8a1bb16d6e56aa4d5cadc9abd9d31d0f6d3bca59`. Silkscreen rings identify the anode at the lamp and socket. The tube footprint uses the manufacturer's positions 2 through 13. The routes for the decimal point and digits 8 and 9 follow the tube passport while preserving the Rev2 motherboard pin assignments. [IN-8-2 manufacturer passport, page 2](../../assets/Nixie/IN-8-2.pdf)

The positions below are viewed from the tube side with the gap in the lamp pin circle at the top. Square pads mark socket pin 1.

| Socket | Position | Pin 1 | Pin 2 | Pin 3 |
| --- | --- | --- | --- | --- |
| J1 | Lower right | Decimal point | Digit 9 | Digit 8 |
| J2 | Lower left | Digit 7 | Digit 6 | Digit 5 |
| J3 | Upper left | Digit 4 | Digit 3 | Digit 2 |
| J4 | Upper right | Digit 1 | Digit 0 | Anode |

The lamp's [SolidCraft source](../../assets/Nixie/IN-8-2.sc) uses the documented maximum bulb envelope and the twelve legacy drill centers. Lead diameter, trimming, and bulb standoff are modeling assumptions. The supplied SolidWorks file could not be imported. The [model check](../../assets/Nixie/IN-8-2-qa.json) records the assumptions and verifies every lead against its plated hole. Physical fit and powered operation remain unverified.

## Release status

The GitHub Action target is `dock` and the release tag is `dock_rev1`. The [JLCPCB fabrication-only profile](../../assets/manufacturing/dock_rev1.yaml) selects the board, drill, drawing, and 3D artifacts for this hand-assembled design. KiCad ERC and DRC with schematic parity reported zero findings.
