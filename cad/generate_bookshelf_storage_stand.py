from __future__ import annotations

from math import cos, pi, sin, sqrt
from pathlib import Path


PHI = (1 + sqrt(5)) / 2

# Dimensions are in millimeters.
# Derived from scan/cornix_lp_scaniverse_2026-06-16_221047.stl and photo ruler checks.
# Confirm with calipers before a final print.
KEYBOARD_LONG_EDGE_MAX = 163.9
KEYBOARD_LONG_EDGE_CONTACT = 144.0
KEYBOARD_SHORT_EDGE_MAX = 111.3
KEYBOARD_SHORT_EDGE_CONTACT = 88.0
KEYBOARD_THICKNESS_MAX_SCAN = 26.4
KEYBOARD_THICKNESS = 10.0
FIT_CLEARANCE = 0.8
GROOVE_CAPTURE_HEIGHT = 1.0
GROOVE_LIP_WIDTH = 1.0
GROOVE_FLOOR_HEIGHT = 0.35
GROOVE_END_INSET = 3.0
ENTRY_LENGTH_EXTRA = 1.0
ENTRY_FLARE_CENTER = 4.0
ENTRY_FLARE_OUTER = 8.0

GROOVE_INNER_LENGTH = KEYBOARD_SHORT_EDGE_CONTACT + FIT_CLEARANCE
SLOT_INNER_LENGTH = GROOVE_INNER_LENGTH + ENTRY_LENGTH_EXTRA
GROOVE_INNER_WIDTH = KEYBOARD_THICKNESS + FIT_CLEARANCE
SLOT_INNER_WIDTH = GROOVE_INNER_WIDTH + ENTRY_FLARE_CENTER + ENTRY_FLARE_OUTER

BENTO_REFERENCE_DEPTH = 120.0
BENTO_REFERENCE_HEIGHT = 55.0

BASE_THICKNESS = 5.0
BASE_CHAMFER = 10.0
BASE_TOP_INSET = 2.5
BASE_FRAME_RAIL = 4.5
BASE_CROSS_RAIL = 2.8
BASE_SIDE_MARGIN = 3.0
BASE_ROOT_PAD_RAIL = round(BASE_FRAME_RAIL * PHI, 1)
BASE_DIAGONAL_RAIL = BASE_FRAME_RAIL
BASE_SIDE_SPINE_WAIST = BASE_ROOT_PAD_RAIL
SOFT_CHAMFER = 1.2
TIP_FLAT_WIDTH = 1.6
TIP_SHOULDER_DROP = 3.0

OUTER_WALL_THICKNESS = 5.0
DIVIDER_THICKNESS = 6.0
END_STOP_THICKNESS = 4.0

STAND_OVERALL_HEIGHT = min(BENTO_REFERENCE_HEIGHT, round(KEYBOARD_LONG_EDGE_CONTACT / PHI**2, 1))
SIDE_WALL_HEIGHT = STAND_OVERALL_HEIGHT - BASE_THICKNESS
LOWER_CAPTURE_HEIGHT = 12.0
END_STOP_HEIGHT = 10.0
END_STOP_HOOK_OVERHANG = 0.0

RIB_THICKNESS = 2.8
CENTER_TRIANGLE_RIB_THICKNESS = round(RIB_THICKNESS * PHI, 1)
OUTER_GUARD_PILLAR_WIDTH = CENTER_TRIANGLE_RIB_THICKNESS
GOLDEN_SUPPORT_RATIOS = (1 / PHI**2, 1 / PHI)
CENTER_FIN_TENON_DEPTH = BASE_THICKNESS

SLOT_PAIR_WIDTH = SLOT_INNER_WIDTH * 2 + DIVIDER_THICKNESS
BASE_WIDTH = max(
    BENTO_REFERENCE_DEPTH / PHI,
    SLOT_PAIR_WIDTH + OUTER_WALL_THICKNESS * 2 + BASE_SIDE_MARGIN * 2,
)
BASE_DEPTH = max(
    BENTO_REFERENCE_DEPTH,
    BASE_WIDTH * PHI,
    KEYBOARD_SHORT_EDGE_MAX + END_STOP_THICKNESS * 2 + BASE_FRAME_RAIL * 2,
    SLOT_INNER_LENGTH + END_STOP_THICKNESS * 2 + BASE_FRAME_RAIL * 2,
)
SLOT_X0 = (BASE_WIDTH - SLOT_PAIR_WIDTH) / 2
SLOT_1_X0 = SLOT_X0
SLOT_1_X1 = SLOT_1_X0 + SLOT_INNER_WIDTH
DIVIDER_X0 = SLOT_1_X1
DIVIDER_X1 = DIVIDER_X0 + DIVIDER_THICKNESS
SLOT_2_X0 = DIVIDER_X1
SLOT_2_X1 = SLOT_2_X0 + SLOT_INNER_WIDTH

SLOT_Y0 = (BASE_DEPTH - SLOT_INNER_LENGTH) / 2
SLOT_Y1 = SLOT_Y0 + SLOT_INNER_LENGTH
GROOVE_Y0 = (BASE_DEPTH - GROOVE_INNER_LENGTH) / 2
GROOVE_Y1 = GROOVE_Y0 + GROOVE_INNER_LENGTH

Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]
Triangle = tuple[str, Vec3, Vec3, Vec3]

triangles: list[Triangle] = []


def normal(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = (nx * nx + ny * ny + nz * nz) ** 0.5
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (nx / length, ny / length, nz / length)


def add_triangle(name: str, a: Vec3, b: Vec3, c: Vec3) -> None:
    triangles.append((name, a, b, c))


def add_quad(name: str, a: Vec3, b: Vec3, c: Vec3, d: Vec3) -> None:
    add_triangle(name, a, b, c)
    add_triangle(name, a, c, d)


def rounded_rect(x0: float, y0: float, x1: float, y1: float, radius: float, segments: int = 4) -> list[Vec2]:
    r = min(radius, (x1 - x0) / 2, (y1 - y0) / 2)
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    corners = [
        (x1 - r, y0 + r, -pi / 2, 0.0),
        (x1 - r, y1 - r, 0.0, pi / 2),
        (x0 + r, y1 - r, pi / 2, pi),
        (x0 + r, y0 + r, pi, pi * 3 / 2),
    ]
    points: list[Vec2] = []
    for cx, cy, start, end in corners:
        for index in range(segments + 1):
            if points and index == 0:
                continue
            angle = start + (end - start) * index / segments
            points.append((cx + cos(angle) * r, cy + sin(angle) * r))
    return points


def octagon_outline(x0: float, y0: float, x1: float, y1: float, chamfer: float) -> list[Vec2]:
    c = min(chamfer, (x1 - x0) / 2, (y1 - y0) / 2)
    return [
        (x0 + c, y0),
        (x1 - c, y0),
        (x1, y0 + c),
        (x1, y1 - c),
        (x1 - c, y1),
        (x0 + c, y1),
        (x0, y1 - c),
        (x0, y0 + c),
    ]


def add_ring_prism(name: str, outer: list[Vec2], inner: list[Vec2], z0: float, z1: float) -> None:
    if len(outer) != len(inner):
        raise ValueError("Outer and inner loops must have the same point count")

    count = len(outer)
    outer_bottom = [(x, y, z0) for x, y in outer]
    outer_top = [(x, y, z1) for x, y in outer]
    inner_bottom = [(x, y, z0) for x, y in inner]
    inner_top = [(x, y, z1) for x, y in inner]

    for i in range(count):
        j = (i + 1) % count
        add_quad(name, outer_bottom[i], outer_bottom[j], outer_top[j], outer_top[i])
        add_quad(name, inner_bottom[i], inner_top[i], inner_top[j], inner_bottom[j])
        add_quad(name, outer_top[i], outer_top[j], inner_top[j], inner_top[i])
        add_quad(name, outer_bottom[i], inner_bottom[i], inner_bottom[j], outer_bottom[j])


def add_octagonal_outer_frame(name: str, rail: float, z0: float, z1: float) -> None:
    outer = octagon_outline(0.0, 0.0, BASE_WIDTH, BASE_DEPTH, BASE_CHAMFER)
    inner = [
        (BASE_CHAMFER, rail),
        (BASE_WIDTH - BASE_CHAMFER, rail),
        (BASE_WIDTH - rail, BASE_CHAMFER),
        (BASE_WIDTH - rail, BASE_DEPTH - BASE_CHAMFER),
        (BASE_WIDTH - BASE_CHAMFER, BASE_DEPTH - rail),
        (BASE_CHAMFER, BASE_DEPTH - rail),
        (rail, BASE_DEPTH - BASE_CHAMFER),
        (rail, BASE_CHAMFER),
    ]
    add_ring_prism(name, outer, inner, z0, z1)


def soft_peak_profile(x0: float, x1: float, z0: float, z1: float) -> list[Vec2]:
    mid = (x0 + x1) / 2
    half_width = min(TIP_FLAT_WIDTH / 2, (x1 - x0) / 4)
    shoulder = min(TIP_SHOULDER_DROP, (z1 - z0) / 3)
    return [
        (x0, z0),
        (x1, z0),
        (x1, z1 - shoulder),
        (mid + half_width, z1),
        (mid - half_width, z1),
        (x0, z1 - shoulder),
    ]


def outer_capture_guard_profile(inner_x: float, outer_x: float, z0: float, z1: float) -> list[Vec2]:
    direction = -1 if outer_x < inner_x else 1
    thickness = abs(outer_x - inner_x)
    top_flat = min(TIP_FLAT_WIDTH, thickness * 0.42)
    upper_shoulder = min(6.0, (z1 - z0) * 0.16)
    lower_shoulder = min(LOWER_CAPTURE_HEIGHT, (z1 - z0) * 0.28)
    mid_x = inner_x + direction * min(thickness * 0.64, thickness - SOFT_CHAMFER)
    return [
        (inner_x, z0),
        (inner_x, z1),
        (inner_x + direction * top_flat, z1),
        (inner_x + direction * top_flat * 1.45, z1 - upper_shoulder),
        (mid_x, z0 + lower_shoulder + TIP_SHOULDER_DROP),
        (outer_x, z0 + lower_shoulder),
        (outer_x, z0),
    ]


def add_layered_prism(name: str, layers: list[tuple[float, list[Vec2]]]) -> None:
    count = len(layers[0][1])
    if any(len(points) != count for _, points in layers):
        raise ValueError("All layers must have the same point count")

    lower_z, lower_xy = layers[0]
    upper_z, upper_xy = layers[-1]
    lower = [(x, y, lower_z) for x, y in lower_xy]
    upper = [(x, y, upper_z) for x, y in upper_xy]

    for i in range(1, count - 1):
        add_triangle(name, lower[0], lower[i + 1], lower[i])
        add_triangle(name, upper[0], upper[i], upper[i + 1])

    for layer_index in range(len(layers) - 1):
        z0, xy0 = layers[layer_index]
        z1, xy1 = layers[layer_index + 1]
        ring0 = [(x, y, z0) for x, y in xy0]
        ring1 = [(x, y, z1) for x, y in xy1]
        for i in range(count):
            j = (i + 1) % count
            add_quad(name, ring0[i], ring0[j], ring1[j], ring1[i])


def add_box(name: str, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> None:
    v000 = (x0, y0, z0)
    v100 = (x1, y0, z0)
    v110 = (x1, y1, z0)
    v010 = (x0, y1, z0)
    v001 = (x0, y0, z1)
    v101 = (x1, y0, z1)
    v111 = (x1, y1, z1)
    v011 = (x0, y1, z1)

    add_quad(name, v000, v010, v110, v100)
    add_quad(name, v001, v101, v111, v011)
    add_quad(name, v000, v100, v101, v001)
    add_quad(name, v010, v011, v111, v110)
    add_quad(name, v000, v001, v011, v010)
    add_quad(name, v100, v110, v111, v101)


def add_soft_box(
    name: str,
    x0: float,
    y0: float,
    z0: float,
    x1: float,
    y1: float,
    z1: float,
    chamfer: float = SOFT_CHAMFER,
) -> None:
    outline = rounded_rect(x0, y0, x1, y1, chamfer)
    add_layered_prism(name, [(z0, outline), (z1, outline)])


def add_y_prism(name: str, y0: float, y1: float, xz: list[Vec2]) -> None:
    front = [(x, y0, z) for x, z in xz]
    back = [(x, y1, z) for x, z in xz]
    count = len(xz)

    for i in range(1, count - 1):
        add_triangle(name, front[0], front[i + 1], front[i])
        add_triangle(name, back[0], back[i], back[i + 1])

    for i in range(count):
        j = (i + 1) % count
        add_quad(name, front[i], back[i], back[j], front[j])


def add_y_sweep(name: str, layers: list[tuple[float, list[Vec2]]]) -> None:
    count = len(layers[0][1])
    if any(len(points) != count for _, points in layers):
        raise ValueError("All sweep profiles must have the same point count")

    front_y, front_xz = layers[0]
    rear_y, rear_xz = layers[-1]
    front = [(x, front_y, z) for x, z in front_xz]
    rear = [(x, rear_y, z) for x, z in rear_xz]

    for i in range(1, count - 1):
        add_triangle(name, front[0], front[i + 1], front[i])
        add_triangle(name, rear[0], rear[i], rear[i + 1])

    for layer_index in range(len(layers) - 1):
        y0, xz0 = layers[layer_index]
        y1, xz1 = layers[layer_index + 1]
        ring0 = [(x, y0, z) for x, z in xz0]
        ring1 = [(x, y1, z) for x, z in xz1]
        for i in range(count):
            j = (i + 1) % count
            add_quad(name, ring0[i], ring1[i], ring1[j], ring0[j])


def add_x_prism(name: str, x0: float, x1: float, yz: list[Vec2]) -> None:
    left = [(x0, y, z) for y, z in yz]
    right = [(x1, y, z) for y, z in yz]
    count = len(yz)

    for i in range(1, count - 1):
        add_triangle(name, left[0], left[i], left[i + 1])
        add_triangle(name, right[0], right[i + 1], right[i])

    for i in range(count):
        j = (i + 1) % count
        add_quad(name, left[i], right[i], right[j], left[j])


def add_xy_bar(name: str, start: Vec2, end: Vec2, width: float, z0: float, z1: float) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = x1 - x0
    dy = y1 - y0
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return
    nx = -dy / length * width / 2
    ny = dx / length * width / 2
    bottom = [
        (x0 + nx, y0 + ny),
        (x1 + nx, y1 + ny),
        (x1 - nx, y1 - ny),
        (x0 - nx, y0 - ny),
    ]
    add_layered_prism(name, [(z0, bottom), (z1, bottom)])


def add_side_spine_segment(
    name: str,
    y0: float,
    y1: float,
    inner0: float,
    inner1: float,
    z0: float,
    z1: float,
) -> None:
    if y1 <= y0:
        return

    left = [
        (0.0, y0),
        (0.0, y1),
        (inner1, y1),
        (inner0, y0),
    ]
    right = [
        (BASE_WIDTH, y0),
        (BASE_WIDTH - inner0, y0),
        (BASE_WIDTH - inner1, y1),
        (BASE_WIDTH, y1),
    ]
    add_layered_prism(f"left_faceted_side_spine_{name}", [(z0, left), (z1, left)])
    add_layered_prism(f"right_faceted_side_spine_{name}", [(z0, right), (z1, right)])


def add_faceted_side_spines(z0: float, z1: float) -> None:
    y_positions = [SLOT_Y0 + SLOT_INNER_LENGTH * ratio for ratio in GOLDEN_SUPPORT_RATIOS]
    root_half = BASE_ROOT_PAD_RAIL / 2
    root_reach = SLOT_1_X0
    waist = BASE_SIDE_SPINE_WAIST
    end_width = BASE_FRAME_RAIL
    y_front = max(BASE_CHAMFER, SLOT_Y0 - END_STOP_THICKNESS - root_half)
    y_mid = (y_positions[0] + y_positions[1]) / 2
    y_rear = min(BASE_DEPTH - BASE_CHAMFER, SLOT_Y1 + END_STOP_THICKNESS + root_half)

    segments = [
        ("front_taper", BASE_CHAMFER, y_front, end_width, waist),
        ("front_shoulder", y_front, y_positions[0] - root_half, waist, root_reach),
        ("front_root", y_positions[0] - root_half, y_positions[0] + root_half, root_reach, root_reach),
        ("center_tuck_a", y_positions[0] + root_half, y_mid, root_reach, waist),
        ("center_tuck_b", y_mid, y_positions[1] - root_half, waist, root_reach),
        ("rear_root", y_positions[1] - root_half, y_positions[1] + root_half, root_reach, root_reach),
        ("rear_shoulder", y_positions[1] + root_half, y_rear, root_reach, waist),
        ("rear_taper", y_rear, BASE_DEPTH - BASE_CHAMFER, waist, end_width),
    ]

    for name, y0, y1, inner0, inner1 in segments:
        add_side_spine_segment(name, y0, y1, inner0, inner1, z0, z1)


def add_yz_bar(name: str, x0: float, x1: float, start: Vec2, end: Vec2, width: float) -> None:
    y0, z0 = start
    y1, z1 = end
    dy = y1 - y0
    dz = z1 - z0
    length = (dy * dy + dz * dz) ** 0.5
    if length == 0:
        return
    ny = -dz / length * width / 2
    nz = dy / length * width / 2
    yz = [
        (y0 + ny, z0 + nz),
        (y1 + ny, z1 + nz),
        (y1 - ny, z1 - nz),
        (y0 - ny, z0 - nz),
    ]
    add_x_prism(name, x0, x1, yz)


def add_solid_octagonal_base() -> None:
    outline = octagon_outline(0.0, 0.0, BASE_WIDTH, BASE_DEPTH, BASE_CHAMFER)
    add_layered_prism("solid_octagonal_base_plate", [(0.0, outline), (BASE_THICKNESS, outline)])


def add_print_safe_foundations() -> None:
    z0 = 0.0
    z1 = BASE_THICKNESS

    for index, (x0, x1) in enumerate(((SLOT_1_X0, SLOT_1_X1), (SLOT_2_X0, SLOT_2_X1)), start=1):
        groove_x0, groove_x1 = groove_edges(index, x0, x1)
        add_soft_box(
            f"supported_bottom_groove_keel_{index}",
            groove_x0 - GROOVE_LIP_WIDTH,
            GROOVE_Y0 + GROOVE_END_INSET,
            z0,
            groove_x1 + GROOVE_LIP_WIDTH,
            GROOVE_Y1 - GROOVE_END_INSET,
            z1,
        )

    x0 = SLOT_1_X0 - OUTER_WALL_THICKNESS
    x1 = SLOT_2_X1 + OUTER_WALL_THICKNESS
    stop_pad = END_STOP_THICKNESS * PHI
    add_soft_box(
        "front_stop_integrated_foundation",
        x0,
        SLOT_Y0 - stop_pad,
        z0,
        x1,
        SLOT_Y0,
        z1,
    )
    add_soft_box(
        "rear_stop_integrated_foundation",
        x0,
        SLOT_Y1,
        z0,
        x1,
        SLOT_Y1 + stop_pad,
        z1,
    )

    for index, ratio in enumerate(GOLDEN_SUPPORT_RATIOS, start=1):
        y = SLOT_Y0 + SLOT_INNER_LENGTH * ratio
        y0 = y - BASE_ROOT_PAD_RAIL / 2
        y1 = y + BASE_ROOT_PAD_RAIL / 2
        add_soft_box(
            f"left_outer_pillar_root_pad_{index}",
            SLOT_1_X0 - OUTER_WALL_THICKNESS,
            y0,
            z0,
            SLOT_1_X0,
            y1,
            z1,
        )
        add_soft_box(
            f"center_fin_root_pad_{index}",
            DIVIDER_X0,
            y0,
            z0,
            DIVIDER_X1,
            y1,
            z1,
        )
        add_soft_box(
            f"right_outer_pillar_root_pad_{index}",
            SLOT_2_X1,
            y0,
            z0,
            SLOT_2_X1 + OUTER_WALL_THICKNESS,
            y1,
            z1,
        )


def groove_edges(slot_index: int, x0: float, x1: float) -> tuple[float, float]:
    if slot_index == 1:
        return x0 + ENTRY_FLARE_OUTER, x1 - ENTRY_FLARE_CENTER
    return x0 + ENTRY_FLARE_CENTER, x1 - ENTRY_FLARE_OUTER


def add_base() -> None:
    rail = BASE_FRAME_RAIL
    z0 = 0.0
    z1 = BASE_THICKNESS

    add_octagonal_outer_frame("continuous_octagonal_outer_frame", rail, z0, z1)
    add_faceted_side_spines(z0, z1)

    for index, ratio in enumerate(GOLDEN_SUPPORT_RATIOS, start=1):
        y = SLOT_Y0 + SLOT_INNER_LENGTH * ratio
        add_soft_box(
            f"golden_ratio_base_crossbar_{index}",
            rail,
            y - BASE_CROSS_RAIL / 2,
            z0,
            BASE_WIDTH - rail,
            y + BASE_CROSS_RAIL / 2,
            z1,
        )

    add_xy_bar(
        "base_diagonal_lattice_a",
        (rail + 2.0, SLOT_Y0 - END_STOP_THICKNESS),
        (BASE_WIDTH - rail - 2.0, SLOT_Y1 + END_STOP_THICKNESS),
        BASE_DIAGONAL_RAIL,
        z0,
        z1,
    )
    add_xy_bar(
        "base_diagonal_lattice_b",
        (BASE_WIDTH - rail - 2.0, SLOT_Y0 - END_STOP_THICKNESS),
        (rail + 2.0, SLOT_Y1 + END_STOP_THICKNESS),
        BASE_DIAGONAL_RAIL,
        z0,
        z1,
    )


def add_lattice_wall(
    name: str,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    center_triangles: bool = False,
    outer_capture_guard: bool = False,
) -> None:
    z0 = BASE_THICKNESS
    z_lower = z0 + LOWER_CAPTURE_HEIGHT
    z_top1 = z0 + SIDE_WALL_HEIGHT

    if outer_capture_guard:
        if (x0 + x1) / 2 < BASE_WIDTH / 2:
            inner_x = max(x0, x1)
            outer_x = min(x0, x1)
        else:
            inner_x = min(x0, x1)
            outer_x = max(x0, x1)
        for index, ratio in enumerate((1 / PHI**2, 1 / PHI), start=1):
            y = y0 + (y1 - y0) * ratio
            guard_y0 = max(y0, y - OUTER_GUARD_PILLAR_WIDTH / 2)
            guard_y1 = min(y1, y + OUTER_GUARD_PILLAR_WIDTH / 2)
            add_y_prism(
                f"{name}_sloped_outer_capture_pillar_{index}",
                guard_y0,
                guard_y1,
                outer_capture_guard_profile(inner_x, outer_x, z0, z_top1),
            )
    else:
        add_soft_box(f"{name}_lower_capture_rail", x0, y0, z0, x1, y1, z_lower)

    if center_triangles:
        # Keep the visible fin silhouette, but run it through the base so slicers
        # treat the two center stops as locked into the solid octagonal plate.
        rounded_triangle = soft_peak_profile(x0, x1, z0 - CENTER_FIN_TENON_DEPTH, z_top1)
        for index, ratio in enumerate((1 / PHI**2, 1 / PHI), start=1):
            y = y0 + (y1 - y0) * ratio
            rib_y0 = max(y0, y - CENTER_TRIANGLE_RIB_THICKNESS / 2)
            rib_y1 = min(y1, y + CENTER_TRIANGLE_RIB_THICKNESS / 2)
            add_y_prism(f"{name}_soft_golden_triangle_fin_{index}", rib_y0, rib_y1, rounded_triangle)


def add_outer_left_wall() -> None:
    x_inner = SLOT_1_X0
    x_outer = x_inner - OUTER_WALL_THICKNESS
    add_lattice_wall("left_snug_lattice_wall", x_outer, x_inner, SLOT_Y0, SLOT_Y1, outer_capture_guard=True)


def add_outer_right_wall() -> None:
    x_inner = SLOT_2_X1
    x_outer = x_inner + OUTER_WALL_THICKNESS
    add_lattice_wall("right_snug_lattice_wall", x_inner, x_outer, SLOT_Y0, SLOT_Y1, outer_capture_guard=True)


def center_divider_profile(z_top: float) -> list[Vec2]:
    z0 = 0.0
    z_lower = BASE_THICKNESS + LOWER_CAPTURE_HEIGHT
    top = max(z_lower, z_top)
    mid = (DIVIDER_X0 + DIVIDER_X1) / 2
    half_width = min(TIP_FLAT_WIDTH / 2, DIVIDER_THICKNESS / 4)
    shoulder = 0.0 if top <= z_lower else min(TIP_SHOULDER_DROP, (top - z0) / 3)
    return [
        (DIVIDER_X0, z0),
        (DIVIDER_X1, z0),
        (DIVIDER_X1, top - shoulder),
        (mid + half_width, top),
        (mid - half_width, top),
        (DIVIDER_X0, top - shoulder),
    ]


def add_center_divider() -> None:
    z_lower = BASE_THICKNESS + LOWER_CAPTURE_HEIGHT
    z_top = BASE_THICKNESS + SIDE_WALL_HEIGHT
    rib_half = CENTER_TRIANGLE_RIB_THICKNESS / 2
    layers: list[tuple[float, list[Vec2]]] = [(SLOT_Y0, center_divider_profile(z_lower))]

    for ratio in GOLDEN_SUPPORT_RATIOS:
        y = SLOT_Y0 + SLOT_INNER_LENGTH * ratio
        fin_y0 = max(SLOT_Y0, y - rib_half)
        fin_y1 = min(SLOT_Y1, y + rib_half)
        layers.extend(
            [
                (fin_y0, center_divider_profile(z_lower)),
                (fin_y0, center_divider_profile(z_top)),
                (fin_y1, center_divider_profile(z_top)),
                (fin_y1, center_divider_profile(z_lower)),
            ]
        )

    layers.append((SLOT_Y1, center_divider_profile(z_lower)))
    deduped: list[tuple[float, list[Vec2]]] = []
    for y, profile in sorted(layers, key=lambda item: item[0]):
        if deduped and abs(y - deduped[-1][0]) < 0.001 and profile == deduped[-1][1]:
            deduped[-1] = (y, profile)
        else:
            deduped.append((y, profile))

    add_y_sweep("center_unibody_stepped_divider", deduped)


def add_end_stops() -> None:
    z0 = BASE_THICKNESS
    x0 = SLOT_1_X0 - OUTER_WALL_THICKNESS
    x1 = SLOT_2_X1 + OUTER_WALL_THICKNESS

    front_outer = SLOT_Y0 - END_STOP_THICKNESS
    front_inner = SLOT_Y0
    front_yz = [
        (front_outer, z0),
        (front_inner, z0),
        (front_inner, z0 + END_STOP_HEIGHT * 0.68),
        (front_inner + END_STOP_HOOK_OVERHANG, z0 + END_STOP_HEIGHT),
        (front_outer + END_STOP_THICKNESS * 0.42, z0 + END_STOP_HEIGHT),
        (front_outer, z0 + END_STOP_HEIGHT * 0.52),
    ]
    add_x_prism("front_short_edge_hook_stop", x0, x1, front_yz)

    rear_inner = SLOT_Y1
    rear_outer = SLOT_Y1 + END_STOP_THICKNESS
    rear_yz = [
        (rear_inner, z0),
        (rear_outer, z0),
        (rear_outer, z0 + END_STOP_HEIGHT * 0.52),
        (rear_outer - END_STOP_THICKNESS * 0.42, z0 + END_STOP_HEIGHT),
        (rear_inner - END_STOP_HOOK_OVERHANG, z0 + END_STOP_HEIGHT),
        (rear_inner, z0 + END_STOP_HEIGHT * 0.68),
    ]
    add_x_prism("rear_short_edge_hook_stop", x0, x1, rear_yz)


def add_bottom_capture_grooves() -> None:
    for index, (x0, x1) in enumerate(((SLOT_1_X0, SLOT_1_X1), (SLOT_2_X0, SLOT_2_X1)), start=1):
        y0 = GROOVE_Y0 + GROOVE_END_INSET
        y1 = GROOVE_Y1 - GROOVE_END_INSET
        groove_x0, groove_x1 = groove_edges(index, x0, x1)
        add_box(
            f"bottom_groove_floor_{index}",
            groove_x0,
            y0,
            BASE_THICKNESS,
            groove_x1,
            y1,
            BASE_THICKNESS + GROOVE_FLOOR_HEIGHT,
        )
        add_box(
            f"left_1mm_bottom_groove_lip_{index}",
            groove_x0 - GROOVE_LIP_WIDTH,
            y0,
            BASE_THICKNESS,
            groove_x0,
            y1,
            BASE_THICKNESS + GROOVE_CAPTURE_HEIGHT,
        )
        add_box(
            f"right_1mm_bottom_groove_lip_{index}",
            groove_x1,
            y0,
            BASE_THICKNESS,
            groove_x1 + GROOVE_LIP_WIDTH,
            y1,
            BASE_THICKNESS + GROOVE_CAPTURE_HEIGHT,
        )


def build_model() -> None:
    add_solid_octagonal_base()
    add_outer_left_wall()
    add_center_divider()
    add_outer_right_wall()
    add_end_stops()
    add_bottom_capture_grooves()


def write_stl(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="ascii", newline="\n") as file:
        file.write("solid cornix_lp_short_edge_snug_storage_stand\n")
        for name, a, b, c in triangles:
            nx, ny, nz = normal(a, b, c)
            file.write(f"  facet normal {nx:.6f} {ny:.6f} {nz:.6f}\n")
            file.write("    outer loop\n")
            file.write(f"      vertex {a[0]:.3f} {a[1]:.3f} {a[2]:.3f}\n")
            file.write(f"      vertex {b[0]:.3f} {b[1]:.3f} {b[2]:.3f}\n")
            file.write(f"      vertex {c[0]:.3f} {c[1]:.3f} {c[2]:.3f}\n")
            file.write("    endloop\n")
            file.write("  endfacet\n")
        file.write("endsolid cornix_lp_short_edge_snug_storage_stand\n")


if __name__ == "__main__":
    build_model()
    output = Path(__file__).resolve().parents[1] / "stl" / "cornix_lp_bookshelf_storage_stand.stl"
    write_stl(output)
    print(f"Wrote {output}")
    print(f"Triangles: {len(triangles)}")
    print(f"Base: {BASE_WIDTH:.1f} x {BASE_DEPTH:.1f} x {BASE_THICKNESS:.1f} mm")
    print(f"Overall height: {BASE_THICKNESS + SIDE_WALL_HEIGHT:.1f} mm")
    print(f"Solid octagonal base: {BASE_THICKNESS:.1f} mm")
    print(f"Keyboard contact rectangle: {KEYBOARD_LONG_EDGE_CONTACT:.1f} x {KEYBOARD_SHORT_EDGE_CONTACT:.1f} mm")
    print(f"Slot insertion length: {SLOT_INNER_LENGTH:.1f} mm")
    print(f"Slot insertion width: {SLOT_INNER_WIDTH:.1f} mm")
    print(f"Entry length extra: +{ENTRY_LENGTH_EXTRA:.1f} mm")
    print(f"Entry flare: center +{ENTRY_FLARE_CENTER:.1f} mm, outer +{ENTRY_FLARE_OUTER:.1f} mm")
    print(f"Bottom groove inner length: {GROOVE_INNER_LENGTH:.1f} mm")
    print(f"Bottom groove inner width: {GROOVE_INNER_WIDTH:.1f} mm")
    print(f"Bottom groove height: {GROOVE_CAPTURE_HEIGHT:.1f} mm")
    print(f"Fit clearance: {FIT_CLEARANCE:.1f} mm total")
