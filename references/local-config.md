# Local Config

Use these defaults for this workstation:

```text
HFSS executable:
F:\AnsysEM\v221\Win64\ansysedt.exe

Bundled HFSS-MATLAB-API root:
F:\2026fall\HFSS_SKILL design\hfss-design-optimizer\assets\hfss-api-master
```

MATLAB initialization:

```matlab
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
```

Use `fullfile(pwd, ...)` for generated `.m`, `.vbs`, `.aedt`, and exported result files.

Preferred HFSS scratch directory for large local solves:

```text
E:\HFSS
```

When C: has limited free space, set both `TEMP` and `TMP` to this directory before launching AEDT from PowerShell and confirm the path in the HFSS log.

If the skill folder is moved, set `HFSS_DESIGN_OPTIMIZER_ROOT` to the new skill root before running generated MATLAB scripts. The bundled API must live at `assets\hfss-api-master` under that root.

During debugging, execute HFSS with:

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
```

For unattended batch runs after the script is verified:

```matlab
hfssExecuteScript(hfssExePath, tmpScriptFile, true, true);
```

Always call `fclose(fid)` before `hfssExecuteScript`.

