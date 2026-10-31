# bambu — 3D printing (Bambu A1 Mini) and the design-for-print knowledge base

**This repo is public.** No personal or family details, photos, or names in anything committed.

This repo is where everything learned about designing parts for FDM printing is collected, for every project: the
rules, the measured numbers, and the **solved mechanisms** (`docs/design-for-print/10-solved-mechanisms.md`: joints,
latches, mounts and couplings already built and tried, with their numbers and failed versions). Sessions in other
repos are pointed here by a user-level rule and the `design-for-print` skill. Project files (part generators, 3MFs for
a specific build) live in their own repos, not here. One exception: `talkbot-head/` is a one-way export from a private project (its parts are attached to tagged GitHub Releases, not committed). Never edit it here; change the source and re-export.

## Read before designing or packaging a print

- Playbook `headless_blender_3d_design` (`~/.openclaw/workspace/memory/playbooks/`): headless Blender
  modeling, mesh hygiene (MANIFOLD booleans), preview renders, and pointers to the games-repo
  Blender tooling. Most of that tooling is Roblox round-trip handling; only the headless approach carries over.
- Playbook `bambu_3mf_workflow`: STL + settings markdown to a Bambu Studio `.3mf`.
- **`docs/DESIGN-FOR-PRINT.md`: the engineering rules, entry point.** Section 0 (design for the builder), the
  order for holding two parts together (print it in > snap > press fit > screw into a printed hole > glue as clamp >
  drill as last resort), what is not yet measured on this printer, and an index of the topic files in
  `docs/design-for-print/` (fits and holes, materials and orientation, screws and inserts, micro servo, snap fits and
  retention, adhesives, design for assembly, this printer and its calibration coupons, tools). Read it before designing
  a part that has to fit or hold something, and **add what you learn to the right topic file in the same session**: it
  is the one place design-for-print knowledge is collected (the playbooks above hold tooling and workflow). Public
  repo: generic wording, no project paths or personal details.
- **`personas/fdm-design-for-print-engineer_persona.md`**: the reviewing lens (how a design-for-print engineer
  questions a part, its standards of evidence, blind spots); research cache beside it. `/become-expert` framing for
  this repo: `.claude/become-expert-local.md`.
- **`calibration/`**: the calibration coupon set (`fit_coupons.py`, two 3MFs, labelled renders). The measuring sheet
  and the results table are in `docs/design-for-print/8-printer-and-calibration.md`.

## Tools

- Headless Blender: `/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>.py`.
  STL has no units and Blender defaults to meters, so check sizes in mm.
- **`blendercad.py`**: shared helpers for headless part generators. Import it instead of
  re-deriving them: rounded-edge slabs from 2D outlines, MANIFOLD booleans, one-solid engraving,
  pixel-art outlines with `unpinch()`, exact half-space cuts, STL export in mm, Workbench preview
  renders, `bbox_dims()`. Its docstring lists the traps each one avoids.
- Fold-out part on a friction hinge (knuckle clearance, swing bevel, preload tilt, print orientation): the rules are
  in `docs/design-for-print/10-solved-mechanisms.md`. The old example generators (a fold-out phone stand, a blocky
  figurine) were untracked on 2026-10-30 and stay in git history: `git log --oneline -- phone-kickstand`, then
  `git show <that commit>~1:phone-kickstand/generate.py`.
- **`bambu_sweep.py`**: measures how settings change a project's print time. It edits a 3MF's
  settings, slices it headlessly with the Bambu Studio CLI, and checks the gcode to confirm each
  override took. Use it before guessing which setting to change for speed. `--write` bakes
  overrides into a copy of the original 3MF. Include a positive control (e.g. `layer_height=0.28`).
  One measurement so far (a 4-color, 205-layer figurine, 2026-10-04): 364 swaps took ~10 of 13 h,
  about 99 s each. Most of that is fixed swap overhead (cut, chute, wipe). Flush tuning saved
  25–60 min. Fewer layers (thicker) or fewer colors per layer saved hours.
- **`gcode_features.py`**: reads a sliced `plate_1.gcode` (what `bambu_sweep.py --workdir` keeps): feature
  counts, extrusion extent against the bed (brim included), and where the supports are by radius, height and
  angle sector. Run it before changing geometry to kill a support: it tells you what the support props up.
- **Geometry without Blender**: `uv run --with manifold3d --with numpy python gen.py` gives exact booleans and
  volume/bbox assertions as fit checks, with Blender used only for the renders (`blendercad.py` from the
  exported STLs). Worked example and traps: playbook `headless_blender_3d_design`, "CSG in Python with manifold3d".
- `stl_to_bambu_3mf.py` packages **one material per run**. Multicolor (AMS Lite) isn't supported
  yet: export one STL per color in a shared frame, import them together in Bambu Studio as a
  single object, and assign a filament to each part.
- **Known bug (2026-10-04): don't print a 3MF from `stl_to_bambu_3mf.py` without checking
  the filament slot.** The object goes on extruder 1. Slot 1 gets the material's preset *name*,
  but keeps the template's type and temperatures (TPU, 220 °C). The tool's checker still reports
  PASS. Fix prompt: `prompts/fix-3mf-filament-slot-mismatch.md` (gitignored, mini only). Until it's
  fixed, open the STL in Bambu Studio and pick the filament profile by hand.
