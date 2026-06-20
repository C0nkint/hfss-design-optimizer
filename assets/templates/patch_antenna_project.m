% Microstrip patch antenna template for HFSS-MATLAB-API.
% Adjust dimensions and materials before running.

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
runHFSS = false;

projectName = 'patch_antenna';
designName = 'Patch';
tmpPrjFile = fullfile(pwd, [projectName, '.aedt']);
tmpScriptFile = fullfile(pwd, [projectName, '.vbs']);
csvPrefix = fullfile(pwd, [projectName, '_s11']);

units = 'mm';
fCenterGHz = 2.45;
fStartGHz = 2.0;
fStopGHz = 3.0;

subEr = 4.4;
subTanD = 0.02;
subH = 1.6;
subX = 80;
subY = 70;

patchL = 29.0;
patchW = 38.0;
feedL = 22.0;
feedW = 3.0;
portH = subH;
airMargin = 35;

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, designName);

hfssAddMaterial(fid, 'User_FR4', subEr, 0, subTanD);

hfssBox(fid, 'Substrate', [-subX/2, -subY/2, -subH], [subX, subY, subH], units);
hfssAssignMaterial(fid, 'Substrate', 'User_FR4');
hfssSetColor(fid, 'Substrate', [0, 128, 0]);
hfssSetTransparency(fid, {'Substrate'}, 0.35);

hfssRectangle(fid, 'Patch', 'Z', [-patchL/2, -patchW/2, 0], patchL, patchW, units);
hfssRectangle(fid, 'Feed', 'Z', [-patchL/2 - feedL, -feedW/2, 0], feedL, feedW, units);
hfssUnite(fid, {'Patch', 'Feed'});
hfssAssignPE(fid, 'PatchMetal', {'Patch'});
hfssSetColor(fid, 'Patch', [220, 170, 40]);
hfssSetTransparency(fid, {'Patch'}, 0);

hfssRectangle(fid, 'Ground', 'Z', [-subX/2, -subY/2, -subH], subX, subY, units);
hfssAssignPE(fid, 'GroundMetal', {'Ground'});

hfssRectangle(fid, 'Port', 'X', [-patchL/2 - feedL, -feedW/2, 0], feedW, -portH, units);
hfssAssignLumpedPort(fid, 'LPort', 'Port', ...
    [-patchL/2 - feedL, 0, 0], [-patchL/2 - feedL, 0, -portH], units, 50, 0);

airStart = [-subX/2 - airMargin, -subY/2 - airMargin, -subH - airMargin];
airSize = [subX + 2*airMargin, subY + 2*airMargin, subH + 2*airMargin];
hfssBox(fid, 'AirBox', airStart, airSize, units);
hfssAssignRadiation(fid, 'Radiation', 'AirBox');
hfssSetTransparency(fid, {'AirBox'}, 0.95);

hfssInsertSolution(fid, 'Setup', fCenterGHz, 0.02, 25);
hfssInterpolatingSweep(fid, 'Sweep', 'Setup', fStartGHz, fStopGHz, 401);
hfssSolveSetup(fid, 'Setup');
hfssCreateReport(fid, 'S11', 2, 1, 'Setup', 'Sweep', [], 'Sweep', ...
    {'Freq'}, {'Freq', 'dB(S(LPort,LPort))'});
hfssExportToFile(fid, 'S11', csvPrefix, 'csv');

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

if runHFSS
    hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
end

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);
