# HFSS-MATLAB-API Map

Read this before generating MATLAB scripts that call the local API.

## General Project Control

- `hfssIncludePaths([relPath])`: add API subfolders. `relPath` must end with a slash or `filesep`.
- `hfssRemovePaths([relPath])`: remove API subfolders.
- `hfssNewProject(fid)`: create a new HFSS project in VBScript.
- `hfssOpenProject(fid, hfssProjectFile)`: open an existing project.
- `hfssInsertDesign(fid, designName, [designType])`: insert active design. `designType`: `driven modal`, `driven terminal`, `eigenmode`.
- `hfssSetDesign(fid, designName)`: set an existing design active.
- `hfssSaveProject(fid, projectFile, [Overwrite])`: save active project. Save before solving.
- `hfssCloseActiveProject(fid)`: close active project.
- `hfssExecuteScript(hfssExePath, ScriptFile, [iconMode], [runAndExit])`: run HFSS script.
- `hfssSetVariable(fid, variable, value, [units])`: create local design variable. `value` may be numeric or an expression string.
- `hfssVariableChange(fid, variable, value, units)`: change an existing variable.
- `hfssAddMaterial(fid, Name, Er, bSigma, tanDelta)`: define a dielectric material.

## 3D Modeler

- `hfssBox(fid, Name, Start, Size, Units, [Center, Radius, Axis]...)`: create cuboid; optional cylindrical holes.
- `hfssRectangle(fid, Name, Axis, Start, Width, Height, Units)`: create sheet rectangle. `Axis` is the normal.
- `hfssCircle(fid, Name, Axis, Center, Radius, Units, [coverLines])`: create circle sheet.
- `hfssCylinder(fid, Name, Axis, Center, Radius, Height, Units)`: create cylinder.
- `hfssHollowCylinder(fid, Name, Axis, Center, inRadius, outRadius, Height, Units)`: create hollow cylinder.
- `hfssUncoveredCylinder(fid, Name, Axis, Center, Radius, Height, Units)`: create open cylinder.
- `hfssSphere(fid, Name, Center, Radius, Units)`: create sphere.
- `hfssPolyline(fid, Name, Points, Units, [Closed], [segmentType], [Color], [Transparency])`: create polyline. `Points` is `N x 3`.
- `hfssPolygon(fid, Name, Points, Units, ...)`: create polygon.
- `hfssPLObject(fid, Name, Points, startP, endP, Axis, Units, ...)`: create polyline object variant.
- `hfssDipole(fid, Name, Axis, Center, Length, Size, gapLen, Units)`: create two-arm dipole geometry.
- `hfssCoaxialCable(fid, Names, Axis, Center, Radii, Height, Units)`: create coax geometry.
- `hfssUnite(fid, ObjectList)`: boolean unite.
- `hfssSubtract(fid, blankParts, toolParts, [Clone])`: boolean subtract.
- `hfssConnect(fid, Names)`: connect sheet/line objects.
- `hfssMove(fid, ObjectList, tVector, Units)`: translate objects.
- `hfssRotate(fid, ObjectList, Axis, Degrees)`: rotate objects.
- `hfssDuplicateAlongLine(fid, ObjectList, dVector, nClones, Units, [Attach])`: duplicate array.
- `hfssDuplicateMirror(fid, ObjectList, Base, Normal, Units, [Attach])`: mirror duplicate.
- `hfssSweepAlongVector(fid, Object, Vector, Units, ...)`: sweep 2D object.
- `hfssSweepAroundAxis(fid, Object, Axis, SweepAngle, ...)`: revolve 2D object.
- `hfssThickenSheet(fid, ObjectList, Thickness, Units)`: thicken sheets.
- `hfssRename(fid, oldName, newName)`: rename object.
- `hfssAssignMaterial(fid, Object, Material)`: assign material. For `copper` and `pec`, solve-inside becomes false.
- `hfssSetColor(fid, Objects, Color)`: RGB color.
- `hfssSetTransparency(fid, ObjectList, Value)`: transparency, usually `0` to `0.95`.
- `hfssSetSolveInside(fid, Object, solveInsideFlag)`: set solve-inside.
- `hfssSetWCS(fid, Name)`, `hfssCreateRelativeCS(fid, Name, Origin, Units)`: coordinate systems.

## Boundaries And Ports

- `hfssAssignPE(fid, Name, ObjectList, [infGND])`: perfect E boundary or ground.
- `hfssAssignRadiation(fid, Name, Object, [UseIE])`: radiation boundary on a closed object, usually AirBox.
- `hfssAssignLumpedPort(fid, Name, ObjName, iLStart, iLEnd, Units, [Resistance], [Reactance])`: lumped port on sheet.
- `hfssAssignWavePort(fid, PortName, SheetObject, nModes, isLine, intStart, intEnd, Units)`: wave port on sheet.
- `hfssCircularPort(fid, Name, ObjectName, Axis, Center, Radius, Units)`: circular port helper.
- `hfssAssignFloquetPort(fid, Name, ObjName, Deembed, Phi, Theta, ...)`: periodic/Floquet port.
- `hfssAssignMaster(fid, Name, ObjName, iUStart, iUEnd, Units, [ReverseV])`: master boundary.
- `hfssAssignSlave(fid, Name, ObjName, iUStart, iUEnd, Units, Master, ScanAngle, Units)`: slave boundary.
- `hfssEditSlave(fid, Name, Master, variable, values, units)`: edit slave scan.
- `hfssEditFloquetPort(fid, Name, variable, value, units)`: edit Floquet port.
- `hfssAssignImpedance(fid, ImpedanceName, SheetObject, Resistance, Reactance, InfGroundPlane)`: impedance boundary.
- `hfssAssignLumpedRLC(fid, Name, ObjName, UseResist, UseInduct, UseCap, R, L, C, iLStart, iLEnd, Units)`: lumped RLC boundary.

## Analysis And Sweeps

- `hfssInsertSolution(fid, Name, fGHz, [maxDeltaS], [maxPass], [minPass], [minConvPass], [MaxRef])`: solution setup. Frequency is GHz.
- `hfssInterpolatingSweep(fid, Name, SolutionName, fStartGHz, fStopGHz, [nPoints], [nMaxSols], [iTol])`: interpolating sweep in GHz.
- `hfssSweepAnalysis(fid, Name, Analysis, Type, Variables, Data, ...)`: variable sweep analysis.
- `hfssSolveSetup(fid, SetupName)`: solve a setup.
- `hfssSolveSweepAnalysis(fid, SetupName)`: solve sweep analysis.
- `hfssExportNetworkData(fid, fileName, setupName, sweepName, [expFileType], [renormZ])`: export S/Z/f. Types: `h`, `t`, `s`, `c`, `m`, `z`.

## Radiation And Reports

- `hfssInsertFarFieldSphereSetup(fid, Name, Theta, Phi, [WCS])`: far-field radiation sphere. `Theta` and `Phi` are `[start stop step]` in degrees.
- `hfssCreateReport(fid, ReportName, Type, Display, Solution, Sweep, Context, Domain, VarObj, DataObj)`: create report.
- `hfssExportToFile(fid, ReportName, FileName, Type)`: export report as `txt`, `csv`, `tab`, or `dat`.

Report type values:

- `1`: Modal S Parameter
- `2`: Terminal S Parameters
- `3`: Eigenmode Parameters
- `4`: Fields
- `5`: Far Fields
- `6`: Near Fields
- `7`: Emission Test

Display values:

- `1`: Rectangular Plot
- `3`: Radiation Pattern
- `5`: Data Table
- `6`: 3D Rectangular Plot
- `7`: 3D Polar Plot

## Fields Calculator

- `hfssEnterQty(fid, Qty)`: enter field quantity.
- `hfssCalcOp(fid, Op)`: calculator operation.
- `hfssCalcStack(fid, Op)`: stack operation.
- `hfssCreatePTS(Name, Start, Stop, Spacing, Units)`: create point sample file.
- `hfssExportToFileFC(fid, Name, PTS, Solution, Freq, [Phase])`: export field calculator data.

## Mesh

- `hfssAssignLengthOp(fid, Name, Object, MaxLength, Units, [Inside], [RestrictElem], [NumMaxElem])`: mesh length operation.

## Important Conventions

- Many geometry functions default material to `vacuum`; assign materials explicitly.
- Use GHz for `hfssInsertSolution` and `hfssInterpolatingSweep`.
- Use full paths for script, project, and export files.
- Close the VBS file before executing HFSS.
- Keep `runAndExit=false` while debugging; otherwise HFSS may close silently after script errors.
