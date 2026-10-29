"""
fit_coupons.py -- the calibration coupon set: print once, measure with calipers, write the numbers into
docs/design-for-print/8-printer-and-calibration.md.

    uv run --with manifold3d --with numpy python calibration/fit_coupons.py            # STLs + checks
    uv run --with manifold3d --with numpy python calibration/fit_coupons.py --package  # also the two 3MFs

Two plates, both PLA, 0.2 mm layers, no supports:
  fit_coupons   vertical holes 2-6 mm; horizontal holes round and teardrop 3-6 mm; self-tapping pilot ladder
                (1.5-1.8 for a ~2 mm screw, 2.4-2.8 for M3); a 6 mm peg and a plate of holes 5.9-6.5; a 3 mm tab and
                a plate of slots 3.0-3.5
  snap_ladder   one keeper channel and five clips whose arms bend 0.5-2.5 mm (strain 0.7-3.6 % by the cantilever
                formula); the arm lies flat, so it bends along its layers

Sizes run smallest to largest from the notched end. The clips carry 1-5 notches. Every check probes the geometry
and has a control that must fail. --package needs a template 3MF (below) and
rewrites filament slot 0 to Generic PLA, because stl_to_bambu_3mf.py leaves the template's material there.
--template (or env BAMBU_PLA_TEMPLATE) names an A1 mini Bambu Studio 3MF whose slots hold Generic PLA.
"""

import argparse
import json
import math
import os
import struct
import subprocess
import zipfile
from pathlib import Path

import manifold3d as m
import numpy as np

M, CS = m.Manifold, m.CrossSection
HERE = Path(__file__).parent
BAMBU = HERE.parent
BED = 180.0
FN = 128

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(HERE / "out"))
ap.add_argument("--package", action="store_true")
ap.add_argument("--template", default=os.environ.get("BAMBU_PLA_TEMPLATE", ""),
                help="any Bambu Studio 3MF saved for the A1 mini with Generic PLA in its slots (env BAMBU_PLA_TEMPLATE)")
args = ap.parse_args()
TEMPLATE = Path(args.template)
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------ sizes (mm). Change these, not the code.

V_HOLES = [2.0, 2.5, 3.0, 4.0, 5.0, 6.0]          # vertical-axis holes: shrink
H_HOLES = [3.0, 4.0, 5.0, 6.0]                    # horizontal-axis holes, once round, once teardrop
PILOTS = [1.5, 1.6, 1.7, 1.8, 2.4, 2.6, 2.8]      # self-tapping pilots: ~2 mm screw, then M3
PEG = 6.0                                         # peg and the fit ladder's nominal
FIT = [-0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5]        # diametral clearance of each hole over the peg
TAB = 3.0                                         # tab thickness (printed flat: 15 layers at 0.2)
SLOT = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]             # slot width over the tab
CHAMFER = 0.4                                     # bed-side chamfer on holes that take a pin (elephant's foot)
SNAP = {"t": 1.6, "L": 13.0, "b": 5.0, "handle": (8.0, 10.0), "gap": 0.2, "ramp_deg": 30.0,
        "defl": [0.5, 1.0, 1.5, 2.0, 2.5]}       # arm thickness, root-to-catch length, width; deflection ladder

report = {}


def check(name, ok, detail):
    report[name] = {"ok": bool(ok), "detail": detail}
    print(("PASS " if ok else "FAIL ") + name + ": " + str(detail))
    assert ok, name


# ------------------------------------------------------------------ helpers


def box(x0, x1, y0, y1, z0, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def poly(pts):
    p = np.array(pts, float)
    a = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
    return CS([p if a > 0 else p[::-1]])


def circle(cx, cy, d):
    return CS.circle(d / 2, FN).translate([cx, cy])


def teardrop(cx, cy, d):
    """Circle plus a 45-degree point on +y (90-degree included angle), so it prints without support."""
    r = d / 2
    s = r / math.sqrt(2)
    return circle(cx, cy, d) + poly([(cx - s, cy + s), (cx + s, cy + s), (cx, cy + r * math.sqrt(2))])


def prism_y(cs, y0, y1):
    """2D shape in (x, z) extruded along Y from y0 to y1."""
    return cs.extrude(y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def vhole(x, y, d, h, chamfer=0.0):
    """Vertical through hole for a plate 0..h, optional 45-degree chamfer on the bed side."""
    c = M.cylinder(h + 2, d / 2, d / 2, FN).translate([x, y, -1])
    if chamfer:
        c = c + M.cylinder(chamfer + 1, d / 2 + chamfer + 1, d / 2, FN).translate([x, y, -1])
    return c


def vnotch(x, y_face, z0, z1, depth=1.0, w=1.4, inward=+1):
    """V notch through a face at y = y_face, cut `depth` into the solid (inward = +1: solid is at y > face)."""
    tri = poly([(x - w / 2, y_face - inward * 0.5), (x + w / 2, y_face - inward * 0.5), (x, y_face + inward * depth)])
    return tri.extrude(z1 - z0 + 2).translate([0, 0, z0 - 1])


def bbox(mf):
    b = mf.bounding_box()
    return np.array(b[:3]), np.array(b[3:])


def vol(mf):
    return mf.volume() if not mf.is_empty() else 0.0


def write_stl(mf, path):
    mesh = mf.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float32)
    f = np.asarray(mesh.tri_verts)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    with open(path, "wb") as fh:
        fh.write(b"fit_coupons".ljust(80, b" "))
        fh.write(struct.pack("<I", len(f)))
        rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec["n"], rec["v"] = n, tri
        fh.write(rec.tobytes())


def void_dims_z(solid, x0, x1, y0, y1, z):
    """Width (x) and depth (y) of the empty space inside a window of the slice at height z."""
    win = CS.square([x1 - x0, y1 - y0]).translate([x0, y0])
    hole = win - (solid.slice(z) ^ win)
    if hole.is_empty():
        return 0.0, 0.0, 0.0
    b = hole.bounds()
    return b[2] - b[0], b[3] - b[1], hole.area()


def solo(mf, name):
    """One solid body, sitting on the bed, inside the bed."""
    parts = mf.decompose()
    check(f"{name}: one body", len(parts) == 1, len(parts))
    lo, hi = bbox(mf)
    check(f"{name}: on the bed", abs(lo[2]) < 1e-6, lo[2])
    check(f"{name}: fits the bed", (hi - lo)[0] < BED - 10 and (hi - lo)[1] < BED - 10, (hi - lo).round(2).tolist())


def spread(sizes, x0, gap):
    """x centres for holes laid out left to right with `gap` mm of wall between them."""
    xs, x = [], x0
    for i, d in enumerate(sizes):
        x += (d / 2 if i == 0 else sizes[i - 1] / 2 + gap + d / 2)
        xs.append(x)
    return xs


# ------------------------------------------------------------------ fit plate parts

parts = {}

# 1. vertical holes: shrink. Plate 4 mm thick, holes chamfered on the bed side so the first layer doesn't close them.
xs = spread(V_HOLES, 6, 6)
L = xs[-1] + V_HOLES[-1] / 2 + 6
p = box(0, L, 0, 16, 0, 4)
for x, d in zip(xs, V_HOLES):
    p -= vhole(x, 8, d, 4, CHAMFER)
p -= vnotch(0.0 + 3, 0, 0, 4)          # one notch on the long edge at the small end
parts["holes_vertical"] = p
for x, d in zip(xs, V_HOLES):
    w, dp, a = void_dims_z(p, x - d / 2 - 2, x + d / 2 + 2, 8 - d / 2 - 2, 8 + d / 2 + 2, 2.0)
    check(f"holes_vertical: {d} mm hole is {d} at mid-height", abs(w - d) < 0.005 and abs(dp - d) < 0.005,
          (round(w, 3), round(dp, 3)))
w0, _, _ = void_dims_z(box(0, L, 0, 16, 0, 4), 0, 5, 4, 12, 2.0)
check("holes_vertical: control, a plate with no hole measures no hole", w0 == 0.0, w0)

# 2. horizontal holes, axis along Y: round then teardrop. Block stands 14 tall, 10 deep.
sizes = H_HOLES + H_HOLES
xs = spread(sizes, 6, 6)
L = xs[-1] + sizes[-1] / 2 + 6
zc = 6.0
hb = box(0, L, 0, 10, 0, 14)
shapes = [circle(x, zc, d) for x, d in zip(xs[:4], H_HOLES)] + [teardrop(x, zc, d) for x, d in zip(xs[4:], H_HOLES)]
for s in shapes:
    hb -= prism_y(s, -1, 11)
hb -= vnotch(3, 0, 0, 14)
parts["holes_horizontal"] = hb
# measure in the XZ plane: rotate so that Y becomes Z, slice at mid-depth
hb_r = hb.rotate([-90, 0, 0])       # (x, y, z) -> (x, z, -y): mid-depth y=5 -> z=-5
for i, (x, d) in enumerate(zip(xs, sizes)):
    tear = i >= 4
    w, h, a = void_dims_z(hb_r, x - d / 2 - 2, x + d / 2 + 2, zc - d / 2 - 1, zc + d, -5.0)
    want_h = d / 2 + (d / 2 * math.sqrt(2) if tear else d / 2)
    check(f"holes_horizontal: {'teardrop' if tear else 'round'} {d} is {d} wide, {want_h:.2f} tall",
          abs(w - d) < 0.005 and abs(h - want_h) < 0.005, (round(w, 3), round(h, 3)))
check("holes_horizontal: control, a teardrop is taller than the round hole of the same size",
      void_dims_z(hb_r, xs[4] - 4, xs[4] + 4, zc - 3, zc + 6, -5.0)[1] >
      void_dims_z(hb_r, xs[0] - 4, xs[0] + 4, zc - 3, zc + 6, -5.0)[1] + 0.5, "")

# 3. pilot ladder: 10 mm deep, vertical, a wider gap between the ~2 mm group and the M3 group.
xs = spread(PILOTS[:4], 5, 5) + [x + 0 for x in spread(PILOTS[4:], 0, 5)]
off = xs[3] + PILOTS[3] / 2 + 8 - (xs[4] - PILOTS[4] / 2)
xs = xs[:4] + [x + off for x in xs[4:]]
L = xs[-1] + PILOTS[-1] / 2 + 5
pb = box(0, L, 0, 10, 0, 10)
for x, d in zip(xs, PILOTS):
    pb -= vhole(x, 5, d, 10)
pb -= vnotch(2, 0, 0, 10)
parts["pilots"] = pb
for x, d in zip(xs, PILOTS):
    w, dp, a = void_dims_z(pb, x - d / 2 - 1.5, x + d / 2 + 1.5, 5 - d / 2 - 1.5, 5 + d / 2 + 1.5, 5.0)
    check(f"pilots: {d}", abs(w - d) < 0.005, round(w, 3))
check("pilots: sizes ascend from the notched end", PILOTS == sorted(PILOTS) and xs == sorted(xs), xs)

# 4. peg and fit ladder. Peg stands up: 0.4 chamfer at the foot (elephant's foot), 0.6 lead-in at the top.
peg = M.cylinder(14 - 0.6, PEG / 2, PEG / 2, FN) + M.cylinder(0.6, PEG / 2, PEG / 2 - 0.6, FN).translate([0, 0, 13.4])
peg = (peg - M.cylinder(0.4 + 1, PEG / 2 + 1.4, PEG / 2, FN).translate([0, 0, -1])) + \
    M.cylinder(0.4, PEG / 2 - 0.4, PEG / 2, FN)
parts["fit_peg"] = peg
fit_d = [PEG + c for c in FIT]
xs = spread(fit_d, 6, 5)
L = xs[-1] + fit_d[-1] / 2 + 6
fp = box(0, L, 0, 14, 0, 6)
for x, d in zip(xs, fit_d):
    fp -= vhole(x, 7, d, 6, CHAMFER)
fp -= vnotch(3, 0, 0, 6)
parts["fit_plate"] = fp
for x, d in zip(xs, fit_d):
    w, _, _ = void_dims_z(fp, x - d / 2 - 1.5, x + d / 2 + 1.5, 0.5, 13.5, 3.0)
    check(f"fit_plate: hole {d:.1f}", abs(w - d) < 0.005, round(w, 3))
w, _, _ = void_dims_z(peg, -5, 5, -5, 5, 7.0)
pw = bbox(peg)[1][0] - bbox(peg)[0][0]
check("fit_peg: 6.0 across at mid-height", abs(pw - PEG) < 0.005, round(pw, 3))
# the peg modelled in each hole: the -0.1 hole collides, every other one clears (control and check in one)
hits = [vol(peg.translate([x, 7, 0.0]) ^ fp) > 1e-6 for x in xs]
check("fit_plate: modelled peg collides only with the interference hole", hits == [c < 0 for c in FIT], hits)

# 5. tab and slot ladder. Slots run along Y, 12 long; the tab is printed flat, 3.0 thick in Z.
slot_w = [TAB + c for c in SLOT]
xs = spread(slot_w, 7, 6)
L = xs[-1] + slot_w[-1] / 2 + 7
sp = box(0, L, 0, 18, 0, 8)
for x, w in zip(xs, slot_w):
    sp -= box(x - w / 2, x + w / 2, 3, 15, -1, 9)
sp -= vnotch(3, 0, 0, 8)
parts["slot_plate"] = sp
parts["slot_tab"] = box(0, 30, 0, 11, 0, TAB)
for x, w in zip(xs, slot_w):
    ww, dd, _ = void_dims_z(sp, x - w / 2 - 1.5, x + w / 2 + 1.5, 1, 17, 4.0)
    check(f"slot_plate: slot {w:.1f}", abs(ww - w) < 0.005 and abs(dd - 12) < 0.005, (round(ww, 3), round(dd, 3)))
tab_up = parts["slot_tab"].rotate([0, -90, 0])      # stand the tab on end: its 3.0 thickness now runs along X
lo, hi = bbox(tab_up)
hits = [vol(tab_up.translate([x - (lo[0] + hi[0]) / 2, 3.5 - lo[1], -5 - lo[2]]) ^ sp) > 1e-6 for x in xs]
check("slot_plate: the tab stood in each slot touches none (0.0 is line-on-line)", not any(hits), hits)
fat = box(0, 30, 0, 11, 0, TAB + 0.15).rotate([0, -90, 0])
lo, hi = bbox(fat)
check("slot_plate: control, a tab 0.15 thicker hits the 0.0 and 0.1 slots",
      [vol(fat.translate([x - (lo[0] + hi[0]) / 2, 3.5 - lo[1], -5 - lo[2]]) ^ sp) > 1e-6 for x in xs][:3] ==
      [True, True, False], "")

for name in ["holes_vertical", "holes_horizontal", "pilots", "fit_peg", "fit_plate", "slot_plate", "slot_tab"]:
    solo(parts[name], name)

# ------------------------------------------------------------------ snap ladder

t, Lf, b, gap = SNAP["t"], SNAP["L"], SNAP["b"], SNAP["gap"]
hx, hy = SNAP["handle"]
cot = 1 / math.tan(math.radians(SNAP["ramp_deg"]))
xa = hx + Lf                              # catch face: the barb's root-side face
base_z = 2.0                              # keeper floor thickness; clips sit on it in the assembled frame


def clip(i, d):
    """Clip i (1-based) whose arm must bend d mm to pass the keeper's wall. Built in the assembled frame."""
    h = d + gap
    tip = xa + 1.0 + h * cot
    c2 = CS.square([hx, hy]) + CS.square([tip - hx, t]).translate([hx, hy - t])
    c2 += poly([(xa, hy), (xa, hy + h), (xa + 1.0, hy + h), (tip, hy)])
    r = 0.8                               # root fillet on the arm's inner corner
    c2 += CS.square([r, r]).translate([hx, hy - t - r]) - CS.circle(r, 48).translate([hx + r, hy - t - r])
    cl = c2.extrude(b).translate([0, 0, base_z])
    for k in range(i):                    # i notches on the handle's back face (x = 0)
        cl -= box(-0.5, 0.8, 1.2 + 1.6 * k, 1.2 + 1.6 * k + 0.8, base_z - 1, base_z + b + 1)
    return cl, h


keeper = box(-2, 40, -4, hy + 6, 0, base_z)
keeper += box(-2, 40, -4, -gap, base_z, base_z + b)                    # lower guide wall
keeper += box(-2, xa - gap, hy + gap, hy + 6, base_z, base_z + b)      # upper wall: guide and catch
parts["snap_keeper"] = keeper
strains = {}
for i, d in enumerate(SNAP["defl"], 1):
    cl, h = clip(i, d)
    name = f"snap_clip_{i}"
    # closed: nothing touches; pulled back 1 mm the barb hits the wall (the lock); 0.1 mm does not (control)
    check(f"{name}: closed, clear of the keeper", vol(cl ^ keeper) < 1e-9, vol(cl ^ keeper))
    check(f"{name}: pulled back 1 mm, the barb hits the wall", vol(cl.translate([-1.0, 0, 0]) ^ keeper) > 1e-3, "")
    check(f"{name}: control, pulled back 0.1 mm, still clear", vol(cl.translate([-0.1, 0, 0]) ^ keeper) < 1e-9, "")
    # halfway in, the unbent clip overlaps the wall by exactly the deflection the arm must take
    ov = cl.translate([-10, 0, 0]) ^ keeper
    lo, hi = bbox(ov)
    defl = hi[1] - lo[1]
    check(f"{name}: halfway in, the arm must bend {d} mm", abs(defl - d) < 0.005 and lo[1] >= hy + gap - 1e-6,
          round(defl, 3))
    # the catch face from the geometry: the leftmost point of the clip above the arm's top face
    above = cl ^ box(-5, 60, hy + 0.05, hy + 10, -5, 20)
    L_meas = bbox(above)[0][0] - hx
    eps = 1.5 * t * defl / L_meas ** 2
    strains[name] = round(100 * eps, 2)
    check(f"{name}: strain {100 * eps:.2f} % (t {t}, deflection {defl:.2f}, length {L_meas:.2f})",
          abs(L_meas - Lf) < 0.005, round(L_meas, 3))
    # print each clip lying on its side as modelled (arm flat on the bed, bending in the layer plane)
    parts[name] = cl.translate([0, 0, -base_z])
    solo(parts[name], name)
# the assembled picture: clip 3 closed in the keeper, in the assembled frame (render_coupons.py)
write_stl(keeper, OUT / "assembled__snap_keeper.stl")
write_stl(clip(3, SNAP["defl"][2])[0], OUT / "assembled__snap_clip_3.stl")
check("snap ladder: strains ascend clip 1 to 5", list(strains.values()) == sorted(strains.values()), strains)
solo(keeper, "snap_keeper")

# ------------------------------------------------------------------ lay out the plates and export

PLATES = {
    "fit_coupons": ["holes_vertical", "holes_horizontal", "pilots", "fit_plate", "slot_plate", "fit_peg", "slot_tab"],
    "snap_ladder": ["snap_keeper"] + [f"snap_clip_{i}" for i in range(1, 6)],
}
for plate, names in PLATES.items():
    y = 20.0
    x0 = 20.0
    placed = []
    for n in names:
        mf = parts[n]
        lo, hi = bbox(mf)
        if n in ("fit_peg", "slot_tab"):          # small parts go in a column on the right
            mf = mf.translate([140 - lo[0], (40 if n == "fit_peg" else 60) - lo[1], 0])
        else:
            mf = mf.translate([x0 - lo[0], y - lo[1], 0])
            y += (hi - lo)[1] + 6
        placed.append(mf)
        write_stl(mf, OUT / f"{plate}__{n}.stl")
    allp = M.batch_boolean(placed, m.OpType.Add)
    lo, hi = bbox(allp)
    check(f"{plate}: everything inside the {BED:.0f} mm bed with 5 mm to spare",
          lo[0] >= 5 and lo[1] >= 5 and hi[0] <= BED - 5 and hi[1] <= BED - 5, (lo.round(1).tolist(), hi.round(1).tolist()))
    check(f"{plate}: no two parts touch", len(allp.decompose()) == len(names), len(allp.decompose()))

(OUT / "report.json").write_text(json.dumps({"checks": report, "snap_strain_percent": strains}, indent=2))
print(f"{sum(r['ok'] for r in report.values())} checks pass; STLs in {OUT}")

# ------------------------------------------------------------------ package

if args.package:
    assert args.template and TEMPLATE.exists(), \
        f"--template missing or not found: {args.template!r} (save any A1 mini project with Generic PLA from Bambu Studio)"
    for plate, names in PLATES.items():
        dst = OUT / f"{plate}.3mf"
        cmd = ["uv", "run", "-q", "--with", "numpy", "--with", "numpy-stl", "--with", "trimesh", "python",
               str(BAMBU / "stl_to_bambu_3mf.py")]
        for n in names:
            cmd += ["--stl", str(OUT / f"{plate}__{n}.stl")]
        cmd += ["--settings", str(BAMBU / "presets" / "pla.md"), "--material", "PLA", "--plate-name",
                f"{plate} (PLA)", "--template", str(TEMPLATE), "--output", str(dst)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        assert r.returncode == 0 and "ALL CHECKS PASSED" in r.stdout, r.stdout[-2000:] + r.stderr[-2000:]
        with zipfile.ZipFile(dst) as z:
            items = {n: z.read(n) for n in z.namelist()}
        cfg = json.loads(items["Metadata/project_settings.config"])
        print(f"{plate}.3mf before the fix: slot 0 = {cfg['filament_settings_id'][0]!r}, "
              f"{cfg['filament_type'][0]} at {cfg['nozzle_temperature'][0]} C")
        cfg["filament_settings_id"][0] = "Generic PLA @BBL A1M"
        over = {"layer_height": "0.2", "enable_support": "0", "brim_type": "auto_brim"}
        cfg.update(over)
        diff = cfg["different_settings_to_system"]
        diff[0] = ";".join(sorted(set(n for n in diff[0].split(";") if n) | set(over)))
        items["Metadata/project_settings.config"] = json.dumps(cfg, indent=4).encode()
        tmp = dst.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for n, data in items.items():
                z.writestr(n, data)
        tmp.replace(dst)
        with zipfile.ZipFile(dst) as z:
            c = json.loads(z.read("Metadata/project_settings.config"))
        check(f"{plate}.3mf: slot 0 is PLA at 220 C",
              c["filament_type"][0] == "PLA" and c["nozzle_temperature"][0] == "220" and
              c["filament_settings_id"][0] == "Generic PLA @BBL A1M", (c["filament_type"][0], c["nozzle_temperature"][0]))
        check(f"{plate}.3mf: overrides stored and marked modified",
              all(c[k] == v for k, v in over.items()) and
              all(k in c["different_settings_to_system"][0].split(";") for k in over), over)
        print("ok", dst)
