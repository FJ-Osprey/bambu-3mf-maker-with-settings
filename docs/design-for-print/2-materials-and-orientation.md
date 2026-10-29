# 2. Materials, print orientation and strength settings

Back to the [entry point](../DESIGN-FOR-PRINT.md). Tags: *settled*, *disputed*, *untested here*.

## Published numbers

"X-Y" is a test bar printed lying flat (pulled along its layers); "Z" is printed standing (pulled across them).

| Source | Tensile | Modulus | Elongation | Flexural | Impact | Heat |
|---|---|---|---|---|---|---|
| Bambu PLA Basic, Bambu's TDS (X-Y / Z) | 35 ± 4 / 31 ± 3 MPa | (bending) 2750 ± 160 MPa | at break 12.2 ± 1.8 / 7.5 % | 76 ± 5 / 59 ± 6 MPa | Charpy unnotched 26.6 / 13.8 kJ/m², notched 7.9 | HDT 57 °C at 0.45 MPa |
| Bambu PETG Basic, Bambu's TDS V3.0 (X-Y / Z) | 32 ± 4 / 28 ± 4 MPa | — | 11.2 / 5.7 % | 65 / 48 MPa | 52.7 / 13.6 kJ/m² | HDT 69 °C at 0.45 MPa, Tg 68 °C |
| Prusament PLA, Prusa's TDS (horizontal / vertical XZ specimens) | yield 51 ± 3 / 59 ± 2 MPa | 2.3 / 2.4 GPa | at yield 2.9 / 3.2 % | 83 / 99 MPa | Charpy 13 / 14 kJ/m² | — |

Sources: Bambu PLA Basic and PETG Basic technical data sheets (PDFs linked from the store pages; PETG read from a
copy, and Bambu has revised that sheet since, so re-check before relying on a PETG figure), Bambu filament guide PDF
(HDT, ABS/ASA), prusament.com PLA TDS 2021-10. Prusament's "vertical XZ" is a specimen standing on its edge, not the
across-layers case.

## Layer lines: the weak direction

- **Across the layers is the weak direction.** Bambu's own sheets put PLA's across-layer tensile at 89 % of in-plane,
  bending 78 %, elongation 60 %, impact about half. Independent tests are harsher: CNC Kitchen's standing hooks held
  55 % of the flat ones in Prusament PLA, 46 % in PETG and 29 % in ASA, and standing tensile bars about half (*settled*
  that it is weaker; *disputed* how much: 50-90 % depending on the test and settings). Design for about 50 % across
  layers when it matters, and expect it to fail suddenly.
- **Orient the part so the load runs along the layers,** never pulling them apart or bending them open (peel). A part
  that splits across its layers can be several times stronger turned on its side; if no single orientation suits every
  load, split the part and join it (Prusa forum; Hubs; Rahix R1.1) (*settled*). Snap arms, hooks and clips lie flat on
  the bed so they bend in the plane of the layers (section 5).
- **Layer height**: up to about half the nozzle (0.2 mm on a 0.4 nozzle) costs little strength; 0.3 mm held about
  half the load between layers in CNC Kitchen's test and 0.4 almost nothing; one study measured about 11 % lost going
  from 0.1 to 0.2 (*disputed* below 0.2, *settled* that thick layers are weak).

## Choosing a material for a functional part on an open-frame A1 mini

- **PLA**: stiffest and strongest in short tests (flat hooks: PLA 73 kg, ASA 57, PETG 55; stiffness 3300 vs 2300 vs
  1900 MPa, CNC Kitchen), easy to print, accurate. Brittle: it snaps rather than bends. Creeps the worst of the common
  plastics under a sustained load (short-term creep study in Strojniški vestnik). Softens from about 55-60 °C (a car in
  the sun, a hot enclosure, near a lamp). Good for: rigid parts, enclosures, anything at room temperature and lightly
  loaded.
- **PETG**: tougher (it bends and yields before it breaks; "never snapped through, just stretched"), takes about twice
  the snap-fit strain of PLA, about 12-15 °C more heat. Weaker across layers on an open printer (Bambu says enclosed
  printing improves it), strings more, and Bambu's PETG HF "must be dried before use". Good for: snap fits, clips,
  hinges, anything warm or knocked about.
- **ASA, ABS, PC, nylon**: Bambu does not recommend them on the A1 mini (open frame: warping, parts detaching, weak
  layers); small low-infill parts at most (Bambu wiki A1 mini FAQ and filament material table) (*settled*). So the
  practical choice on this printer is PLA or PETG (and TPU for flexible parts).
- **Heat, cold, sunlight**: PLA HDT about 54-57 °C, PETG 65-69 °C, ABS about 87, ASA about 100 (Bambu). At 0-10 °C
  PLA is a little more brittle and fits do not change.

## Design numbers for a back-of-envelope check (PLA)

Tensile 30 MPa, shear about 18 MPa (0.6 × tensile), bearing or compressive about 50 MPa, modulus 2.5 GPa, and keep
**sustained** stress under about 5-10 MPa because PLA creeps (a clamped screw loses preload over days; a press fit
relaxes; a latch held bent relaxes). Form holds, friction doesn't: teeth, ledges, screw heads on floors.

## Slicer settings that matter for strength

- **Walls before infill.** More perimeters raise strength more than more infill: hooks with 2 walls held 20 kg, 4 walls
  33 kg, at the same infill (CNC Kitchen) (*settled*). Thin features (snap arms, pins under about 4 mm) end up solid
  walls anyway; give them 3-4 walls.
- **Infill** matters for thick parts: PLA bars bent at 61 MPa with 30 % infill, 91 MPa at 100 % (PETG 49 vs 72; CNC
  Kitchen, "3D prints or wood"). Pattern matters less; gyroid or cubic at 15-30 % is the usual default (*disputed* in
  the details).
- **Hotter prints bond layers better**: standing PLA bars went from 20 MPa at 190 °C to about 40 MPa at 210-230 °C;
  PETG peaked near 230-245 °C (CNC Kitchen, 2020, one filament). Print at the upper half of the filament's range for
  strength, dry filament, and less part cooling helps layer bond (*settled* direction).
- **Wider lines** (up to about 150 % of the nozzle) bond layers better (CNC Kitchen, 2019).
- **Brick layers** (Bambu Studio/Orca option that staggers walls) gained 10-14 % layer adhesion in one test (CNC
  Kitchen, 2024) (*untested here*).

## Sources

Bambu PLA Basic TDS, PETG Basic TDS V3.0 and filament guide; Prusament PLA TDS; Bambu wiki A1 mini FAQ and filament
material table; CNC Kitchen: "Comparing PLA, PETG & ASA", "What's stronger, 3D prints or wood", "The effect of
extrusion width", "Brick layers", temperature vs strength video; Strojniški vestnik short-term creep study (PLA, ABS,
CPE, PC, nylon); mechanics.ju.se creep chapter; University of Warmia and Mazury layer-height study; Springer review
(10.1007/s00170-023-11270-y); Rahix design guide; Hubs FDM design guide.
