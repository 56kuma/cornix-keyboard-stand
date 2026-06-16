from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SCAN_PATH = ROOT / "scan" / "cornix_lp_scaniverse_2026-06-16_221047.stl"
OUT_DIR = ROOT / "docs" / "scan-analysis"


def load_stl_vertices(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if len(data) >= 84:
        tri_count = struct.unpack_from("<I", data, 80)[0]
        expected_size = 84 + tri_count * 50
        if expected_size == len(data):
            vertices = np.empty((tri_count * 3, 3), dtype=np.float64)
            offset = 84
            out = 0
            for _ in range(tri_count):
                offset += 12  # normal
                for _ in range(3):
                    vertices[out] = struct.unpack_from("<fff", data, offset)
                    offset += 12
                    out += 1
                offset += 2
            return vertices

    vertices: list[tuple[float, float, float]] = []
    for line in data.decode("utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) == 4 and parts[0] == "vertex":
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    if not vertices:
        raise ValueError(f"No vertices found in {path}")
    return np.asarray(vertices, dtype=np.float64)


def robust_extents(coords: np.ndarray, low: float, high: float) -> np.ndarray:
    lo = np.percentile(coords, low, axis=0)
    hi = np.percentile(coords, high, axis=0)
    return hi - lo


def unit_scale(raw_extents: np.ndarray) -> tuple[float, str]:
    max_extent = float(raw_extents.max())
    if max_extent < 2.0:
        return 1000.0, "raw STL units look like meters; converted to mm"
    if max_extent < 20.0:
        return 10.0, "raw STL units look like centimeters; converted to mm"
    return 1.0, "raw STL units treated as mm"


def pca_axes(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    center = points.mean(axis=0)
    centered = points - center
    covariance = np.cov(centered.T)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    return center, values[order], vectors[:, order]


def summarize(points: np.ndarray) -> dict[str, object]:
    raw_min = points.min(axis=0)
    raw_max = points.max(axis=0)
    scale, unit_note = unit_scale(raw_max - raw_min)
    points_mm = points * scale

    center, values, axes = pca_axes(points_mm)
    coords = (points_mm - center) @ axes
    pca_min = coords.min(axis=0)
    pca_max = coords.max(axis=0)
    pca_extents = pca_max - pca_min
    pca_extents_1_99 = robust_extents(coords, 1, 99)
    pca_extents_05_995 = robust_extents(coords, 0.5, 99.5)

    sorted_extents = np.sort(pca_extents)[::-1]
    sorted_robust = np.sort(pca_extents_1_99)[::-1]
    sorted_robust_wide = np.sort(pca_extents_05_995)[::-1]

    return {
        "source": str(SCAN_PATH),
        "vertex_count": int(points.shape[0]),
        "triangle_count_estimate": int(points.shape[0] / 3),
        "unit_note": unit_note,
        "raw_bounds": {
            "min": raw_min.tolist(),
            "max": raw_max.tolist(),
            "extents": (raw_max - raw_min).tolist(),
        },
        "pca_extents_mm": pca_extents.tolist(),
        "pca_extents_1_99_mm": pca_extents_1_99.tolist(),
        "pca_extents_0_5_99_5_mm": pca_extents_05_995.tolist(),
        "sorted_extents_mm": sorted_extents.tolist(),
        "sorted_extents_1_99_mm": sorted_robust.tolist(),
        "sorted_extents_0_5_99_5_mm": sorted_robust_wide.tolist(),
        "recommended": {
            "KEYBOARD_LONG_EDGE": float(sorted_robust_wide[0]),
            "KEYBOARD_SHORT_EDGE": float(sorted_robust_wide[1]),
            "KEYBOARD_THICKNESS": float(sorted_robust_wide[2]),
            "FIT_CLEARANCE": 0.8,
            "note": "Uses 0.5-99.5 percentile PCA extents to reduce scan noise. Confirm with calipers before final print.",
        },
    }


def draw_projection(points: np.ndarray, axes: np.ndarray, center: np.ndarray, out: Path) -> None:
    coords = (points - center) @ axes
    pairs = [
        (0, 1, "Top PCA view: long edge x short edge"),
        (0, 2, "Side PCA view: long edge x thickness"),
        (1, 2, "End PCA view: short edge x thickness"),
    ]
    panel_w, panel_h = 760, 560
    margin = 52
    image = Image.new("RGB", (panel_w * 2, panel_h * 2), (16, 19, 26))
    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\meiryob.ttc", 28)
        font_small = ImageFont.truetype(r"C:\Windows\Fonts\meiryo.ttc", 20)
    except OSError:
        font_title = ImageFont.load_default()
        font_small = ImageFont.load_default()

    for index, (a, b, title) in enumerate(pairs):
        col = index % 2
        row = index // 2
        ox = col * panel_w
        oy = row * panel_h
        draw.rectangle([ox + 18, oy + 18, ox + panel_w - 18, oy + panel_h - 18], fill=(25, 30, 40), outline=(62, 72, 92), width=2)
        xy = coords[:, [a, b]]
        lo = np.percentile(xy, 0.2, axis=0)
        hi = np.percentile(xy, 99.8, axis=0)
        span = np.maximum(hi - lo, 1e-9)
        scale = min((panel_w - margin * 2) / span[0], (panel_h - margin * 2 - 50) / span[1])
        projected = (xy - lo) * scale
        projected[:, 1] = (span[1] * scale) - projected[:, 1]
        projected[:, 0] += ox + margin
        projected[:, 1] += oy + margin + 46

        # Subsample for file size and speed.
        step = max(1, len(projected) // 22000)
        for x, y in projected[::step]:
            draw.point((int(x), int(y)), fill=(92, 208, 255))

        draw.text((ox + 36, oy + 34), title, fill=(248, 250, 255), font=font_title)
        ext = robust_extents(coords[:, [a, b]], 0.5, 99.5)
        draw.text((ox + 36, oy + 76), f"robust extents: {ext[0]:.1f} x {ext[1]:.1f} mm", fill=(205, 214, 230), font=font_small)

    draw.text(
        (panel_w + 36, panel_h + 36),
        "Recommended values",
        fill=(248, 250, 255),
        font=font_title,
    )
    ext = np.sort(robust_extents(coords, 0.5, 99.5))[::-1]
    lines = [
        f"long edge: {ext[0]:.1f} mm",
        f"short edge: {ext[1]:.1f} mm",
        f"thickness: {ext[2]:.1f} mm",
        "",
        "Use calipers for final fit.",
        "The scan can include noise or missing underside.",
    ]
    for i, line in enumerate(lines):
        draw.text((panel_w + 36, panel_h + 86 + i * 32), line, fill=(205, 214, 230), font=font_small)

    image.save(out, quality=92)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    points = load_stl_vertices(SCAN_PATH)
    summary = summarize(points)

    scale, _ = unit_scale(np.asarray(summary["raw_bounds"]["extents"]))
    points_mm = points * scale
    center, _, axes = pca_axes(points_mm)
    draw_projection(points_mm, axes, center, OUT_DIR / "scaniverse-pca-projections.jpg")

    out_json = OUT_DIR / "scaniverse-analysis.json"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary["recommended"], indent=2, ensure_ascii=False))
    print(out_json)
    print(OUT_DIR / "scaniverse-pca-projections.jpg")


if __name__ == "__main__":
    main()
