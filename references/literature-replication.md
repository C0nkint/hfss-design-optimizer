# Literature Reproduction Workflow

Use this when reproducing an antenna, microwave circuit, metamaterial, filter, waveguide, or RF structure from a paper, PDF, thesis, patent, or image.

## Extraction Pass

Extract and tabulate:

- Structure type and intended operating band.
- All dimensions with units.
- Materials: dielectric constant, loss tangent, conductivity, thickness, metal type.
- Feeding method: lumped port, wave port, coax, microstrip, CPW, Floquet, or discrete source.
- Boundary conditions: radiation, PEC/PMC, periodic, master/slave, symmetry planes.
- Simulation frequency range and mesh/convergence settings if stated.
- Measured/simulated outputs: S-parameters, gain, efficiency, pattern cuts, axial ratio, current distribution.

If the source has figures only, estimate dimensions only when scale is unambiguous. Otherwise ask for clarification or mark as an assumption.

## Assumption Table

Always produce an assumption table for missing details. Common missing items:

- Air-box size.
- Metal thickness.
- Port sheet size and integration line.
- Exact material library name.
- Substrate loss tangent.
- Mesh operation or adaptive pass settings.
- Connector/coax details.
- Whether finite ground, infinite ground, or radiation boundary was used.

## Reproduction Build Order

1. Build the baseline geometry using paper dimensions.
2. Add materials exactly as specified; create custom material if needed.
3. Add ports and boundaries from the paper.
4. Add the same sweep range and report types.
5. Export comparable data.
6. Compare against paper curves.
7. Tune only parameters justified by ambiguity, manufacturing tolerance, or missing details.

For expensive structures, create two solver profiles in the script:

- Fast profile: coarse mesh, relaxed convergence, fewer sweep points, and a visibly named sweep such as `SweepFast...`.
- Final profile: paper-matching sweep range, tighter convergence, and mesh settings suitable for comparison.

Use the fast profile only to catch geometry, port, and transition mistakes early. Do not claim paper agreement from a nonconverged or coarse run.

## Mismatch Triage

When a rough run is far from the paper target, inspect modeling assumptions before tightening the mesh:

- Port type, port plane placement, reference impedance, and integration line direction.
- Whether the port launches the intended mode and whether de-embedding is needed.
- Transition geometry, taper overlap, conductor width/thickness, and any omitted discontinuities.
- Material loss, conductivity, sheet-metal versus finite-thickness metal, and substrate roughness assumptions.
- Air gaps, assembly offsets, finite ground effects, and radiation boundary distance.
- Whether the paper result includes fixtures, probes, calibration planes, or measured de-embedding.

## Curve Comparison

When paper data is available as CSV/digitized points:

- Interpolate simulation and paper data to a common frequency grid.
- Compare resonance frequency shift.
- Compare minimum S11 or peak gain.
- Compare bandwidth endpoints.
- Report absolute and relative deviations.

When only plots are available:

- State qualitative match: resonance location, bandwidth, level, pattern shape.
- Avoid claiming exact reproduction without digitized data.

## Output

For a reproduction task, produce:

- `paper_parameters.md`: extracted dimensions and assumptions.
- MATLAB script that generates the HFSS model.
- Export settings matching the paper.
- A comparison checklist.
- A list of unresolved ambiguities and likely causes of mismatch.

