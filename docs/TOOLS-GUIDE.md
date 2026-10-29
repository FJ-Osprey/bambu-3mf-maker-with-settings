# Tools guide

What each tool is, what to say to use it, its options, where it lives. Append-only.

## gcode_features.py (added 2026-10-26)
What a sliced plate_1.gcode contains: feature counts, whether every extrusion (brim included) fits the bed, and where the supports are by radius, height and 15-degree sector, so a stray support cluster can be traced to the feature it holds up.
Say: "check the sliced gcode for stray supports / does it fit the bed". Options: `--bed 180` (bed size), `--r-outside 80` (report supports farther than this from the part's centre, by sector).
Lives at `bambu/gcode_features.py`; input is the gcode `bambu_sweep.py --workdir <dir>` leaves in `<dir>/<variant>/plate_1.gcode`.

## calibration/fit_coupons.py (added 2026-10-29)
The calibration coupon set: hole shrink (vertical, horizontal, teardrop), screw-pilot ladder, peg-in-hole and tab-in-slot fit ladders, and a five-clip snap-strain ladder; 110 geometry checks with controls.
Say: "regenerate the calibration coupons" / "package the coupons". Options: `--package` (also the two 3MFs), `--template <A1 mini Generic PLA 3MF>` or env `BAMBU_PLA_TEMPLATE`, `--out <dir>`; sizes are the constants at the top.
Lives at `bambu/calibration/fit_coupons.py`; run `uv run --with manifold3d --with numpy python calibration/fit_coupons.py --package`; pictures: `calibration/render_coupons.py` (docstring has the two commands); what to measure: `docs/design-for-print/8-printer-and-calibration.md`.
