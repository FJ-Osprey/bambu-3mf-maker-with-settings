# 7. Design for assembly and the prototyping loop

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*. Section 0 is the
short checklist; this is the reasoning behind it.

## Design for assembly (DFA)

The classic rules (Boothroyd and Dewhurst, as summarised in the LibreTexts DFM course and the DfAM literature) (*settled*):

- **Fewer parts.** A part stays separate only if it moves relative to its neighbour, is a different material, or must
  come apart for assembly or service. Printing pushes further: hinges, captive pins and chains can be printed already
  assembled ("print in place"), and several parts can become one (part consolidation). The reverse is also allowed:
  split a part when that removes supports from a mating face or puts the layers the right way under load.
- **Assemble from one direction onto a base part,** so gravity holds what is placed until it is secured, with each
  part going in by one straight motion. Secure each part as soon as it is placed.
- **Self-locating before fastening.** Each part finds its position on a printed feature (a pin, a slot, a step, a
  chamfered lead-in) before anything holds it. The fastener clamps; it does not locate: screw clearance holes always
  leave wiggle (engineerdog). Lead-in chamfers on everything that goes into something are the cheapest
  self-alignment feature there is.
- **Symmetric or obviously asymmetric, never nearly symmetric.** If a part can go in two ways and only one is right,
  add a key, offset a hole or chamfer a corner so the wrong way cannot seat (poka-yoke) (sekkei-tech; engineerdog).
- **Controlled compliance**: give the assembly one deliberately flexible element (a spring arm, crush ribs, a slot) that
  absorbs print error, instead of demanding exact fits everywhere (engineerdog) (*untested here*).
- **Serviceability**: anything that hides a mechanism opens without tools and closes the same way every time (a 45°
  snap, magnets, a slide-on lid, a bayonet). Glue and tape are not service closures.

## Insertion paths and assembly order

- Write the assembly as numbered steps before modelling the last part, and for each step name the part, the direction
  it moves in, and what it rests on. A part that has to move sideways after it is inside something usually can't.
- **Sweep each moving part along its path in the generator** and assert it clears (with a control that collides): a
  coupling that needs several millimetres of travel to press together cannot be pressed together inside a shell.
- **Fingers and tools need room too**: a screw needs a straight line for the screwdriver; a snap needs a way to reach
  its release.

## Tolerance stacks

- Errors add along a chain of parts: N parts at ±0.2 mm can be N × 0.2 off in the worst case (the root-sum-square
  estimate √N × 0.2 is the typical case). For one-off hobby builds use the worst case (Layer X; CLT 3D) (*settled* math;
  the ±0.2 per part is vendor-asserted).
- Reduce the stack: locate everything from one datum feature, not part to part; make one hole of each mounting pair a
  slot; keep fewer parts in the loop; keep mating features in the same print plane, because Z is quantised to the
  layer and XY is not (Syntax3D Lab; Layer X) (*settled*).
- A printer's accuracy is roughly ±0.1-0.3 mm in XY (Prusa FAQ: about 0.3 mm X/Y for a well-built printer, 0.05 after
  extra calibration; Rahix about ±0.1 per surface; one A1 mini owner: under ±0.3 in PLA) (*disputed*, *untested here*).

## The prototyping loop professionals use

1. **Clearances are variables.** Every fit in the model is a named parameter (one per fit class), not a number typed
   into a sketch, so a coupon result changes one value and regenerates every part (Prusa KB on iterating) (*settled*).
2. **Coupon before part.** Print just the mating feature, in the real material, orientation and settings, at several
   clearances in 0.1 mm steps, marked so they can be told apart (section 1). As stiff as the real feature, or it proves
   nothing.
3. **Check the model before printing**: one solid body per part, on the bed, fits the bed; clearances and collisions
   by geometry; each load direction resisted; each check with a positive control (section 5).
4. **Print, fit, write it down.** Record what was printed, what was measured, and what changed, in the project's notes
   and, if the lesson is general, in these files. A fit that was "a hair snug" is a number to write down next to the
   clearance that produced it.
5. **Revise one variable at a time**, reprint the coupon, then print the part.

## Sources

LibreTexts, "Design for Manufacturing (DFM)" (Northeast Wisconsin Technical College course); Politecnico di Milano
DfAM keynote review (part consolidation); engineerdog, "Design for assembly tips: building a better 3D printed linear
actuator" (2018); sekkei-tech, "Poka-yoke in design" (2026); Layer X and CLT 3D on tolerance stack-up; Syntax3D Lab
tolerances guide; Prusa KB "Modeling with 3D printing in mind" and FAQ; Rahix design guide; note.com A1 mini owner
notes (mikannohako).
