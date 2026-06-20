# Common HFSS Patterns

## Microstrip Patch

Objects:

- Substrate: `hfssBox`
- Patch: `hfssRectangle` on `Z`
- Feed line: `hfssRectangle` on `Z`, then `hfssUnite`
- Ground: `hfssRectangle` on `Z`
- Lumped port: small `hfssRectangle` normal to feed direction
- Air box: `hfssBox` plus `hfssAssignRadiation`

Reports:

- Terminal or modal S-parameter rectangular plot.
- Far-field sphere plus gain/directivity reports when requested.

## Wire Dipole

Objects:

- `hfssDipole` or two cylinders.
- Gap source rectangle.
- Lumped port across gap.
- Air box with radiation boundary.

Optimization:

- Primary parameter is length.
- Resonance shifts downward when length increases.

## Folded Dipole

Objects:

- Circles swept around axis for bends.
- Cylinders for straight arms.
- Unite and assign copper.
- Lumped port across feed gap.

## Horn Or Profile-Based Antenna

Objects:

- Read `N x 3` points from CSV.
- Create edge polylines with `hfssPolyline`.
- Connect sheets with `hfssConnect`.
- Mirror or duplicate plates as needed.
- Add coax/wave port feed.

For sheet-based pyramidal or sectoral horns:

- Create each wall as a covered closed polyline sheet.
- Repeat the first point as the final point; `IsPolylineClosed` alone may not be enough for ACIS to cover the sheet.
- Assign PEC after all wall sheets exist.
- Use a wave port on the waveguide back face.
- Place the air-box back boundary at the wave-port plane, or otherwise ensure the port is not an internal wave port with solve-inside air on both sides.
- Run a geometry-save batch before adding solve/export commands.

## Periodic Unit Cell

Objects:

- Unit-cell geometry centered in local coordinate system.
- Master/slave boundaries or Floquet port.
- Parameterized scan angle if needed.

Checks:

- Opposite periodic faces must be congruent.
- Integration vectors must be consistent.

## Report Expressions

Use expressions such as:

- `dB(S(Port,Port))`
- `mag(S(Port,Port))`
- `re(Z(Port,Port))`
- `im(Z(Port,Port))`
- `dB(GainTotal)`
- `dB(DirTotal)`

The exact port name in expressions must match the assigned port name.

## Common Gotchas

- Some reports require Modal S Parameter (`Type=1`) and others Terminal S Parameters (`Type=2`). Match the design and port type.
- `hfssCreateReport` expects report data strings to be quoted correctly; use existing examples as a pattern.
- Boolean operations can rename or remove tool objects. Assign boundaries/materials after the final object exists.
- Negative rectangle widths/heights are used in existing examples and can be valid, but prefer positive dimensions and explicit starts for clarity.
- The first HFSS run should stay open (`runAndExit=false`) for debugging.
