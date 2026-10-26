#!/usr/bin/env python3
"""
gcode_features.py -- what a sliced Bambu plate_1.gcode actually contains: feature block counts, the XY extent of
every extrusion (does it fit the 180 x 180 bed, brim included), and WHERE the supports are, by radius, height
and angle around the part. Use it to find out what a stray support cluster is holding up before changing geometry.

    python3 gcode_features.py plate_1.gcode [--bed 180] [--r-outside 80]

Reads the gcode bambu_sweep.py leaves in its --workdir (<workdir>/<variant>/plate_1.gcode).

Why it exists (2026-10-26, Verity head): a rim-down hemisphere showed supports outside its rim. The guess was the
rim joint's 1.5 mm step; a 45-degree chamfer changed nothing. Bucketing the support points by angle showed they
were all in one 15-degree sector: the cable hole's arch. Angle + height tells you what is being propped; a count
alone doesn't.
"""

import argparse
import collections
import math
import re
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gcode")
    ap.add_argument("--bed", type=float, default=180.0, help="bed size (square), mm")
    ap.add_argument("--r-outside", type=float, default=None,
                    help="report support points farther than this from the part's outer-wall centroid")
    a = ap.parse_args()

    feat = None
    z = 0.0
    counts = collections.Counter()
    xs, ys = [], []
    walls, sup, brim = [], [], []
    rx = re.compile(r"X([\d.-]+)")
    ry = re.compile(r"Y([\d.-]+)")
    rz = re.compile(r"Z([\d.-]+)")
    re_ = re.compile(r"E([\d.-]+)")
    arcs = 0
    for line in open(a.gcode, errors="replace"):
        if line.startswith("; FEATURE:"):
            feat = line.split(":", 1)[1].strip()
            counts[feat] += 1
            continue
        line = line.split(";", 1)[0]
        if line.startswith("G2") or line.startswith("G3"):
            me = re_.search(line)
            if me and float(me.group(1)) > 0:
                arcs += 1
            continue
        if line.startswith("G1") or line.startswith("G0"):
            mz = rz.search(line)
            if mz:
                z = float(mz.group(1))
            me = re_.search(line)
            if not me or float(me.group(1)) <= 0:      # travel, retract or wipe
                continue
            mx, my = rx.search(line), ry.search(line)
            if not (mx and my):
                continue
            p = (float(mx.group(1)), float(my.group(1)), z)
            xs.append(p[0])
            ys.append(p[1])
            if feat == "Outer wall":
                walls.append(p)
            elif feat and feat.startswith("Support"):
                sup.append(p)
            elif feat == "Brim":
                brim.append(p)

    print("feature blocks:", ", ".join(f"{k} {v}" for k, v in counts.most_common()))
    if arcs:
        print(f"WARNING: {arcs} G2/G3 arc extrusions ignored (arc fitting is on); extents and centroid undercount")
    if not xs:
        sys.exit("no extrusion moves found")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    fits = x0 >= 0 and y0 >= 0 and x1 <= a.bed and y1 <= a.bed
    print(f"extrusion extent X {x0:.1f}..{x1:.1f}  Y {y0:.1f}..{y1:.1f}  "
          f"({'fits' if fits else 'DOES NOT FIT'} a {a.bed:.0f} mm bed)")
    if brim:
        bx = [p[0] for p in brim]
        by = [p[1] for p in brim]
        print(f"brim: {len(brim)} pts, extent X {min(bx):.1f}..{max(bx):.1f}  Y {min(by):.1f}..{max(by):.1f}")
    if not walls:
        print("no outer-wall moves; skipping support geometry")
        return
    cx = sum(p[0] for p in walls) / len(walls)
    cy = sum(p[1] for p in walls) / len(walls)
    print(f"outer-wall centroid ({cx:.1f}, {cy:.1f}), part height {max(p[2] for p in walls):.1f}")
    if not sup:
        print("supports: none")
        return
    rs = [math.hypot(p[0] - cx, p[1] - cy) for p in sup]
    print(f"supports: {len(sup)} pts, r up to {max(rs):.1f}, z {min(p[2] for p in sup):.2f}..{max(p[2] for p in sup):.2f}")
    byr = collections.defaultdict(lambda: [0, 0.0])
    for p, r in zip(sup, rs):
        b = byr[int(r // 10) * 10]
        b[0] += 1
        b[1] = max(b[1], p[2])
    print("  by radius (r bucket: pts, max z):", ", ".join(f"{k}-{k + 10}: {v[0]}, {v[1]:.1f}" for k, v in sorted(byr.items())))
    if a.r_outside is not None:
        out = [(p, r) for p, r in zip(sup, rs) if r > a.r_outside]
        print(f"  outside r > {a.r_outside:.0f}: {len(out)} pts")
        if out:
            sec = collections.defaultdict(lambda: [0, 0.0])
            for p, r in out:
                k = int(math.degrees(math.atan2(p[1] - cy, p[0] - cx)) // 15 * 15)
                sec[k][0] += 1
                sec[k][1] = max(sec[k][1], p[2])
            print("    by 15-degree sector (deg: pts, max z):",
                  ", ".join(f"{k}: {v[0]}, {v[1]:.1f}" for k, v in sorted(sec.items())))
            print("    one or two sectors = a local feature (a hole's arch, a boss); all sectors = the rim itself")


if __name__ == "__main__":
    main()
