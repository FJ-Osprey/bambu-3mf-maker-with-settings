# 8. This printer (Bambu A1 mini) and the calibration coupons

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*.

## What the printer does to a part

- **Elephant's foot**: the first layer is squashed wider than the rest, because it is still soft and the layers above
  press on it. It matters most for anything that slides, snaps or takes a pin. Bambu Studio's
  `elefant_foot_compensation` shrinks the first layer to make up for it; an old release note gives the A1 mini default
  as 0 mm (A1 0.075, X1/P1 0.15) and the current wiki says only that the default suits general models (*untested
  here*: read the value in the app). Bambu's way to measure it: print a 25 × 25 × 10 mm cube at compensation 0, no
  brim, and with calipers measure the bottom edge and the top in X and Y at mid-side with light pressure; the
  compensation is the average of the two differences (e.g. 0.09 and 0.11 → 0.10). Run auto bed levelling and flow
  dynamics first; the value is per build plate (Bambu wiki, "Elephant foot") (*settled* procedure).
  The design fix needs no setting: a 0.4-0.5 mm × 45° chamfer on every bed edge that has to fit something (Hubs;
  Syntax3D Lab) (*settled*).
- **Hole and outline compensation**: `xy_hole_compensation` and `xy_contour_compensation`, both default 0, change
  holes and outer outlines by the entered value per side (section 1). Bambu calibrates them per filament, holes with
  known metric screws and outlines with Bambu's reusable spool (a 55 mm reference). Before changing them, rule out what
  mimics the same symptom: elephant's foot, wet filament, flow dynamics not calibrated, holes near nozzle size, no
  lead-in chamfer, the seam (Bambu wiki, "XY hole/contour compensation").
- **Filament shrinkage** (Bambu Studio's `Shrinkage` %) scales the outer X/Y size only and does not change holes;
  PLA shrinks about 0.3-0.5 %, PETG 0.2-1 % (third-party figures; Hubs: 0.2-1 % for FDM generally) (*disputed*,
  matters only for long parts: 0.4 % of 150 mm is 0.6 mm).
- **Accuracy**: no Bambu figure for the A1 mini; one owner reports under ±0.3 mm in PLA. Treat ±0.2 mm in XY as
  normal and Z as whole layers (*untested here*).
- **Flow dynamics** (pressure advance, the K value): the A1 series calibrates it automatically since firmware
  01.04.00.00, sensing extrusion force at the wiper. Bambu notes the auto value can read higher than a manual one by
  design, to keep corners from bulging and parts fitting together. A partial clog or a third-party hotend gives a wrong
  K (Bambu wiki, "Flow dynamics calibration") (*settled*).
- **Materials on this printer**: PLA, PETG, TPU; Bambu does not recommend ABS, ASA, PC or nylon on the open-frame A1
  mini (section 2).

## Supports and the faces they touch

- Bambu Studio adds support under any surface flatter than its threshold (30° default, measured from the bed);
  Bambu's overhang guide says to support below 45°. Design so nothing needs it: chamfers instead of horizontal fillets
  on the bed side, 45° roofs, teardrop holes, bridges under about 5 mm (Hubs; Rahix; Bambu wiki "Support" and
  "Overhangs") (*settled*).
- **A support leaves a scar** (nubs and pits of 0.2-0.5 mm, measured here) on the face it touched. Put supported faces
  where nothing mates (choose the orientation for that), or keep anything that moves at least 1 mm from them, or
  plan "scrape flat, then dry-fit" in the assembly steps (*settled* principle). With support of the same filament,
  leave the top Z distance near 0.2 mm (Bambu wiki).
- **Which face goes on the bed**: the largest flat face, unless that puts a snap arm or a pulled feature across its
  layers (section 2) or a mating face on supports. Fit-critical holes with their axis vertical where possible.

## The calibration coupon set

Two plates that measure, on this printer and filament, the numbers section 1, 3 and 5 can only guess. Print them once
per filament (and again after a nozzle change). Generator, with its checks: `calibration/fit_coupons.py`; pictures:
`calibration/renders/` (`fit_coupons.png`, `snap_ladder.png`, `snap_assembled.png`).

| Plate | File | Time (slicer estimate) | Filament |
|---|---|---|---|
| Fit coupons | `calibration/out/fit_coupons.3mf` | about 1 h 30 min | about 28 g |
| Snap ladder | `calibration/out/snap_ladder.3mf` | about 26 min | about 6 g |

Both: PLA, 0.2 mm layers, no supports, auto brim. The 3MFs set filament slot 1 to Generic PLA at 220 °C; check the
slot shows the filament actually loaded before pressing print. Bambu Studio rearranges the parts on the plate; tell
them apart by shape and by the notch at the small end of each strip.

### What to measure, and where to write it

Tools: calipers. A set of drill bits makes a good set of gauge pins: the shank of a 3 mm bit is a 3 mm pin. The
inside jaws of the calipers (the small upper pair) read a hole's diameter; take two readings 90° apart.

- **A, holes with the axis up** (2, 2.5, 3, 4, 5, 6 mm): for each, the biggest drill shank that goes through, and the
  caliper reading for 4, 5 and 6. Gives the hole shrink and the `xy_hole_compensation` value (half the shrink).
- **B, holes on their side** (round 3-6, then teardrop 3-6): width and height of each with the inside jaws.
  Gives how much a horizontal hole sags and whether the teardrop keeps its round part round.
- **C, screw pilots** (1.5-1.8 for the ~2 mm screws in a servo bag; 2.4-2.8 for M3): which is the smallest a screw
  starts in by hand and drives home without the block cracking, and which strips. Record the screw.
- **D, peg in the peg holes** (holes 5.9-6.5 for the 6.0 peg): for each hole, one of *won't go*, *press* (goes in with
  a push and stays), *snug* (slides in, no wobble), *slides* (free, slight wobble), *loose*. Do the same with a 6 mm
  drill shank (a metal pin) if there is one.
- **E, tab in the slots** (slots 3.0-3.5 for the 3.0 tab): the same words for each slot.
- **Snap ladder** (clips 1-5, 0.7-3.6 % strain): push each clip arm first into the keeper's channel (picture) until it
  clicks, pull it out by pressing the arm tip toward the channel's middle, ten times. For each: clicked / held when
  pulled / turned white at the bend / cracked, and after how many cycles. The highest clip that survives ten cycles
  without whitening is this filament's working snap strain; the doc's guess for PLA is 1-2 %. The strains are
  computed with L = 13 mm, root to the catch face; full deflection is reached 1 mm further on, so the true strains are
  up to about 14 % lower, and at L/t ≈ 8 the formula is approximate (section 5): read the ladder as a ranking with
  rough values. Correction (2026-10-29, review): this caveat was missing.

Write the results in the table below (date, filament, the reading), then move each item off the "not yet measured"
list on the entry page, and change the starting numbers in sections 1, 3 and 5 to the measured ones, marked
"measured here".

### Results

| Date | Filament | Coupon | Reading | What it changes |
|---|---|---|---|---|
| — | — | — | not yet printed | — |
