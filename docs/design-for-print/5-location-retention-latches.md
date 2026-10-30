# 5. Location, retention and latches: every part needs a place to sit, and a check per load direction

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*. The general snap-fit
rules come first; worked cases from one build (an internal mount in a printed sphere, a two-half shell's latch)
follow, then the retention checks.

## Snap fits: the engineering

The formulas are from the plastics makers' snap-fit manuals (Bayer MaterialScience "Snap-fit joints for plastics", the
Covestro copy of it, and BASF's snap-fit design manual) (*settled* for moulded plastics; the strain limits for
printed parts are not).

- **Cantilever arm of constant thickness** (a straight hook): strain at the root
  ε = 1.5 · t · y / L², where t is the arm thickness in the bending direction, y the deflection needed to clear the
  catch (the undercut), and L the length from root to where the catch acts. Equivalently the allowed deflection is
  y = 0.67 · ε · L² / t. Valid for L/t above about 10; a shorter, stubbier arm deflects less than the formula says
  (BASF adds a correction factor).
- **Tapered arm** (thickness halving from root to tip): y = 1.09 · ε · L² / t, about 60 % more deflection for the same
  strain. Taper when the arm is short.
- **Force to deflect**: P = b · t² · E · ε / (6 · L), with b the arm width and E the modulus. **Force to push it on**:
  W = P · (μ + tan α) / (1 − μ · tan α), with α the entry-ramp angle and μ the friction coefficient (0.4-0.6
  for plastic on plastic; no published figure for printed PLA, whose layer texture likely raises it). The same formula
  with the catch-face angle gives the pull-off force: a 90° catch face does not release by pulling; a 45° one does.
- **Annular snap** (a ring over a bead): allowed undercut y = ε · d, with d the diameter at the joint.
- **Strain limits**. Moulded plastics, one assembly: polycarbonate 4 %, PC/ABS 2.5 % (Bayer), ABS 6-7 % (BASF);
  **use 60 % of the table value for joints that are opened and closed often** (Bayer). Correction (2026-10-29, review): ABS 6-7 % is BASF's
  table, not Bayer's. Printed parts have no measured figure; the
  guides' working values for an arm printed flat: **PLA about 1-2 %, PETG about 3-4 %** (Loftsmith; CLT 3D; minicad;
  3dprinterstuff; layerx3d) (*disputed*: one guide says PLA 4-8 %, which is near its break strain). Halve it for an
  arm that bends across its layers, and don't build one that way: Formlabs and Hubs both say a cantilever built
  standing in Z loses about half its elongation (*settled*). The calibration set (section 8) has a strain ladder.
- **Geometry rules of thumb**: root fillet radius at least half the arm thickness (Hubs; CLT 3D; Bayer's stress
  concentration chart); arm at least 3 perimeters thick (1.2 mm at a 0.4 nozzle) so it is solid wall, 5 mm or more
  wide, 8 mm or more long; entry ramp 30° (guides range 20-45°; steeper pushes harder); catch overlap from the formula,
  not a guide's number (one guide's worked example contradicts its own formula) (*disputed* in the details).
- **Don't leave it bent.** A snap arm should be deflected only while it goes together and sit relaxed in service
  (Hubs). PLA held bent creeps: it takes a permanent set and loses force over days (mechanics.ju.se; an older 2018 clip
  test found PLA clips set but still clamped). A latch that is designed to sit slightly bent to pull a seam shut (the
  preloaded catch in the worked case below) trades this rule for zero play; keep that preload strain well under the
  limit, and expect it to relax and need re-testing after weeks (*untested here*). Cycle life of printed snaps has no
  test data (guides say anything from 5-20 to 200 cycles for PLA).

## Hinges, slides, twist-locks, keys and magnets

- **Print-in-place hinge**: radial gap about 0.3 mm (0.35-0.45 for PETG or a stringy printer), axial gap between
  knuckles 0.3 mm if printed flat, or two whole layers (0.4 mm) if the gap is horizontal; 45° cones on the pin ends so
  every surface prints without support; pin 3 mm or more; never start a moving gap on the first layer, chamfer it or
  lift it 0.2-0.4 mm (Loftsmith; buildcad.ai; the3dai hinge generator) (*disputed* by ±0.1, *untested here*).
  Separate pin through printed knuckles: hole = pin + 0.2-0.3 mm.
- **Dovetail slide**: a trapezoid that slides on, captures every direction but the sliding one, and aligns itself;
  flank angle about 7-10°, sliding-fit clearance from section 1 (grandpacad) (*untested here*).
- **Bayonet or twist-lock**: push in, turn about 90° along an L-shaped slot; 3-4 lugs, 0.3-0.5 mm running gaps, and a
  small bump (detent) so it cannot turn back by itself. It needs one half to rotate relative to the other.
- **Keyed and one-way fits** (poka-yoke, Japanese for mistake-proofing): make a part either symmetric, so any way in
  is right, or obviously asymmetric, so only one way seats: offset one hole, chamfer one corner, add a key. Never
  "nearly symmetric" (Boothroyd-Dewhurst DFA via engineerdog; sekkei-tech) (*settled* principle). Section 7.
- **Magnet pockets**: for a 6 × 3 mm disc magnet, pocket 6.1 mm to press in, 6.2-6.3 mm to glue, depth magnet +
  0.1-0.2 mm; 0.4-0.8 mm of plastic between magnet and the outside face; or pause the print, drop the magnet into a
  closed pocket and print 2-4 layers over it (totalelement; magnetenspecialist; propbuilds; draftid tested 6.2 mm in
  Bambu Studio with a pause) (*settled* across four vendors, *untested here*). Glue with CA or epoxy, not hot glue.
  Mark the polarity of every magnet before it goes in: a round pocket cannot enforce it. Neodymium magnets are rated to
  about 80 °C, which is the A1 mini's maximum bed temperature.

## Worked cases from one build

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

Correction (2026-10-30, same build, design stage): that plug's hot glue was the only thing resisting pull-out, and it
was loaded in peel. A servo's torque stays small in normal motion (paddle of 11 g, about 2×10⁻⁵ kg·m², under 20 mN·m
at 8 Hz) but a hobby servo drives at full torque whenever its target jumps, and a push on the driven part pulls directly on the
joint: about 10 N and up to 30 N at the seat's edge on a 27 mm seat, against an estimated 5-20 N of hot-glue peel. For anything a servo drives or
a person can touch, keep the plug as the locator and add a mechanical second mount: a thin ear on the part, screwed
to a post on the shell's wall, with the screw axis along the insertion direction so a driver reaches from the open
side, the post's face modelled to touch the ear exactly when the plug seats (a nominal gap there is closed by the screws
tipping the part off the plug's seat: section 10), and a deep pilot so the joint works for the bag's screw length
(measure the screw's head before adding a counterbore: section 10). See section 10.

**A two-part shell needs a repeatable fastener, not tape.** A slip-fit rim joint (a lip on one half, a recess on
the other) holds nothing, and tape or glue dabs are not serviceable when the mechanism is inside. Nothing on the
other half faces the direction it comes off in (every face in a lip joint faces the same way), so a positive lock
needs either a hole through that half or a part that goes round the seam. With both halves already printed and no
drill, one all-printed answer is a **pinned latch** with glued clips. It was rejected at the bench the same day it was
designed ("you glue clips on and then lock them with a peg?"): if a part can be reprinted, the latch belongs in the
part, and the builder would rather reprint 16 hours of halves than glue add-ons. The printed-in answer is the snap
latch in the next paragraph; the pinned latch is kept here for the case where a reprint is truly impossible: at two places on the seam, a clip glued to each half carries a
small block that reaches over the seam (0.3 mm above the other half); the two blocks sit side by side along the
seam, each with a tunnel through it, and a printed pin slides along the seam through both. The pin ties the blocks
together across the seam with 0.4 mm of play, so the halves cannot slide apart; push the pin out of one block and
the shell opens. Put the pin's head uphill of the upper block and bigger than the tunnel, so gravity holds it
closed, and make the pin longer than its opening travel plus the uphill tunnel, so it stays in that tunnel when open (a 30 mm pin, 15 mm of travel, a 12 mm tunnel). Gravity returns the pin on release, so one latch per seam is better than two where the lip joint already keeps the halves aligned: opening then takes one hand on the pin and one on the shell. Print a spare set; the clips are identical and go on either half. Assembly is
self-aligning: glue one clip, hang the other on the pin, close the shell, glue the second clip. Checks that matter:
each clip's contact is on its own half only; the pin sits in both tunnels and clears the shell; the far half moved
±1 mm along its come-off direction collides with the pin (the lock), with a control where it does not; the pin
pushed open clears the far block and is still inside the near tunnel; the pin pushed downhill hits the near block
(the gravity stop). A version with drilled screw holes through glued blocks was also written down here once; it is
withdrawn (2026-10-29): it is rung 6 of the entry point's order (drilling an already-printed part), only for a shell
that truly cannot be reprinted and a builder who has the drill and the screws. Where a reprint is possible, print the
screw bosses and their pilots into the halves (section 3). Either way, put the latches where nothing else sits on the shell: a
cap or lid seat, a stand's rim, a cable hole. And plan the assembly order in the generator: a coupling that needs
a few millimetres of travel to press together cannot be pressed inside the shell; sweep the whole assembled unit
along its insertion path and assert it clears.

**Snap latch printed into a two-half shell (2026-10-28).** The constraint first: both halves print rim-down (one on
its lip, one on its rim), so no integral feature can cross the seam plane; anything past it is below the bed. What
can be printed is a hook on the back half that reaches exactly to the seam plane, and a catch bar on the front half
inside the lip's own extent (the lip already stands past the seam). Lay the hook's **arm along the seam**, not out
from the wall: an arm that stands along Z bends across its layers and cracks (Formlabs' snap-fit guide and the
Hackaday enclosure write-ups say so, and the published across-layer numbers in section 2 agree); an arm lying on the
bed has its layers along its length and flexes in-plane, where PLA's elongation is 12 % rather than 7.5 %. Numbers
that passed the generator's checks on a 170 mm sphere with a 3 mm wall, three sites: arm 1.8 mm thick (radial), 8 mm
along the axis, 22 mm long with a 19 mm free length; barb 6 mm long at the free end, crest 0.3 mm under the lip, 45°
entry ramp and 45° catch face; bar under the lip 10 mm long, 2.5 mm along the axis, reaching 2 mm in from the lip,
45° catch face; deflection 2.0 mm, strain 1.5·t·δ/L² = 1.5 %, about 8.5 N per hook, so about 45 N to part or close
three (pull-release; a 90° catch needs an outside release, and there is none at a covered seam). Revolve the profiles
about the seam's axis: a 30 mm feature on an 85 mm sphere is 2.5 mm off a flat box, and fuse parts with a 0.5 mm
overlap, since faces that merely touch do not union after a rotation. Checks: closed, nothing touches; the back half
moved 1 mm off hits every bar and 0.2 mm hits none; the hook with its barb pressed in by the deflection sweeps in
along the axis without touching the front, and the unpressed barb does hit; the hooks' feet and the bars' feet are
at the bed plane, nothing past it; strain under 2.5 %. What the coupons taught (2026-10-28/29): the first coupon
clicked and flopped open 2 mm, because the catch was modelled with 0.6 mm of axial clearance and the printed crest
and bar edge both came out short; with 45° faces every bit of radial shortfall is axial play. A latch is a
**preloaded** fit: model the catch face about 1.5 to 2 mm past where a clearance fit would put it, so the model
interferes and the print absorbs it (the measured shortfall here was about 1.3 mm); the hook then sits slightly bent
when closed and pulls the seam shut. Then **list the joint's degrees of freedom and what stops each.** The clearance,
lock and entry checks all passed while nothing at all resisted a twist of the halves about the seam's axis, and on
the coupon the barb slid clean off its bar: a snap on a round seam needs a rotational key (here, a block on the back
half each side of every bar, a few tenths off its ends, with a check that a 1 mm twist hits and 0.2 mm does not).
And a **coupon of a multi-site ring joint is the ring**, not one site: a one-site arc pivots about its one hook, so
it cannot be judged, and its arcs flex apart to let the barb pass where the ring cannot (the stiffness rule in
section 1). Two full hoops of the rims, every site, cable hole filled, cost about 35 g and an hour each and answer
the question the halves would. **Postscript (2026-10-29): the push-on snap was replaced by a twist-lock, and why.** Two full-hoop coupons of the
push-on snap showed what the one-site arcs had hidden: three preloaded cantilever hooks need about 47 N to close on a
ring that cannot flex, nothing resisted a twist about the seam axis, and the builder had pictured a twist lock from
the start. Lessons, in the order they would have saved the most time:
- **Agree the motion before the geometry.** Write the joint as the hands will do it (set on, turn this way this far,
  feel this, stop here; reverse to open) and draw it in two or three states from where the builder's eyes are, before
  any solid exists. The push-on snap passed every check and was the wrong mechanism.
- **Form holds, a spring only indexes.** On a seam with no outside access, a bayonet-type lock is better than a snap:
  lugs under the front lip turn a few degrees into channels on the back half, a stop ends the turn, and a light
  detent (a cantilever along the seam, bending radially, in-plane, with 30° ramps *along the turn* both ways) only
  keeps it from turning back. Numbers that passed: lug 8 mm, 12° of turn, detent 1.68 thick (four 0.42 mm walls, no
  gap fill) × 8 × 20 mm free, 0.6 mm engagement, strain 0.4 %, about 2.7 N tangential per site, 0.66 N·m for three,
  8 N at the equator of a 170 mm ball, same to unlock, detent relaxed when locked.
- **Find the true seat.** A rim with a 45° outer chamfer and no flat face at the parting plane seats where the other
  rim's corner meets the cone, 0.35 mm deeper than the model's plane here. Every axial clearance was wrong by that
  until a check pushed one shell into the other and found first contact. Then make the retainer's flat top the axial
  seat (a layer-accurate top face in both prints) instead of a stepped cam into the stiffest part of a cantilever.
- **Root a retainer along its length, not off a post.** A tongue hung from a post loads the post across its layers,
  and a post bonded to the wall only above the rim's inner chamfer has a few mm of bond: the same root as the stop
  blocks a builder snapped off by hand. A C-channel (flange under the lug, web inside it, 45° flare into the wall)
  carries the pull over its whole length at about 1 MPa.
- **Two parts on the bed less than a line width apart are one part.** A spring finger's free end 0.08 mm from a fixed
  feature would have printed welded; keep 1 mm or more, and check it with the finger relaxed and bent.
- **Break the symmetry.** Three identical sites at 120° let the front lock turned 120°; move one site 10° (poka-yoke).
- **Widen whatever crosses the parting line** for the turn (here the cable notch, by the entry offset), and sweep
  the moving half's features through the approach and the turn against everything inside, not only the locked state.
- **Give coupons an index.** Full hoops with no cable notch could be "locked" against the next site's root; two
  printed ticks (entry and locked) on the outside cost nothing.
- Review before printing paid for itself: two independent passes on a one-page spec found the welded detent, the
  false seat, the post root and the symmetry; none of these had a failing check.
- **And the reviewed version still failed in the hand**, for a reason both reviewers had flagged and the designer
  deferred: the pocket floor was set from the seat depth read off the model (0.35 mm), never measured on a print, and
  the lug stopped at the pocket's mouth. Two rules from that: (1) **a pocket that holds a part axially should set
  both axial directions itself**, floor and roof with the part's thickness plus a few tenths between them and lead-ins
  at the mouth, so the rest of the assembly's seat depth does not matter; (2) **a pocket the builder cannot see into
  from any side will be used wrong**: a closed box with one obvious open mouth reads correctly in the slicer and in
  the hand, an open channel whose slot is hidden under a flare does not. If a number the design depends on is
  "unverified", the coupon that measures it comes before the coupon that depends on it.
- **And the closed box jammed too** (next print, same day), with the part barely in the mouth. Rule (1) above had been
  read as "a few tenths": a 2.0 mm bar in a 2.3 mm slot only fits when the unmeasured seat lands in a 0.3 mm window,
  the roof of a box is a drooping overhang, and a 0.3 mm "lead-in" at 90° is a wall. Three more rules: **give the
  part a millimetre, not tenths**, when its position rides on a number nobody measured, and let one face (the floor
  the pull lands on) do the holding while the other only closes the box; **a lead-in is a ramp**, not a step (a
  staircase of 0.1 mm steps over 1.2 mm is fine in a revolved profile); and **run the fit check at both ends of the
  unmeasured range and through the whole motion, with a control just past it that must collide**. A check that
  places the part "centred in the slot" tests the one position where a tight slot cannot jam.
- **A hole that two moving parts share goes in one of them.** A cable hole split across a seam that turns cannot line
  up at insertion and needs a widening as long as the turn; a slot through one wall a few mm off the seam, hidden
  where the assembly sits, needs nothing and leaves the seam a plain ring.

What the research found for the alternatives, for the record: large printed
threads work (screw-together spheres exist on Printables; 2–4 mm pitch, 0.25–0.45 mm flank offset, axis along Z) and
bayonets work (twist-lock containers; 3–4 lugs, 0.3–0.5 mm running gaps, a detent against back-off), but both turn
one half relative to the other, which a seam-crossing cable or a feature straddling the seam rules out, and a smooth
ball gives no grip for the twist.

## Retention checks in the generator

**Retention: check each load direction, not just clearance.** A set of clearance checks ("no overlap", "clear of
the shell", "foot touches the wall") is invariant under "held by nothing": a bracket that let the servo lift
straight out along its shaft passed every one. For every mounted or coupled part write down what resists each load
direction (torque, pull along the shaft, lift, sideways) and assert it in the generator: tabs on a ledge, a screw
head on a floor, teeth in a wall. Give every geometric check a positive control (a deliberate collision or a removed
feature that must make it fail), or the check may be blind. Two blind spots found by mutation on 2026-10-28: a check
that is symmetric under mirroring the part passes a mount built on the wrong side (only an unrelated "one solid
piece" check caught it), and nothing in a set of fit checks sees an upside-down print orientation. Assert the side
(which half-space the locating feature lies in) and the orientation (bed footprint area, the lowest face, which way
a pocket opens) as their own checks. Two more from the same day's reviews: a check that reads the same with a
mechanism open as closed (a pin that "opens" by zero millimetres still passed "open clears the lower block") cannot
see a mechanism that never opens, so assert the state change itself (pin out of the lower tunnel, with a not-quite
position as the control); and when identical printed copies of a chiral part are placed at several sites, the
generator must not mirror the part at any site, because the printed copies cannot build the mirror. Model each
site's arrangement with the one part as printed.

## Sources

Bayer MaterialScience, "Snap-fit joints for plastics: a design guide" (and the Covestro copy); BASF snap-fit design
manual; Covestro engineering polymers brochure; Formlabs, "Designing 3D printed snap-fit enclosures"; Hubs, "How to
design snap-fit joints for 3D printing"; CLT 3D Printing, "Designing snap fits for FDM"; Loftsmith snap-fit and
print-in-place hinge guides; minicad.io; 3dprinterstuff.com; layerx3d; filamentfeed; buildcad.ai and the3dai hinge
generators; grandpacad printable connectors; mechanics.ju.se creep chapter; thrinter.com creep test (2018);
totalelement, magnetenspecialist.nl, propbuilds and draftid on magnets; engineerdog DFA tips; sekkei-tech on
poka-yoke; Hackaday enclosure write-ups (the snap latch case).
