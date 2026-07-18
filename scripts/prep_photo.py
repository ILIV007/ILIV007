#!/usr/bin/env python3
"""
prep_photo.py — prepare the knight source image for ASCII conversion.

Steps:
  1. Load the source image, convert to grayscale.
  2. Boost local contrast with CLAHE (contrast-limited adaptive histogram
     equalization) so flat areas get real highlights and shadows.
  3. Composite onto pure white so the background maps to the blank end of
     the ASCII ramp.
  4. Trim the white border so the helmet fills the canvas.

Usage:
  python scripts/prep_photo.py [source-photo]

If no source is given, defaults to knight-angled.png in the repo root.
Output: data/prepped.png
"""

import sys
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def clahe(gray_np: np.ndarray) -> np.ndarray:
    """Apply CLAHE to a uint8 grayscale array."""
    if not HAS_CV2:
        # Fallback: simple histogram equalization via PIL
        return np.array(ImageOps.equalize(Image.fromarray(gray_np)))
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray_np)


def trim_white(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Crop uniform white borders."""
    bg = Image.new(img.mode, img.size, (255,))
    diff = ImageChops_difference(img, bg) if False else None
    # Simple approach: find bbox of non-white pixels
    np_img = np.array(img.convert("L"))
    mask = np_img < threshold
    if not mask.any():
        return img
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    top, bottom = np.where(rows)[0][[0, -1]]
    left, right = np.where(cols)[0][[0, -1]]
    return img.crop((left, top, right + 1, bottom + 1))


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else "knight-angled.png"
    out = Path("data/prepped.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {source}...")
    img = Image.open(source).convert("L")
    arr = np.array(img)

    print("Applying CLAHE local-contrast boost...")
    arr = clahe(arr)

    # Composite on pure white
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr).convert("L")

    print("Trimming white border...")
    img = trim_white(img)

    print(f"Saving prepped image to {out}...")
    img.save(out)
    print(f"Done. Size: {img.size}")


if __name__ == "__main__":
    main()
