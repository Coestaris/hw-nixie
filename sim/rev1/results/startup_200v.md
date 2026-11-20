# Startup simulation at the 200 V command

Run conditions: current production schematic with `R6=1 MΩ`, 5 V USB source ramped over 100 µs, converter enabled at 1 ms, `MC_BOOST_CV=1.65 V`, `RLOAD=100 kΩ`, 100 ms transient, and initially discharged output capacitors. KiCad 10.0.4 exported the schematic directly and ngspice 46 completed the run.

`T1` is the TDK `ATB322524-0110-T000` (`C249001`). Its simulation subcircuit uses the manufacturer values: 7 µH primary inductance, 1:10.2 turns ratio, 0.5/60 Ω maximum winding DCR, and coupling derived from the 0.4 µH maximum leakage inductance.

| Measurement | Current schematic |
|---|---:|
| Average output, 99–100 ms | 199.94 V |
| Output ripple, 99–100 ms | 0.19 Vpp |
| Output peak | 200.05 V |
| 5% settling time | 76.52 ms |
| Primary on-current peak | 1.18 A |
| Switch-node peak | 60.59 V |
| Positive secondary-node peak | 201.28 V |
| Time-weighted USB current, 99–100 ms | 183 mA |

## Interpretation

The corrected behavioral model reaches the requested 200 V operating point without startup overshoot and with modest final ripple, so the symbol pin mapping, KiCad SPICE glue, transformer ratio, rectifier polarity, and feedback direction are internally consistent. The power stage is now a passive switch rather than the behavioral current-source switch that produced nonphysical energy accounting, and reported averages use time-weighted integration. The large negative secondary excursion remains a topology-model result and is not a trustworthy component-stress prediction.

This does not prove that the physical converter is ready to order. TDK does not mark relative winding polarity with dots, so the simulation assumes pins 1 and 2 are the in-phase winding starts. The transformer model omits saturation, winding capacitance, core loss, temperature behavior, and statistical tolerances. XLSEMI specifies built-in soft-start and switch-pin overvoltage protection but does not publish their timing or threshold; the model therefore assumes a 50 ms ramp and a 60 V clamp. The simulated 60.59 V clamp-knee peak is not component-stress sign-off. Hardware validation should confirm polarity, peak/RMS winding current, switch and diode stress, thermal rise, regulation, startup, and fault behavior.

The exported netlist, raw waveform, metrics JSON, and ngspice log are generated under `sim/build/sim-fix/` and are intentionally ignored by Git.
