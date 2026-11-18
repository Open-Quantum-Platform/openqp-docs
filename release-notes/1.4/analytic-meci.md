# Analytical NAC and two-state MECI optimization

OpenQP 1.4 provides static analytical nonadiabatic couplings for singlet MRSF-TDDFT with a two-SOMO ROHF or ROKS triplet reference. Use `nac(S0,S1,type=analytical)` for a static calculation. The native calculation evaluates all retained singlet pairs. The log reports the gap-scaled coupling `h = (E_j − E_i) d` in hartree per bohr and the derivative coupling `d` in inverse bohr.

Use `meci(S0,S1,algorithm=analytic)` to optimize a gas-phase two-state crossing with the analytical MRSF coupling. At each geometry the optimizer evaluates the coupling for the chosen pair and uses it with the gradient difference to define the branching plane. The convergence criteria include the energy change, energy gap, displacement, and projected gradient.

Set explicit positive SCF and TDHF convergence thresholds of at most `1e-8`. The ethylene input uses `1e-10` for both thresholds and `tdhf(tlf=0)`. The adjoint equation uses an absolute residual norm of `1e-10`. If the adjoint fails that criterion, OpenQP reports the failure and stops the calculation.

Download the [ethylene analytical MECI input](ethylene-meci-analytic.oqp) and run it in a dedicated working directory.

```shell
openqp --nompi ethylene-meci-analytic.oqp
```

The log identifies the `S0, S1` analytical NAC calculation and reports whether geometry optimization converged. Inspect `opt_status.txt` for the energy gap and convergence criteria at each evaluation and `opt_geom.xyz` for the final geometry. The [ethylene MECI worked example](worked-examples/ethylene-meci.md) explains the branching vectors and how to examine the final crossing.
