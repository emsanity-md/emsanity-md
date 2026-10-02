#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IN_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def date_to_cell(start: datetime, d: datetime) -> tuple[int, int]:
    delta = (d - start).days
    col = delta // 7
    row = delta % 7
    return col, row


def main() -> None:
    data = json.loads(IN_PATH.read_text(encoding="utf-8"))
    days = data.get("days", [])
    if not days:
        raise RuntimeError("No contribution day data found")

    by_date = {item["date"]: item for item in days}
    last_day = datetime.strptime(days[-1]["date"], "%Y-%m-%d")

    start = last_day - timedelta(days=370)
    while start.weekday() != 6:  # Sunday
        start -= timedelta(days=1)

    cell = 13
    gap = 4
    left = 26
    top = 34
    weeks = 53
    width = left * 2 + weeks * (cell + gap) + 8
    height = 210

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="14" fill="#0d1117" stroke="#30363d"/>',
        '<g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="12" fill="#8b949e">',
        '<text x="26" y="20">Contribution activity (last 53 weeks)</text>',
        '</g>',
        '<g>',
    ]

    for col in range(weeks):
        for row in range(7):
            d = start + timedelta(days=col * 7 + row)
            ds = d.strftime("%Y-%m-%d")
            item = by_date.get(ds, {"count": 0, "level": 0})
            level = int(item.get("level", 0))
            if level < 0:
                level = 0
            if level >= len(PALETTE):
                level = len(PALETTE) - 1

            x = left + col * (cell + gap)
            y = top + row * (cell + gap)
            delay = (col + row) * 0.012
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{PALETTE[level]}" opacity="0">'
                f'<title>{ds}: {item.get("count", 0)} contributions</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="0.20s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 -4" to="0 0" begin="{delay:.3f}s" dur="0.20s" fill="freeze"/>'
                "</rect>"
            )

    legend_x = width - 190
    legend_y = 172
    parts.extend(['</g>', '<g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="11" fill="#8b949e">'])
    parts.append(f'<text x="{legend_x}" y="{legend_y}">Less</text>')
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{legend_x + 34 + i * 16}" y="{legend_y - 10}" width="12" height="12" rx="2" fill="{color}"/>'
        )
    parts.append(f'<text x="{legend_x + 34 + len(PALETTE) * 16 + 8}" y="{legend_y}">More</text>')

    total = int(data.get("total_last_year", 0))
    current = int(data.get("current_streak", 0))
    longest = int(data.get("longest_streak", 0))
    parts.append(
        f'<text x="26" y="{legend_y}">{total:,} contributions in the last year • current streak {current} • longest streak {longest}</text>'
    )
    parts.append('</g></svg>')

    OUT_PATH.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
