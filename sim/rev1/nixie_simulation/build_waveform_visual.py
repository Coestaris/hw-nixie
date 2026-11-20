"""Build the inline waveform comparison from compact simulation summaries."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


WIDTH = 720


def scale(value: float, low: float, high: float, start: float, stop: float) -> float:
    return start + (value - low) * (stop - start) / (high - low)


def polyline(
    xs: list[float],
    ys: list[float],
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    box: tuple[float, float, float, float],
) -> str:
    left, top, right, bottom = box
    points = []
    for x, y in zip(xs, ys, strict=True):
        px = scale(x, x_range[0], x_range[1], left, right)
        py = scale(y, y_range[0], y_range[1], bottom, top)
        points.append(f"{px:.2f},{py:.2f}")
    return " ".join(points)


def grid(
    x_ticks: list[float],
    y_ticks: list[float],
    x_range: tuple[float, float],
    y_range: tuple[float, float],
    box: tuple[float, float, float, float],
    x_unit: str,
    y_unit: str,
) -> str:
    left, top, right, bottom = box
    parts = []
    for tick in x_ticks:
        x = scale(tick, x_range[0], x_range[1], left, right)
        parts.append(
            f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" />'
            f'<text class="axis-label" x="{x:.2f}" y="{bottom + 24}" text-anchor="middle">{tick:g}</text>'
        )
    for tick in y_ticks:
        y = scale(tick, y_range[0], y_range[1], bottom, top)
        parts.append(
            f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" />'
            f'<text class="axis-label" x="{left - 10}" y="{y + 5:.2f}" text-anchor="end">{tick:g}</text>'
        )
    parts.append(
        f'<text class="axis-label" x="{(left + right) / 2:.2f}" y="{bottom + 48}" text-anchor="middle">Time ({html.escape(x_unit)})</text>'
        f'<text class="axis-label" transform="translate(16 {(top + bottom) / 2:.2f}) rotate(-90)" text-anchor="middle">{html.escape(y_unit)}</text>'
    )
    return "".join(parts)


def fmt(value: float | None, digits: int = 2, suffix: str = "") -> str:
    if value is None:
        return "Not reached"
    return f"{value:.{digits}f}{suffix}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("diagnostic", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    diagnostic = json.loads(args.diagnostic.read_text(encoding="utf-8"))
    bm = baseline["metrics"]
    dm = diagnostic["metrics"]

    startup_box = (58, 34, 690, 268)
    startup_grid = grid(
        list(range(0, 31, 5)),
        [0, 50, 100, 150, 200],
        (0, 30),
        (0, 230),
        startup_box,
        "ms",
        "Output voltage (V)",
    )
    baseline_startup = polyline(
        baseline["startup"]["time_ms"],
        baseline["startup"]["vout_v"],
        (0, 30),
        (0, 230),
        startup_box,
    )
    diagnostic_startup = polyline(
        diagnostic["startup"]["time_ms"],
        diagnostic["startup"]["vout_v"],
        (0, 30),
        (0, 230),
        startup_box,
    )
    target_y = scale(200, 0, 230, startup_box[3], startup_box[1])
    baseline_y = scale(bm["vout_final_avg_v"], 0, 230, startup_box[3], startup_box[1])
    diagnostic_y = scale(dm["vout_final_avg_v"], 0, 230, startup_box[3], startup_box[1])

    detail_box = (58, 30, 690, 218)
    detail_grid = grid(
        [0, 5, 10, 15, 20, 25],
        [0, 10, 20, 30, 40],
        (0, 25),
        (-5, 45),
        detail_box,
        "us around peak",
        "Switch node (V)",
    )
    baseline_detail = polyline(
        baseline["switching_detail"]["time_us"],
        baseline["switching_detail"]["switch_v"],
        (0, 25),
        (-5, 45),
        detail_box,
    )
    diagnostic_detail = polyline(
        diagnostic["switching_detail"]["time_us"],
        diagnostic["switching_detail"]["switch_v"],
        (0, 25),
        (-5, 45),
        detail_box,
    )

    fragment = f'''<div id="nixieBoostWaveforms">
  <p class="sr-only">Comparison of the simulated Nixie boost converter with production R6 at 100 kiloohms and a diagnostic R6 at 1 megaohm.</p>
  <svg class="waveform-chart" viewBox="0 0 {WIDTH} 330" role="img" aria-labelledby="startup-title startup-desc">
    <title id="startup-title">Output-voltage startup comparison</title>
    <desc id="startup-desc">The production 100 kiloohm curve peaks below 176 volts, while the diagnostic 1 megaohm curve reaches approximately 205 volts.</desc>
    <text class="plot-label" x="58" y="18">Output startup</text>
    {startup_grid}
    <line class="target" x1="{startup_box[0]}" y1="{target_y:.2f}" x2="{startup_box[2]}" y2="{target_y:.2f}" />
    <text class="axis-label" x="{startup_box[0] + 8}" y="{target_y - 7:.2f}">200 V command</text>
    <polyline class="series baseline" points="{baseline_startup}" />
    <polyline class="series diagnostic" points="{diagnostic_startup}" />
    <circle class="mark baseline-fill" cx="{startup_box[2]}" cy="{baseline_y:.2f}" r="4" />
    <circle class="mark diagnostic-fill" cx="{startup_box[2]}" cy="{diagnostic_y:.2f}" r="4" />
    <text class="direct-label" x="{startup_box[2] - 8}" y="{baseline_y + 18:.2f}" text-anchor="end">R6 100 kOhm: {bm['vout_final_avg_v']:.1f} V</text>
    <text class="direct-label" x="{startup_box[2] - 8}" y="{diagnostic_y - 10:.2f}" text-anchor="end">R6 1 MOhm: {dm['vout_final_avg_v']:.1f} V</text>
  </svg>

  <svg class="waveform-chart" viewBox="0 0 {WIDTH} 280" role="img" aria-labelledby="switch-title switch-desc">
    <title id="switch-title">Switch-node waveform near worst peak</title>
    <desc id="switch-desc">The modeled switch peaks are approximately 33 volts with production R6 and 38.5 volts with diagnostic R6.</desc>
    <text class="plot-label" x="58" y="18">Worst switch-node window</text>
    {detail_grid}
    <polyline class="series baseline" points="{baseline_detail}" />
    <polyline class="series diagnostic" points="{diagnostic_detail}" />
    <text class="direct-label" x="{detail_box[2] - 8}" y="48" text-anchor="end">R6 1 MOhm peak: {dm['switch_node_max_v']:.1f} V</text>
    <text class="direct-label" x="{detail_box[2] - 8}" y="70" text-anchor="end">R6 100 kOhm peak: {bm['switch_node_max_v']:.1f} V</text>
  </svg>

  <table class="table table-sm" aria-label="Simulation measurement comparison">
    <thead><tr><th>Measurement</th><th class="text-end">R6 100 kOhm</th><th class="text-end">R6 1 MOhm</th></tr></thead>
    <tbody>
      <tr><td>Average output, 29-30 ms</td><td class="text-end">{fmt(bm['vout_final_avg_v'], 2, ' V')}</td><td class="text-end">{fmt(dm['vout_final_avg_v'], 2, ' V')}</td></tr>
      <tr><td>Output peak</td><td class="text-end">{fmt(bm['vout_peak_v'], 2, ' V')}</td><td class="text-end">{fmt(dm['vout_peak_v'], 2, ' V')}</td></tr>
      <tr><td>Ripple, 29-30 ms</td><td class="text-end">{fmt(bm['vout_final_ripple_vpp'], 2, ' Vpp')}</td><td class="text-end">{fmt(dm['vout_final_ripple_vpp'], 2, ' Vpp')}</td></tr>
      <tr><td>Settled within 5% of 200 V</td><td class="text-end">{fmt(bm['settling_time_5pct_ms'], 2, ' ms')}</td><td class="text-end">{fmt(dm['settling_time_5pct_ms'], 2, ' ms')}</td></tr>
      <tr><td>Peak USB current</td><td class="text-end">{fmt(bm['input_current_peak_a'], 2, ' A')}</td><td class="text-end">{fmt(dm['input_current_peak_a'], 2, ' A')}</td></tr>
    </tbody>
  </table>
</div>
<style>
  #nixieBoostWaveforms {{ color: var(--foreground); font-size: var(--font-size-base); }}
  #nixieBoostWaveforms .waveform-chart {{ display: block; width: 100%; height: auto; overflow: visible; }}
  #nixieBoostWaveforms .grid {{ stroke: var(--border); stroke-width: 1; vector-effect: non-scaling-stroke; }}
  #nixieBoostWaveforms .target {{ stroke: var(--muted-foreground); stroke-width: 1.5; stroke-dasharray: 6 5; vector-effect: non-scaling-stroke; }}
  #nixieBoostWaveforms .series {{ fill: none; stroke-width: 2; vector-effect: non-scaling-stroke; }}
  #nixieBoostWaveforms .baseline {{ stroke: var(--viz-series-1); }}
  #nixieBoostWaveforms .diagnostic {{ stroke: var(--viz-series-2); }}
  #nixieBoostWaveforms .baseline-fill {{ fill: var(--viz-series-1); }}
  #nixieBoostWaveforms .diagnostic-fill {{ fill: var(--viz-series-2); }}
  #nixieBoostWaveforms .axis-label {{ fill: var(--muted-foreground); }}
  #nixieBoostWaveforms .plot-label,
  #nixieBoostWaveforms .direct-label {{ fill: var(--foreground); font-weight: 500; }}
  #nixieBoostWaveforms .mark {{ stroke: var(--background); stroke-width: 2; vector-effect: non-scaling-stroke; }}
</style>
'''

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(fragment, encoding="utf-8", newline="\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
