"""Summarize the Nixie ngspice startup raw file and emit compact plot data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def read_raw(path: Path) -> tuple[dict[str, str], list[str], np.ndarray]:
    headers: dict[str, str] = {}
    variables: list[str] = []
    reading_variables = False

    with path.open("rb") as handle:
        while True:
            raw_line = handle.readline()
            if not raw_line:
                raise ValueError("Raw file ended before Binary or Values section")
            line = raw_line.decode("utf-8", errors="replace").strip()
            if line == "Binary:":
                encoding = "binary"
                break
            if line == "Values:":
                encoding = "ascii"
                break
            if line == "Variables:":
                reading_variables = True
                continue
            if reading_variables:
                parts = line.split()
                if len(parts) >= 3 and parts[0].isdigit():
                    variables.append(parts[1].lower())
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()

        variable_count = int(headers["no. variables"])
        point_count = int(headers["no. points"])
        if len(variables) != variable_count:
            raise ValueError(
                f"Expected {variable_count} variables, parsed {len(variables)}"
            )
        if encoding == "binary":
            flat = np.fromfile(handle, dtype="<f8", count=variable_count * point_count)
        else:
            flat = np.empty(variable_count * point_count, dtype=np.float64)
            offset = 0
            for point in range(point_count):
                first = handle.readline().decode("utf-8", errors="replace").split()
                if len(first) < 2 or int(first[0]) != point:
                    raise ValueError(f"Malformed ASCII raw data at point {point}")
                flat[offset] = float(first[-1])
                offset += 1
                for _ in range(1, variable_count):
                    value = handle.readline().decode("utf-8", errors="replace").strip()
                    if not value:
                        raise ValueError(f"ASCII raw data ended at point {point}")
                    flat[offset] = float(value)
                    offset += 1

    if flat.size != variable_count * point_count:
        raise ValueError("Raw binary payload is shorter than its header")
    return headers, variables, flat.reshape(point_count, variable_count)


def column(variables: list[str], data: np.ndarray, name: str) -> np.ndarray:
    wanted = name.lower()
    try:
        return data[:, variables.index(wanted)]
    except ValueError as error:
        raise KeyError(f"Missing vector {name!r}; available: {variables}") from error


def finite(value: float | None) -> float | None:
    if value is None or not np.isfinite(value):
        return None
    return round(float(value), 6)


def downsample(indices: np.ndarray, limit: int) -> np.ndarray:
    if indices.size <= limit:
        return indices
    stride = int(np.ceil(indices.size / limit))
    sampled = indices[::stride]
    if sampled[-1] != indices[-1]:
        sampled = np.append(sampled, indices[-1])
    return sampled


def rounded(values: np.ndarray, digits: int) -> list[float]:
    return np.round(values, digits).tolist()


def time_average(time: np.ndarray, values: np.ndarray, mask: np.ndarray) -> float:
    selected_time = time[mask]
    selected_values = values[mask]
    if selected_time.size == 0:
        raise ValueError("Cannot average an empty time window")
    duration = float(selected_time[-1] - selected_time[0])
    if duration <= 0:
        return float(selected_values[-1])
    return float(np.trapezoid(selected_values, selected_time) / duration)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--target", type=float, default=200.0)
    parser.add_argument("--load", type=float, default=100_000.0)
    args = parser.parse_args()

    headers, variables, data = read_raw(args.raw)
    time = column(variables, data, "time")
    vout = column(variables, data, "v(line)")
    fb = column(variables, data, "v(fb)")
    control = column(variables, data, "v(mc_boost_cv)")
    switch = column(variables, data, "v(net-_d1-a_)")
    secondary = column(variables, data, "v(net-_d2-a_)")
    rectified = column(variables, data, "v(net-_d2-k_)")
    q1_source = column(variables, data, "v(net-_q1-s_)")
    q1_gate = column(variables, data, "v(net-_q1-g_)")
    input_current = -column(variables, data, "i(vusb)")
    primary_on_current = -column(variables, data, "i(@l.xt1.lprimary[i])")

    final_start = max(float(time[-1]) - 1e-3, float(time[0]))
    final = time >= final_start
    target = args.target
    band = np.abs(vout - target) <= target * 0.05
    remains_in_band = np.logical_and.accumulate(band[::-1])[::-1]
    settled_indices = np.flatnonzero(remains_in_band)
    settling_time = float(time[settled_indices[0]]) if settled_indices.size else None

    final_vout = time_average(time, vout, final)
    final_iin = time_average(time, input_current, final)
    output_power = time_average(time, vout**2 / args.load, final)
    input_power = time_average(time, 5.0 * input_current, final)
    active = time >= 1e-3
    input_energy = float(np.trapezoid(5.0 * input_current[active], time[active]))
    load_energy = float(np.trapezoid(vout[active] ** 2 / args.load, time[active]))
    load_to_input_energy = load_energy / input_energy if input_energy > 0 else None

    startup_indices = downsample(np.arange(time.size), 1600)
    switch_peak_index = int(np.argmax(switch))
    detail_start = max(float(time[switch_peak_index]) - 10e-6, float(time[0]))
    detail_stop = min(float(time[switch_peak_index]) + 15e-6, float(time[-1]))
    detail_window = (time >= detail_start) & (time <= detail_stop)
    detail_indices = downsample(np.flatnonzero(detail_window), 1600)
    detail_origin = float(time[detail_indices[0]])

    result = {
        "source": str(args.raw),
        "headers": headers,
        "variables": variables,
        "metrics": {
            "target_v": target,
            "simulated_ms": finite(float(time[-1]) * 1e3),
            "points": int(time.size),
            "vout_final_avg_v": finite(final_vout),
            "vout_final_min_v": finite(float(np.min(vout[final]))),
            "vout_final_max_v": finite(float(np.max(vout[final]))),
            "vout_final_ripple_vpp": finite(float(np.ptp(vout[final]))),
            "vout_peak_v": finite(float(np.max(vout))),
            "fb_final_avg_v": finite(time_average(time, fb, final)),
            "q1_source_final_avg_v": finite(
                time_average(time, q1_source, final)
            ),
            "q1_gate_final_avg_v": finite(time_average(time, q1_gate, final)),
            "input_current_final_avg_a": finite(final_iin),
            "input_current_peak_a": finite(float(np.max(input_current))),
            "input_current_peak_after_enable_a": finite(
                float(np.max(input_current[active]))
            ),
            "primary_on_current_peak_a": finite(
                float(np.max(primary_on_current))
            ),
            "input_power_final_avg_w": finite(input_power),
            "output_power_final_avg_w": finite(output_power),
            "load_to_input_energy_ratio": finite(load_to_input_energy),
            "settling_time_5pct_ms": finite(
                settling_time * 1e3 if settling_time is not None else None
            ),
            "switch_node_min_v": finite(float(np.min(switch))),
            "switch_node_max_v": finite(float(np.max(switch))),
            "switch_peak_time_ms": finite(float(time[switch_peak_index]) * 1e3),
            "secondary_node_min_v": finite(float(np.min(secondary))),
            "secondary_node_max_v": finite(float(np.max(secondary))),
            "rectified_node_max_v": finite(float(np.max(rectified))),
        },
        "startup": {
            "time_ms": rounded(time[startup_indices] * 1e3, 6),
            "vout_v": rounded(vout[startup_indices], 5),
            "fb_v": rounded(fb[startup_indices], 6),
            "q1_source_v": rounded(q1_source[startup_indices], 6),
            "control_v": rounded(control[startup_indices], 6),
            "input_current_a": rounded(input_current[startup_indices], 6),
        },
        "switching_detail": {
            "time_us": rounded((time[detail_indices] - detail_origin) * 1e6, 6),
            "switch_v": rounded(switch[detail_indices], 5),
            "secondary_v": rounded(secondary[detail_indices], 5),
            "rectified_v": rounded(rectified[detail_indices], 5),
            "vout_v": rounded(vout[detail_indices], 5),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
