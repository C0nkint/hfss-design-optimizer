% Literature reproduction template for HFSS-MATLAB-API.
% Fill the parameter block from a paper extraction table before running.

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
fastApprox = false;

paperId = 'paper_reproduction';
designName = 'Reproduction';
tmpPrjFile = fullfile(pwd, [paperId, '.aedt']);
tmpScriptFile = fullfile(pwd, [paperId, '.vbs']);
csvPrefix = fullfile(pwd, [paperId, '_sparams']);

% Replace this block with extracted paper parameters.
units = 'mm';
fCenterGHz = 2.45;
fStartGHz = 2.0;
fStopGHz = 3.0;
nSweepPoints = 401;
sweepMaxSolutions = 101;
sweepTolerance = 0.5;
maxDeltaS = 0.02;
maxPass = 15;
minPass = 2;
minConvPass = 2;
maxRefinement = 20;
sweepName = 'Sweep';
substrateName = 'Paper_Substrate';
substrateEr = 4.4;
substrateTanD = 0.02;
substrateH = 1.6;
substrateX = 80;
substrateY = 70;
metalMaterial = 'pec';
airMargin = 35;

% Example placeholder geometry: rectangular microstrip radiator.
radiatorL = 29;
radiatorW = 38;
feedL = 22;
feedW = 3;

if fastApprox
    nSweepPoints = 41;
    sweepMaxSolutions = 15;
    sweepTolerance = 1.0;
    maxDeltaS = 0.08;
    maxPass = 2;
    minPass = 1;
    minConvPass = 1;
    maxRefinement = 10;
    sweepName = 'SweepFast';
end

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, designName);

hfssAddMaterial(fid, substrateName, substrateEr, 0, substrateTanD);

hfssBox(fid, 'Substrate', [-substrateX/2, -substrateY/2, -substrateH], ...
    [substrateX, substrateY, substrateH], units);
hfssAssignMaterial(fid, 'Substrate', substrateName);

hfssRectangle(fid, 'Radiator', 'Z', [-radiatorL/2, -radiatorW/2, 0], ...
    radiatorL, radiatorW, units);
hfssRectangle(fid, 'Feed', 'Z', [-radiatorL/2 - feedL, -feedW/2, 0], ...
    feedL, feedW, units);
hfssUnite(fid, {'Radiator', 'Feed'});
hfssAssignMaterial(fid, 'Radiator', metalMaterial);

hfssRectangle(fid, 'Ground', 'Z', [-substrateX/2, -substrateY/2, -substrateH], ...
    substrateX, substrateY, units);
hfssAssignMaterial(fid, 'Ground', metalMaterial);

hfssRectangle(fid, 'Port', 'X', [-radiatorL/2 - feedL, -feedW/2, 0], ...
    feedW, -substrateH, units);
hfssAssignLumpedPort(fid, 'Port1', 'Port', ...
    [-radiatorL/2 - feedL, 0, 0], [-radiatorL/2 - feedL, 0, -substrateH], ...
    units, 50, 0);

hfssBox(fid, 'AirBox', ...
    [-substrateX/2 - airMargin, -substrateY/2 - airMargin, -substrateH - airMargin], ...
    [substrateX + 2*airMargin, substrateY + 2*airMargin, substrateH + 2*airMargin], ...
    units);
hfssAssignRadiation(fid, 'Radiation', 'AirBox');
hfssSetTransparency(fid, {'AirBox'}, 0.95);

hfssInsertSolution(fid, 'Setup', fCenterGHz, maxDeltaS, ...
    maxPass, minPass, minConvPass, maxRefinement);
hfssInterpolatingSweep(fid, sweepName, 'Setup', fStartGHz, fStopGHz, ...
    nSweepPoints, sweepMaxSolutions, sweepTolerance);
hfssSolveSetup(fid, 'Setup');
hfssCreateReport(fid, 'S11', 2, 1, 'Setup', sweepName, [], 'Sweep', ...
    {'Freq'}, {'Freq', 'dB(S(Port1,Port1))'});
hfssExportToFile(fid, 'S11', csvPrefix, 'csv');

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

if runHFSS
    hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
end

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);




