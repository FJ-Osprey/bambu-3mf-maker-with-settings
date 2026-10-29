"""
render_coupons.py -- top-down pictures of the two coupon plates, labelled, for the measuring sheet.

    /Applications/Blender.app/Contents/MacOS/Blender -b --python calibration/render_coupons.py
    uv run --with pillow python calibration/render_coupons.py --label

Run fit_coupons.py first (it writes the STLs). The first command renders calibration/renders/<plate>_raw.png with an
orthographic camera looking straight down, so a bed coordinate maps linearly to a pixel; the second writes the
labelled <plate>.png from it. The labels' positions are the parts' bed coordinates from the STLs.
"""

import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT, REN = HERE / "out", HERE / "renders"
RES, VIEW = 1200, 180.0          # px, mm across the picture: the whole bed
AX0, AY0, AVIEW = -6.0, -14.0, 50.0   # the assembled close-up: lower-left corner and width, mm
PLATES = {"fit_coupons": ["holes_vertical", "holes_horizontal", "pilots", "fit_plate", "slot_plate", "fit_peg",
                          "slot_tab"],
          "snap_ladder": ["snap_keeper"] + [f"snap_clip_{i}" for i in range(1, 6)]}
LABELS = {
    "holes_vertical": "A  holes, axis up: 2 / 2.5 / 3 / 4 / 5 / 6",
    "holes_horizontal": "B  holes on their side: round 3-6, then teardrop 3-6",
    "pilots": "C  screw pilots: 1.5 1.6 1.7 1.8 | 2.4 2.6 2.8",
    "fit_plate": "D  peg holes: 5.9 6.0 6.1 6.2 6.3 6.4 6.5",
    "slot_plate": "E  tab slots: 3.0 3.1 3.2 3.3 3.4 3.5",
    "fit_peg": "D peg",
    "slot_tab": "E tab",
    "snap_keeper": "keeper (the channel)",
}
for i, s in enumerate(["0.7", "1.4", "2.1", "2.8", "3.6"], 1):
    LABELS[f"snap_clip_{i}"] = f"clip {i}: {i} notch{'es' if i > 1 else ''}, {s} % strain"


def stl_bbox(path):
    data = Path(path).read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    xs, ys = [], []
    for k in range(n):
        v = struct.unpack("<12f", data[84 + 50 * k: 84 + 50 * k + 48])[3:]
        xs += v[0::3]
        ys += v[1::3]
    return min(xs), max(xs), min(ys), max(ys)


if "--label" in sys.argv:
    from PIL import Image, ImageDraw, ImageFont
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except OSError:
        font = ImageFont.load_default()
    px = lambda x, y: (x / VIEW * RES, (VIEW - y) / VIEW * RES)
    for plate, names in PLATES.items():
        im = Image.open(REN / f"{plate}_raw.png").convert("RGB")
        d = ImageDraw.Draw(im)
        for n in names:
            x0, x1, y0, y1 = stl_bbox(OUT / f"{plate}__{n}.stl")
            if n in ("fit_peg", "slot_tab"):
                at = px(x0, y1 + 1.5)
                at = (at[0], at[1] - 26)
            elif n.startswith("snap_clip"):
                at = px(x1 + 3, (y0 + y1) / 2)
            else:
                at = px(x0, y1 + 1.5)
                at = (at[0], at[1] - 26)
            d.text(at, LABELS[n], fill=(20, 20, 20), font=font)
        foot = {"fit_coupons": "smallest size at the notched end of each strip; B's holes run through the 10 mm side",
                "snap_ladder": "clip number = notches on its back; push a clip arm-first into the keeper until it clicks"}
        d.text((20, RES - 40), foot[plate], fill=(20, 20, 20), font=font)
        im.save(REN / f"{plate}.png")
        print("wrote", REN / f"{plate}.png")
    im = Image.open(REN / "snap_assembled_raw.png").convert("RGB")
    d = ImageDraw.Draw(im)
    pa = lambda x, y: ((x - AX0) / AVIEW * RES, (AY0 + AVIEW - y) / AVIEW * RES)
    for (x, y), s in [((-1, 18), "keeper wall: the barb rides along it, bending the arm"),
                      ((22, 14.5), "barb clicks past the wall's end"),
                      ((0, -7), "push the clip this way (to the right) into the channel"),
                      ((22, 8.5), "to release: press the arm tip down, pull back")]:
        d.text(pa(x, y), s, fill=(20, 20, 20), font=font)
    im.save(REN / "snap_assembled.png")
    print("wrote", REN / "snap_assembled.png")
    sys.exit(0)

sys.path.insert(0, str(HERE.parent))
import bpy  # noqa: E402
from blendercad import clear, camera, setup_render, render, color  # noqa: E402

REN.mkdir(exist_ok=True)
COL = {"snap_keeper": (0.35, 0.45, 0.6)}
for plate, names in PLATES.items():
    clear()
    for n in names:
        bpy.ops.wm.stl_import(filepath=str(OUT / f"{plate}__{n}.stl"))
        ob = bpy.context.selected_objects[0]
        color(ob, COL.get(n, (0.95, 0.8, 0.15)))
    camera((VIEW / 2, VIEW / 2, 300), (VIEW / 2, VIEW / 2, 0), ortho=VIEW)
    setup_render((RES, RES))
    render(REN / f"{plate}_raw.png")
clear()
for n, c in [("snap_keeper", (0.35, 0.45, 0.6)), ("snap_clip_3", (0.95, 0.8, 0.15))]:
    bpy.ops.wm.stl_import(filepath=str(OUT / f"assembled__{n}.stl"))
    color(bpy.context.selected_objects[0], c)
camera((AX0 + AVIEW / 2, AY0 + AVIEW / 2, 300), (AX0 + AVIEW / 2, AY0 + AVIEW / 2, 0), ortho=AVIEW)
setup_render((RES, RES))
render(REN / "snap_assembled_raw.png")
