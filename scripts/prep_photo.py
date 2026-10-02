#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from rembg import remove


def preprocess_photo(input_path: Path, output_path: Path) -> None:
    source_bytes = input_path.read_bytes()
    cutout = remove(source_bytes)

    rgba = cv2.imdecode(np.frombuffer(cutout, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if rgba is None:
        raise RuntimeError("Could not decode image")

    if rgba.shape[2] == 4:
        bgr = rgba[:, :, :3]
        alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    else:
        bgr = rgba
        alpha = np.ones((rgba.shape[0], rgba.shape[1]), dtype=np.float32)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    boosted = clahe.apply(gray).astype(np.float32)

    white_bg = np.full_like(boosted, 255.0)
    composited = boosted * alpha + white_bg * (1.0 - alpha)
    result = np.clip(composited, 0, 255).astype(np.uint8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), result):
        raise RuntimeError(f"Failed to write image: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare portrait for ASCII conversion")
    parser.add_argument("input", type=Path, help="Path to source photo")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("source-prepped.png"),
        help="Output grayscale image path (default: source-prepped.png)",
    )
    args = parser.parse_args()

    preprocess_photo(args.input, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
