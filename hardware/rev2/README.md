# Nixie clock — revision 2

This revision has a USB-powered 5 V boost supply and four IN-8-2 lamp docks. With `R3=62k`, `R4=5.1k`, and `R13=29.4k`, the nominal feedback equation gives 128.8–180.0 V for a 0–3.3 V DAC command. Component and reference tolerances can take the output beyond these endpoints; the resistor changes do not enforce a hard 180 V ceiling.

The only KiCad project is [`nixie_rev2.kicad_pro`](nixie_rev2.kicad_pro). Its schematic is PCB-linked and also contains the KiCad/ngspice model mappings, testbench includes, and default transient analysis. The [`../../sim/rev2`](../../sim/rev2) directory contains supporting behavioral models, run profiles, result notes, and analysis tools; it does not contain a second schematic or project copy.

## Current hardware state

- `N1`–`N4` use the project-local `nixie_rev2:IN-8-2_Dock` symbol and footprint. Each footprint reproduces the exact four diagonal 1×3, 2.54 mm header locations from the historical lamp-dock design; the inner lamp-solder pads remain part of the manufactured dock and are intentionally not duplicated on the motherboard.
- `Q1` uses the project-local `nixie_rev2:2N7002` symbol with KiCad's standard `Package_TO_SOT_SMD:SOT-23` footprint (`1=G`, `2=S`, `3=D`).
- `T1` is JLCPCB/LCSC `C249001`, TDK `ATB322524-0110-T000` (Extended, Production/NRND). It uses the project-local `nixie_rev2:ATB322524-0110-T000` symbol and datasheet-derived `nixie_rev2:TDK_ATB3225` footprint. Physical pins 1–4 are the primary and pins 2–3 are the secondary.
- `U1` is JLCPCB/LCSC `C5240411`, XLSEMI `XL6007E1`, using the matching 150-mil `SOIC-8_3.9x4.9mm_P1.27mm` footprint.
- `D3` is JLCPCB/LCSC `C84263`, NationStar `NCD0603R1`; its datasheet explicitly matches KiCad's pad-1-cathode LED polarity.
- `F1` is the 1206 resettable PTC JLCPCB/LCSC `C369161`, Jinrui `JK-nSMD100-16` (1 A hold, 16 V maximum).
- `R20`, `R25`, `R30`, and `R37` are 33 kΩ 1206 parts (`C137309`) feeding the digit anodes. `R38` is a 130 kΩ 1206 part (`C229306`) in the dot cathode path. At 180 V and the IN-8-2's 100 V keep-up voltage, nominal digit current is 2.42 mA and dot current is 0.49 mA. The digit resistor dissipates 0.194 W against its 0.25 W rating at 70 °C; a shorted tube exceeds that rating. The lamp may not ignite at the low end of the boost range.
- Simulation defaults are 5 V input, enable asserted at 1 ms, `MC_BOOST_CV=1.65 V`, and a 100 kΩ high-voltage load.
- The current 100 ms mid-scale startup simulation reaches about 156 V, near the 154.4 V feedback-equation target. Its modeled clamp reaches about 60.54 V. The simulation gate permits up to 65 V under an explicit 5 V user allowance; the physical XL6007 switch rating remains 60 V.

This revision has been manufactured. The following model limitations remain relevant. The TDK behavioral models remain suitable only for topology work, not efficiency or stress sign-off. Transformer polarity, saturation, winding capacitance, compensation, startup, component stress, and fault behavior still need bench verification. See [`../../sim/rev2/results/startup_midscale.md`](../../sim/rev2/results/startup_midscale.md).

## Mechanical assembly

N1–N4 each show the [dock STEP assembly](../../assets/Nixie/dock_rev1-assembly.stpz) seated on four straight 1×3, 2.54 mm male headers. The dock model has a Z offset of 11.125 mm from the Rev2 model mount plane. SolidCraft inspection of the assembled STEP confirmed the four header and socket row centers and the mating planes.

In KiCad’s 3D Viewer, enable **Show 3D Models not in POS File** (`P`) and **Show Unspecified 3D Models** (`V`) to display the mechanical references. [KiCad 3D Viewer controls](https://docs.kicad.org/10.0/en/pcbnew/pcbnew.html)

H1–H4 use [M2 × 12 female–female hex spacers](../../assets/Mechanical/Hex_Standoff_M2_L12.stpz) centered under the Ø2.2 mm mounting holes. The 12 mm length leaves 2.1 mm below the tallest modeled underside component. The [SolidCraft source](../../assets/Mechanical/Hex_Standoff_M2_L12.sc) recreates the 4 mm across-flats envelope and uses a simplified axial bore. The supplied `Spacer M2 F F 12mm.stp` from `spacers-m2-1.snapshot.3.zip` contained open surfaces. Its SHA-256 is `842bb0d11cc96b8b27d7705f7006af9b003dc60c31174bb7509f7d39eccfacad`.
