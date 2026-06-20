# HFSS Batch And Troubleshooting

Use this reference whenever running HFSS, generating direct VBS fallback scripts, debugging batch failures, or interpreting solver output.

## Batch Execution Strategy

Use a staged workflow for new models:

1. Generate the model and save the `.aedt` project without solving.
2. Run HFSS batch once and check that geometry, ports, boundaries, setup, and project save succeed.
3. Add `oDesign.Solve Array("SetupName")`.
4. After solving succeeds, add network/report exports.
5. Parse outputs and summarize results.

This isolates geometry/script errors from solver/export errors.

If disk space, runtime, or mesh growth becomes the limiting problem, switch to `fast-approximation.md` before changing the physical design.

## Temp Directory And Disk Space

HFSS may use the user TEMP/TMP location even when the project is saved elsewhere. Large 3D solves can fail or stall when C: is nearly full.

- Check free space before long solves with `Get-PSDrive -PSProvider FileSystem`.
- Prefer a large local scratch directory such as `E:\HFSS` for batch runs when C: is tight.
- In PowerShell batch runs, set `$env:TEMP` and `$env:TMP` before launching `ansysedt.exe`.
- Confirm the active temp path from the latest HFSS log segment; look for `Temp directory: ...`.
- If a solve failed due to temp storage, rerun only after the temp location and free space are confirmed.

## MATLAB Failure Fallback

If `matlab -batch ...` fails because of license checkout, activation, path, or display issues:

- Do not block the task if the VBS can be generated another way.
- Create a small Python or PowerShell VBS generator that writes the same HFSS commands directly.
- Keep the MATLAB driver script as the primary artifact when the user wants MATLAB integration.
- Run `ansysedt.exe /RunScriptAndExit "<script.vbs>"` on the generated VBS.

Record the fallback in the output so the user knows MATLAB did not run.

## VBS Line Continuation Rules

VBScript calls generated for HFSS arrays are sensitive to `_` line continuations.

- Every continued line must end with ` _`.
- Do not add `_` after the final line of a statement.
- When nested arrays continue after a closed parenthesis, the line should still end with `_`.
- A common failure is `Script Error (Code 800a03ee)` near lines like `"CharImp:=", "Zpi")`; check missing continuation underscores or mismatched parentheses.

## Closed Polyline Sheets

For sheet faces created with `oEditor.CreatePolyline`:

- Use `IsPolylineCovered:= true`.
- Use `IsPolylineClosed:= true`.
- Repeat the first point as the final point.
- Create segments for each edge, including the closing edge from the last unique point to the repeated first point.

If HFSS reports `Fail to cover lines. The given curve is open`, the loop was not actually closed even if `IsPolylineClosed` was set.

## Wave Port Placement

HFSS wave ports must see solve-inside material on one side only.

- Place external wave ports on a boundary face of the simulation domain.
- If a port lies inside an air box, HFSS may report: `A wave port must have 'solve inside' objects on one side only`.
- For a waveguide-fed antenna, align the air-box back boundary with the wave-port plane, or model the back side as properly PEC-backed if an internal port is intended.
- Ensure the port sheet exactly spans the waveguide cross-section and the integration line points along the intended E-field direction.

## Solve And Export Order

Use this order in batch scripts:

```vbscript
oProject.SaveAs "path\model.aedt", true
oDesign.Solve Array("SetupName")
Set oModule = oDesign.GetModule("Solutions")
oModule.ExportNetworkData "", Array("SetupName:SweepName"), 7, "path\network.m", Array("All"), true, 50
Set oModule = oDesign.GetModule("ReportSetup")
oModule.CreateReport "S11", "Modal S Parameter", "Rectangular Plot", "SetupName : SweepName", _
    Array("Domain:=", "Sweep"), Array("Freq:=", Array("All")), _
    Array("X Component:=", "Freq", "Y Component:=", Array("dB(S(Port1,Port1))")), Array()
oModule.ExportToFile "S11", "path\s11.csv"
oProject.SaveAs "path\model.aedt", true
```

Do not export solution data before `oDesign.Solve` completes.

## Log Interpretation

HFSS appends to existing `.log` files. Always inspect the latest batch segment, not the whole file.

Look for:

- `Starting Batch Run`: batch started.
- `Stopping Batch Run`: batch ended.
- `Normal completion of simulation`: solve succeeded.
- `Interpolating frequency sweep complete. Converged.`: sweep succeeded.
- `Interpolating frequency sweep did NOT converge`: data may export, but treat it as approximate unless the user explicitly accepts a trend-only result.
- `[error]` in the latest segment: current failure.

Use:

```powershell
python .\hfss-design-optimizer\scripts\summarize_hfss_log.py path\to\model.log
```

## Process And File Checks

During a solve:

- `ansysedt.exe` means AEDT is running.
- `hf3d.exe` means the HFSS solver is active.
- `.aedt.lock` means the project is open or being written.
- `.aedtresults/` and `.asol` files indicate solver artifacts.

After a successful solve/export, expect:

- Updated `.aedt`.
- `.aedtresults/` folder.
- Exported `.csv`, `.m`, Touchstone, or other requested files.

If HFSS reports normal completion but no result files appear, inspect the export calls and setup/sweep names before rerunning the solver.

## Result Summary

For S-parameter CSV files:

```powershell
python .\hfss-design-optimizer\scripts\parse_hfss_csv.py s11.csv --target-ghz 10 --y-column dB --json
```

Report:

- Sweep point count.
- Target-frequency S-parameter.
- Minimum S-parameter and frequency.
- Bandwidth for the requested threshold when applicable.



