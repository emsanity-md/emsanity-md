#!/usr/bin/env python3
from __future__ import annotations

import html
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "source-prepped.png"
OUTPUT = ROOT / "avi-ascii.svg"


def fallback_rows(width: int = 100, height: int = 53) -> list[str]:
    rows: list[str] = []
    cx, cy = width / 2.0, height / 2.0
    for y in range(height):
        line = []
        for x in range(width):
            dx = (x - cx) / (width * 0.35)
            dy = (y - cy) / (height * 0.45)
            d = dx * dx + dy * dy
            level = max(0.0, 1.0 - d)
            idx = int((1.0 - level) * (len(RAMP) - 1))
            line.append(RAMP[min(len(RAMP) - 1, max(0, idx))])
        rows.append("".join(line))
    return rows


def image_to_rows(path: Path, cols: int = 100) -> list[str]:
    if not path.exists():
        return fallback_rows(cols, 53)

    img = Image.open(path).convert("L")
    w, h = img.size
    aspect = h / max(1, w)
    rows = max(20, int(cols * aspect * 0.52))
    resized = img.resize((cols, rows), Image.Resampling.LANCZOS)
    arr = np.asarray(resized)

    ramp_idx = np.round((arr / 255.0) * (len(RAMP) - 1)).astype(int)
    result: list[str] = []
    for r in ramp_idx:
        result.append("".join(RAMP[i] for i in r))
    return result


def build_svg(rows: list[str], out_path: Path) -> None:
    fs = 10
    char_w = 6
    line_h = 12
    pad = 20
    width = pad * 2 + max(len(r) for r in rows) * char_w
    height = pad * 2 + len(rows) * line_h

    parts: list[str] = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    parts.append('<rect width="100%" height="100%" fill="#0d1117" rx="12"/>')
    parts.append('<defs>')

    def baseline(i: int) -> int:
        return pad + (i + 1) * line_h - 2

    # The clip band must line up with the glyph box, which sits above the
    # baseline. Deriving it from the row's top edge instead leaves a full
    # line_h of offset, so each row was clipped to a ~2px sliver.
    def band_top(i: int) -> int:
        return baseline(i) - fs + 2

    row_width = width - pad * 2
    for i, _ in enumerate(rows):
        parts.append(f'<clipPath id="clip-{i}"><rect x="{pad}" y="{band_top(i)}" width="0" height="{line_h}" rx="2">')
        parts.append(f'<animate attributeName="width" from="0" to="{row_width}" begin="{i * 0.05:.2f}s" dur="0.28s" fill="freeze" />')
        parts.append('</rect></clipPath>')
    parts.append('</defs>')

    parts.append(f'<g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="{fs}" fill="#c9d1d9">')
    for i, row in enumerate(rows):
        parts.append(f'<text x="{pad}" y="{baseline(i)}" clip-path="url(#clip-{i})" xml:space="preserve">{html.escape(row)}</text>')

    cursor_h = line_h - 2
    for i, row in enumerate(rows):
        y = band_top(i)
        row_len = len(row) * char_w
        begin = i * 0.05
        dur = 0.28
        parts.append(f'<rect x="{pad}" y="{y}" width="2" height="{cursor_h}" fill="#58a6ff" opacity="0">')
        parts.append(f'<animate attributeName="x" from="{pad}" to="{pad + row_len}" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')
        parts.append(f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.05;0.95;1" begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')
        parts.append('</rect>')
    parts.append('</g></svg>')

    out_path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    rows = image_to_rows(INPUT)
    build_svg(rows, OUTPUT)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
