from __future__ import annotations

from pathlib import Path

import generate_bookshelf_storage_stand as stand


# This is a low-material fit coupon, not the final storage stand.
# The insertion and groove dimensions intentionally mirror the production model.
WALL_THICKNESS = 2.4
FRONT_REAR_MARGIN = 3.0
SKIN_HEIGHT = 0.6
TEST_HEIGHT = 8.0
END_RAIL_THICKNESS = 2.0
END_RAIL_HEIGHT = 4.0

SLOT_X0 = WALL_THICKNESS
SLOT_X1 = SLOT_X0 + stand.SLOT_INNER_WIDTH
BASE_WIDTH = stand.SLOT_INNER_WIDTH + WALL_THICKNESS * 2

SLOT_Y0 = FRONT_REAR_MARGIN
SLOT_Y1 = SLOT_Y0 + stand.SLOT_INNER_LENGTH
BASE_DEPTH = stand.SLOT_INNER_LENGTH + FRONT_REAR_MARGIN * 2

GROOVE_Y0 = SLOT_Y0 + stand.ENTRY_LENGTH_EXTRA / 2
GROOVE_Y1 = GROOVE_Y0 + stand.GROOVE_INNER_LENGTH


def add_box(name: str, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> None:
    stand.add_box(f"fit_coupon_{name}", x0, y0, z0, x1, y1, z1)


def build_coupon() -> None:
    stand.triangles.clear()

    # Full contact skin keeps every detail connected for Bambu Studio while using very little material.
    add_box("unibody_skin", 0.0, 0.0, 0.0, BASE_WIDTH, BASE_DEPTH, SKIN_HEIGHT)

    # Low side guides preserve the production insertion width.
    add_box("center_side_low_guide", 0.0, SLOT_Y0, SKIN_HEIGHT, WALL_THICKNESS, SLOT_Y1, TEST_HEIGHT)
    add_box("outer_side_low_guide", SLOT_X1, SLOT_Y0, SKIN_HEIGHT, BASE_WIDTH, SLOT_Y1, TEST_HEIGHT)

    # Low end rails preserve the production insertion length without printing the full stand height.
    add_box(
        "front_length_reference_rail",
        0.0,
        SLOT_Y0 - END_RAIL_THICKNESS,
        SKIN_HEIGHT,
        BASE_WIDTH,
        SLOT_Y0,
        END_RAIL_HEIGHT,
    )
    add_box(
        "rear_length_reference_rail",
        0.0,
        SLOT_Y1,
        SKIN_HEIGHT,
        BASE_WIDTH,
        SLOT_Y1 + END_RAIL_THICKNESS,
        END_RAIL_HEIGHT,
    )

    # Right-slot orientation: center side has +4 mm, outer side has +8 mm.
    groove_x0 = SLOT_X0 + stand.ENTRY_FLARE_CENTER
    groove_x1 = SLOT_X1 - stand.ENTRY_FLARE_OUTER

    add_box(
        "bottom_groove_floor",
        groove_x0,
        GROOVE_Y0 + stand.GROOVE_END_INSET,
        SKIN_HEIGHT,
        groove_x1,
        GROOVE_Y1 - stand.GROOVE_END_INSET,
        SKIN_HEIGHT + stand.GROOVE_FLOOR_HEIGHT,
    )
    add_box(
        "center_1mm_groove_lip",
        groove_x0 - stand.GROOVE_LIP_WIDTH,
        GROOVE_Y0 + stand.GROOVE_END_INSET,
        SKIN_HEIGHT,
        groove_x0,
        GROOVE_Y1 - stand.GROOVE_END_INSET,
        SKIN_HEIGHT + stand.GROOVE_CAPTURE_HEIGHT,
    )
    add_box(
        "outer_1mm_groove_lip",
        groove_x1,
        GROOVE_Y0 + stand.GROOVE_END_INSET,
        SKIN_HEIGHT,
        groove_x1 + stand.GROOVE_LIP_WIDTH,
        GROOVE_Y1 - stand.GROOVE_END_INSET,
        SKIN_HEIGHT + stand.GROOVE_CAPTURE_HEIGHT,
    )


def main() -> None:
    build_coupon()
    output = Path(__file__).resolve().parents[1] / "stl" / "cornix_lp_fit_check_coupon.stl"
    stand.write_stl(output)
    print(f"Wrote {output}")
    print(f"Triangles: {len(stand.triangles)}")
    print(f"Coupon: {BASE_WIDTH:.1f} x {BASE_DEPTH:.1f} x {TEST_HEIGHT:.1f} mm")
    print(f"Insertion opening: {stand.SLOT_INNER_LENGTH:.1f} x {stand.SLOT_INNER_WIDTH:.1f} mm")
    print(f"Bottom groove: {stand.GROOVE_INNER_LENGTH:.1f} x {stand.GROOVE_INNER_WIDTH:.1f} x {stand.GROOVE_CAPTURE_HEIGHT:.1f} mm")
    print(f"Entry flare: center +{stand.ENTRY_FLARE_CENTER:.1f} mm, outer +{stand.ENTRY_FLARE_OUTER:.1f} mm")


if __name__ == "__main__":
    main()
