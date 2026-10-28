# Design for FDM printing: fits, PLA numbers, screws, servo couplings, retention

What a part designer needs that the slicer docs don't say. Collected from builds on a Bambu A1 mini (0.4 mm nozzle,
0.2 mm layers, PLA unless stated) and from published data sheets. **Add to this file in the same session you learn
something**: a fit that worked or failed, a material number, a mechanism rule, a slicer behaviour. Keep entries
generic (this repo is public): what was measured, on what printer and material, and what to do about it.

Tooling and workflow live elsewhere: `CLAUDE.md` in this repo (headless Blender, manifold3d CSG, 3MF packaging,
`bambu_sweep.py`, `gcode_features.py`). This file is the engineering side.

## 1. Fits and tolerances

- **Printed holes come out smaller than modelled.** Rules of thumb from several tolerance guides: 0.1-0.3 mm under
  for a vertical-axis hole of 2-6 mm; horizontal-axis holes also sag at the top of the arc (the bridge), so they are
  shorter top-to-bottom than side-to-side. The amount depends on printer, material and the slicer's
  `xy_hole_compensation`, so for anything that has to fit, measure it or print a coupon.
- **Clearances (diametral, i.e. total gap, not per side):** slip fit about 0.3-0.5 mm; snug 0.2; press fit 0.1-0.3 mm
  of interference. Guides disagree on whether their numbers are per side or on the diameter: say which when writing
  one down.
- **Elastic range.** PLA yields or cracks at roughly 1-3 % strain (section 2), so an interference that stretches a
  bore by more than about 1 % of its diameter does not spring; it deforms or splits. Teeth cutting grooves into a
  bore (a spline, a knurl) is fine; stretching a hub over a round shaft by 0.3 mm is not. For a toothed shaft, size
  the bore between the root and the tip diameter so only the teeth bite.
- **Print a coupon in the same orientation as the feature,** with three sizes bracketing the guess, marked by notch
  counts (text in CSG is a chore; one, two, three notches is not). It costs ten minutes and saves the hour-long part.
  Worked examples: a three-width fit coupon (`phone-kickstand/generate.py`), the rim-joint coupons and the
  three-pocket spline coupon described below (private project).
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
| Bambu PLA Basic, Bambu's data sheet | 35 ± 4 MPa | (bending) 2750 ± 160 MPa | 12.2 ± 1.8 % at break | 76 ± 5 MPa | 26.6 ± 2.8 kJ/m² | HDT 57 °C at 0.45 MPa |
| Prusament PLA, Prusa's TDS (horizontal / vertical XZ specimens) | yield 51 ± 3 / 59 ± 2 MPa | 2.3 / 2.4 GPa | at yield 2.9 / 3.2 % | 83 / 99 MPa | Charpy 13 / 14 kJ/m² | — |

Sources: eu.store.bambulab.com PLA Basic product page (TDS table), Bambu filament guide PDF (HDT),
prusament.com PLA TDS 2021-10. Prusament's "vertical XZ" is a specimen standing on its edge, so it is not the
across-layers (Z) case; no data sheet found gives Z strength. The usual community figure is 50-80 % of in-plane
strength for layer adhesion: **unverified**, so put loads in-plane or make the section thick where a load crosses
layers.

For a back-of-envelope design check use: tensile 30 MPa, shear about 18 MPa (0.6 × tensile), bearing or compressive
about 50 MPa, modulus 2.5 GPa, and keep **sustained** stress under about 5-10 MPa because PLA creeps (a clamped
screw loses preload over days; a press fit relaxes). Form holds, friction doesn't: teeth, ledges, screw heads on
floors. PLA softens from about 55-60 °C (a car in the sun, a hot enclosure, a lamp); PETG for those. At porch
temperatures (0-10 °C) PLA is already glassy at room temperature, so expect slightly lower impact strength and no
change in fit.

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
plastic on the SG90), 21 teeth, about 4.7-4.8 mm across the tips, about 4 mm tall, with a tapped hole down its
centre for the **horn screw**. A **horn** is one of the plastic arms in the bag that press onto the spline. The bag
holds one horn screw, two longer tab screws (about 1.9 mm thread) and a few horns.

**Clone dimensions vary and the data sheets leave things out.** Measure before designing a mount: case length and
width, base to tab underside, tab thickness, width and tip-to-tip span, tab hole spacing (27.0 mm on one 2026 clone;
27.5 scaled from a drawing; no data sheet dimensions it), gear-housing top and spline top above the tabs, spline
diameter and height, where the lead leaves the case, and the three screws' lengths.

**Coupling a printed part to the spline, in order of preference:**

1. **Stock horn captured in a pocket**, screwed to the printed part through its outer holes, plus the horn screw.
   Strongest and the way commercial animatronics do it; needs the horn's dimensions, which vary by clone.
2. **Printed hub with a blind round pocket pressed onto the spline, plus the horn screw through the pocket floor.**
   The same joint as a stock horn, in PLA. Used on a Halloween animatronic jaw (2026-10-28): hub 16 mm across and
   6 mm thick, pocket 4.6 mm modelled and 3.5 mm deep (shallower than the 4 mm spline so the floor seats on the
   spline top and the screw clamps it there; a deeper pocket would leave the floor floating and the screw would bend
   it), 2.2 mm screw hole, 2.5 mm floor. A three-pocket coupon (4.5 / 4.6 / 4.7) in the same print orientation picks
   the size. The screw is the axial retention; the teeth take the torque.
3. **Bare press fit with no screw.** Nothing stops it working off the shaft. Don't.

A printed 21-tooth spline socket at 0.4 mm nozzle (0.7 mm tooth pitch) has not been tried here; the round pocket
that the teeth broach is the version that works without luck.

**Why option 2 holds, with the numbers above.** An MG90S stalls at 1.8-2.2 kg·cm, about 0.2 N·m, and a light jaw
needs under 0.01 N·m to move, so the coupling only ever sees stall torque in a jam. With the teeth biting 0.15 mm
into the wall over 3.5 mm of engagement, the bearing area is about 21 × 0.15 × 3.5 ≈ 11 mm²; 0.2 N·m at a 2.3 mm
radius is about 90 N, so about 8 MPa of bearing stress against a 50 MPa allowable. Hoop stress stays low as long as
the printed bore is no smaller than the spline's root (about 4.3-4.4 mm): the teeth cut, the hub isn't stretched. The
horn screw at hand torque gives 100-200 N on an annulus of about 12 mm² between the 2.2 mm hole and the 4.6 mm
pocket: 8-16 MPa, which is why "snug, not cranked". A plastic-gear servo strips in a stall; a metal-gear one
survives and passes the stall torque into the printed coupling, so set the travel on the bench before fitting the
mechanism.

**Mounting the case:** a pocket the case drops into until its tabs rest on a ledge, with pilot holes under the tab
holes for the servo's own tab screws. Pocket clearance 0.4 mm a side modelled. The pilot and the lead exit sit on the
same centreline, so the pilots must stop at least 2 mm above the lead notch; with the tabs 17.5 mm above the base
and 7 mm pilots there is just enough room. A pocket that merely wraps the case, with a zip-tie groove that never
reaches the case, holds nothing (section 5).

## 5. Retention: check each load direction, not just clearance

A set of clearance checks ("no overlap", "clear of the shell", "foot touches the wall") is invariant under "held by
nothing": a bracket that let the servo lift straight out along its shaft passed every one. For every mounted or
coupled part write down what resists each load direction (torque, pull along the shaft, lift, sideways) and assert
it in the generator: tabs on a ledge, a screw head on a floor, teeth in a wall. Give every geometric check a positive
control (a deliberate collision or a removed feature that must make it fail), or the check may be blind.

## 6. Adhesives on PLA (looked up 2026-10-27)

- Hot glue tacks and holds unloaded parts; it is not a structural joint and peels with a knife.
- Epoxy bonds PLA well with both faces scuffed and clean, fills small gaps, and needs its full cure before load.
- CA bonds close-fitting PLA but is brittle under ongoing stress and across gaps.
- Acetal (POM) and nylon servo horns are low-surface-energy plastics: CA and epoxy don't grip them without a primer.
  Screw, wire or zip-tie a horn; don't glue it.
- Sources: sigmafilament.com (best glue for PLA/PETG), natecue.com gluing guide, silitech.ch on sticking POM,
  learn.adafruit.com animatronics guide, loctiteproducts.com (how to glue PLA), Devcon 5-minute epoxy data sheet.
