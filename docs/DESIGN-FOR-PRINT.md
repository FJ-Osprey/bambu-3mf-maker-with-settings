# Design for FDM printing: fits, PLA numbers, screws, servo couplings, retention

What a part designer needs that the slicer docs don't say. Collected from builds on a Bambu A1 mini (0.4 mm nozzle,
0.2 mm layers, PLA unless stated) and from published data sheets. **Add to this file in the same session you learn
something**: a fit that worked or failed, a material number, a mechanism rule, a slicer behaviour. Keep entries
generic (this repo is public): what was measured, on what printer and material, and what to do about it.

Tooling and workflow live elsewhere: `CLAUDE.md` in this repo (headless Blender, manifold3d CSG, 3MF packaging,
`bambu_sweep.py`, `gcode_features.py`). This file is the engineering side.

## 0. Design for the builder: walk this list before publishing any part

The person printing and assembling the part is not the person who modelled it, may be new to the vocabulary, and
has only what is on the bench. Every one of these was learned by getting it wrong on a live build (2026-10-28).

1. **Tools and hardware in hand only.** Ask what the builder has (drill? screws, which sizes? glue, which kinds?
   magnets? Velcro?) before designing anything that needs it. Never require drilling a printed part: holes are
   printed. Never specify screws, nuts or inserts that were not confirmed in hand. The servo's own bag of screws
   and a hot-glue gun are a safe baseline; everything else is a question.
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

## 1. Fits and tolerances

- **Printed holes come out smaller than modelled.** Rules of thumb from several tolerance guides: 0.1-0.3 mm under
  for a vertical-axis hole of 2-6 mm; horizontal-axis holes also sag at the top of the arc (the bridge), so they are
  shorter top-to-bottom than side-to-side. The amount depends on printer, material and the slicer's
  `xy_hole_compensation`, so for anything that has to fit, measure it or print a coupon.
- **Clearances (diametral, i.e. total gap, not per side):** slip fit about 0.3-0.5 mm; snug 0.2; press fit 0.1-0.3 mm
  of interference. Guides disagree on whether their numbers are per side or on the diameter: say which when writing
  one down.
- **Elastic range.** PLA yields at about 3 % strain and breaks at 7-12 % (section 2), so an interference that
  stretches a bore by more than about 1 % of its diameter is into yield: it creeps or deforms rather than springing
  back, and a thin hub can split. Teeth cutting grooves into a bore (a spline, a knurl) is fine; stretching a hub over
  a round shaft by 0.3 mm is not. For a toothed shaft, size the bore between the root and the tip diameter so only
  the teeth bite.
- **Print a coupon in the same orientation as the feature,** with three sizes bracketing the guess, marked by notch
  counts (text in CSG is a chore; one, two, three notches is not). It costs ten minutes and saves the hour-long part.
  Worked examples: a three-width fit coupon (`phone-kickstand/generate.py`) and the three-pocket spline coupon
  described below.
- **A coupon has to be as stiff as the feature it stands for, or it proves nothing.** An 8 mm tall ring sliced off a
  170 mm rim flexes in the hand, so pushing two such rings together tells you nothing about how the rigid halves
  will fit; the person holding them sees them squash and rightly asks what the test is for (2026-10-28). For a big
  joint, print the first half and trial-fit the other half's rim coupon on the real part, or accept that the halves
  themselves are the test. Say in the instructions what a coupon is and what result counts as right; the person
  printing it may never have heard the word.
- **Data point (2026-10-27, A1 mini, yellow PLA, 0.2 mm layers):** a 4.5 mm modelled hole with a horizontal axis,
  3 mm long, took a 21-tooth metal micro-servo spline (about 4.8 mm across the tips) with hand force and held with
  no visible crack. The spline's root is near 4.4 mm, so this fit was stretching the hub as well as cutting grooves;
  the follow-up design uses 4.6 mm so only the teeth bite.
- **Support nubs eat clearances.** Where tree supports touched, 0.2-0.5 mm nubs and pits remain. Keep anything that
  moves at least 1 mm from a supported surface, or write "scrape the wall flat, then dry-fit" into the assembly steps.
- **First-layer squish closes small holes.** A 1.5 mm round hole on the first layer can close entirely under
  elephant's foot; 2.0 mm holes stayed open. Slots survive better than round holes of the same width.
  `elefant_foot_compensation` and `xy_hole_compensation` are the slicer levers.

## 2. PLA numbers (published) and what to design with

| Source | Tensile | Modulus | Elongation | Flexural | Impact | Heat |
|---|---|---|---|---|---|---|
| Bambu PLA Basic, Bambu's TDS (X-Y / Z) | 35 ± 4 / 31 ± 3 MPa | (bending) 2750 ± 160 MPa | at break 12.2 ± 1.8 / 7.5 % | 76 ± 5 / 59 ± 6 MPa | Charpy unnotched 26.6 / 13.8 kJ/m², notched 7.9 | HDT 57 °C at 0.45 MPa |
| Prusament PLA, Prusa's TDS (horizontal / vertical XZ specimens) | yield 51 ± 3 / 59 ± 2 MPa | 2.3 / 2.4 GPa | at yield 2.9 / 3.2 % | 83 / 99 MPa | Charpy 13 / 14 kJ/m² | — |

Sources: Bambu PLA Basic technical data sheet (PDF linked from the store page; it gives X-Y and Z columns), Bambu
filament guide PDF (HDT), prusament.com PLA TDS 2021-10. Prusament's "vertical XZ" is a specimen standing on its
edge, not the across-layers case. Across layers on Bambu PLA Basic: tensile 89 % of X-Y, bending 78 %, elongation
60 %, impact about half. The community's "50-80 %" is right for bending and pessimistic for tensile on this material.
Put loads in-plane where you can; where one crosses layers, size for about 75 % and expect it to be more brittle.

For a back-of-envelope design check use: tensile 30 MPa, shear about 18 MPa (0.6 × tensile), bearing or compressive
about 50 MPa, modulus 2.5 GPa, and keep **sustained** stress under about 5-10 MPa because PLA creeps (a clamped
screw loses preload over days; a press fit relaxes). Form holds, friction doesn't: teeth, ledges, screw heads on
floors. PLA softens from about 55-60 °C (a car in the sun, a hot enclosure, a lamp); PETG for those. At
temperatures outdoors in autumn (0-10 °C) PLA is already glassy at room temperature, so expect slightly lower impact
strength and no change in fit.

## 3. Screws in PLA

- **Self-tapping pilot hole: 80-85 % of the screw's thread diameter**, modelled; the printed hole shrinks a little
  more, which is the right direction. For the 1.8-1.9 mm screws in a micro-servo bag, model 1.7 mm and say "drill to
  1.8 if it won't start". Orient pilots vertical in the print where you can (roundest holes).
- **Depth:** screw length minus everything it passes through, plus 1 mm. A screw that bottoms out before its head
  clamps strips the PLA or snaps; the fix on the day is a washer under the head.
- **Wall round a pilot:** 2 mm or more where possible. Next to a pocket that holds the screwed part it can be less
  (a micro servo's tab holes are only about 2 mm from its case, so the bracket wall between pilot and pocket is about
  0.9 mm by construction); the part in the pocket backs the wall.
- **Snug, not cranked.** The clamp force creeps away anyway; the thread holds by form. Repeated in and out damages the
  thread, so design for a few cycles or use heat-set inserts (not yet tried here).

## 4. Micro servo (SG90 / MG90S class): coupling the output and mounting the case

Vocabulary, for anyone new to servos: the **spline** is the toothed gear on the output shaft (metal on the MG90S,
plastic on the SG90), 21 teeth, about 4.7-4.8 mm across the tips and about 4 mm tall by the usual figures (no
manufacturer drawing dimensions it; measure yours), with a tapped hole down its centre for the **horn screw**. A **horn** is one of the plastic arms in the bag that press onto the spline. The bag
holds one horn screw, two longer tab screws (about 1.9 mm thread) and a few horns.

**Clone dimensions vary and the data sheets leave things out.** Measure before designing a mount: case length and
width, base to tab underside, tab thickness, width and tip-to-tip span, tab hole spacing (27.0 mm on one 2026 clone;
27.5 scaled from a drawing; no data sheet dimensions it), gear-housing top and spline top above the tabs, spline
diameter and height, where the lead leaves the case, and the three screws' lengths.

**Coupling a printed part to the spline, in order of preference:**

1. **Stock horn captured in a pocket**, screwed to the printed part through its outer holes, plus the horn screw.
   Strongest and the way commercial animatronics do it; needs the horn's dimensions, which vary by clone.
2. **Printed hub with a blind round pocket pressed onto the spline, plus the horn screw through the pocket floor.**
   The same joint as a stock horn, in PLA. Used on an animatronic jaw (2026-10-28, not yet printed and tested as
   this is written): hub 16 mm across and 6 mm thick, pocket 4.6 mm modelled and 0.5 mm shallower than the spline
   height as first modelled (so the floor seats on the spline top and the screw clamps it there; a deeper pocket would
   leave the floor floating and the screw would bend it, and a pocket deeper than the real spline is the failure to
   design out, so measure the spline height first: on the servo in hand it was 4.8 mm, not the 4 mm of the usual
   figures, and the 3.5 mm pocket already printed was kept, leaving the hub face 1.3 mm off the housing), 2.2 mm
   screw hole, 2.5 mm floor. A three-pocket coupon (4.5 / 4.6 / 4.7) in the
   same print orientation picks the size, and the horn screw is tried through the coupon's floor before the part is
   printed. The screw is the axial retention; the teeth take the torque.
3. **Bare press fit with no screw.** Nothing stops it working off the shaft. Don't.

A printed 21-tooth spline socket at 0.4 mm nozzle (0.7 mm tooth pitch) has not been tried here; the round pocket
that the teeth broach is the version that works without luck.

**Why option 2 should hold: an estimate, not a test result.** An MG90S stalls at 1.8-2.2 kg·cm, about 0.2 N·m,
and a light jaw needs under 0.01 N·m to move, so the coupling only ever sees stall torque in a jam. If the teeth bite
0.15 mm into the wall over 3.5 mm of engagement and all 21 shared the load, the bearing area would be about
21 × 0.15 × 3.5 ≈ 11 mm²; 0.2 N·m at a 2.3 mm radius is about 90 N, so about 8 MPa. A hand-pressed printed bore
won't share evenly, so take a factor of three for the few teeth that bite first: about 25 MPa against a 50 MPa
allowable, still a margin. Hoop stress stays low only if the printed bore is no smaller than the spline's root
(about 4.3-4.4 mm by the usual figures): the teeth cut, the hub isn't stretched. By the shrink rule in section 1 a
4.6 mm pocket prints at 4.3-4.5, so this is not guaranteed on paper; it is what the coupon settles. The horn screw's
clamp force at hand torque is not measured; a typical estimate for an M2 is 100-200 N, on a head about 3.5-4 mm
across, so 10-20 MPa under the head, at or above the sustained-stress guide in section 2. That is why the screw is
retention only, the torque goes through the teeth, and the instruction is "snug, not cranked". A plastic-gear servo
strips in a stall; a metal-gear one survives and passes the stall torque into the printed coupling, so set the
travel on the bench before fitting the mechanism.

**Mounting the case:** a pocket the case drops into until its tabs rest on a ledge, with pilot holes under the tab
holes for the servo's own tab screws. Pocket clearance 0.4 mm a side modelled. The pilot and the lead exit sit on the
same centreline, so the pilots must stop at least 2 mm above the lead notch; with a case 17.5 mm below the tabs and
7 mm pilots that leaves about 2 mm of solid, and a tab screw longer than about 9.5 mm then bottoms out (measure the
screws; the bag's lengths vary by clone). A pocket that merely wraps the case, with a zip-tie groove that never
reaches the case, holds nothing (section 5). And the pocket block itself must sit on something that locates it: a
foot on a curved shell does not (section 5).

## 5. Location and retention: every part needs a place to sit, and a check per load direction

**Location before retention.** Every internal part needs a printed feature it registers against: a hole, a slot, a
rim, a step. A foot "shaped to the inner wall" of a sphere locates nothing, because a sphere has the same curvature
everywhere, so "epoxy it where it lands" means holding the part by hand, in position, while the glue cures. That was
rejected on a build as not assemblable (2026-10-28), after the shell was already printed. The fix that needed no
reprint of the shell: hang the mount off a plug that fits a hole the shell already has. An elliptical plug in an
elliptical hole at a 0.15 mm fit cannot rotate; a flange whose back is a sphere of the wall's radius seats on the
wall round the hole and fixes the other three degrees of freedom; a strut from that flange carries the mount. Glue
then does retention only (it stops the plug backing out; the hole gives no grip against that), with nothing to hold
still while it cures, and hot glue is enough because the hole, not the glue, carries the position. Assert it in the
generator: the plug fills its hole and a plug 0.1 mm fatter collides; the seat has a stated area on the wall; nothing
else on the part touches the shell (a second contact point over-constrains against a shell that is not exactly the
model). State the lever from the seat to the working point, because any seat error is multiplied by it, and tell
the assembler to scrape support nubs off the wall under the seat.

**A two-part shell needs a repeatable fastener, not tape.** A slip-fit rim joint (a lip on one half, a recess on
the other) holds nothing, and tape or glue dabs are not serviceable when the mechanism is inside. Nothing on the
other half faces the direction it comes off in (every face in a lip joint faces the same way), so a positive lock
needs either a hole through that half or a part that goes round the seam. With both halves already printed and no
drill, the all-printed answer is a **pinned latch**: at two places on the seam, a clip glued to each half carries a
small block that reaches over the seam (0.3 mm above the other half); the two blocks sit side by side along the
seam, each with a tunnel through it, and a printed pin slides along the seam through both. The pin ties the blocks
together across the seam with 0.4 mm of play, so the halves cannot slide apart; push the pin out of one block and
the shell opens. Put the pin's head uphill of the upper block and bigger than the tunnel, so gravity holds it
closed, and make the pin longer than its opening travel plus the uphill tunnel, so it stays in that tunnel when open (a 30 mm pin, 15 mm of travel, a 12 mm tunnel). Gravity returns the pin on release, so one latch per seam is better than two where the lip joint already keeps the halves aligned: opening then takes one hand on the pin and one on the shell. Print a spare set; the clips are identical and go on either half. Assembly is
self-aligning: glue one clip, hang the other on the pin, close the shell, glue the second clip. Checks that matter:
each clip's contact is on its own half only; the pin sits in both tunnels and clears the shell; the far half moved
±1 mm along its come-off direction collides with the pin (the lock), with a control where it does not; the pin
pushed open clears the far block and is still inside the near tunnel; the pin pushed downhill hits the near block
(the gravity stop). When a drill and screws are in hand, the simpler version is blocks (16 × 16 × 8, at least 2 mm
beyond the pilot on every side) glued inside behind the lip and M3 screws through the overlap, drilled after gluing
so the block's position never has to be exact. Either way, put the latches where nothing else sits on the shell: a
cap or lid seat, a stand's rim, a cable hole. And plan the assembly order in the generator: a coupling that needs
a few millimetres of travel to press together cannot be pressed inside the shell; sweep the whole assembled unit
along its insertion path and assert it clears.

**Retention: check each load direction, not just clearance.** A set of clearance checks ("no overlap", "clear of
the shell", "foot touches the wall") is invariant under "held by nothing": a bracket that let the servo lift
straight out along its shaft passed every one. For every mounted or coupled part write down what resists each load
direction (torque, pull along the shaft, lift, sideways) and assert it in the generator: tabs on a ledge, a screw
head on a floor, teeth in a wall. Give every geometric check a positive control (a deliberate collision or a removed
feature that must make it fail), or the check may be blind. Two blind spots found by mutation on 2026-10-28: a check
that is symmetric under mirroring the part passes a mount built on the wrong side (only an unrelated "one solid
piece" check caught it), and nothing in a set of fit checks sees an upside-down print orientation. Assert the side
(which half-space the locating feature lies in) and the orientation (bed footprint area, the lowest face, which way
a pocket opens) as their own checks.

## 6. Adhesives on PLA (looked up 2026-10-27)

- Hot glue tacks and holds unloaded parts; it is not a structural joint and peels with a knife.
- Epoxy bonds PLA well with both faces scuffed and clean, fills small gaps, and needs its full cure before load.
- CA bonds close-fitting PLA but is brittle under ongoing stress and across gaps.
- Acetal (POM) and nylon servo horns are low-surface-energy plastics: CA and epoxy don't grip them without a primer.
  Screw, wire or zip-tie a horn; don't glue it.
- Sources: sigmafilament.com (best glue for PLA/PETG), natecue.com gluing guide, silitech.ch on sticking POM,
  learn.adafruit.com animatronics guide, loctiteproducts.com (how to glue PLA), Devcon 5-minute epoxy data sheet.
