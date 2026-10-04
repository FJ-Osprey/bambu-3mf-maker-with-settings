# bambu — 3D printing (Bambu A1 Mini)

**This repo is public.** No personal or family details, photos, or names in anything committed.

## Read before designing or packaging a print

- Playbook `headless_blender_3d_design` (`~/.openclaw/workspace/memory/playbooks/`): headless Blender
  modeling, mesh hygiene (MANIFOLD booleans), preview renders, and pointers to the games-repo
  Blender tooling. Most of that tooling is Roblox round-trip handling; only the headless approach carries over.
- Playbook `bambu_3mf_workflow`: STL + settings markdown to a Bambu Studio `.3mf`.
- Worked examples: `pirate-shedletsky/generate.py`, `phone-kickstand/generate.py`.

## Tools

- Headless Blender: `/Applications/Blender.app/Contents/MacOS/Blender -b --python <script>.py`.
  STL has no units and Blender defaults to meters, so check sizes in mm.
- `stl_to_bambu_3mf.py` packages **one material per run**. Multicolor (AMS Lite) isn't supported
  yet: export one STL per color in a shared frame, import them together in Bambu Studio as a
  single object, and assign a filament to each part.
