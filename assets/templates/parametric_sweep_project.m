% Parameter sweep template for HFSS-MATLAB-API.
% Example: sweep dipole length around half wavelength.

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

units = 'meter';
c0 = 3e8;
targetFreq = 150e6;
lambda0 = c0/targetFreq;
lengthValues = (0.85:0.05:1.15)*(lambda0/2);

results = table('Size', [0 4], ...
    'VariableTypes', {'double', 'double', 'double', 'string'}, ...
    'VariableNames', {'Index', 'Length_m', 'BestS11_dB', 'Status'});

for i = 1:numel(lengthValues)
    candidateDir = fullfile(pwd, sprintf('candidate_%03d', i));
    if ~exist(candidateDir, 'dir')
        mkdir(candidateDir);
    end

    scriptFile = fullfile(candidateDir, 'candidate.vbs');
    projectFile = fullfile(candidateDir, 'candidate.aedt');
    dataFile = fullfile(candidateDir, 'network.m');

    fid = fopen(scriptFile, 'wt');
    writeDipoleCandidate(fid, lengthValues(i), targetFreq, units, projectFile, dataFile);
    fclose(fid);

    status = "generated";
    bestS11 = NaN;

    if runHFSS
        hfssExecuteScript(hfssExePath, scriptFile, true, true);
        if exist(dataFile, 'file')
            run(dataFile);
            bestS11 = min(20*log10(abs(S(:))));
            status = "solved";
        else
            status = "missing_data";
        end
    end

    results = [results; {i, lengthValues(i), bestS11, status}]; %#ok<AGROW>
end

writetable(results, fullfile(pwd, 'optimization_log.csv'));

hfssRemovePaths([apiRoot filesep]);
rmpath(apiRoot);

function writeDipoleCandidate(fid, dipoleLength, targetFreq, units, projectFile, dataFile)
    c0 = 3e8;
    lambda0 = c0/targetFreq;
    dipoleRadius = 0.01*lambda0;
    gapLength = 0.02*lambda0;
    airMargin = lambda0/4;

    hfssNewProject(fid);
    hfssInsertDesign(fid, 'Candidate');
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

    hfssInsertSolution(fid, 'Setup', targetFreq/1e9);
    hfssInterpolatingSweep(fid, 'Sweep', 'Setup', ...
        0.75*targetFreq/1e9, 1.25*targetFreq/1e9, 201);
    hfssSolveSetup(fid, 'Setup');
    hfssExportNetworkData(fid, dataFile, 'Setup', 'Sweep', 'm', 50);
    hfssSaveProject(fid, projectFile, true);
end
