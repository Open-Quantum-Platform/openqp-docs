# `[dftgrid]`

## Quadrature screening

The 74-, 230- and 266-point Lebedev rules contain negative quadrature
weights. Their signed contributions enter the integrated density, XC energy,
Fock matrix and derivatives. Grid-point and density-slice screening use the
absolute weights so that these contributions are retained. For an unpruned
230-point angular grid, use `dftgrid(pruned=none,ang_npts=230)`.

Small quadrature weights also occur near heavy nuclei, where the electron
density and XC energy density can be large. XC integration retains these
points and applies density-based screening. Points assigned zero or
machine-tiny weights by the atomic partition are omitted.

Energies and gradients can therefore differ from references generated with
earlier weight-screening rules. The correction applies to ordinary DFT
calculations and the XC integrals used for response and derivatives.
