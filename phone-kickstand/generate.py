"""
generate.py -- parametric replacement kickstands for a phone case whose ring
stand snapped off its hinge leaf. Headless Blender script: builds each concept,
exports an STL (mm), and renders preview views against a placeholder case.

    /Applications/Blender.app/Contents/MacOS/Blender -b --python generate.py -- [--no-render]

ALL DIMENSIONS BELOW ARE PLACEHOLDERS estimated from one photo. Measure the
real case and replace the CASE / LEAF blocks before printing anything.

Frame (part-local, mm): origin on the hinge axis, +Y runs along the part when
it is folded shut against the case, Z = away from the case back. The case back
surface is Z = 0 in the phone frame.
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix

OUT = Path(__file__).resolve().parent
RENDER_DIR = OUT / "renders"

# ---- CASE (placeholder) ---------------------------------------------------
PHONE_W, PHONE_H, PHONE_T = 76.0, 150.0, 10.0
RING_CY = -8.0            # ring recess centre, phone Y (0 = phone centre)
RING_OD, RING_ID = 58.0, 46.0
HINGE_BELOW_RING = 5.0    # hinge axis sits this far below the recess bottom edge
HINGE_Z = 1.6             # hinge axis height above the case back
KNUCKLE_D, KNUCKLE_L = 3.2, 11.0

# ---- LEAF (placeholder) -- the moving hinge leaf the part clamps onto -----
LEAF_W, LEAF_L, LEAF_T = 16.0, 10.0, 0.8
RIVET_D, RIVET_H = 3.0, 0.6

# ---- PART ------------------------------------------------------------------
T = 2.6                   # plate thickness
EDGE_R = 0.9              # rounded edge radius (snag-proofing)
PRELOAD_DEG = 2.0         # built-in angle that presses the free end into the case
OPEN_DEG = 135.0          # the hinge's full-open stop

HINGE_Y = RING_CY - RING_OD / 2 - HINGE_BELOW_RING
RC = RING_CY - HINGE_Y    # ring centre in part-local Y
R_MID = (RING_OD + RING_ID) / 4
R_HALF = (RING_OD - RING_ID) / 4


# ---------------------------------------------------------------- 2D helpers
def arc(cx, cy, r, a0, a1, n=24):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def circle(cx, cy, r, n=48):
    return arc(cx, cy, r, 0, 360, n)[:-1]


def mirror_x(pts):
    return [(-x, y) for x, y in reversed(pts)]


# ---------------------------------------------------------------- 3D helpers
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.unit_settings.system = 'METRIC'
    s.unit_settings.scale_length = 0.001


def slab(name, loops, z0, z1, round_r=0.0):
    """Extrude closed 2D outlines (outer + holes, even-odd) from z0 to z1 with rounded edges."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions = '2D'
    cu.fill_mode = 'BOTH'
    cu.resolution_u = 2
    h = (z1 - z0) / 2
    if round_r > 0:
        r = min(round_r, h * 0.95)
        cu.bevel_depth = r
        cu.bevel_resolution = 3
        cu.offset = -r
        cu.extrude = h - r
    else:
        cu.extrude = h
    for pts in loops:
        sp = cu.splines.new('POLY')
        sp.points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.points, pts):
            p.co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    ob = bpy.data.objects.new(name, cu)
    bpy.context.collection.objects.link(ob)
    ob.location.z = (z0 + z1) / 2
    to_mesh(ob)
    return ob


def to_mesh(ob):
    bpy.context.view_layer.objects.active = ob
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.to_mesh(ob.data)
    bm.free()


def box(name, cx, cy, cz, dx, dy, dz):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (dx, dy, dz)
    bpy.ops.object.transform_apply(scale=True)
    return ob


def cyl(name, r, depth, loc, rot=(0, 0, 0), n=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=n)
    ob = bpy.context.active_object
    ob.name = name
    return ob


def boolean(target, tool, op):
    m = target.modifiers.new("b", 'BOOLEAN')
    m.operation = op
    m.solver = 'MANIFOLD'  # Blender 4.5+; EXACT left thousands of open edges on tangent rounds
    m.object = tool
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(tool, do_unlink=True)


def groove(pts, w=0.7, depth=0.6):
    """Engraved line along a polyline: one closed stroke outline (offset both sides, round-ish
    ends) extruded as a single clean solid. A chain of overlapping boxes self-intersects, and
    the Manifold solver silently drops geometry when a tool does that."""
    h = w / 2
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L * h, dx / L * h
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    # extend ends by h so the cut reads as a rounded stroke
    def ext(p, q):
        dx, dy = p[0] - q[0], p[1] - q[1]
        L = math.hypot(dx, dy) or 1.0
        return (dx / L * h, dy / L * h)
    e0, e1 = ext(pts[0], pts[1]), ext(pts[-1], pts[-2])
    left[0] = (left[0][0] + e0[0], left[0][1] + e0[1]); right[0] = (right[0][0] + e0[0], right[0][1] + e0[1])
    left[-1] = (left[-1][0] + e1[0], left[-1][1] + e1[1]); right[-1] = (right[-1][0] + e1[0], right[-1][1] + e1[1])
    return slab("groove", [left + right[::-1]], T - depth, T + 1.0, 0)


# ------------------------------------------------------------ hinge mount
def mount():
    """Sleeve over the hinge leaf. Pocket keyed to the rivet heads; glue as backup.
    Leaf starts just past the knuckle radius; sleeve wraps it top and bottom."""
    y0 = KNUCKLE_D / 2 + 0.4
    wall = 1.0
    outer = slab("mount", [rounded_rect(0, y0 + (LEAF_L + wall) / 2, LEAF_W + 2 * wall, LEAF_L + wall, 2.0)],
                 0, T, EDGE_R)
    # leaf slot, open toward the knuckle, centred on the leaf plane (Z = HINGE_Z - 0 offset handled at assembly)
    slot = box("slot", 0, y0 + LEAF_L / 2 - 0.5, T / 2, LEAF_W + 0.3, LEAF_L + 1.0, LEAF_T + 0.25)
    boolean(outer, slot, 'DIFFERENCE')
    for rx in (-LEAF_W / 2 + 3, 0, LEAF_W / 2 - 3):
        c = cyl("rivet", RIVET_D / 2 + 0.2, RIVET_H * 2 + LEAF_T + 0.3,
                (rx, y0 + LEAF_L * 0.6, T / 2))
        boolean(outer, c, 'DIFFERENCE')
    return outer


def rounded_rect(cx, cy, w, h, r, n=6):
    pts = []
    for (qx, qy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                         (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        pts += arc(cx + qx, cy + qy, r, a0, a0 + 90, n)
    return pts


# ------------------------------------------------------------ concepts
def polar(a, r):
    return (r * math.cos(math.radians(a)), RC + r * math.sin(math.radians(a)))


def feather(a0, a1, r0, r1, tip=14.0, n=10):
    """One feather lying along the ring arc from angle a0 to a1 (degrees, CCW), radial band r0..r1.
    The tip end at a1 is a rounded point, like a folded primary."""
    body = [polar(a0 + (a1 - tip - a0) * i / n, r1) for i in range(n + 1)]
    # symmetric rounded point: no cusp against the inner edge (the edge round folds over a cusp)
    tipc = []
    for i in range(1, 16):
        th = math.pi * i / 16
        a = a1 - tip + tip * math.sin(th) ** 0.55
        r = (r1 + r0) / 2 + (r1 - r0) / 2 * math.cos(th)
        tipc.append(polar(a, r))
    back = [polar(a1 - tip - (a1 - tip - a0) * i / n, r0) for i in range(n + 1)]
    return body + tipc + back, tipc


# layered folded wing on the right side, root at the hinge, tip sweeping up past the top
WING_R_IN = RING_ID / 2 - 0.5
WING_FEATHERS = [  # (start angle, end angle, outer radius): steps must be ~2.5 mm or they vanish
    (-100, -38, RING_OD / 2 + 8.0),
    (-96, -12, RING_OD / 2 + 5.8),
    (-92, 14, RING_OD / 2 + 3.8),
    (-88, 40, RING_OD / 2 + 2.0),
    (-84, 66, RING_OD / 2 + 0.4),
    (-80, 96, RING_OD / 2 - 1.2),
]


def wing_outlines(end_extra=0.0, dr=0.0):
    loops, tips = [], []
    for i, (a0, a1, r1) in enumerate(WING_FEATHERS):
        last = i == len(WING_FEATHERS) - 1
        # stagger radii so no two feathers share a surface (exact boolean chokes on tangent rounds)
        pts, tipc = feather(a0, a1 + (end_extra if last else 0), WING_R_IN - 0.45 * i + 0.3 * (len(WING_FEATHERS) - 1) + dr,
                            r1 + dr, tip=16 if last else 13)
        loops.append(pts)
        tips.append(tipc)
    return loops, tips


def wing_body(name, mirror=False, end_extra=0.0, dr=0.0):
    loops, tips = wing_outlines(end_extra, dr)
    if mirror:
        loops = [mirror_x(p) for p in loops]
        tips = [[(-x, y) for x, y in t] for t in tips]
    body = slab(name, [loops[0]], 0, T, EDGE_R)
    for i, p in enumerate(loops[1:]):
        boolean(body, slab(f"{name}{i}", [p], 0, T, EDGE_R), 'UNION')
    # engrave each covered feather tip so the layering reads
    for t in tips[:-1]:
        boolean(body, groove(t, w=0.8, depth=0.7), 'DIFFERENCE')
    # scale rows (coverts) near the root: little U-shaped grooves, staggered
    for row in range(3):
        r = WING_R_IN + 2.6 + row * 2.8
        for k in range(4 - (row == 2)):
            a = -78 + row * 4 + k * 9.5
            cx, cy = polar(a, r)
            # U opens toward the wing tip (tangent direction)
            tang = math.radians(a + 90)
            u = []
            for i in range(9):
                th = tang + math.pi / 2 + math.pi * i / 8
                u.append((cx + 1.5 * math.cos(th), cy + 1.5 * math.sin(th)))
            if mirror:
                u = [(-x, y) for x, y in u]
            boolean(body, groove(u, w=0.55, depth=0.5), 'DIFFERENCE')
    return body


def root_block():
    """Shoulder that blends the mount into the design."""
    return slab("root", [rounded_rect(0, 8.0, LEAF_W + 2.4, 12.0, 3.0)], 0, T, EDGE_R)


def concept_wing():
    """Single folded raptor wing up one side. Keeps the MagSafe disc clear; asymmetric."""
    body = wing_body("wing")
    boolean(body, root_block(), 'UNION')
    return body


def concept_wingring():
    """Two folded wings wrapping the recess, tips crossing at the top, tail fan at the hinge.
    A finger loop again, keeps the MagSafe disc clear, symmetric stand."""
    body = wing_body("wr", end_extra=0)
    # offset the mirrored wing's radii: where the two wings overlap (bottom, crossed tips) their
    # surfaces would otherwise coincide exactly
    boolean(body, wing_body("wl", mirror=True, dr=0.25), 'UNION')
    tail = []
    for k, dx in enumerate((-6.0, 0.0, 6.0)):
        ang = math.radians(dx * 2.2)
        pts = []
        for i in range(24):
            t = 2 * math.pi * i / 24
            x, y = 3.2 * math.cos(t), 7.0 * math.sin(t)
            pts.append((dx + x * math.cos(ang) - y * math.sin(ang), 6.5 + x * math.sin(ang) + y * math.cos(ang)))
        tail.append(pts)
    for i, p in enumerate(tail):
        boolean(body, slab(f"tail{i}", [p], 0, T, EDGE_R), 'UNION')
    for dx in (-6.0, 0.0, 6.0):
        boolean(body, groove([(dx * 0.8, 10.5), (dx * 1.05, 2.5)], w=0.5, depth=0.45), 'DIFFERENCE')
    return body


def concept_sword():
    """Blocky game-style sword; the hilt is the mount. Blade covers the MagSafe disc."""
    tip_y = RC + RING_OD / 2 + 1
    guard_y = 17.0
    bw = 10.0
    ogive = []
    for i in range(1, 12):
        t = i / 12
        ogive.append((bw / 2 * math.cos(t * math.pi / 2) ** 0.7, tip_y - 12 + 12 * math.sin(t * math.pi / 2)))
    blade = [(bw / 2, guard_y + 2), (bw / 2, tip_y - 12)] + ogive + [(0, tip_y)] + \
        [(-x, y) for x, y in reversed(ogive)] + [(-bw / 2, tip_y - 12), (-bw / 2, guard_y + 2)]
    guard = [(-15, guard_y + 3.5), (-13.5, guard_y - 1), (13.5, guard_y - 1), (15, guard_y + 3.5),
             (13, guard_y + 4.5), (4, guard_y + 3.2), (-4, guard_y + 3.2), (-13, guard_y + 4.5)]
    grip = rounded_rect(0, 13.0, 7, 8, 1.2)
    body = slab("blade", [blade], 0, T, EDGE_R)
    boolean(body, slab("guard", [guard], 0, T, EDGE_R), 'UNION')
    boolean(body, slab("grip", [grip], 0, T, EDGE_R), 'UNION')
    pommel = [(0, -0.5), (6, 1.0), (LEAF_W / 2 + 1.2, 5.5), (LEAF_W / 2 + 1.2, 10.5), (4.5, 13.5),
              (-4.5, 13.5), (-LEAF_W / 2 - 1.2, 10.5), (-LEAF_W / 2 - 1.2, 5.5), (-6, 1.0)]
    boolean(body, slab("pommel", [pommel], 0, T, EDGE_R), 'UNION')
    boolean(body, cyl("gem", 1.6, 1.2, (0, 4.2, T)), 'DIFFERENCE')
    boolean(body, groove([(0, guard_y + 6), (0, tip_y - 11)], w=1.6, depth=0.7), 'DIFFERENCE')
    for k in range(3):
        boolean(body, groove([(-3.0, 10.2 + 2.2 * k), (3.0, 11.2 + 2.2 * k)], w=0.6), 'DIFFERENCE')
    return body


CONCEPTS = {
    "wingring": concept_wingring,
    "wing": concept_wing,
    "sword": concept_sword,
}


# ------------------------------------------------------------ assembly
def build_part(fn):
    body = fn()
    boolean(body, mount(), 'UNION')
    body.name = "part"
    return body


def nonmanifold_count(ob):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    return n


def export_stl(ob, path):
    for o in bpy.context.selected_objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    # scene scale_length=0.001 means 1 BU = 1 mm; export raw BU so the STL is in mm
    bpy.ops.wm.stl_export(filepath=str(path), export_selected_objects=True,
                          global_scale=1.0, use_scene_unit=False, apply_modifiers=True)


def case_model():
    """Placeholder case back, recess, disc, knuckle. Phone frame: back surface at Z=0."""
    objs = []
    body = slab("case", [rounded_rect(0, 0, PHONE_W, PHONE_H, 11, 8)], -PHONE_T, 0, 1.5)
    objs.append((body, (0.16, 0.16, 0.17)))
    recess = slab("recess", [circle(0, RING_CY, RING_OD / 2, 96), circle(0, RING_CY, RING_ID / 2, 96)],
                  -0.9, 0.02, 0)
    objs.append((recess, (0.03, 0.03, 0.035)))
    disc = slab("disc", [circle(0, RING_CY, RING_ID / 2 - 0.3, 96)], -0.2, 0.35, 0.3)
    objs.append((disc, (0.12, 0.12, 0.13)))
    bump = slab("bump", [rounded_rect(-PHONE_W / 2 + 22, PHONE_H / 2 - 22, 38, 38, 8)], 0, 2.0, 1.0)
    objs.append((bump, (0.55, 0.57, 0.6)))
    k = cyl("knuckle", KNUCKLE_D / 2, KNUCKLE_L, (0, HINGE_Y, HINGE_Z), rot=(0, math.pi / 2, 0))
    objs.append((k, (0.75, 0.72, 0.62)))
    return objs


def place_part(part, open_deg, preload=True):
    """Put the part on the hinge in the phone frame. open_deg=0 is folded shut."""
    ang = math.radians(open_deg - (PRELOAD_DEG if preload and open_deg == 0 else 0))
    part.matrix_world = (Matrix.Translation((0, HINGE_Y, HINGE_Z)) @ Matrix.Rotation(ang, 4, 'X')
                         @ Matrix.Translation((0, 0, -T / 2)))


def color(ob, rgb):
    ob.color = (*rgb, 1.0)


def camera(loc, look_at, ortho=None, lens=60):
    cam = bpy.data.cameras.new("cam")
    ob = bpy.data.objects.new("cam", cam)
    bpy.context.collection.objects.link(ob)
    ob.location = loc
    d = Vector(look_at) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if ortho:
        cam.type = 'ORTHO'
        cam.ortho_scale = ortho
    else:
        cam.lens = lens
    cam.clip_start = 1
    cam.clip_end = 5000
    bpy.context.scene.camera = ob
    return ob


def setup_render(res=(900, 900)):
    s = bpy.context.scene
    s.render.engine = 'BLENDER_WORKBENCH'
    s.display.shading.light = 'STUDIO'
    s.display.shading.color_type = 'OBJECT'
    s.display.shading.show_cavity = True
    s.display.shading.cavity_type = 'BOTH'
    s.display.shading.show_shadows = True
    s.display.shading.show_specular_highlight = True
    s.render.resolution_x, s.render.resolution_y = res
    s.render.film_transparent = False
    s.world = bpy.data.worlds.new("w")
    s.world.color = (0.82, 0.84, 0.86)
    s.display_settings.display_device = 'sRGB'


def render(path):
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


PART_RGB = (0.20, 0.21, 0.23)      # PETG-CF-ish charcoal
PART_RGB_ALT = (0.85, 0.35, 0.10)  # orange so it reads against the black case


def scene_closed(name, fn):
    clear()
    setup_render()
    for ob, rgb in case_model():
        color(ob, rgb)
    part = build_part(fn)
    color(part, PART_RGB_ALT)
    place_part(part, 0)
    camera((0, RING_CY - 2, 260), (0, RING_CY - 2, 0), ortho=100)
    render(RENDER_DIR / f"{name}_closed_top.png")
    camera((150, RING_CY - 190, 170), (0, RING_CY - 2, 0), lens=70)
    render(RENDER_DIR / f"{name}_closed_34.png")
    # edge-on at case level: how proud of the back is it?
    camera((200, HINGE_Y + 30, 4.0), (0, HINGE_Y + 30, 4.0), ortho=80)
    render(RENDER_DIR / f"{name}_closed_side.png")


def stand_pose(part_local, open_deg):
    """Portrait stand: phone rests on its bottom-back edge and the part's lowest point.
    Returns (phi, lean_from_vertical) or None if the phone would tip onto its face."""
    M = (Matrix.Translation((0, HINGE_Y, HINGE_Z)) @ Matrix.Rotation(math.radians(open_deg), 4, 'X')
         @ Matrix.Translation((0, 0, -T / 2)))
    pv = [M @ v for v in part_local]
    edge = Vector((0, -PHONE_H / 2, -PHONE_T))
    best = None
    # phi rotates the phone about X; phone Y axis -> (0, cos, sin). Back faces the table when cos(phi) < 0.
    for i in range(1800):
        phi = math.radians(90 + i * 0.05)
        c, s = math.cos(phi), math.sin(phi)
        ze = edge.y * s + edge.z * c
        zp = min(p.y * s + p.z * c for p in pv)
        if zp <= ze:        # part foot reaches the table at this lean
            # centre of mass (phone centre) must lie between edge and foot in world Y
            foot = min(pv, key=lambda p: p.y * s + p.z * c)
            ye, yf, yc = edge.y * c - edge.z * s, foot.y * c - foot.z * s, 0.0 * c - (-PHONE_T / 2) * s
            ok = min(ye, yf) < yc < max(ye, yf)
            best = (phi, math.degrees(phi) - 90, ok)
            break
    return best


def scene_stand(name, fn, lean_target=20.0):
    """Phone standing in portrait on the part, at the open angle that gives ~lean_target."""
    clear()
    setup_render()
    part = build_part(fn)
    local = [v.co.copy() for v in part.data.vertices]
    choice = None
    for od in range(20, int(OPEN_DEG) + 1):
        r = stand_pose(local, od)
        if r and r[2] and (choice is None or abs(r[1] - lean_target) < abs(choice[2] - lean_target)):
            choice = (od, r[0], r[1])
    if choice is None:
        return None
    od, phi, lean = choice
    objs = case_model() + [(part, PART_RGB_ALT)]
    place_part(part, od)
    R = Matrix.Rotation(phi, 4, 'X')
    for ob, rgb in objs:
        color(ob, rgb)
        ob.matrix_world = R @ ob.matrix_world
    bpy.context.view_layer.update()
    zmin = min((ob.matrix_world @ v.co).z for ob, _ in objs for v in ob.data.vertices)
    for ob, _ in objs:
        ob.matrix_world = Matrix.Translation((0, 0, -zmin)) @ ob.matrix_world
    table = box("table", 0, 0, -0.5, 500, 500, 1)
    color(table, (0.62, 0.55, 0.45))
    # camera behind and to the side, looking at the back of the phone
    back = (R.to_3x3() @ Vector((0, 0, 1))).normalized()
    tgt = Vector((0, back.y * 20, 45))
    camera(tuple(tgt + Vector((-170, 0, 0)) + back * 190 + Vector((0, 0, 40))), tuple(tgt), lens=55)
    render(RENDER_DIR / f"{name}_stand.png")
    return od, lean


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    do_render = "--no-render" not in args
    RENDER_DIR.mkdir(exist_ok=True)
    report = []
    for name, fn in CONCEPTS.items():
        clear()
        part = build_part(fn)
        stl = OUT / f"kickstand_{name}.stl"
        export_stl(part, stl)
        bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
        dims = [max(p[i] for p in bb) - min(p[i] for p in bb) for i in range(3)]
        nm = nonmanifold_count(part)
        line = f"{name}: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm, non-manifold edges {nm}"
        # A zero non-manifold count does NOT mean the booleans worked: a bad operand makes the
        # solver silently drop whole pieces and still return a closed mesh. Length catches that.
        if dims[1] < 55:
            line += "  <-- SHORT: a boolean probably dropped geometry"
        if do_render:
            scene_closed(name, fn)
            st = scene_stand(name, fn)
            line += (f", portrait stand: open {st[0]} deg, leans {st[1]:.0f} deg" if st
                     else ", portrait stand: NO stable pose")
        report.append(line)
    print("\nREPORT")
    for l in report:
        print("  " + l)


main()
