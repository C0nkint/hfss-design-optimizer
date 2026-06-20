---
name: hfss-design-optimizer
description: Design, generate, simulate, optimize, and reproduce Ansys HFSS models using the bundled HFSS-MATLAB-API. Use for HFSS/AEDT/VBS/MATLAB scripting tasks, antenna/RF/microwave model creation, parameter sweeps, S-parameter/gain/bandwidth optimization, reproducing HFSS structures from papers or PDFs, and learning reusable design methods from paper plus simulation-file bundles.
---

# HFSS Design Optimizer

Use this skill to turn RF/microwave design requirements, literature descriptions, and paper-plus-simulation bundles into MATLAB scripts and reusable HFSS design methods using the bundled HFSS-MATLAB-API.

## Local Defaults

- HFSS executable: `F:\AnsysEM\v221\Win64\ansysedt.exe`
- Bundled API root: `F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master`
- MATLAB API style: write `.vbs` with `fprintf` wrappers, save an `.aedt`, then optionally run HFSS with `hfssExecuteScript`.
- Movable skill override: set `HFSS_DESIGN_OPTIMIZER_ROOT` to the skill folder when this skill is copied elsewhere.

If the HFSS executable path is invalid, ask the user for the replacement before attempting to run HFSS. If the bundled API path is invalid, first check whether `HFSS_DESIGN_OPTIMIZER_ROOT` should point to the current skill folder. Generating scripts does not require HFSS to be installed.

## Workflow

1. Clarify the design target only when required values are missing: structure type, center frequency, units, substrate/materials, ports, boundary type, sweep range, and target metric.
2. Load `references/api-map.md` before writing code that calls this API.
3. For a new model, load `references/design-workflow.md`; for HFSS batch execution, direct VBS fallback, solve monitoring, or troubleshooting, load `references/hfss-batch-troubleshooting.md`; for an optimization task, load `references/optimization-workflow.md`; for paper reproduction, load `references/literature-replication.md`; for paper plus simulation-file learning, load `references/research-bundle-learning.md`.
4. Prefer copying and adapting a template from `assets/templates/` over writing a script from scratch.
5. Generate a MATLAB driver script that creates a VBS file, saves the AEDT project, and optionally executes HFSS. If MATLAB cannot start because of licensing, generate the VBS directly with a small script and preserve the MATLAB version for later use.
6. Validate generated MATLAB scripts with `scripts/validate_matlab_hfss_script.py` before presenting them as ready to run.
7. When the user asks for a fast approximate result or the first solve is too slow, load `references/fast-approximation.md` and switch to an explicit coarse mode before rerunning.
8. For a first HFSS run, prefer a two-stage batch: create/save the model first, inspect or check logs, then add solve/export commands.
9. When executing HFSS, monitor the latest batch log segment with `scripts/summarize_hfss_log.py`; do not mistake old appended errors for the current run.
10. When results are available, parse exported CSV files with `scripts/parse_hfss_csv.py` and compare against the target.

## Script Pattern

Use this skeleton unless an existing project requires another pattern:

```matlab
clc; clear variables; close all;

skillRoot = getenv('HFSS_DESIGN_OPTIMIZER_ROOT');
if isempty(skillRoot)
    skillRoot = 'F:\2026fall\HFSS_SKILL design\hfss-design-optimizer';
end
apiRoot = fullfile(skillRoot, 'assets', 'hfss-api-master');
if ~exist(apiRoot, 'dir')
    error('Bundled HFSS-MATLAB-API not found: %s', apiRoot);
end
addpath(apiRoot);
hfssIncludePaths([apiRoot filesep]);

hfssExePath = 'F:\AnsysEM\v221\Win64\ansysedt.exe';
tmpPrjFile = fullfile(pwd, 'design.aedt');
tmpScriptFile = fullfile(pwd, 'design.vbs');

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, 'Design1');

% Geometry, materials, boundaries, ports, setup, reports.

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

% Use false,false while debugging so HFSS stays open after running the script.
% hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);
```

## Output Expectations

For design generation, provide:

- A parameter table with units.
- The generated or modified MATLAB file path.
- The generated AEDT/VBS/output file names.
- Instructions for running HFSS only when execution was not performed.

For optimization, provide:

- Objective function and constraints.
- Sweep/optimizer strategy.
- Best parameter set and result summary.
- Any failed runs or missing result files.

For literature reproduction, provide:

- Extracted paper parameters and assumptions.
- Missing or ambiguous details.
- The reproduction script.
- A comparison plan against the paper curves or tables.
- If a coarse or nonconverged run was used, clearly label it as a trend check and list the next geometry, port, or transition assumptions to inspect before claiming agreement.

For paper plus simulation bundle learning, provide:

- A concise innovation map grounded in paper text and simulation artifacts.
- A simulation gap report covering geometry, materials, ports, boundaries, solver setup, and exported metrics.
- Reusable skill improvement candidates separated from project-specific notes.
- The generated bundle analysis file path and any files that could not be parsed.

## Resources

- `references/local-config.md`: local paths and run assumptions.
- `references/api-map.md`: function signatures and API usage map.
- `references/design-workflow.md`: model creation checklist.
- `references/hfss-batch-troubleshooting.md`: HFSS batch execution, direct VBS fallback, solver status checks, and fixes for common failures.
- `references/fast-approximation.md`: coarse-mesh, short-sweep, and low-pass settings for quick first-look results.
- `references/optimization-workflow.md`: parameter sweep and optimization loop.
- `references/literature-replication.md`: paper-to-HFSS reproduction process.
- `references/research-bundle-learning.md`: workflow for learning innovation points and reusable HFSS design methods from paper plus simulation files.
- `references/common-hfss-patterns.md`: common geometry, boundary, port, and report patterns.
- `assets/hfss-api-master/`: bundled HFSS-MATLAB-API used by generated scripts.
- `assets/templates/`: starter MATLAB scripts to copy and adapt.
- `scripts/`: utility scripts for API indexing, MATLAB script validation, and result parsing.



