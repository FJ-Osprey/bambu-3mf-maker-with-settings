"""
blendercad.py -- reusable helpers for printable parts built with headless Blender.

    import sys; sys.path.insert(0, "<bambu repo>"); from blendercad import *

Units: mm (clear() sets scale_length=0.001; export_stl writes raw mm). Every boolean uses the
MANIFOLD solver. The traps these helpers exist to avoid are in the openclaw-memory playbook
`headless_blender_3d_design`; the short version:

- slab(): 2D outlines -> rounded-edge solid via a curve fill + bevel. Outlines must have no cusps
  and must not repeat their first point.
- groove(): an engraving as ONE stroke solid (a chain of boxes self-intersects).
- grid_loops()/grid_outline(): pixel art traced on an integer lattice (never union per-pixel
  boxes: float seams turn into grooves). Run unpinch() on any region whose pixels may touch only
  at a corner, or the curve fill drops the region silently.
- bisect_keep(): exact half-space cut (a rotated cutter box cut in the wrong place on 5.2).
- A zero nonmanifold_count() does NOT prove a boolean worked; check bbox_dims() too.

Worked example: phone-kickstand/generate.py.
"""

import math

import bpy
import bmesh
from mathutils import Vector, Matrix


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


def groove(pts, top, w=0.7, depth=0.6):
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
    return slab("groove", [left + right[::-1]], top - depth, top + 1.0, 0)


# ------------------------------------------------------------ hinge mount


def rounded_rect(cx, cy, w, h, r, n=6):
    pts = []
    for (qx, qy, a0) in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90),
                         (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        pts += arc(cx + qx, cy + qy, r, a0, a0 + 90, n)
    return pts


# ------------------------------------------------------------ concepts


def unpinch(cells, allowed):
    """Fill corner-only contacts (two cells touching diagonally, the other two empty) with one of the
    empty pair, taken from `allowed`. A pinched region traces as a self-touching loop, which the
    curve fill silently drops (the relief on the diagonal sword vanished that way)."""
    cells = set(cells)
    changed = True
    while changed:
        changed = False
        for (x, y) in list(cells):
            for dx, dy in ((1, 1), (1, -1)):
                if (x + dx, y + dy) in cells and (x + dx, y) not in cells and (x, y + dy) not in cells:
                    for f in ((x + dx, y), (x, y + dy)):
                        if f in allowed:
                            cells.add(f)
                            changed = True
                            break
    return cells


def grid_outline(cellset, px, y0):
    return [[((x - 0.5) * px, y0 + y * px) for x, y in loop] for loop in grid_loops(cellset)]


def grid_loops(cellset):
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
    nxt = {}
    for (a, b) in edges:
        nxt.setdefault(a, []).append(b)
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, prev, cur = [start], start, nxt[start].pop()
        if not nxt[start]:
            del nxt[start]
        while cur != start:
            loop.append(cur)
            outs = nxt[cur]
            if len(outs) > 1:
                # pinch vertex (cells touching only at a corner): take the sharpest right turn so
                # the two loops separate instead of crossing
                din = (cur[0] - prev[0], cur[1] - prev[1])
                outs.sort(key=lambda q: din[0] * (q[1] - cur[1]) - din[1] * (q[0] - cur[0]))
            prev, cur = cur, outs.pop(0)
            if not outs:
                del nxt[prev]
        pts = [q for i, q in enumerate(loop)
               if (loop[i - 1][0] - q[0]) * (loop[(i + 1) % len(loop)][1] - q[1])
               != (loop[i - 1][1] - q[1]) * (loop[(i + 1) % len(loop)][0] - q[0])]
        loops.append(pts)
    return loops


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


def bisect_keep(ob, p0, n):
    """Cut ob with the plane through p0 (normal n) and cap it, keeping the side n points to."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=Vector(p0), plane_no=Vector(n),
                                 clear_inner=True)
    cut = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    if cut:
        bmesh.ops.holes_fill(bm, edges=cut)
    bm.to_mesh(ob.data)
    bm.free()


def bbox_dims(ob):
    """World-space bounding-box size (x, y, z) in mm."""
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return [max(p[i] for p in bb) - min(p[i] for p in bb) for i in range(3)]
