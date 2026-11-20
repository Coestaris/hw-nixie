# Y8-8682053A — rotation review, 2026-11-04

The submitted CPL reproduces the earlier corrected file exactly, but this does not verify JLCPCB’s final SMT placements. The supplied production package is PCB fabrication/CAM data. Its Gerber and ODB++ files have no component layer, final placement table, or assembly drawing. The DDW archive also contains PCB layers and CAM processing data rather than SMT placements. PCB fabrication confirmation and SMT placement confirmation are separate decisions; this review does not approve the PCB CAM geometry.

## Result

Hold SMT orientation approval pending JLCPCB’s final Part Placement view. The screenshot has **Confirm Parts Placement: No**, so request an explicit placement-review hold rather than assuming a later approval prompt will appear.

The prior 59-change file missed the MMBTA92 group below. Exact numbered-footprint comparison indicates quarter-turn discrepancies in the submitted CPL:

| Reference | LCSC part | Submitted | Candidate to verify |
|---|---|---:|---:|
| Q2 | C19184662 | 135° | 225° |
| Q5 | C19184662 | 135° | 225° |
| Q7 | C19184662 | 225° | 135° |
| Q9 | C19184662 | 225° | 135° |

The part-specific EasyEDA footprint is `SOT-23-3_L2.9-W1.3-P0.95-LS2.4-BR`. All three numbered pads select the candidate orientation, with RMS center difference about 0.203 mm, compared with about 1.839 mm at the submitted angle. The remaining 0.203 mm reflects different KiCad/vendor land-pattern spans, so this is orientation screening, not a dimensional fit approval. The original model screenshot is consistent with this zero frame; JLCPCB’s final selected-part/model orientation and any engineer adjustments must still be checked.

The original preview had no visible model for Q3/Q4/Q6/Q8/Q22 (C50229541). The current exact-part CAD lookup returns component-not-found, so these five also require the actual final SMT view. Do not infer their zero orientation from another SOT-23 supplier.

## Checks completed

- Submitted BOM, CPL and current database usages contain the same 106 references, with matching exact LCSC parts, footprints and values.
- All submitted X/Y coordinates and bottom-side assignments match the current board.
- Submitted CPL is byte-identical to the earlier 59-change preview: SHA-256 `75e4cc0ddc62b05122a8a64e0ab3d5d40cd2375ab82fdf22b18fafe1e2f7d984`.
- All 59 stored targets match the submitted CPL; their database status remains `proposed`.
- Local BOM/CPL structural validation passes. This validator does not establish physical orientation.
- All 16 original Gerber/drill files retained in the YG archive match the submitted Gerber ZIP byte-for-byte.
- No final SMT placements were found in the Gerber, ODB++ or DDW archive inventory.

## What to obtain before SMT assembly

Ask JLCPCB to hold SMT assembly until the final Part Placement view is checked. Inspect Q2/Q5/Q7/Q9 and Q3/Q4/Q6/Q8/Q22, then the IC pin-1 and polarized-part markings on C5/D2/D3/D12/U1/U3/U8/U9/U10/U11/U12/U13. Obtain the final matched LCSC parts and placement data where available. The candidate changes above have not been applied to the submitted files or the database during this review.

The order settings also differ from the repository profile: Standard versus economic assembly, 1.2 versus 1.6 mm board thickness, and 0.5 versus 1 oz inner copper. This rotation-focused check does not certify the fabrication settings or processed CAM geometry.

## Evidence

[Machine-readable report](review.json) retains the hashes, numbered-pad coordinates, and residuals for all candidate angles. Source: **JLCEDA/EasyEDA Official Library** ([JLCEDA](https://lceda.cn/), [EasyEDA](https://easyeda.com/)); the original API response and its source/license metadata are preserved in [C19184662-easyeda-2026-11-04.json](C19184662-easyeda-2026-11-04.json).

JLCPCB describes the downloaded `ok`/`yg` package as a [PCB production-file review](https://jlcpcb.com/help/article/how-to-confirm-the-production-file). Its [assembly FAQ](https://jlcpcb.com/help/article/pcb-assembly-faqs-part-2) distinguishes orientation marks from guaranteed pin-1 identification and explains the diode polarity symbols.
