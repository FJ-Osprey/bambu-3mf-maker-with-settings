# 10. Solved mechanisms: reuse these before inventing a joint

Back to the [entry point](../DESIGN-FOR-PRINT.md). Every mechanism here was designed for a real build on this printer,
went round the print-fit-revise loop, and has its numbers written down. **Before designing a latch, lid, seam,
mount, coupling or hinge, look here first.** If one fits, start from its numbers and its failed versions, not from a
blank page; if you adapt one, scale the numbers that depend on size and keep the ones that came from the printer (gaps,
ramps, wall counts). If you solve a new one, add an entry in the same session.

Each entry says when to use it, the motion as the hands do it, the numbers, what failed on the way and why, and its
status:
- **worked in the hand**: printed and operated by a builder, result reported;
- **printed, not yet proven**: printed, but the result that matters has not been reported;
- **designed and checked**: modelled with geometry checks, not yet printed.

The long-form reasoning and the sources are in the section each entry links to.

| Mechanism | Use it for | Status |
|---|---|---|
| [Twist-lock seam for a two-half shell](#twist-lock-seam-for-a-two-half-shell) | closing a round or cylindrical shell from the inside, no hardware, opened now and then | worked in the hand (final lengths not yet printed) |
| [Printed hub on a micro-servo spline](#printed-hub-on-a-micro-servo-spline) | driving a printed arm, jaw or paddle from an SG90/MG90S | printed, not yet proven |
| [Side-entry micro-servo mount](#side-entry-micro-servo-mount) | holding a micro servo in a printed block when its lead leaves the end face | designed and checked |
| [Crush-rib socket](#crush-rib-socket) | pressing a printed part into a printed bore that has to stay put without glue | designed and checked |
| [Ear-and-post second mount inside a shell](#ear-and-post-second-mount-inside-a-shell) | anchoring a part already located by a hole, with no fastener showing outside | designed and checked |
| [Fold-out plate on a friction hinge](#fold-out-plate-on-a-friction-hinge) | a printed plate fixed to an existing hinge leaf (a stand, a flap) | designed and checked |

## Twist-lock seam for a two-half shell

**Use it when** two halves of a shell must close with nothing outside to grab (no screws, no clips showing), be
opened again for service, and stay shut when lifted by either half. Section 5 has the whole story; this is the
recipe.

**Motion**: hold the halves with the alignment ticks lined up at "entry", push them together (the rims locate), turn
about 12° (18 mm along the seam on a 170 mm ball) in the marked direction: a soft bump as each lug pushes a spring
finger aside, then a hard stop. Ticks line up at "locked". Reverse to open, same force. Pulling without turning does
nothing.

**Parts**, at each of three sites (one half carries the lug, the other the box, post and detent):
- **Lug**: a plain bar under the lip, 12 mm long along the seam, 2.0 mm thick along the shell's axis, about 2.2 mm
  deep radially, inside a 3 mm rim band.
- **Box** that the lug turns into, closed on every side but its mouth: a floor under the lug (floor top 0.1 mm below
  the lug at the nominal seat), a web 0.5 mm inside the lug's inner face, a roof 1.4 mm thick bridged out into the
  wall, and the post closing the far end. **Slot height = lug thickness + 1.0 mm** (3.0 for a 2.0 lug). The floor is
  what holds (pull the halves apart and the lugs land on it); the rims set the depth; the roof only closes the box, so
  nothing depends on how deep the rims really seat. Box 11.1 mm long, so 11 of the lug's 12 mm are inside when
  locked. Rooted to the wall along its whole length, not hung off a post.
- **Mouth**: a staircase ramp, floor 0.4 mm lower and roof 0.4 mm higher at the entry, stepping back over 1.2 mm in
  0.1 mm steps. Not a 0.3 mm step: at 90° that is a wall.
- **Post**: the stop, 6 mm long, bonded to the wall over a long height (not just above a chamfer).
- **Detent**: a cantilever along the seam bending radially, 1.68 mm thick (four 0.42 mm walls, no gap fill) × 8 mm
  tall, about 20 mm free, a barb with 0.6 mm engagement and 30° ramps both ways along the turn, 1.0 mm of twist play
  between the locked lug and the barb. Strain about 0.4 %, about 2.7 N tangential per site, about 0.7 N·m for three, 8 N
  at the equator of a 170 mm ball, the same to lock and unlock. Relaxed when locked (PLA creeps; section 5). Its tip
  stays 1.2 mm or more from the box mouth so the two print as separate pieces.
- **Sites at 0°, 120° and 250°**, not 240°: three equal sites let the half lock turned by a third.
- **Ticks**: one on the box half, two on the lug half (entry and locked), 0.8 mm proud, on the outside where the builder
  looks while assembling.
- Clearances: 0.45 mm radial under the lip for anything on the box half; 0.35 mm radial in the rim joint.
- Everything prints without support in both halves standing on their rims.

**Failed on the way** (each is a rule in section 5):
1. Push-on snap with three preloaded hooks: passed every check, needed about 47 N to close on a ring that cannot flex,
   resisted no twist, and was not the motion the builder pictured. Agree the motion first.
2. Twist-lock with an open channel whose floor was set from the model's seat depth (never measured): the lug stopped
   at the channel's mouth.
3. Closed box with a slot 0.3 mm over the lug and a 0.3 mm step as a lead-in: jammed at the mouth; the lug only fitted
   for seat depths in a 0.3 mm window. Give the part a millimetre, not tenths, when its position rides on an
   unmeasured number.
4. Box with the numbers above but 7 mm long for an 8 mm lug: the lug went in to the stop with nothing in its way,
   but most of it stuck out of the mouth. The final version lengthens both by 4 mm.

**Test before the halves**: two full-hoop coupons (a 12 mm band of each rim with every site, about an hour and 15-22 g
each). A one-site arc proves nothing: it pivots and flexes where the ring can't.

## Printed hub on a micro-servo spline

**Use it when** a printed arm, jaw or paddle must be driven by an SG90/MG90S and a stock horn won't fit. Full numbers
and the strength estimate: section 4.

Hub 16 mm across, 6 mm thick; a blind round pocket (4.6 mm modelled, picked from a 4.5 / 4.6 / 4.7 coupon printed in
the same orientation) pressed onto the spline so the teeth broach it; the pocket shallower than the spline so the
floor seats on the spline top; the bag's horn screw through a 2.2 mm hole in a 2.5 mm floor into the shaft, snug not
cranked. The teeth carry the torque, the screw only stops it working off. Measure the spline height first: one
servo's was 4.8 mm against the usual 4 mm. A bare press fit with no screw, and a printed 21-tooth socket, are the
versions not to use.

## Side-entry micro-servo mount

**Use it when** a micro servo sits in a printed block on its tabs and its lead leaves the middle of the end face (the
usual MG90S clone). Section 4 has the dimensions.

Leave one side wall off; the case slides in sideways over the tab ledge until it meets the far wall, with the lead
bent flat against the case end into a groove in the end wall's inner face below the pilot (about 3.5 deep × 7 wide,
45° roof, open to the entry side and out through the bottom). Pocket 0.4 mm a side; pilots for the bag's tab screws
(1.6-1.7 mm modelled for about 1.9 mm screws); the two tab screws stop it sliding back out. **Failed on the way**: a
top-entry pocket with a floor notch (the plug had to be threaded blind) and a slot down from the ledge (it either cut
the pilot or missed the lead). Model the lead as a ribbon and sweep it along the insertion path.

## Crush-rib socket

**Use it when** a printed lip (spigot) goes into a printed bore to locate two parts, must not rattle, and must push
home by hand whatever the print error. Here gravity held the parts together, so the joint only locates; for a joint
that must also hold against a pull, add a form feature (section 5). Section 1 (press fits).

An 8 mm lip, 2 mm wall, 0.4 mm radial clearance to the bore, so the lip itself never touches; twelve thin vertical ribs
on the lip's outer face (1.6 mm wide at the base, 0.6 at the tip) reaching 0.05 mm past the bore's modelled radius,
stopping short of the bore's first-layer flare, with a 0.8 mm chamfer on the lip's top as a lead-in. The ribs squash,
the wall doesn't; too tight, shave the ribs with a knife. Guides suggest ribs about 0.2 mm proud; this used 0.05
because printed holes already come out small (section 1). Report the fit (won't go / push / slides) when printed.

## Ear-and-post second mount inside a shell

**Use it when** a part inside a shell is located by a plug in a hole, nothing may show on the outside, and glue alone
would be peeled. Section 5 has the reasoning.

**Motion**: the part goes in along its insertion axis, the plug seats, a thin ear lands beside a post grown from the wall,
two screws go in along the same axis from the open side.

Ear 3 mm thick, on a face that puts it on the bed so it needs no support; holes 2.6 mm for about 1.9 mm screws, with a
5 mm counterbore 1.5 deep. Post a plain prism along the insertion axis, 14 × 16 mm, its face in the same plane as the ear's
(no gap: see below), pilots 1.7 mm and 9 mm deep. With a rim-down shell the post's face points at the bed and hangs on tree supports (a
20-minute slicer penalty on a 9-hour half; confirm supports reach the whole face in the gcode). Scrape the face, clear
the pilots with a screw. Check by intersecting the screws with the piloted part, not the solid post; a screw test on
the solid post passes with the pilots missing.

**No nominal gap between ear and post.** The first version left 0.3 mm "so the post can't unseat the plug", to be closed
by the screws. A 3 mm ear a few millimetres from its root is about 2500 N/mm, so screws never bend it: they turn the whole
part about the top edge of its other seat. Probing the solids with that pivot (the seat's top, not the plug's centre)
gave 1.7 degrees for 0.3 mm, the seat's far edge lifting 0.7 mm off the wall and the driven part sitting 2 mm deeper.
Nothing collided, but the seat the design relies on was no longer touching. Two seats on one part that both fix the
same freedom must be modelled to land together; the one that prints long (a face on supports) is scraped to fit, and a
slit left after scraping is filled, never pulled shut. General rule: a clearance that screws are expected to close must
be closed by something compliant, or it moves the part off its other datum. A headless slice of the final file showed
support interface up to one layer under the face and the face's first layer printed as a bridge. **Not yet printed.**

## Fold-out plate on a friction hinge

**Use it when** a printed plate is fixed to an existing metal hinge leaf (a replacement stand or flap), so the hinge's
own friction holds it at any angle.

- Nothing nearer the hinge axis than the knuckle radius plus 0.5 mm.
- Material behind the axis sweeps an arc as the plate opens: bevel the near edge so nothing dips more than about
  0.6 mm into the surface beneath, checked through the full opening angle (125° in the worked case).
- **Preload**: model the plate tilted about 1.5° toward the closed position, so its tip lands first and the plate
  flexes flat when shut; it then holds itself closed. Undo the tilt for the print file so the top face lies flat on
  the bed.
- Fix to the leaf with keys into existing features and a 0.2 mm recess for epoxy (section 6); a glued plate must
  locate on a printed feature, never "where it lands".
- When there are no calipers, print a fit coupon of the leaf's width at three sizes (e.g. 13.0 / 13.4 / 13.8) before
  the part.
