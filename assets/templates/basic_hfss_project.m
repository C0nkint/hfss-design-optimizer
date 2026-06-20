% Basic HFSS-MATLAB-API project template.
% Creates a center-fed dipole, solves an interpolating sweep, and exports
% network data. Copy this file before editing.

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

projectName = 'basic_dipole';
designName = 'Dipole';
tmpPrjFile = fullfile(pwd, [projectName, '.aedt']);
tmpScriptFile = fullfile(pwd, [projectName, '.vbs']);
tmpDataFile = fullfile(pwd, [projectName, '_network.m']);

units = 'meter';
c0 = 3e8;
fCenter = 150e6;
lambda0 = c0/fCenter;
dipoleLength = lambda0/2;
dipoleRadius = 0.01*lambda0;
gapLength = 0.02*lambda0;
airMargin = lambda0/4;

fStartGHz = 0.75*fCenter/1e9;
fStopGHz = 1.25*fCenter/1e9;
fSolveGHz = fCenter/1e9;

fid = fopen(tmpScriptFile, 'wt');
hfssNewProject(fid);
hfssInsertDesign(fid, designName);

hfssDipole(fid, 'Dipole', 'X', [0, 0, 0], dipoleLength, ...
    2*dipoleRadius, gapLength, units);
hfssAssignPE(fid, 'DipoleMetal', {'Dipole1', 'Dipole2'});

hfssRectangle(fid, 'GapSource', 'Y', [-gapLength/2, 0, -dipoleRadius], ...
    2*dipoleRadius, gapLength, units);
hfssAssignLumpedPort(fid, 'LumpedPort', 'GapSource', ...
    [-gapLength/2, 0, 0], [gapLength/2, 0, 0], units, 50, 0);

airSize = [dipoleLength + 2*airMargin, 2*airMargin, 2*airMargin];
hfssBox(fid, 'AirBox', -airSize/2, airSize, units);
hfssAssignRadiation(fid, 'Radiation', 'AirBox');
hfssSetTransparency(fid, {'AirBox'}, 0.95);

hfssInsertSolution(fid, 'Setup', fSolveGHz);
hfssInterpolatingSweep(fid, 'Sweep', 'Setup', fStartGHz, fStopGHz, 201);
hfssSolveSetup(fid, 'Setup');
hfssExportNetworkData(fid, tmpDataFile, 'Setup', 'Sweep', 'm', 50);

hfssSaveProject(fid, tmpPrjFile, true);
fclose(fid);

if runHFSS
    hfssExecuteScript(hfssExePath, tmpScriptFile, false, false);
end

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);
