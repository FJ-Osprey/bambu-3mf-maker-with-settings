# 3. Screws, heat-set inserts and nut traps

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*. This is rung 4 of
"how to hold two parts together": every hole here is printed. Design around a screw, nut or insert only once the
builder has confirmed it is in hand (section 0).

## Which one

Measured pull-out in printed PLA and PETG (CNC Kitchen; M3; Prusa printers, 100 % infill, so treat as trends):

| Method | Pull-out | Torque before it strips or turns | Reassembly | Notes |
|---|---|---|---|---|
| Self-tapping screw into a printed pilot, PLA | about 140 kg (2.7 mm hole) | about 1 N·m | a few times, then the thread is gone | no extra parts |
| Same, PETG | about 118 kg | about 1 N·m | same | |
| Heat-set insert, PLA | 150-205 kg across tests | (PETG test: 3 N·m) | many | needs a soldering iron and inserts |
| Heat-set insert, PETG | about 119 kg | 3 N·m | many | the gain in PETG is torque, not pull-out |
| Nut in a trap open at the bottom, PETG | 166 kg | 2 N·m (plastic crushed under the nut) | many | nuts fall out during assembly |
| Nut in a trap open at the side, PETG | 86 kg | | many | weaker than the bottom trap |
| Thread-repair coil (Helicoil) | same as a bare screw | 1 N·m | | adds nothing |

So: a self-tapping screw into a printed pilot for something assembled once or twice; a heat-set insert for anything
taken apart repeatedly or tightened hard; a nut trap when there are nuts but no inserts.

## Self-tapping screws into a printed pilot

- **Pilot diameter**: 75-90 % of the screw's thread diameter, modelled (*disputed*: guides say 75-85 %; CNC Kitchen
  tested M3 at 2.7 mm, 90 %, and got 140 kg). The printed hole shrinks a little more, which is the right direction.
  Orient pilots vertical in the print where you can (roundest holes). Print a pilot ladder (section 8) and pick the
  smallest the screw starts in by hand. For the 1.8-1.9 mm screws in a micro-servo bag, 1.6-1.7 mm modelled is the
  starting range. If the chosen pilot is too tight on the day, open the printed hole by hand with a bit of the pilot
  size (reaming a printed hole, section 1); don't design on the assumption that a drill will be used.
- **Depth**: screw length minus everything it passes through, plus 1 mm. A screw that bottoms out before its head
  clamps strips the PLA or snaps; the fix on the day is a washer under the head.
- **Wall round a pilot**: 2 mm or more where possible. Next to a pocket that holds the screwed part it can be less
  (a micro servo's tab holes are only about 2 mm from its case, so the bracket wall between pilot and pocket is about
  0.9 mm by construction); the part in the pocket backs the wall.
- **Snug, not cranked.** The clamp force creeps away anyway; the thread holds by form. Repeated in and out damages the
  thread ("screw a bolt straight into a 3D printed part a few times and the thread is gone", CNC Kitchen).
- **Screws made for plastic** (thread-forming "PT" style, 30° flank) are designed for reuse in moulded plastics, with
  pilots of 0.75-0.85 × the thread diameter and engagement about 2 × (PSM data); no printed-PLA data found
  (*untested here*). Crush ribs in the hole that an ordinary screw forms threads in are another option (Rahix).

## Heat-set inserts

- **Hole**: the insert maker's hole is for a hole that comes out exactly that size. For an M3 insert with a 4.0 mm
  datasheet hole, model about 4.1-4.2 mm so the printed hole lands at 4.0-4.1; pull-out falls off sharply once the
  finished hole passes 4.1-4.2 (CNC Kitchen 2026: 4.2 mm modelled gave about 90 % of the maximum, about 1400 N;
  asked3d: 4.1) (*settled* method, size *untested here*: print a 4.0-4.4 ladder). Smaller inserts: add 0.2-0.3 mm.
- **Depth**: blind holes about 1 mm deeper than the insert; straight walls, no taper, usually no chamfer.
- **Wall**: about 1.6 mm round an M3 insert (1.3 mm M2) by the insert maker's table, seen only as a search extract
  (*untested here*); plenty of walls and infill round it, since the plastic must not fail before the insert.
- **Install**: soldering iron 10-20 °C above the print temperature (about 225 °C PLA, 245 °C PETG), with an insert
  tip; melt to about 90 % depth, then press flush with a flat tool and hold a few seconds (CNC Kitchen "Tips and
  tricks"). Inserts are poor for a screw coming in from the other side: molten plastic fills the hole below.

## Nut traps

- A hexagonal pocket, printed, open at the bottom of the load path, holds better than a side slot (166 vs 86 kg).
  Nuts fall out during assembly; a pocket a hair tight, or a pause in the print to drop the nut in and print over it,
  fixes that (Rahix; the print pause is a slicer feature).
- A pocket printed upright ends in an overhang; one bridging layer closes it (section 1, sacrificial bridge).

## Creep and preload

- Printed plastic creeps under a screw head: an M6 joint in PLA lost 3 % of its tightening torque in 7 days, PETG
  11.5 % (one study, Ender-3, 100 % infill) (*disputed*: single study with internal inconsistencies). Short screws in
  thin plastic lose a larger share, because nearly all the preload is stored by squashing the plastic, not by
  stretching the screw (Jönköping University machine-elements notes, a calculation).
- Countermeasures: a washer under the head (a 7 mm washer under an M3 head about doubles the bearing area; Correction (2026-10-29, review): "nearly triples" did not survive the arithmetic), the longest screw
  that fits, a metal compression sleeve where the load is high (*settled* engineering practice; no printed-part tests).

## Sources

CNC Kitchen: "Are our heat-set insert datasheets wrong?" (2026), "Tips & tricks for heat-set inserts", "Threaded
inserts, cheap vs expensive" (2019), "Helicoils vs threaded inserts vs embedded nuts" (2020), "Threaded inserts in
resin prints"; asked3d.com M3 insert hole; Rahix design guide; Jönköping University "Bolted joints" (mechanics.ju.se);
PSM Fasteners PT series; MDPI Polymers 2021, 13, 4132 (accelerated ageing and bolt preload).
