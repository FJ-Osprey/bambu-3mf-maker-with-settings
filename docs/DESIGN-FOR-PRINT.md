# Design for FDM printing: the entry point

What a part designer needs that the slicer docs don't say: how to hold parts together, fits and holes, materials and
print orientation, screws and inserts, snaps and latches, glue, design for assembly, and what this printer (a Bambu A1
mini, 0.4 mm nozzle, 0.2 mm layers, PLA unless stated) does to a part. Read this page top to bottom before designing
anything that has to fit, hold or come apart; open the topic files below when a design needs their numbers.

**Add to these files in the same session you learn something**: a fit that worked or failed, a material number, a
mechanism rule, a slicer behaviour. Keep entries generic (this repo is public): what was measured, on what printer
and material, and what to do about it. Tooling and workflow live in `CLAUDE.md` in this repo (headless Blender,
manifold3d CSG, 3MF packaging, `bambu_sweep.py`, `gcode_features.py`). These files are the engineering side.

**How sure each number is.** Every number carries one of three tags:
- *settled*: several authoritative sources agree (manufacturer design guides, data sheets, tested lab data);
- *disputed*: sources disagree, or it is common practice that the literature contests; the range is given;
- *untested here*: one source only, or a published rule nobody has yet checked on this printer and filament.
Almost every *fit* number is *untested here* until the calibration coupons in section 8 come back measured. A
number from a guide written for another printer is a starting point for a coupon, never a final size.

## Topic files

| § | File | What is in it |
|---|---|---|
| 0 | this page | design for the builder (the checklist), how to hold two parts together, what is not yet measured |
| 1 | [fits and holes](design-for-print/1-fits-and-holes.md) | hole shrink by orientation, teardrops, counterbores, slicer hole compensation, clearances, press fits, coupons, reaming |
| 2 | [materials and orientation](design-for-print/2-materials-and-orientation.md) | PLA and PETG numbers, layer-line weakness, which way to lay a part, PLA vs PETG vs ASA/nylon, slicer settings for strength |
| 3 | [screws, inserts, nuts](design-for-print/3-screws-inserts-nuts.md) | pilot holes for self-tapping screws, heat-set inserts, nut traps, creep and preload |
| 4 | [micro servo](design-for-print/4-micro-servo.md) | coupling a printed part to an SG90/MG90S spline, mounting the case |
| 5 | [location, retention, latches](design-for-print/5-location-retention-latches.md) | every part needs a place to sit; snap-fit formulas and limits; hinges, dovetails, bayonets, magnets; checks per load direction |
| 6 | [adhesives](design-for-print/6-adhesives.md) | which glue for which plastic, joint shape, glue gap |
| 7 | [assembly and prototyping](design-for-print/7-assembly-and-prototyping.md) | part count, self-locating parts, one-way fits, insertion paths, tolerance stacks, the print-fit-revise loop |
| 8 | [this printer and the calibration coupons](design-for-print/8-printer-and-calibration.md) | elephant foot, compensation settings, supports and their scars, calibration, the coupon set to print and measure |
| 9 | [tools worth owning](design-for-print/9-tools.md) | what each tool enables, rough cost, what to ask the builder |

## 0. Design for the builder: walk this list before publishing any part

The person printing and assembling the part is not the person who modelled it, may be new to the vocabulary, and
has only what is on the bench. Every one of these was learned by getting it wrong on a live build (2026-10-28 and 10-29).

1. **Tools and hardware in hand only.** Ask what the builder has (drill? screws, which sizes? glue, which kinds?
   magnets? Velcro?) before designing anything that needs it. Never require drilling a printed part: holes are
   printed (the order below says when anything else is acceptable). Never *design around* screws, nuts, inserts or tools that were not confirmed in hand: ask first. Asking is not
   the same as withholding: recommending a tool or part is welcome (builders often want the advice and will buy it),
   so name it, say why, and let the builder decide. The servo's own bag of screws and a hot-glue gun are a safe
   baseline until they answer.
2. **Every part has a place to sit.** Name the printed feature it registers against (section 5). "Glue it where it
   lands" is not a design.
3. **What holds it, in each load direction**, and what lets it come out again (section 5). Anything that hides a
   mechanism gets a repeatable, tool-free closure.
4. **Assembly order and insertion path.** Build the sequence step by step and sweep each moving-in part along its
   path in the generator; a coupling that needs millimetres of travel to press together cannot be pressed in place.
5. **Already-printed parts are fixed.** When a shell is printed, locate and fasten new parts on features it already
   has (a hole, a rim, a lip, an existing cut-out); don't plan a reprint of a long part as the fix.
6. **Test pieces prove something,** are as stiff as what they stand for, and the instructions say what "right" looks
   like (section 1).
7. **Instructions in plain words**, every term defined the first time (spline, horn, pocket, coupon, lip, pilot), a
   labelled picture per mechanism, and a one-line answer to "what do I print now".
8. **Bought parts as they really are.** For every bought part the design touches (servo, motor, board, switch,
   battery), get photos of the unit in hand from every side and caliper the features the design meets; a drawing or
   data sheet is a starting point, and clones differ. List everything that leaves the part: cables and where exactly
   they exit, connectors and plugs, tabs, shafts, screw heads, and anything that needs a finger or a tool to reach.
   Model those too, bent the way they really bend, and sweep them along the insertion path with the body (item 4). A
   check that only proves a slot is empty passes while the cable beside it hits the wall. Place every cut for a cable
   from the photo, not where there is room.
9. **Agree the motion before the geometry.** Offer the builder two or three candidate motions (push on, slide in,
   twist, hinge), each written as the hands do it, and get their pick before any solid exists; the method is in
   section 5. A mechanism that passes every check can still be the wrong mechanism.
10. **A second reader before the print.** Write a one-page spec of each new mechanism (motion, sizes, what holds it,
    what was assumed) and have it reviewed by someone or something that did not design it, against the model and
    the photos, not against the plan. If the whole part takes more than about 20 minutes, print just the region that meets a bought part (a short slice with the
    pocket, the pilots and the cable path) and try the real part in it before printing the whole piece. Most
    problems found this way have no failing check.

## How to hold two parts together, most preferred first

Plan A is to print the part the way it is needed: holes printed in, locating features printed in, the latch printed
into the part. Work down this list and stop at the first rung that does the job; say in the design which rung was
chosen and why the ones above it did not fit.

1. **Don't have two parts.** Classic design for assembly (Boothroyd and Dewhurst) keeps a part separate only if it
   must move relative to its neighbour, must be a different material, or must come apart for assembly or service; if
   all three answers are no, merge them (*settled*: LibreTexts DFM course; Politecnico di Milano DfAM review, "part
   consolidation"). Printing makes merging cheaper still: a hinge or a captive pin can be **printed in place**, already
   assembled, with about 0.3 mm of gap between the moving surfaces (*disputed* 0.2-0.5 mm across guides, *untested
   here*; section 5). The opposite move is also legitimate: split a part when one piece would need supports on a
   mating face or a weak layer direction under load (Prusa KB, "splitting the model"), and then hold the pieces
   together with a rung below.
2. **A snap or latch printed into the parts**, or for a lid that opens often, **magnets in printed pockets**. No
   tools, no hardware for a snap; reusable if its catch face is 45° rather than 90°. Size the arm with the strain
   formula in section 5 and keep it within the material's limit. In PLA keep strain low (about 1-2 %), lay the arm
   flat on the bed so it bends along its layers, and don't leave it bent in service: PLA creeps (*settled* direction,
   numbers *disputed*). PETG takes about twice the strain. Magnets need buying (section 9).
3. **A press or interference fit**, ideally with crush ribs (thin ribs inside the hole that squash) rather than a
   plain round bore. It needs no hardware, but a printed press fit relaxes over weeks (PLA creeps), so it locates
   well and retains poorly; give it a second retainer if the load is sustained (section 1).
4. **A screw into a printed hole**: a self-tapping screw into a printed pilot, a nut in a printed trap, or a heat-set
   threaded insert (a brass insert melted into a printed hole with a soldering iron). All three holes are printed.
   Measured in PLA (CNC Kitchen): an M3 self-tapper pulls out at about 140 kg but strips at about 1 N·m and wears out
   after a few reassemblies; an insert holds 150-200 kg and survives reassembly; a nut in a bottom trap held 166 kg
   in PETG (*untested here*: one lab's trends; section 3). Correction (2026-10-29, review): the nut-trap figure is PETG, not PLA. Only design around screws, nuts or inserts the builder has confirmed.
5. **Glue, as the clamp, never the locator.** A printed feature (socket, tongue and groove, pins, a step) puts the
   parts in position; glue only stops them leaving. Then there is nothing to hold still while it cures. Best quick test
   numbers on PLA: CA about 10 MPa, 5-minute epoxy about 6 MPa (Prusa, one sample each; section 6). Glue peels far
   more easily than it pulls apart.
6. **Drilling: last resort, and only for a hole that could not be printed.** No source found recommends drilling a
   new hole in a print where printing it was possible; the guides print holes in and correct size with the slicer's
   hole compensation or a coupon (sources in section 1). The exceptions the sources do accept, and which are not the
   same thing as drilling a new hole: (a) **reaming** (opening a printed hole a few tenths with a reamer, or a drill bit
   turned by hand) to final size for a bearing seat, a dowel or a precise pin, "only where absolutely required"
   (Rahix; Syntax3D Lab; Hubs) (*mainstream*); (b) clearing a one-layer **sacrificial bridge** printed across a hole to
   avoid supports (section 1); (c) a part that is already printed and cannot reasonably be reprinted. Each needs the
   builder to have the tool, which section 0 says to ask about.

**Choosing by what the joint must do.** Never comes apart: rungs 1, 3 or 5. Comes apart now and then for service: a
45° snap, or a screw into a heat-set insert. Opens every day: magnets, a bayonet or a slide-on lid (section 5). Under
sustained load or heat: form, not friction (a ledge, a screw head on a floor, a hook behind a bar), and PETG over
PLA (section 2).

## Not yet measured on this printer

These are the numbers the rest of the files lean on that have not been checked on this A1 mini with this filament.
The calibration coupon set (section 8) measures the first five in one session with calipers; record the results here,
dated, with the coupon file's name, and move each line out of this list as it is measured.

- How much a printed hole shrinks, vertical axis, 2-6 mm (published 0.1-0.3 mm; one other printer measured 0.25).
- How a horizontal-axis hole comes out (taller or shorter than wide), round vs teardrop.
- Which clearance gives a slip, snug and press fit for a printed peg in a printed hole, and for a metal pin.
- Which slot width takes a printed tab freely.
- Which strain a flat-printed PLA snap arm survives repeatedly (published PLA "design strain" ranges from 1 % to 8 %).
- The right pilot for a ~2 mm self-tapping screw and for M3 (published 75-90 % of thread diameter).
- The heat-set insert hole on this printer (published: model 4.1-4.2 mm for an M3 insert; needs inserts in hand).
- Bambu Studio's current A1 mini defaults for `elefant_foot_compensation`, `xy_hole_compensation`,
  `xy_contour_compensation` (an old release note says elephant foot 0 for the A1 mini; read the values in the app).
- From earlier builds, single data points only: the micro-servo spline pocket (section 4) and the printed snap
  latch's preload (section 5).
