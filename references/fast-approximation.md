# Fast Approximation Runs

Use this when the user wants a quick rough HFSS result, the first solve is too slow, or a paper reproduction needs a low-cost sanity check before refinement.

## Coarse Mode Pattern

Add an explicit switch in generated MATLAB scripts:

```matlab
fastApprox = true;
includeSolveCommands = true;
```

Keep the normal paper-quality values in the default parameter block, then override them inside `if fastApprox`. Name the sweep with a visible suffix such as `SweepFast...` so exported files and logs show which mode was used.

## Starting Settings

Use these as first-pass values, then adjust by electrical size and geometry risk:

- Adaptive passes: `maxPass = 1` to `2`, `minPass = 1`, `minConvPass = 1`.
- Convergence: `maxDeltaS = 0.05` to `0.10`.
- Sweep points: 17 to 41 points over the band of interest.
- Interpolating sweep max solutions: 5 to 15.
- Interpolating sweep tolerance: `1.0` for trend-only runs.
- Mesh length operations: use coarse object-level limits on critical dielectrics and metals; start around `lambda_eff/6` to `lambda_eff/10` for dielectric volumes, then loosen only if the solver is still too slow.
- Narrow conductors or tips: do not set mesh lengths so large that the smallest feed/taper feature disappears. Use geometry simplification first when the feature itself is below the intended accuracy.

For G-band silicon/quartz interconnect first-look runs, the known workable coarse baseline is:

- Sweep: 140-220 GHz, 41 points.
- Adaptive setup: 160 GHz, `maxDeltaS = 0.08`, `maxPass = 2`.
- Mesh operations: HR silicon `0.200 mm`, metal sheets `0.150 mm`.
- Temp directory: `E:\HFSS` when C: has limited free space.

## Escalation Ladder

If the fast run is still too slow:

1. Export only the adaptive-frequency result before adding a broadband sweep.
2. Reduce sweep points to 17 and interpolating max solutions to 5.
3. Use `maxPass = 1` for a geometry/port sanity check.
4. Temporarily narrow the frequency band around the design frequency.
5. Simplify highly detailed tapers, fillets, vias, or conductor thickness if they are not the current uncertainty.

If the fast run finishes but the interpolating sweep does not converge, keep the data only as a trend check. Report the warning and avoid presenting the curve as final agreement with a paper or specification.

## Result Reporting

Always write a short result summary beside the exports:

- Solver profile: fast/coarse vs final.
- Frequency range, point count, pass limits, mesh limits, and temp directory.
- Target-frequency S-parameters and best/worst values.
- Whether the latest log segment has errors, normal completion, and sweep convergence.
- Next likely causes if the trend is far from the target: port definition, transition geometry, material loss, air gaps, boundary placement, or missing manufacturing details.
