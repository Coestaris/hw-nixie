# Native KiCad simulation support

The PCB-linked schematic at [`../../hardware/rev2/nixie_rev2.kicad_sch`](../../hardware/rev2/nixie_rev2.kicad_sch) is the simulation schematic. It embeds `Sim.Device`, `Sim.Library`, `Sim.Name`, and `Sim.Pins` mappings and includes the local source/load deck plus the default 100 ms transient profile. No generated schematic copy is required.

## Run in KiCad

1. Open [`../../hardware/rev2/nixie_rev2.kicad_pro`](../../hardware/rev2/nixie_rev2.kicad_pro).
2. Open the schematic and choose **Inspect → Simulator**.
3. Run the included transient analysis. Probe `LINE`, `FB`, `Net-(D1-A)`, `Net-(D2-A)`, `Net-(D2-K)`, and `I(VUSB)`.

The default setup is:

| Net or source | Value | Purpose |
|---|---:|---|
| `VCC` / `VUSB` | 5 V | Future USB supply |
| `MC_BOOST_EN` / `VEN` | 5 V at 1 ms | Enables the XL6007 model |
| `MC_BOOST_CV` / `VCV` | 1.65 V | Mid-scale 0–3.3 V command; 154.4 V nominal output with the current feedback network |
| `LINE` / `RLOAD` | 100 kΩ | About 1.54 mA at the nominal mid-scale output |

The test points `TP1`–`TP5` and one-pin external connectors `J2`–`J7` are excluded from SPICE export. KiCad's DNP flag excludes the unpopulated clamp parts `R2`, `C3`, and `D1`. Resistors, capacitors, and `L1` export as native primitives; local mappings cover `F1`, `D1`, `D2`, `Q1`, `T1`, `U1`, and `U2`.

## Important nets

| Net | Role |
|---|---|
| `VCC` | 5 V before `F1` |
| `Net-(T1-P2)` | Fused 5 V rail and transformer primary input |
| `Net-(D1-A)` | XL6007 switch node and the other primary terminal |
| `Net-(D2-A)` | Full-secondary flyback node before `D2` |
| `Net-(D2-K)` | Rectified high-voltage node before `L1` |
| `LINE` | Filtered high-voltage output |
| `FB` | XL6007 feedback and Q1 drain node |
| `MC_BOOST_CV` | Output-voltage command |

## Model status

| Reference | Model | Status |
|---|---|---|
| `U1` XL6007 | 400 kHz passive PWM switch with 90% maximum duty, approximate 2 A cycle limit, assumed 50 ms soft-start, and approximate 60 V clamp | Soft-start time and clamp characteristic are assumptions; no detailed compensation, thermal, or loss behavior |
| `U2` MCP6001 | Rail-limited 1 MHz behavioral op-amp | Replace with the manufacturer macro-model for detailed work |
| `T1` TDK ATB322524-0110-T000 / C249001 | Coupled inductors: 7 µH, 1:10.2, 0.5/60 Ω max DCR, coupling derived from 0.4 µH max leakage | Datasheet-based approximation; no saturation, winding capacitance, core loss, temperature, or verified polarity |
| `D2` ES2J | Generic 600 V fast-diode model | Forward/recovery behavior is approximate |
| `D1` ES2D | Excluded | The clamp diode and its `R2`/`C3` network are DNP |
| `D3` NCD0603R1 | Generic red-LED diode model | Electrical loading only; no optical model |
| `Q1` 2N7002 | Level-1 NMOS | Generic electrical approximation |
| `F1` JK-nSMD100-16 1 A polyfuse | 55 mΩ resistor | Closed-state approximation only |

ERC intentionally ignores the included-source `power_pin_not_driven` reports, the XL6007 SW5/SW6 `pin_to_pin` report, and the inherited cached-symbol mismatch. All other enabled ERC checks pass.

The current mid-scale startup investigation is documented in [`results/startup_midscale.md`](results/startup_midscale.md). The earlier [`results/startup_200v.md`](results/startup_200v.md) is historical and predates the feedback resistor change. The included run-deck filename remains `startup_200v.spice` for compatibility with the schematic directive; its 1.65 V command now targets about 154.4 V. Raw data and exported files are generated under `build/` and ignored by Git. The analysis tool uses time-weighted integration for averages because ngspice transient points are adaptively spaced.

The reusable Nixie analysis helpers are an independent UV project in
[`../rev1`](../rev1). From the repository root, invoke
`uv run --project sim/rev1 nixie-build-run-deck`,
`nixie-analyze-startup`, or `nixie-build-waveform-visual`; use `--help` for
each command's file arguments.

## References

- [XL6007 datasheet](https://www.xlsemi.com/datasheet/XL6007-EN.pdf)
- [MCP6001 product page and simulation model](https://www.microchip.com/en-us/product/mcp6001)
- [TDK ATB322524-0110-T000 product page](https://product.tdk.com/en/search/transformer/transformer/step-up/info?part_no=ATB322524-0110-T000)
- [LCSC C249001 datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_1810201243_TDK-ATB322524-0110-T000_C249001.pdf)
- [ES2A–ES2J datasheet](https://www.smc-diodes.com/propdf/ES2%28A-J%29%20N0160%20REV.D.pdf)
- [onsemi 2N7002 datasheet](https://www.onsemi.com/download/data-sheet/pdf/nds7002a-d.pdf)
