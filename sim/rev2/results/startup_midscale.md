# Current mid-scale startup simulation

The current schematic has `R10`–`R12 = 3 MΩ` in series, `R13 = 29.4 kΩ`, `R3 = 62 kΩ`, `R4 = 5.1 kΩ`, and `R7 = 14.7 kΩ`. With a 1.25 V feedback reference and a 1.65 V DAC command, its nominal output target is

`1.25 × (1 + 3 MΩ / 29.4 kΩ) + (3 MΩ / 14.7 kΩ) × (1.65 × 5.1 kΩ / (62 kΩ + 5.1 kΩ)) = 154.39 V`.

The same equation gives 128.80 V and 179.99 V at 0 V and 3.3 V command. These are nominal setpoints, not guaranteed output bounds. The simulation uses 5 V USB input, enable at 1 ms, a 100 kΩ load, initially discharged output capacitors, and a 100 ms transient. The deck is named `startup_200v.spice` for historical compatibility with the schematic include; its command remains 1.65 V.

| Measurement | Current run | Check |
|---|---:|---|
| Average output, 99–100 ms | 155.915 V | Within 154.39 ± 5 V |
| Output ripple, 99–100 ms | 0.0448 Vpp | Below 1 Vpp |
| Output peak | 159.296 V | Below 169.39 V startup limit |
| Switch-node peak | 60.543 V | Within the approved 65 V simulation limit; above the XL6007 60 V absolute maximum |

The output target check now follows the current resistor network, so the earlier 170–200 V test window no longer applies. The 65 V simulation limit is a specific user-approved allowance of 5 V above the device rating. [XLSEMI's current XL6007 datasheet](https://www.xlsemi.com/datasheet/XL6007-EN.pdf) gives the switch pin a 60 V absolute maximum and mentions built-in overvoltage protection without publishing a clamp threshold or waveform. The behavioral model assumes a 60 V avalanche-style clamp. Its simulated 60.54 V peak is therefore a model-knee result, not a prediction of real silicon stress or proof that the board is safe at 60 V. The DNP `D1`/`R2`/`C3` clamp network is absent from this run. Confirm the physical switch waveform, transformer polarity and saturation, and any required clamp/snubber design on hardware before manufacturing sign-off.

Exploratory runs using the same exported circuit and 0 V/3.3 V commands gave 135.48 V/180.26 V at 99–100 ms, against nominal setpoints of 128.80 V/179.99 V. Their switch peaks were 60.495 V/60.568 V. The low-command error and simulated feedback voltages around 1.30–1.31 V show the limits of the behavioral controller; the XL6007 datasheet's 1.213–1.287 V feedback specification is stated at different input, output, and load conditions. These endpoint runs are diagnostic and do not establish a guaranteed control range.

Run `uv run --project tools python sim/rev2/simulate.py --format json` from the repository root. Generated netlist, log, and JSON report are under `sim/build/release/` and ignored by Git.
