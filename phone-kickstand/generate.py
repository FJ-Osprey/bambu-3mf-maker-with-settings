"""
generate.py -- parametric replacement kickstands for a phone case whose ring
stand snapped off its hinge leaf. Headless Blender script: builds each concept,
exports an STL (mm), and renders preview views against a placeholder case.

    /Applications/Blender.app/Contents/MacOS/Blender -b --python generate.py -- [--no-render]

Dimensions are ESTIMATED FROM PHOTOS (no calipers), scaled off an iPhone 12 Pro Max
(160.8 x 78.1 mm) in a leather case; the recess matching the ~55 mm MagSafe ring
cross-checks the scale. Print the fit coupon before trusting LEAF_* numbers.

Frame (part-local build coords, mm): +Y runs along the part when it is folded
shut, Z = away from the case. Z = 0 is the leaf's top face (about flush with the
leather), the hinge axis is at (Y=0, Z=HINGE_Z). Phone frame: case back surface
at Z = 0, phone centre at the origin.
"""

import math
import sys
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector, Matrix

OUT = Path(__file__).resolve().parent
RENDER_DIR = OUT / "renders"

# ---- CASE (from photos, 2026-09-30) ----------------------------------------
PHONE_W, PHONE_H, PHONE_T = 81.5, 164.5, 10.5
RING_CY = 0.0             # ring recess centre, phone Y (0 = phone centre); hinge ~51 mm above case bottom
RING_OD, RING_ID = 55.5, 43.7
HINGE_BELOW_RING = 3.85   # hinge axis below the recess's outer edge (31.6 mm below ring centre)
KNUCKLE_D, KNUCKLE_L = 2.4, 14.0   # calipers: OD ~2.4 (hard to measure)

# ---- LEAF (calipers, 2026-10-04) --------------------------------------------
# Stack when shut, case side up: steel hinge leaf (knuckle + curved "ears" the ring was riveted
# to), then the black stub of the snapped ring riveted on top. The cap sits on the black face.
LEAF_W = 13.4             # black stub width (narrowest, next to the knuckle)
LEAF_L = 1.2 + 6.7        # axis to the black stub's far edge (6.6-6.7 mm from the knuckle)
EAR_W = 17.6              # steel ears, overall width
EAR_Y0, EAR_Y1 = 3.0, 7.0 # ears' 4 mm band along Y (from the photos' proportions)
METAL_T = 0.6             # GUESS: steel leaf thickness -- measure at an ear
BLACK_T = 1.6             # GUESS: black stub thickness above the steel -- measure
EAR_KEY_D = BLACK_T - 0.4 # keys drop into the space above the ears where the ring used to be
GLUE_GAP = 0.2            # shallow recess over the black face for epoxy
HINGE_Z = KNUCKLE_D / 2 - METAL_T - BLACK_T   # axis height relative to the black face (negative = below)
KNUCKLE_CLEAR = KNUCKLE_D / 2 + 0.5           # nothing nearer the axis than this
SWING_DEG = 125.0         # material behind the axis must clear the case up to this opening...
SWING_ALLOW = 0.6         # ...allowing this much dip into the teardrop recess / leather

# ---- PART ------------------------------------------------------------------
T = 2.6                   # plate thickness
EDGE_R = 0.9              # rounded edge radius (snag-proofing)
PRELOAD_DEG = 1.5         # plate tilted toward the case relative to the leaf: the tip lands
                          # first and the plate flexes flat as it closes, so no gap at the tip
OPEN_DEG = 135.0          # the hinge's full-open stop (the stand search stops at SWING_DEG)

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
def glue_recess():
    y0 = KNUCKLE_CLEAR
    return slab("glue", [rounded_rect(0, (y0 - 1 + LEAF_L + 0.3) / 2, LEAF_W + 0.4, LEAF_L + 1.3 - y0, 0.8)],
                -1, GLUE_GAP, 0)


def ear_keys():
    """Two keys that drop beside the black stub into the space above the steel ears (where the ring
    used to be): they locate the part and take side/twist loads off the glue."""
    keys = []
    for sx in (1, -1):
        xi, xo = LEAF_W / 2 + 0.3, EAR_W / 2 - 0.2
        keys.append(slab("key", [rounded_rect(sx * (xi + xo) / 2, (EAR_Y0 + EAR_Y1) / 2, xo - xi,
                                              EAR_Y1 - EAR_Y0 - 0.4, 0.5)], -EAR_KEY_D, 0.3, 0.3))
    boolean(keys[0], keys[1], 'UNION')
    return keys[0]


def mount():
    """Top cap glued onto the black stub's face, with the ear keys underneath."""
    y0, y1 = KNUCKLE_CLEAR, LEAF_L + 1.4
    cap = slab("cap", [rounded_rect(0, (y0 + y1) / 2, EAR_W + 2.4, y1 - y0, 2.5)], 0, T, EDGE_R)
    boolean(cap, glue_recess(), 'DIFFERENCE')
    boolean(cap, ear_keys(), 'UNION')
    return cap


def swing_clip(ob):
    """Bevel the near edge so nothing dips more than SWING_ALLOW into the case when the part swings
    open to SWING_DEG (the axis sits below the part, so the near top edge swings down behind it).
    World z after opening = HINGE_Z + n.(p - axis) with n = (0, sin, cos); keep n.(p - axis) >= d.
    Done as a planar bisect + cap: a rotated cutter box silently cut ~20 mm in the wrong place."""
    th = math.radians(SWING_DEG)
    n = Vector((0, math.sin(th), math.cos(th)))
    d = -SWING_ALLOW - HINGE_Z
    p0 = Vector((0, 0, HINGE_Z)) + n * d
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=p0, plane_no=n, clear_inner=True)
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if cut_edges:
        bmesh.ops.holes_fill(bm, edges=cut_edges)
    bm.to_mesh(ob.data)
    bm.free()


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
        # start far enough round that the feather's outer edge stays clear of the knuckle
        lim = (KNUCKLE_CLEAR + 1.0 - RC) / r1
        if lim > -1:
            a0 = max(a0, math.degrees(math.asin(lim)) + 4)
        a1 = max(a1, a0 + 30)     # a clamped start must never pass the tip (inside-out polygon)
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
    y0, y1 = KNUCKLE_CLEAR, 14.0
    return slab("root", [rounded_rect(0, (y0 + y1) / 2, EAR_W + 2.4, y1 - y0, 3.0)], 0, T, EDGE_R)


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


# Blocky voxel-game sword, drawn upright (straight blade, pixel-stepped tip) the way foam toy
# versions are, rather than the diagonal inventory icon: the straight blade edges snag less.
# o = outline (dark), c = blade (cyan), h = grip (brown). Rows bottom (hinge) to top.
MC_ROWS = [
    ".ooooooo.",   # pommel: the cap -- must cover the ear keys (+-9.4 mm) and the black stub
    ".ooocooo.",
    "..ooooo..",
    "...oho...",
    "...oho...",
    ".ooooooo.",   # guard
] + ["..occco.."] * 10 + [
    "...oco...",
    "....o....",
]
MC_PX = 3.2
MC_RELIEF = 0.6       # one-colour version: blade/grip pixels sit this much below the outline
MC_COLORS = {"o": ("outline", (0.10, 0.11, 0.12)), "c": ("blade", (0.20, 0.80, 0.80)),
             "h": ("grip", (0.45, 0.28, 0.12))}


def grid_outline(cellset, px, y0):
    """Boundary loops (mm) of a union of grid cells: cancel shared edges, chain the rest, drop
    collinear points. Integer lattice until the end, so no float seams (a union of per-pixel boxes
    left sliver seams that the bevel turned into grooves across the blade)."""
    edges = {}
    for (ix, iy) in cellset:
        c = [(ix, iy), (ix + 1, iy), (ix + 1, iy + 1), (ix, iy + 1)]
        for k in range(4):
            e = (c[k], c[(k + 1) % 4])
            if (e[1], e[0]) in edges:
                del edges[(e[1], e[0])]
            else:
                edges[e] = True
    nxt = {a: b for (a, b) in edges}
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, cur = [start], nxt.pop(start)
        while cur != start:
            loop.append(cur)
            cur = nxt.pop(cur)
        pts = [q for i, q in enumerate(loop)
               if (loop[i - 1][0] - q[0]) * (loop[(i + 1) % len(loop)][1] - q[1])
               != (loop[i - 1][1] - q[1]) * (loop[(i + 1) % len(loop)][0] - q[0])]
        loops.append([((x - 0.5) * px, y0 + y * px) for x, y in pts])
    return loops


def concept_mcsword(mono=False):
    cells = {}
    for iy, row in enumerate(MC_ROWS):
        for ix, ch in enumerate(row):
            if ch != ".":
                cells[(ix - len(row) // 2, iy)] = ch
    y0 = KNUCKLE_CLEAR
    body = slab("mc", grid_outline(cells, MC_PX, y0), 0, T, EDGE_R)
    # blade and grip pixels never touch the silhouette, so each colour is body ∩ its own prism
    prisms = {k: slab(f"pr{k}", grid_outline([c for c, ch in cells.items() if ch == k], MC_PX, y0),
                      -5, T + 5, 0) for k in ("c", "h")}
    if mono:
        for k, pr in prisms.items():
            boolean(body, slab(f"rel{k}", grid_outline([c for c, ch in cells.items() if ch == k], MC_PX, y0),
                               T - MC_RELIEF, T + 1, 0), 'DIFFERENCE')
            bpy.data.objects.remove(pr, do_unlink=True)
        return body
    out = {"o": None}
    for k, pr in prisms.items():
        piece = body.copy()
        piece.data = body.data.copy()
        bpy.context.collection.objects.link(piece)
        t = pr.copy()
        t.data = pr.data.copy()
        bpy.context.collection.objects.link(t)
        boolean(piece, t, 'INTERSECT')
        boolean(body, pr, 'DIFFERENCE')
        out[k] = (piece, MC_COLORS[k][1])
    out["o"] = (body, MC_COLORS["o"][1])
    return out


concept_mcsword.own_cap = True


CONCEPTS = {
    "wingring": concept_wingring,
    "wing": concept_wing,
    "mcsword": concept_mcsword,
}


# ------------------------------------------------------------ assembly
def _finish_piece(body):
    """Knuckle clip + preload tilt about the hinge axis, applied to a decorative piece."""
    boolean(body, box("clip", 0, KNUCKLE_CLEAR - 50, T / 2, 300, 100, 20), 'DIFFERENCE')
    body.matrix_world = (Matrix.Translation((0, 0, HINGE_Z)) @ Matrix.Rotation(math.radians(-PRELOAD_DEG), 4, 'X')
                         @ Matrix.Translation((0, 0, -HINGE_Z)))
    for o in bpy.context.selected_objects:
        o.select_set(False)
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def build_part(fn, **kw):
    """Returns [(object, rgb)]. A concept returns one object, or {colour_name: (object, rgb)} for a
    multicolour print; the cap is unioned into the first colour."""
    res = fn(**kw)
    pieces = list(res.values()) if isinstance(res, dict) else [(res, PART_RGB_ALT)]
    for ob, _ in pieces:
        _finish_piece(ob)
    if getattr(fn, "own_cap", False):
        # the design's own pixels form the cap: just add keys and cut the glue recess
        boolean(pieces[0][0], ear_keys(), 'UNION')
        for ob, _ in pieces:
            boolean(ob, glue_recess(), 'DIFFERENCE')
    else:
        boolean(pieces[0][0], mount(), 'UNION')
        for ob, _ in pieces[1:]:      # cap belongs to colour 1 only: no overlapping volumes
            t = ob.copy()
            t.data = ob.data.copy()
            bpy.context.collection.objects.link(t)
            boolean(pieces[0][0], t, 'DIFFERENCE')
    for ob, _ in pieces:
        swing_clip(ob)
        ob.name = "part"
    return pieces


def merged(pieces):
    """Single solid of all pieces (for the one-material STL and checks)."""
    base = pieces[0][0].copy()
    base.data = pieces[0][0].data.copy()
    bpy.context.collection.objects.link(base)
    for ob, _ in pieces[1:]:
        t = ob.copy()
        t.data = ob.data.copy()
        bpy.context.collection.objects.link(t)
        boolean(base, t, 'UNION')
    return base


def part_matrix(open_deg):
    """Part build coords -> phone frame. open_deg = 0: cap flat on the leaf, hinge flat."""
    return (Matrix.Translation((0, HINGE_Y, HINGE_Z)) @ Matrix.Rotation(math.radians(open_deg), 4, 'X')
            @ Matrix.Translation((0, 0, -HINGE_Z)))


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
    bump = slab("bump", [rounded_rect(-PHONE_W / 2 + 23, PHONE_H / 2 - 23, 40, 40, 9)], 0, 2.0, 1.0)
    objs.append((bump, (0.55, 0.57, 0.6)))
    tear = slab("tear", [rounded_rect(0, HINGE_Y - 1.6 - 7.5, 13.6, 15, 6.7)], -0.8, 0.02, 0)
    objs.append((tear, (0.03, 0.03, 0.035)))
    k = cyl("knuckle", KNUCKLE_D / 2, KNUCKLE_L, (0, HINGE_Y, HINGE_Z), rot=(0, math.pi / 2, 0))
    objs.append((k, (0.75, 0.72, 0.62)))
    return objs


def place_part(part, open_deg):
    """Put the part on the hinge in the phone frame. Shut = open by PRELOAD_DEG, which is where
    the tilted plate's tip lands on the leather (before the plate is flexed flat)."""
    part.matrix_world = part_matrix(open_deg if open_deg else PRELOAD_DEG)


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
    for part, rgb in build_part(fn):
        color(part, rgb)
        place_part(part, 0)
    camera((0, RING_CY - 2, 260), (0, RING_CY - 2, 0), ortho=100)
    render(RENDER_DIR / f"{name}_closed_top.png")
    camera((150, RING_CY - 190, 170), (0, RING_CY - 2, 0), lens=70)
    render(RENDER_DIR / f"{name}_closed_34.png")
    # edge-on at case level: how proud of the back is it?
    camera((200, HINGE_Y + 30, 4.0), (0, HINGE_Y + 30, 4.0), ortho=80)
    render(RENDER_DIR / f"{name}_closed_side.png")


def scene_detail(name, fn):
    """The part alone: underside (keys, glue recess) and, for multicolour designs, the one-colour
    relief version from above."""
    clear()
    setup_render((900, 700))
    for part, rgb in build_part(fn):
        color(part, rgb)
    camera((60, -40, -70), (0, 14, 0), lens=55)
    render(RENDER_DIR / f"{name}_underside.png")
    if "mono" in fn.__code__.co_varnames:
        clear()
        setup_render((900, 700))
        for part, _ in build_part(fn, mono=True):
            color(part, (0.20, 0.21, 0.23))
        camera((70, -50, 90), (0, 26, 0), lens=55)
        render(RENDER_DIR / f"{name}_mono.png")


def stand_pose(part_local, open_deg):
    """Portrait stand: phone rests on its bottom-back edge and the part's lowest point.
    Returns (phi, lean_from_vertical) or None if the phone would tip onto its face."""
    M = part_matrix(open_deg)
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
    pieces = build_part(fn)
    local = [v.co.copy() for part, _ in pieces for v in part.data.vertices]
    choice = None
    for od in range(20, int(SWING_DEG) + 1):
        r = stand_pose(local, od)
        if r and r[2] and (choice is None or abs(r[1] - lean_target) < abs(choice[2] - lean_target)):
            choice = (od, r[0], r[1])
    if choice is None:
        return None
    od, phi, lean = choice
    objs = case_model() + pieces
    for part, _ in pieces:
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


def fit_coupon(path, widths=(13.0, 13.4, 13.8)):
    """Three bare caps whose ear keys are spaced for black-stub widths 13.0 / 13.4 / 13.8 mm
    (1/2/3 notches on the tip edge). Set LEAF_W to the one that drops over the stub snugly."""
    global LEAF_W
    keep = LEAF_W
    caps = []
    for i, w in enumerate(widths):
        LEAF_W = w
        c = mount()
        tip = LEAF_L + 1.4
        for k in range(i + 1):
            boolean(c, box("n", (k - i / 2) * 2.2, tip, T, 1.0, 1.6, 2.0), 'DIFFERENCE')
        c.location.x = (i - 1) * (EAR_W + 6)
        caps.append(c)
    LEAF_W = keep
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for c in caps:
        c.select_set(True)
    bpy.context.view_layer.objects.active = caps[0]
    bpy.ops.object.join()
    export_stl(caps[0], path)


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    do_render = "--no-render" not in args
    RENDER_DIR.mkdir(exist_ok=True)
    report = []
    clear()
    fit_coupon(OUT / "fit_coupon.stl")
    for name, fn in CONCEPTS.items():
        clear()
        multi = "mono" in fn.__code__.co_varnames
        pieces = build_part(fn, mono=True) if multi else build_part(fn)
        part = merged(pieces) if len(pieces) > 1 else pieces[0][0]
        export_stl(part, OUT / f"kickstand_{name}.stl")
        bb = [part.matrix_world @ Vector(c) for c in part.bound_box]
        dims = [max(p[i] for p in bb) - min(p[i] for p in bb) for i in range(3)]
        nm = nonmanifold_count(part)
        line = f"{name}: {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm, non-manifold edges {nm}"
        # A zero non-manifold count does NOT mean the booleans worked: a bad operand makes the
        # solver silently drop whole pieces and still return a closed mesh. Length catches that.
        if dims[1] < 50:
            line += "  <-- SHORT: a boolean probably dropped geometry"
        if multi:     # multicolour: one STL per filament, shared frame
            clear()
            for i, (ob, rgb) in enumerate(build_part(fn)):
                export_stl(ob, OUT / f"kickstand_{name}_color{i + 1}.stl")
                line += f"; color{i + 1} non-manifold {nonmanifold_count(ob)}"
        if do_render:
            scene_closed(name, fn)
            scene_detail(name, fn)
            st = scene_stand(name, fn)
            line += (f", portrait stand: open {st[0]} deg, leans {st[1]:.0f} deg" if st
                     else ", portrait stand: NO stable pose")
        report.append(line)
    print("\nREPORT")
    for l in report:
        print("  " + l)


main()
