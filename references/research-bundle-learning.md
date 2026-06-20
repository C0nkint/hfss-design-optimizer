# Research Bundle Learning

Use this when the user provides papers together with HFSS/AEDT/VBS/MATLAB projects, S-parameter exports, figures, or logs and asks the skill to learn the innovation point or improve local HFSS design methods.

## Goal

Turn a paper plus simulation-file bundle into reusable HFSS design knowledge. Separate project-specific facts from general skill improvements.

## Intake

1. Keep the original paper and simulation files unchanged.
2. Run the bundle analyzer from the skill root or workspace:

```powershell
python .\hfss-design-optimizer\scripts\analyze_research_bundle.py "path\to\bundle"
```

The script writes `.hfss_skill_learning\bundle_learning_summary.md` under the bundle by default.

3. Open the generated summary and then inspect the most relevant original files listed there.
4. If PDF text extraction fails, use rendered pages, OCR, or manual excerpts before drawing conclusions.

## Innovation Map

Extract a table with:

- Claimed innovation or contribution.
- Baseline method being improved.
- Electromagnetic mechanism or design idea.
- Geometry, material, feed, boundary, packaging, or calibration features that implement it.
- Target metrics and reported evidence.
- Simulation artifacts that confirm or contradict the claim.
- Missing details that limit reproduction confidence.

Ground each item in paper snippets, equations, figure captions, VBS/MATLAB variables, AEDT setup names, exported CSV/Touchstone metrics, or logs.

## Simulation Gap Report

Compare the paper method against the supplied simulation files:

- Geometry: dimensions, tapers, gaps, ports, finite ground, air boxes, fixtures, probes, and symmetry.
- Materials: dielectric constant, loss tangent, conductivity, roughness, finite metal thickness, and sheet approximations.
- Excitation: port type, calibration/de-embedding plane, integration line, launched mode, reference impedance.
- Solver: adaptive frequency, passes, mesh operations, sweep type, convergence status, and temp/storage issues.
- Results: frequency range, S-parameter trends, target-frequency values, bandwidth, insertion loss, and mismatches.

When the simulation result is far from the paper target, inspect assumptions before tightening mesh.

## Skill Improvement Filter

Promote only reusable lessons into the skill:

- Generic modeling rules, validation checks, solver profiles, parsers, templates, or triage steps belong in `references/`, `scripts/`, or `assets/templates/`.
- Paper-specific dimensions, one-off material values, and project results belong in the project folder unless the user asks for a named reference case.
- Every proposed skill update should state the trigger condition, the reusable action, and the validation method.

## Output

Provide:

- `innovation_map.md` or a concise innovation table.
- `simulation_gap_report.md` or an equivalent section.
- A `skill_update_plan.md` when the user wants the skill changed.
- A list of files parsed, files skipped, and parsing limitations.

If the user asks to update the skill, implement focused changes and validate with `quick_validate.py`, Python syntax checks for scripts, and MATLAB script validation for changed templates.