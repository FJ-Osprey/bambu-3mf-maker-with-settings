# 6. Adhesives and welding

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*. Glue is rung 5 of
"how to hold two parts together": it is the clamp, never the locator.

## Joint shape first

- **A printed feature locates, the glue only retains.** Give glued parts a socket, a tongue and groove, two pins in
  two holes, or a step to seat against, so they go to one position by themselves and nothing has to be held still
  while the glue cures. "Glue it where it lands" is not a design (section 0).
- **Load the glue in shear or compression, not peel.** Glue resists sliding and squeezing far better than one edge
  being lifted; printed parts glued with CA "are much easier twisted or peeled than pulled apart" (Prusa) (*settled*).
  Overlap joints and sockets put the glue in shear; a butt joint end to end puts it in peel at the first knock.
- **Glue gap**: a thin, even gap, roughly 0.1-0.3 mm, is what the adhesive makers design for; CA wants the tightest
  (Loctite, 3M and Sika guidance, seen only as search extracts) (*untested here*). A loose socket filled with glue is
  weak; a press-fit socket leaves no room for glue. Sand the faces, remove the dust, press or clamp while it cures.

## Which glue (PLA and PETG)

| Glue | Measured on printed PLA (Prusa quick test, one sample each) | Use for | Notes |
|---|---|---|---|
| CA (super glue), medium viscosity | about 10 MPa PLA, 13 MPa PETG | close-fitting joints, magnets in pockets | brittle under ongoing stress and across gaps; full strength after 8-24 h |
| 5-minute epoxy | about 6 MPa PLA, 5 MPa PETG | gap filling, larger faces, magnets | weaker than the best CA on smooth coupons in this test; tougher in peel per other guides; full cure before load |
| Hot glue | not tested on PLA; one vendor page gives EVA 0.2-0.8 N/mm in peel on polyethylene and 0.5-3 MPa lap shear on polypropylene, a general study under 4 MPa (*untested here*) | tacking unloaded parts, holding wires | not a structural joint; peels off with a knife; don't use it on magnets (heat weakens them) |
| Polystyrene model cement | one product 0 MPa on PET and ASA; another 3.2 MPa PLA, 3.4 MPa PET | not structural | Correction (2026-10-29, review): the earlier "0 MPa, nothing" was one product |

(*untested here*: one quick, unreplicated test; the ranking between CA and epoxy depends on the joint type.)

- **Solvent welding**: ABS and ASA weld with acetone (*settled*). PLA: Prusa says acetone glues it; other sources say
  it does little (*disputed*). PETG resists every chemical a hobbyist normally has (Prusa; a solvent-resistance study);
  reports of welding it with ethyl acetate or dichloromethane are anecdotal (*disputed*, and both are hazardous).
- **Low-surface-energy plastics** (acetal/POM and nylon, e.g. servo horns): CA and epoxy don't grip them without a
  primer. Screw, wire or zip-tie a horn; don't glue it.
- **Friction welding or a 3D pen** (melting filament into the seam): mentioned by makers, no strength data found
  (*untested here*).

## Sources

Prusa blog, "The great guide to gluing and assembling 3D prints" (2021, tensile test table); sigmafilament.com (best
glue for PLA/PETG); natecue.com gluing guide; silitech.ch on bonding POM; learn.adafruit.com animatronics guide;
loctiteproducts.com (how to glue PLA); Devcon 5-minute epoxy data sheet; Loctite 3D-printing bonding guide, 3M and
Sika bond-gap guidance (search extracts only); totalelement on magnets and hot glue.
