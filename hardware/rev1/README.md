# Nixie clock — revision 1

Manufactured boost-converter board built to test the topology for a USB-powered nixie clock: a nominal 5 V input and an adjustable 150–250 V output. The full clock schematic is in revision 2.

The only KiCad project is [`nixie_rev1.kicad_pro`](nixie_rev1.kicad_pro). Its schematic is PCB-linked and also contains the KiCad/ngspice model mappings, testbench includes, and default transient analysis. The [`../../sim/rev1`](../../sim/rev1) directory contains supporting behavioral models, run profiles, result notes, and analysis tools; it does not contain a second schematic or project copy.

## Current hardware state

- `Q1` uses the project-local `nixie_rev1:2N7002` symbol with KiCad's standard `Package_TO_SOT_SMD:SOT-23` footprint (`1=G`, `2=S`, `3=D`).
- `T1` is JLCPCB/LCSC `C249001`, TDK `ATB322524-0110-T000` (Extended, Production/NRND). It uses the project-local `nixie_rev1:ATB322524-0110-T000` symbol and datasheet-derived `nixie_rev1:TDK_ATB3225` footprint. Physical pins 1–4 are the primary and pins 2–3 are the secondary.
- `U1` is JLCPCB/LCSC `C5240411`, XLSEMI `XL6007E1`, using the matching 150-mil `SOIC-8_3.9x4.9mm_P1.27mm` footprint.
- `D3` is JLCPCB/LCSC `C84263`, NationStar `NCD0603R1`; its datasheet explicitly matches KiCad's pad-1-cathode LED polarity.
- `F1` is the 1206 resettable PTC JLCPCB/LCSC `C369161`, Jinrui `JK-nSMD100-16` (1 A hold, 16 V maximum).
- Simulation defaults are 5 V input, enable asserted at 1 ms, `MC_BOOST_CV=1.65 V`, and a 100 kΩ high-voltage load.
- With the current `R6=1 MΩ` schematic and the C249001 transformer approximation, the 30 ms behavioral startup run settles near 204.75 V with about 0.76 Vpp ripple.

This revision has been manufactured. The following model limitations remain relevant. The TDK transformer ratings and land pattern are verified, but the behavioral models remain suitable only for topology work, not efficiency or stress sign-off. Transformer polarity, saturation, winding capacitance, compensation, startup, component stress, and fault behavior still need bench verification. See [`../../sim/rev1/results/startup_200v.md`](../../sim/rev1/results/startup_200v.md).
