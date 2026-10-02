#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def decode(source_bytes: bytes) -> np.ndarray:
    rgba = cv2.imdecode(np.frombuffer(source_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    if rgba is None:
        raise RuntimeError("Could not decode image")
    return rgba


def cutout(rgba: np.ndarray) -> np.ndarray:
    # A pre-matted PNG already carries a better matte than a generic
    # segmentation model would produce, so only pay for rembg when the
    # input has no usable alpha. Imported lazily to keep it optional.
    if rgba.ndim == 3 and rgba.shape[2] == 4 and (rgba[:, :, 3] < 255).any():
        return rgba

    from rembg import remove

    return decode(remove(cv2.imencode(".png", rgba)[1].tobytes()))


def preprocess_photo(input_path: Path, output_path: Path) -> None:
    rgba = cutout(decode(input_path.read_bytes()))

    if rgba.ndim == 3 and rgba.shape[2] == 4:
        bgr = rgba[:, :, :3]
        alpha = rgba[:, :, 3].astype(np.float32) / 255.0
    else:
        bgr = rgba
        alpha = np.ones((rgba.shape[0], rgba.shape[1]), dtype=np.float32)

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    boosted = clahe.apply(gray).astype(np.float32)

    # Composite onto black: the ASCII ramp maps dark to space, so a black
    # background disappears against the dark SVG card while the subject
    # renders in the brighter glyphs. A white plate would fill the frame.
    background = np.zeros_like(boosted)
    composited = boosted * alpha + background * (1.0 - alpha)
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
