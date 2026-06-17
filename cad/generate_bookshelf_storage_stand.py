from __future__ import annotations

from math import sqrt
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
ENTRY_FLARE_CENTER = 4.0
ENTRY_FLARE_OUTER = 7.0

SLOT_INNER_LENGTH = KEYBOARD_SHORT_EDGE_CONTACT + FIT_CLEARANCE
GROOVE_INNER_WIDTH = KEYBOARD_THICKNESS + FIT_CLEARANCE
SLOT_INNER_WIDTH = GROOVE_INNER_WIDTH + ENTRY_FLARE_CENTER + ENTRY_FLARE_OUTER

BENTO_REFERENCE_DEPTH = 120.0
BENTO_REFERENCE_HEIGHT = 55.0

BASE_THICKNESS = 6.0
BASE_CHAMFER = 8.0
BASE_TOP_INSET = 2.5
BASE_FRAME_RAIL = 5.0
BASE_CROSS_RAIL = 3.2
BASE_SIDE_MARGIN = 3.0
UNIBODY_SKIN_HEIGHT = 0.6

OUTER_WALL_THICKNESS = 5.0
DIVIDER_THICKNESS = 6.0
END_STOP_THICKNESS = 4.0

STAND_OVERALL_HEIGHT = min(BENTO_REFERENCE_HEIGHT, round(KEYBOARD_LONG_EDGE_CONTACT / PHI**2, 1))
SIDE_WALL_HEIGHT = STAND_OVERALL_HEIGHT - BASE_THICKNESS
SIDE_WALL_TOP_BEVEL = 2.4
LOWER_CAPTURE_HEIGHT = 15.0
TOP_RAIL_HEIGHT = 4.0
LATTICE_BAR = 3.0
LATTICE_VERTICALS = 4
END_STOP_HEIGHT = 13.0
END_STOP_HOOK_OVERHANG = 0.0

RIB_THICKNESS = 3.2
RIB_HEIGHT = SIDE_WALL_HEIGHT / PHI
RIB_RUN = 14.0

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


def chamfered_rect(x0: float, y0: float, x1: float, y1: float, chamfer: float) -> list[Vec2]:
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


def add_unibody_bottom_skin() -> None:
    outline = chamfered_rect(0.0, 0.0, BASE_WIDTH, BASE_DEPTH, BASE_CHAMFER)
    add_layered_prism("bambu_safe_unibody_bottom_skin", [(0.0, outline), (UNIBODY_SKIN_HEIGHT, outline)])


def add_print_safe_foundations() -> None:
    for index, (x0, x1) in enumerate(((SLOT_1_X0, SLOT_1_X1), (SLOT_2_X0, SLOT_2_X1)), start=1):
        add_box(
            f"supported_bottom_groove_foundation_{index}",
            x0,
            SLOT_Y0 + GROOVE_END_INSET,
            0.0,
            x1,
            SLOT_Y1 - GROOVE_END_INSET,
            BASE_THICKNESS,
        )

    x0 = SLOT_1_X0 - OUTER_WALL_THICKNESS
    x1 = SLOT_2_X1 + OUTER_WALL_THICKNESS
    add_box(
        "front_stop_integrated_foundation",
        x0,
        SLOT_Y0 - END_STOP_THICKNESS,
        0.0,
        x1,
        SLOT_Y0,
        BASE_THICKNESS,
    )
    add_box(
        "rear_stop_integrated_foundation",
        x0,
        SLOT_Y1,
        0.0,
        x1,
        SLOT_Y1 + END_STOP_THICKNESS,
        BASE_THICKNESS,
    )


def groove_edges(slot_index: int, x0: float, x1: float) -> tuple[float, float]:
    if slot_index == 1:
        return x0 + ENTRY_FLARE_OUTER, x1 - ENTRY_FLARE_CENTER
    return x0 + ENTRY_FLARE_CENTER, x1 - ENTRY_FLARE_OUTER


def add_base() -> None:
    rail = BASE_FRAME_RAIL
    z0 = 0.0
    z1 = BASE_THICKNESS

    add_box("front_open_lattice_frame", BASE_CHAMFER, 0.0, z0, BASE_WIDTH - BASE_CHAMFER, rail, z1)
    add_box("rear_open_lattice_frame", BASE_CHAMFER, BASE_DEPTH - rail, z0, BASE_WIDTH - BASE_CHAMFER, BASE_DEPTH, z1)
    add_box("left_open_lattice_frame", 0.0, BASE_CHAMFER, z0, rail, BASE_DEPTH - BASE_CHAMFER, z1)
    add_box("right_open_lattice_frame", BASE_WIDTH - rail, BASE_CHAMFER, z0, BASE_WIDTH, BASE_DEPTH - BASE_CHAMFER, z1)

    add_xy_bar("front_left_chamfer_frame", (BASE_CHAMFER, rail / 2), (rail / 2, BASE_CHAMFER), rail, z0, z1)
    add_xy_bar(
        "front_right_chamfer_frame",
        (BASE_WIDTH - BASE_CHAMFER, rail / 2),
        (BASE_WIDTH - rail / 2, BASE_CHAMFER),
        rail,
        z0,
        z1,
    )
    add_xy_bar(
        "rear_right_chamfer_frame",
        (BASE_WIDTH - rail / 2, BASE_DEPTH - BASE_CHAMFER),
        (BASE_WIDTH - BASE_CHAMFER, BASE_DEPTH - rail / 2),
        rail,
        z0,
        z1,
    )
    add_xy_bar(
        "rear_left_chamfer_frame",
        (rail / 2, BASE_DEPTH - BASE_CHAMFER),
        (BASE_CHAMFER, BASE_DEPTH - rail / 2),
        rail,
        z0,
        z1,
    )

    support_y0 = max(rail, SLOT_Y0 - END_STOP_THICKNESS)
    support_y1 = min(BASE_DEPTH - rail, SLOT_Y1 + END_STOP_THICKNESS)
    for name, x0, x1 in (
        ("left_wall_underframe", SLOT_1_X0 - OUTER_WALL_THICKNESS, SLOT_1_X0),
        ("center_divider_underframe", DIVIDER_X0, DIVIDER_X1),
        ("right_wall_underframe", SLOT_2_X1, SLOT_2_X1 + OUTER_WALL_THICKNESS),
    ):
        add_box(name, x0, support_y0, z0, x1, support_y1, z1)

    for index, ratio in enumerate((1 / PHI**2, 1 / PHI), start=1):
        y = SLOT_Y0 + SLOT_INNER_LENGTH * ratio
        add_box(
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
        BASE_CROSS_RAIL,
        z0,
        z1,
    )
    add_xy_bar(
        "base_diagonal_lattice_b",
        (BASE_WIDTH - rail - 2.0, SLOT_Y0 - END_STOP_THICKNESS),
        (rail + 2.0, SLOT_Y1 + END_STOP_THICKNESS),
        BASE_CROSS_RAIL,
        z0,
        z1,
    )


def add_lattice_wall(name: str, x0: float, x1: float, y0: float, y1: float, peak: bool = False) -> None:
    z0 = BASE_THICKNESS
    z_lower = z0 + LOWER_CAPTURE_HEIGHT
    z_top0 = z0 + SIDE_WALL_HEIGHT - TOP_RAIL_HEIGHT
    z_top1 = z0 + SIDE_WALL_HEIGHT

    add_box(f"{name}_lower_capture_rail", x0, y0, z0, x1, y1, z_lower)
    add_box(f"{name}_top_lattice_rail", x0, y0, z_top0, x1, y1, z_top1)

    for index in range(LATTICE_VERTICALS):
        ratio = index / (LATTICE_VERTICALS - 1)
        y = y0 + (y1 - y0) * ratio
        post_y0 = max(y0, y - LATTICE_BAR / 2)
        post_y1 = min(y1, y + LATTICE_BAR / 2)
        add_box(f"{name}_vertical_post_{index + 1}", x0, post_y0, z0, x1, post_y1, z_top1)

    y_a = y0 + (y1 - y0) / PHI**2
    y_b = y0 + (y1 - y0) / PHI
    add_yz_bar(f"{name}_diagonal_lattice_a", x0, x1, (y0, z_lower), (y_b, z_top0), LATTICE_BAR)
    add_yz_bar(f"{name}_diagonal_lattice_b", x0, x1, (y_b, z_lower), (y1, z_top0), LATTICE_BAR)
    add_yz_bar(f"{name}_diagonal_lattice_c", x0, x1, (y_a, z_top0), (y1, z_lower), LATTICE_BAR)
    add_yz_bar(f"{name}_diagonal_lattice_d", x0, x1, (y0, z_top0), (y_a, z_lower), LATTICE_BAR)

    if peak:
        peak_x = (x0 + x1) / 2
        add_y_prism(
            f"{name}_center_peak_cap",
            y0,
            y1,
            [
                (x0, z_top0),
                (x1, z_top0),
                (peak_x, z_top1),
            ],
        )


def add_outer_left_wall() -> None:
    x_inner = SLOT_1_X0
    x_outer = x_inner - OUTER_WALL_THICKNESS
    add_lattice_wall("left_snug_lattice_wall", x_outer, x_inner, SLOT_Y0, SLOT_Y1)


def add_outer_right_wall() -> None:
    x_inner = SLOT_2_X1
    x_outer = x_inner + OUTER_WALL_THICKNESS
    add_lattice_wall("right_snug_lattice_wall", x_inner, x_outer, SLOT_Y0, SLOT_Y1)


def add_center_divider() -> None:
    add_lattice_wall("center_snug_lattice_divider", DIVIDER_X0, DIVIDER_X1, SLOT_Y0, SLOT_Y1, peak=True)


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
        y0 = SLOT_Y0 + GROOVE_END_INSET
        y1 = SLOT_Y1 - GROOVE_END_INSET
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


def add_golden_ratio_ribs() -> None:
    y_positions = [
        SLOT_Y0 + SLOT_INNER_LENGTH / PHI**2,
        SLOT_Y0 + SLOT_INNER_LENGTH / PHI,
    ]
    z0 = BASE_THICKNESS
    for index, y_center in enumerate(y_positions, start=1):
        y0 = y_center - RIB_THICKNESS / 2
        y1 = y_center + RIB_THICKNESS / 2
        left_x = SLOT_1_X0 - OUTER_WALL_THICKNESS
        right_x = SLOT_2_X1 + OUTER_WALL_THICKNESS

        left_rib = [
            (left_x, z0),
            (max(0.0, left_x - RIB_RUN), z0),
            (left_x, z0 + RIB_HEIGHT),
        ]
        right_rib = [
            (right_x, z0),
            (min(BASE_WIDTH, right_x + RIB_RUN), z0),
            (right_x, z0 + RIB_HEIGHT),
        ]
        add_y_prism(f"left_golden_ratio_buttress_{index}", y0, y1, left_rib)
        add_y_prism(f"right_golden_ratio_buttress_{index}", y0, y1, right_rib)


def build_model() -> None:
    add_unibody_bottom_skin()
    add_base()
    add_print_safe_foundations()
    add_outer_left_wall()
    add_center_divider()
    add_outer_right_wall()
    add_end_stops()
    add_bottom_capture_grooves()
    add_golden_ratio_ribs()


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
    print(f"Unibody bottom skin: {UNIBODY_SKIN_HEIGHT:.1f} mm")
    print(f"Keyboard contact rectangle: {KEYBOARD_LONG_EDGE_CONTACT:.1f} x {KEYBOARD_SHORT_EDGE_CONTACT:.1f} mm")
    print(f"Slot inner length: {SLOT_INNER_LENGTH:.1f} mm")
    print(f"Slot insertion width: {SLOT_INNER_WIDTH:.1f} mm")
    print(f"Entry flare: center +{ENTRY_FLARE_CENTER:.1f} mm, outer +{ENTRY_FLARE_OUTER:.1f} mm")
    print(f"Bottom groove inner width: {GROOVE_INNER_WIDTH:.1f} mm")
    print(f"Bottom groove height: {GROOVE_CAPTURE_HEIGHT:.1f} mm")
    print(f"Fit clearance: {FIT_CLEARANCE:.1f} mm total")
