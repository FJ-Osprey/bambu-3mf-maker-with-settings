# 1. Fits, holes and tolerances

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here* (defined there).
"Diametral" means the total gap across a diameter; "per side" is half of it. Guides mix the two, so every number
below says which.

## Printed holes

- **Printed holes come out smaller than modelled.** The extruded bead is pushed inward and a circle is sliced as a
  polygon inside the true circle. Measured: 0.25 mm under on a Prusa CORE One L in PLA (CNC Kitchen 2026), 0.1 mm
  under on a Prusa Mk2.5 (CNC Kitchen 2019); guides give 0.1-0.3 mm for 2-6 mm holes (*settled* that they shrink,
  amount *untested here*). The seam (where each layer starts) can add a local bump of a few tenths.
- **Vertical-axis holes** (axis up, the hole is a ring in every layer) are the roundest and most accurate; put holes
  that must fit with their axis vertical where the part allows (*settled*).
- **Horizontal-axis holes** sag at the top of the arc, where each layer bridges over the hole, so they come out
  shorter top to bottom than side to side. Give them a pointed top: a **teardrop** (the circle plus a 45° point on
  top, i.e. a 90° included angle, so every overhang is printable without supports) for small holes, or a flat roof
  for large ones (a 10 mm hole with the roof 0.4 mm above the circle) and expect the roof to droop onto the shaft
  (Rahix "Design for 3D printing"; Syntax3D Lab) (*settled* for the teardrop, roof number *untested here*).
- **The slicer's hole compensation.** Bambu Studio's `xy_hole_compensation` grows every closed hole outline by the
  value entered, **per side**, so the diameter grows by twice it: a hole printing 0.15 mm small wants 0.075, not 0.15
  (Bambu wiki, XY hole/contour compensation; Premy, checked against the Bambu Studio source) (*settled*). It only
  sees holes that are closed rings in a layer: horizontal holes, slots open to an edge and cross-holes get nothing,
  so those are fixed in the model. Compensate in the model or in the slicer, never both. Bambu's calibration
  procedure measures printed holes against known metric screws (M6 gives the best reading; an M6 hole printed at
  5.66 mm, 0.24 mm under, in Bambu's own example) and is per filament. `xy_contour_compensation` does the same to
  outer outlines only.
- **First-layer squish closes small holes.** A 1.5 mm round hole on the first layer can close under elephant's foot
  (the first layer spreading wider than the rest); 2.0 mm holes stayed open (measured here). Slots survive better
  than round holes of the same width. Chamfer the bottom edge of any hole that has to take a pin from below
  (0.4-0.5 mm × 45°), and see section 8 for `elefant_foot_compensation`.
- **Counterbores printed upside down** (the wide part on the bed side) end in a step with nothing under it. Either
  print a one-layer **sacrificial bridge** across the narrow hole and cut it out afterwards (a knife or a drill bit
  turned by hand: it is one layer), or use the staged trick (one layer of crossed strips, then one layer with a square
  the width of the hole, then the round hole), which needs no cleanup but stops working on large diameters (Rahix
  R3.4-R3.5) (*untested here*).
- **Reaming a printed hole.** For a bearing seat, a dowel or a pin that must be exact, the sources accept printing the
  hole a few tenths small and reaming it to size, "only where absolutely required" (Rahix). Use a reamer or a drill
  bit turned slowly by hand; a bit under power wanders into the softer side and widens the hole off-centre (RepRap
  forum). Hubs' FDM guide says the same in a passage seen only as a search extract. Reaming is finishing a printed
  hole; it is not the same as drilling a hole that was never printed, which no source recommends when the hole
  could be printed (*mainstream*).

## Clearances and fits

Starting points to put on a coupon, not final sizes (*disputed* across guides by a factor of two, *untested here*):

| Fit | Diametral clearance (+) or interference (−) | Sources |
|---|---|---|
| Free running (a shaft that turns) | +0.4 to +0.5 mm | Syntax3D Lab; Hubs 0.5 for FDM |
| Sliding (a lid on a rail) | +0.2 to +0.3 mm | Syntax3D Lab; UF makerspace via firstlayerlab 0.20-0.25 |
| Snug (locates, no play) | +0.15 to +0.2 mm | same |
| Light press (removable) | −0.05 to −0.1 mm | minicad; Syntax3D Lab |
| Permanent press | −0.1 to −0.2 mm | minicad; Weerg; mensa3d |
| Print in place (hinges) | +0.3 mm per gap start; 0.2 on a tuned printer | Prusa KB "at least 0.3 for moving parts"; Loftsmith; buildcad |

- **Outer edges print slightly large** (+0.05 to +0.15 mm) while holes print small, so a printed peg in a printed hole
  loses fit from both sides (x3dstudios; rapiddirect) (*settled* direction).
- **A printed press fit relaxes.** PLA creeps at room temperature; a press fit that is tight on day one is looser in a
  week to months (mechanics.ju.se creep chapter; Syntax3D Lab) (*settled* direction, no numbers). Use it to locate;
  retain with form (a lip, a screw head) or glue if the load lasts. Crush ribs (three or more thin ribs inside a
  slightly oversize bore, about 0.2 mm proud) make a press fit forgiving of print error: the ribs squash, the wall
  doesn't (Rahix R2.8-R2.10; grandpacad) (*untested here*). A hexagonal or square hole for a round pin does the same.
- **Wall round a press fit**: about 3 mm; under about 2.5 mm the bore splits along a layer line (minicad) (*untested
  here*). Chamfer the bore entry and the pin tip 0.5-1 mm.
- **Elastic range.** PLA yields at about 3 % strain and breaks at 7-12 % (section 2), so an interference that
  stretches a bore by more than about 1 % of its diameter is into yield: it creeps or deforms rather than springing
  back, and a thin hub can split. Teeth cutting grooves into a bore (a spline, a knurl) is fine; stretching a hub over
  a round shaft by 0.3 mm is not. For a toothed shaft, size the bore between the root and the tip diameter so only
  the teeth bite.
- **Tolerances stack.** Four printed parts in a chain at ±0.2 mm each can be 0.8 mm off in the worst case (about 0.4
  typical). Locate every feature from one datum rather than chaining part to part, make one hole of a pair a slot, and
  keep mating features in the same plane, since Z is quantised to the layer height and XY is not (Layer X; CLT 3D;
  Syntax3D Lab) (*settled*). More in section 7.

## Coupons (test pieces)

- **Print a coupon in the same orientation as the feature,** with three or more sizes bracketing the guess, marked by
  notch counts (text in CSG is a chore; one, two, three notches is not). It costs ten minutes and saves the hour-long
  part. Several clearances on one coupon in 0.1 mm steps is the common practice (Syntax3D Lab; the3dai; Prusa KB on
  iterating) (*settled*). Worked examples: a three-width fit coupon (`phone-kickstand/generate.py`), the spline coupon
  in section 4, and the calibration set in section 8 (`calibration/fit_coupons.py`).
- **A coupon has to be as stiff as the feature it stands for, or it proves nothing.** An 8 mm tall ring sliced off a
  170 mm rim flexes in the hand, so pushing two such rings together tells you nothing about how the rigid halves
  will fit; the person holding them sees them squash and rightly asks what the test is for (2026-10-28). For a big
  joint, print the first half and trial-fit the other half's rim coupon on the real part, or accept that the halves
  themselves are the test. Say in the instructions what a coupon is and what result counts as right; the person
  printing it may never have heard the word.
- **Support nubs eat clearances.** Where tree supports touched, 0.2-0.5 mm nubs and pits remain. Keep anything that
  moves at least 1 mm from a supported surface, or write "scrape the wall flat, then dry-fit" into the assembly steps.

## Untested here: single data points

- **(2026-10-27, A1 mini, yellow PLA, 0.2 mm layers):** a 4.5 mm modelled hole with a horizontal axis, 3 mm long,
  took a 21-tooth metal micro-servo spline (about 4.8 mm across the tips) with hand force and held with no visible
  crack. The spline's root is near 4.4 mm, so this fit was stretching the hub as well as cutting grooves; the
  follow-up design uses 4.6 mm so only the teeth bite.

## Sources

CNC Kitchen, "Are our heat-set insert datasheets wrong?" (2026) and "Threaded inserts, cheap vs expensive" (2019);
Rahix, blog.rahix.de/design-for-3d-printing; Bambu Lab wiki, "XY hole/contour compensation"; premy.co, "Bambu Studio
XY hole compensation" (2026); Syntax3D Lab, "Tolerances and clearances guide" (2026); minicad.io tolerances guide;
firstlayerlab.com "3D printing tolerances"; x3dstudios and rapiddirect tolerance guides; Weerg interlocking parts;
grandpacad hole cheatsheet; Prusa KB "Modeling with 3D printing in mind"; Hubs "Key design considerations" and FDM
design guide; Loftsmith and buildcad.ai print-in-place hinge guides; mechanics.ju.se (Jönköping University) creep
chapter; Layer X and CLT 3D tolerance stack-up articles; RepRap forum thread "Holes too small" (2017).
