#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "info-card.svg"

LINES = [
    ("Now", "Building robust systems + delightful DX"),
    ("Prev", "Full-stack shipping, platform automation"),
    ("Stack", "Python · TypeScript · React · FastAPI · SQL"),
    ("Highlights", "SVG tooling · CI workflows · DevEx"),
]


def line_svg(y: int, idx: int, key: str, value: str, animated: bool) -> str:
    begin = 0.35 + idx * 0.16
    if not animated:
        return (
            f'<text x="26" y="{y}" font-size="15" fill="#58a6ff">{key: <10}</text>'
            f'<text x="150" y="{y}" font-size="15" fill="#c9d1d9">{value}</text>'
        )

    return "".join(
        [
            f'<g opacity="0" transform="translate(0,7)">',
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>',
            f'<animateTransform attributeName="transform" type="translate" from="0 7" to="0 0" begin="{begin:.2f}s" dur="0.35s" fill="freeze"/>',
            f'<text x="26" y="{y}" font-size="15" fill="#58a6ff">{key: <10}</text>',
            f'<text x="150" y="{y}" font-size="15" fill="#c9d1d9">{value}</text>',
            "</g>",
        ]
    )


def build_svg(animated: bool = True) -> str:
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="520" viewBox="0 0 920 520">',
        '<rect width="100%" height="100%" rx="16" fill="#0d1117" stroke="#30363d"/>',
        '<rect x="0" y="0" width="920" height="52" rx="16" fill="#161b22"/>',
        '<circle cx="28" cy="26" r="7" fill="#ff5f56"/><circle cx="50" cy="26" r="7" fill="#ffbd2e"/><circle cx="72" cy="26" r="7" fill="#27c93f"/>',
        '<text x="460" y="33" fill="#8b949e" text-anchor="middle" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="14">neofetch</text>',
        '<g font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">',
        '<text x="26" y="96" fill="#c9d1d9" font-size="22">emsanity-md@github</text>',
        '<text x="26" y="122" fill="#8b949e" font-size="13">──────────────────────────────────────────────────────────</text>',
    ]

    for i, (k, v) in enumerate(LINES):
        pieces.append(line_svg(168 + i * 46, i, k, v, animated))

    pieces.extend(
        [
            '<text x="26" y="390" fill="#8b949e" font-size="13">──────────────────────────────────────────────────────────</text>',
            '<text x="26" y="430" fill="#56d364" font-size="15">$ status --all</text>',
            '<text x="180" y="430" fill="#c9d1d9" font-size="15">open to collabs • building in public</text>',
            '</g></svg>',
        ]
    )
    return "\n".join(pieces)


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    OUTPUT.write_text(build_svg(animated=not static), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
