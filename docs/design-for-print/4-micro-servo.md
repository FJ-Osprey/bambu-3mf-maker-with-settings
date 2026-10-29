# 4. Micro servo (SG90 / MG90S class): coupling the output and mounting the case

Back to the [entry point](../DESIGN-FOR-PRINT.md). Measured and estimated numbers for one servo class; *untested here*
unless a measurement is given.

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

**Mounting the case:** a pocket the case sits in with its tabs resting on a ledge, with pilot holes under the tab
holes for the servo's own tab screws. Pocket clearance 0.4 mm a side modelled. **The lead and the tab holes share the
case's centreline** (on the MG90S clone in hand the flat lead leaves the middle of the end face, low down), so a case
lowered in from the top can't get its lead past the end wall: a floor notch alone means threading the plug through
it blind, and a slot cut from the ledge down either cuts through the pilot or sits beside the lead and misses it
(both failed at the bench, 2026-10-28/29). What works: **side entry.** Leave one side wall off, so the case slides in
sideways over the ledge until it stops on the other side wall; bend the lead down flat against the case end (a flat
ribbon bends easily across its thickness, not edgewise) and give it a groove in the end wall's inner face, below
the pilot, open to the entry side and out through the bottom of the block. About 3.5 mm deep and 7 mm wide across
the case, with a 45° roof rising toward the pocket, it prints with no support and leaves the full wall round the
pilot (about 2 mm of solid under the pilot's end; *untested here* until printed). The two tab screws then hold the servo against sliding
back out the open side and carry its torque reaction, as tab screws alone do in model aircraft; the far side wall
and the end walls locate it. A generator check should model the lead itself (a ribbon fixed to the case) and move
it along the insertion path; a check that only probes the slot passes while the lead hits the wall. With a 17.5 mm
case below the tabs and 7 mm pilots, a tab screw longer than about 9.5 mm bottoms out (measure the screws; the
bag's lengths vary by clone), and measure where the lead leaves the case (one drawing says 4.7 mm above the base).
A pocket that merely wraps the case, with a zip-tie groove that never
reaches the case, holds nothing (section 5). And the pocket block itself must sit on something that locates it: a
foot on a curved shell does not (section 5).
