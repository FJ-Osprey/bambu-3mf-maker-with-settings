# Tools guide

What each tool is, what to say to use it, its options, where it lives. Append-only.

## gcode_features.py (added 2026-10-26)
What a sliced plate_1.gcode contains: feature counts, whether every extrusion (brim included) fits the bed, and where the supports are by radius, height and 15-degree sector, so a stray support cluster can be traced to the feature it holds up.
Say: "check the sliced gcode for stray supports / does it fit the bed". Options: `--bed 180` (bed size), `--r-outside 80` (report supports farther than this from the part's centre, by sector).
Lives at `bambu/gcode_features.py`; input is the gcode `bambu_sweep.py --workdir <dir>` leaves in `<dir>/<variant>/plate_1.gcode`.
