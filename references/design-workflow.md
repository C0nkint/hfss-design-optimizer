# HFSS Design Workflow

Use this checklist for new models.

## 1. Capture Inputs

Create a parameter table with:

- Target frequency and sweep range.
- Unit system.
- Structure type and coordinate orientation.
- Substrate dimensions, dielectric constant, loss tangent, and thickness.
- Metal material and thickness or sheet approximation.
- Port type, reference impedance, and integration line direction.
- Radiation, ground, periodic, or waveguide boundaries.
- Desired exports: S-parameters, impedance, gain, directivity, radiation pattern, fields.

If the user omits non-critical details, choose conservative HFSS defaults and list assumptions.

## 2. Choose Template

- Simple antenna or generic project: `assets/templates/basic_hfss_project.m`
- Parameter sweep or optimization: `assets/templates/parametric_sweep_project.m`
- Literature reproduction: `assets/templates/literature_reproduction_project.m`

Copy the template into the task workspace and adapt it.

## 3. Build MATLAB Script

Use the fixed order:

1. Initialize paths and file names.
2. `fopen` VBS output.
3. `hfssNewProject`.
4. `hfssInsertDesign`.
5. Define design variables if helpful.
6. Build geometry.
7. Assign materials and visual properties.
8. Add ports and boundaries.
9. Add solution setup and sweeps.
10. Add reports and exports.
11. Save project.
12. Close VBS.
13. Optionally run HFSS.
14. Remove API paths.

## 4. Geometry Rules

- Prefer named parameters over numeric literals.
- Use `hfssRectangle` for sheet metals, lumped-port sheets, ground planes, and wave-port faces.
- Use `hfssBox` for substrates, air boxes, and dielectric volumes.
- Use `hfssCylinder`, `hfssHollowCylinder`, and `hfssCircle` for vias, coax feeds, and circular ports.
- Use `hfssPolyline` plus `hfssConnect` for profile-defined sheets such as horns.
- Use `hfssDuplicateAlongLine` for arrays.
- Assign materials after boolean operations when object names may change.

## 5. Boundary And Port Rules

- Radiation: create an air box at least about `lambda/4` away for compact antennas; use larger margins for electrically large or high-Q structures.
- Perfect E: use for ideal sheet metal and ground planes.
- Lumped port: create a small sheet across the gap/feed and define a clear integration line from negative to positive conductor.
- Wave port: create a terminal sheet at a transmission-line or waveguide cross-section.
- Periodic structures: use master/slave or Floquet ports and document unit-cell boundaries.

## 6. Solve And Export

- Use `hfssInsertSolution` at the main frequency in GHz.
- Use `hfssInterpolatingSweep` for broadband S-parameters.
- Use `hfssCreateReport` and `hfssExportToFile` for CSV plots.
- Use `hfssExportNetworkData` for MATLAB `.m`, Touchstone, or tabular network data.
- Add far-field setup before far-field reports.
- If the user asks for a quick approximate result, add a named coarse solver profile before running HFSS; see `fast-approximation.md`.
- For first-time generated models, save and run a geometry-only batch before solving.
- After geometry succeeds, add solve commands before export commands.
- When HFSS runs in batch, inspect only the latest log segment; old errors may remain in the same `.log`.

## 7. Validation Before Run

Run:

```powershell
python .\hfss-design-optimizer\scripts\validate_matlab_hfss_script.py path\to\script.m
```

Check that:

- `apiRoot` resolves to the bundled `assets/hfss-api-master` path and `hfssExePath` is correct.
- Every port references an existing sheet object.
- Every boundary references existing objects.
- Setup and sweep names match report/export calls.
- File paths are full paths or created with `fullfile`.

For HFSS batch execution details and common fixes, read `hfss-batch-troubleshooting.md`.

