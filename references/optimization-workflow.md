# Optimization Workflow

Use this when the task includes tuning, sweep, optimization, matching, bandwidth improvement, gain improvement, or paper-curve fitting.

## Objective Definition

Convert the user's goal into a scalar objective plus constraints.

Common objectives:

- Resonance match: minimize `abs(f_res - f_target)`.
- Return loss: minimize `S11_dB` at target frequency.
- Bandwidth: maximize frequency span where `S11_dB < -10`.
- Matching plus compactness: weighted objective of return loss, bandwidth, and size.
- Gain/directivity: maximize far-field metric at selected angle/frequency.
- Literature fitting: minimize curve error against digitized paper data.

Always state the objective and constraints before running a large sweep.

## Recommended Stages

1. Coarse sweep: broad ranges with few points.
2. Local refinement: narrower ranges around best cases.
3. Confirmation run: higher mesh quality or tighter setup.
4. Sensitivity check: perturb key parameters and report robustness.

## HFSS Loop Pattern

For each candidate:

1. Generate a candidate-specific `.vbs` and `.aedt`.
2. Run HFSS only if the user requested execution and paths are valid.
3. Export CSV, Touchstone, or MATLAB network data.
4. Parse results.
5. Compute objective.
6. Save a row in `optimization_log.csv`.

Keep failed candidates in the log with an error note.

## Parameter Strategy

Use deterministic sweeps first:

- Single-parameter sweep for dominant dimensions.
- 2D grid for coupled dimensions such as patch length and feed inset.
- Coordinate search around the best point.

Use stochastic methods only after deterministic sweeps are too expensive or insufficient. If using genetic, particle swarm, or Bayesian methods, make the random seed explicit.

## Result Parsing

For report CSV files, use:

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py result.csv --target-ghz 2.45 --y-column S
```

For MATLAB network export, generated files usually define `f`, `S`, and `Z`; MATLAB can `run(tmpDataFile)` and compute metrics directly.

## Avoiding Expensive Mistakes

- Start with `runAndExit=false` for the first generated script.
- Do not launch a large optimization before one baseline run succeeds.
- Use coarse mesh/pass settings for exploration and tighter settings only for final confirmation.
- Save every candidate to a unique directory or unique file prefix.
- Never overwrite the best run without copying its parameters and exported data.

## Reporting

Provide:

- Search space and units.
- Number of successful and failed candidates.
- Best parameters.
- Best metric values.
- Comparison to baseline.
- Remaining uncertainty: mesh convergence, missing material data, port assumptions, or paper ambiguity.
