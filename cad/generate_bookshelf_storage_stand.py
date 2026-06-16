from __future__ import annotations

from math import sqrt
from pathlib import Path


PHI = (1 + sqrt(5)) / 2

# Dimensions are in millimeters.
# Measure these two values on the real Cornix LP for a true snug fit.
KEYBOARD_SHORT_EDGE = 96.0
KEYBOARD_THICKNESS = 24.0
FIT_CLEARANCE = 0.5

SLOT_INNER_LENGTH = KEYBOARD_SHORT_EDGE + FIT_CLEARANCE
SLOT_INNER_WIDTH = KEYBOARD_THICKNESS + FIT_CLEARANCE

BENTO_REFERENCE_DEPTH = 120.0
BENTO_REFERENCE_HEIGHT = 55.0

BASE_DEPTH = BENTO_REFERENCE_DEPTH
BASE_WIDTH = BASE_DEPTH / PHI
BASE_THICKNESS = 6.0
BASE_CHAMFER = 8.0
BASE_TOP_INSET = 2.5

OUTER_WALL_THICKNESS = 5.0
DIVIDER_THICKNESS = 6.0
END_STOP_THICKNESS = 4.0

SIDE_WALL_HEIGHT = BENTO_REFERENCE_HEIGHT - BASE_THICKNESS
SIDE_WALL_TOP_BEVEL = 2.4
END_STOP_HEIGHT = 13.0
END_STOP_HOOK_OVERHANG = 1.0

RIB_THICKNESS = 3.2
RIB_HEIGHT = SIDE_WALL_HEIGHT / PHI
RIB_RUN = 14.0

SLOT_PAIR_WIDTH = SLOT_INNER_WIDTH * 2 + DIVIDER_THICKNESS
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


def add_base() -> None:
    bottom = chamfered_rect(0.0, 0.0, BASE_WIDTH, BASE_DEPTH, BASE_CHAMFER)
    top = chamfered_rect(
        BASE_TOP_INSET,
        BASE_TOP_INSET,
        BASE_WIDTH - BASE_TOP_INSET,
        BASE_DEPTH - BASE_TOP_INSET,
        BASE_CHAMFER - BASE_TOP_INSET,
    )
    add_layered_prism("snug_golden_ratio_plinth", [(0.0, bottom), (BASE_THICKNESS, top)])


def add_outer_left_wall() -> None:
    z0 = BASE_THICKNESS
    z1 = BASE_THICKNESS + SIDE_WALL_HEIGHT
    x_inner = SLOT_1_X0
    x_outer = x_inner - OUTER_WALL_THICKNESS
    xz = [
        (x_outer, z0),
        (x_inner, z0),
        (x_inner, z1 - SIDE_WALL_TOP_BEVEL),
        (x_inner - SIDE_WALL_TOP_BEVEL, z1),
        (x_outer, z1 - SIDE_WALL_TOP_BEVEL * 1.6),
    ]
    add_y_prism("left_snug_blade_wall", SLOT_Y0, SLOT_Y1, xz)


def add_outer_right_wall() -> None:
    z0 = BASE_THICKNESS
    z1 = BASE_THICKNESS + SIDE_WALL_HEIGHT
    x_inner = SLOT_2_X1
    x_outer = x_inner + OUTER_WALL_THICKNESS
    xz = [
        (x_inner, z0),
        (x_outer, z0),
        (x_outer, z1 - SIDE_WALL_TOP_BEVEL * 1.6),
        (x_inner + SIDE_WALL_TOP_BEVEL, z1),
        (x_inner, z1 - SIDE_WALL_TOP_BEVEL),
    ]
    add_y_prism("right_snug_blade_wall", SLOT_Y0, SLOT_Y1, xz)


def add_center_divider() -> None:
    z0 = BASE_THICKNESS
    z1 = BASE_THICKNESS + SIDE_WALL_HEIGHT
    peak_x = (DIVIDER_X0 + DIVIDER_X1) / 2
    xz = [
        (DIVIDER_X0, z0),
        (DIVIDER_X1, z0),
        (DIVIDER_X1, z1 - SIDE_WALL_TOP_BEVEL),
        (peak_x, z1),
        (DIVIDER_X0, z1 - SIDE_WALL_TOP_BEVEL),
    ]
    add_y_prism("center_snug_divider", SLOT_Y0, SLOT_Y1, xz)


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


def add_floor_contact_rails() -> None:
    rail_h = 1.1
    rail_w = 2.2
    for index, (x0, x1) in enumerate(((SLOT_1_X0, SLOT_1_X1), (SLOT_2_X0, SLOT_2_X1)), start=1):
        add_box(
            f"thin_short_edge_floor_rail_{index}",
            x0 + rail_w,
            SLOT_Y0 + 3.0,
            BASE_THICKNESS,
            x1 - rail_w,
            SLOT_Y1 - 3.0,
            BASE_THICKNESS + rail_h,
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
    add_base()
    add_outer_left_wall()
    add_center_divider()
    add_outer_right_wall()
    add_end_stops()
    add_floor_contact_rails()
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
    print(f"Slot inner length: {SLOT_INNER_LENGTH:.1f} mm")
    print(f"Slot inner width: {SLOT_INNER_WIDTH:.1f} mm")
    print(f"Fit clearance: {FIT_CLEARANCE:.1f} mm total")
