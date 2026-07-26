#!/usr/bin/env python3
"""
Generate emerald-and-gold alcohol-ink marble artwork for the profile README.

Produces:
    banner.png    wide header banner with name + tagline
    divider.png   thin marble rule for section breaks
    orb.png       circular marble medallion

The look is built from iterated domain-warped fractal noise (the flowing ink
cells), gold veining traced along the gradient ridges of that field, and a
scatter of gold leaf flecks -- the same recipe that produces alcohol-ink
marble in the profile avatar.

Usage:  python3 generate_marble.py
"""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# --------------------------------------------------------------------------
# palette -- sampled from the profile avatar
# --------------------------------------------------------------------------

INK_STOPS = [
    (0.00, "#05221D"),  # deepest pine, the shadowed pools
    (0.16, "#0B3D34"),
    (0.32, "#14584A"),
    (0.46, "#1F7A68"),
    (0.58, "#2E9B85"),  # jade, the signature mid-tone
    (0.70, "#6FB8A6"),
    (0.80, "#A8CFC4"),
    (0.89, "#C9D8D2"),  # cool grey drift
    (1.00, "#EFEFEA"),  # cream highlight
]

GOLD_DARK = "#8A6410"
GOLD_MID = "#C9A227"
GOLD_LIGHT = "#F2DC9B"

SEED = 20260726


# --------------------------------------------------------------------------
# noise
# --------------------------------------------------------------------------


def _value_noise(h, w, cells, rng):
    """One octave of smooth value noise, via bicubic upsampling of a coarse grid."""
    grid = rng.random((cells + 1, cells + 1)).astype(np.float32)
    small = Image.fromarray((grid * 255).astype(np.uint8), mode="L")
    return np.asarray(small.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def fbm(h, w, rng, octaves=6, base_cells=3, gain=0.5, lacunarity=2.0):
    """Fractal Brownian motion: octaves of value noise at halving amplitude."""
    total = np.zeros((h, w), dtype=np.float32)
    amplitude = 1.0
    norm = 0.0
    cells = base_cells
    for _ in range(octaves):
        total += amplitude * _value_noise(h, w, int(cells), rng)
        norm += amplitude
        amplitude *= gain
        cells *= lacunarity
    return total / norm


def warp(field, dx_field, dy_field, strength):
    """Displace `field` by two noise fields -- this is what makes ink *flow*."""
    h, w = field.shape
    ys, xs = np.mgrid[0:h, 0:w]
    xi = np.clip(xs + (dx_field - 0.5) * 2.0 * strength, 0, w - 1).astype(np.int32)
    yi = np.clip(ys + (dy_field - 0.5) * 2.0 * strength, 0, h - 1).astype(np.int32)
    return field[yi, xi]


def normalize(a):
    lo, hi = float(a.min()), float(a.max())
    return (a - lo) / (hi - lo + 1e-9)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0 + 1e-9), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))


def build_lut(stops, size=1024):
    """Piecewise-linear colour ramp -> (size, 3) float LUT."""
    lut = np.zeros((size, 3), dtype=np.float32)
    positions = [p for p, _ in stops]
    colours = [np.array(hex_rgb(c), dtype=np.float32) for _, c in stops]
    for i in range(size):
        t = i / (size - 1)
        j = np.searchsorted(positions, t, side="right") - 1
        j = int(np.clip(j, 0, len(stops) - 2))
        span = positions[j + 1] - positions[j]
        local = 0.0 if span <= 0 else (t - positions[j]) / span
        lut[i] = colours[j] * (1 - local) + colours[j + 1] * local
    return lut


def apply_lut(field, lut):
    idx = np.clip((field * (len(lut) - 1)).astype(np.int32), 0, len(lut) - 1)
    return lut[idx]


# --------------------------------------------------------------------------
# the marble itself
# --------------------------------------------------------------------------


def marble(h, w, seed=SEED, vein_gain=1.0, detail=1.0):
    rng = np.random.default_rng(seed)
    scale = max(h, w) / 1000.0

    # Two rounds of domain warping give the layered, poured-ink silhouettes.
    base = fbm(h, w, rng, octaves=7, base_cells=2)
    wx1 = fbm(h, w, rng, octaves=4, base_cells=2)
    wy1 = fbm(h, w, rng, octaves=4, base_cells=2)
    field = warp(base, wx1, wy1, 190 * scale * detail)

    wx2 = fbm(h, w, rng, octaves=5, base_cells=4)
    wy2 = fbm(h, w, rng, octaves=5, base_cells=4)
    field = warp(field, wx2, wy2, 90 * scale * detail)
    field = normalize(field)

    # Push contrast so the ink separates into distinct cells instead of haze.
    field = np.clip((field - 0.5) * 1.45 + 0.5, 0.0, 1.0)
    field = normalize(field ** 1.08)

    rgb = apply_lut(field, build_lut(INK_STOPS))

    # --- gold veining -------------------------------------------------------
    # Veins collect where the ink field changes fastest: the cell boundaries.
    gy, gx = np.gradient(field.astype(np.float32))
    edge = normalize(np.hypot(gx, gy))
    edge = np.asarray(
        Image.fromarray((edge * 255).astype(np.uint8), mode="L").filter(
            ImageFilter.GaussianBlur(1.1 * scale)
        ),
        dtype=np.float32,
    ) / 255.0
    edge = normalize(edge)

    # A second, coarser contour set: broad gold rivers across the slab.
    contour = np.abs(np.sin(field * math.pi * 5.0))
    rivers = smoothstep(0.93, 1.0, contour)

    # Veins fade in and out rather than running at constant weight.
    breakup = fbm(h, w, rng, octaves=4, base_cells=5)
    presence = smoothstep(0.34, 0.72, breakup)

    vein = np.clip(smoothstep(0.30, 0.78, edge) * 0.95 + rivers * 0.45, 0, 1)
    vein = np.clip(vein * presence * vein_gain, 0, 1)

    # Shimmer: vary gold between dark leaf and bright polish along its length.
    shimmer = fbm(h, w, rng, octaves=4, base_cells=7)
    gold_lut = build_lut([(0.0, GOLD_DARK), (0.5, GOLD_MID), (1.0, GOLD_LIGHT)])
    gold = apply_lut(normalize(shimmer), gold_lut)

    rgb = rgb * (1 - vein[..., None]) + gold * vein[..., None]

    # --- gold leaf flecks ---------------------------------------------------
    speck = rng.random((h, w)).astype(np.float32)
    fleck = (speck > 0.9993) & (presence > 0.42)
    fleck_img = np.asarray(
        Image.fromarray((fleck * 255).astype(np.uint8), mode="L").filter(
            ImageFilter.GaussianBlur(0.85 * scale)
        ),
        dtype=np.float32,
    ) / 255.0
    fleck_img = np.clip(fleck_img * 3.4, 0, 1)
    rgb = rgb * (1 - fleck_img[..., None]) + np.array(
        hex_rgb(GOLD_LIGHT), dtype=np.float32
    ) * fleck_img[..., None]

    # --- finishing ----------------------------------------------------------
    # Faint paper grain keeps it from reading as a flat digital gradient.
    grain = (rng.random((h, w)).astype(np.float32) - 0.5) * 7.0
    rgb = np.clip(rgb + grain[..., None], 0, 255)

    img = Image.fromarray(rgb.astype(np.uint8), mode="RGB")
    return img.filter(ImageFilter.SMOOTH)


# --------------------------------------------------------------------------
# composition helpers
# --------------------------------------------------------------------------


def load_font(candidates, size):
    for path, index in candidates:
        try:
            return ImageFont.truetype(path, size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()


SERIF = [
    ("/System/Library/Fonts/Supplemental/Didot.ttc", 1),
    ("/System/Library/Fonts/Supplemental/Baskerville.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Georgia.ttf", 0),
    ("/Library/Fonts/Georgia.ttf", 0),
]
SANS = [
    ("/System/Library/Fonts/Supplemental/Futura.ttc", 0),
    ("/System/Library/Fonts/Supplemental/Avenir Next.ttc", 0),
    ("/System/Library/Fonts/Helvetica.ttc", 0),
]


def vignette(img, strength=0.55, focus=0.42):
    """Darken toward the left so overlaid text stays legible."""
    w, h = img.size
    xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    mask = smoothstep(focus - 0.35, focus + 0.45, xs)
    mask = np.repeat(mask, h, axis=0)
    shade = 1.0 - (1.0 - mask) * strength
    arr = np.asarray(img, dtype=np.float32) * shade[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def tracked_text(draw, xy, text, font, fill, tracking=0):
    """Draw text with manual letter-spacing (PIL has no tracking option)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x - xy[0] - tracking


def measure_tracked(draw, text, font, tracking=0):
    return sum(draw.textlength(c, font=font) for c in text) + tracking * (len(text) - 1)


# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------


def make_banner(name="Priya", tagline="STUDENT DEVELOPER  ·  ASSISTIVE TECH  ·  iOS & AI", out="banner.png"):
    W, H = 1600, 440
    img = vignette(marble(H, W, seed=SEED), strength=0.72, focus=0.5)
    draw = ImageDraw.Draw(img)

    name_font = load_font(SERIF, 132)
    tag_font = load_font(SANS, 25)

    left = 96
    baseline = 132

    # Soft dark halo behind the wordmark so it reads over any ink cell.
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.text((left, baseline), name, font=name_font, fill=(3, 22, 18, 190))
    halo = halo.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img.convert("RGBA"), halo).convert("RGB")
    draw = ImageDraw.Draw(img)

    draw.text((left, baseline), name, font=name_font, fill=(244, 246, 243))

    # Gold hairline rule beneath the wordmark.
    name_w = draw.textlength(name, font=name_font)
    rule_y = baseline + 178
    draw.line([(left + 4, rule_y), (left + name_w + 150, rule_y)], fill=(201, 162, 39), width=3)

    tracked_text(draw, (left + 6, rule_y + 30), tagline, tag_font, (214, 231, 224), tracking=1.6)

    # Thin gold frame.
    draw.rectangle([1, 1, W - 2, H - 2], outline=(150, 118, 34), width=3)

    img.save(out, optimize=True)
    print(f"wrote {out}  ({W}x{H})")


def make_divider(out="divider.png"):
    W, H = 1600, 10
    img = marble(120, W, seed=SEED + 7, vein_gain=1.35, detail=0.55)
    img = img.crop((0, 52, W, 52 + H))
    ImageDraw.Draw(img).rectangle([0, 0, W - 1, H - 1], outline=(150, 118, 34), width=1)
    img.save(out, optimize=True)
    print(f"wrote {out}  ({W}x{H})")


def make_orb(out="orb.png", size=560):
    img = marble(size, size, seed=SEED + 21, vein_gain=1.15).convert("RGBA")
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    img.putalpha(mask.resize((size, size), Image.LANCZOS))

    ring = ImageDraw.Draw(img)
    ring.ellipse([3, 3, size - 4, size - 4], outline=(201, 162, 39, 235), width=6)
    img.save(out, optimize=True)
    print(f"wrote {out}  ({size}x{size})")


if __name__ == "__main__":
    make_banner()
    make_divider()
    make_orb()
