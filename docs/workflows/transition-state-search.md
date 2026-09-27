# Transition-state searches without a calculated Hessian

The native optimizer supports `prfo` (default), `qst2`, and `qst3`. QST searches
combine synchronous transit with the existing P-RFO optimizer and, by default,
Bofill updates of a model Hessian. They evaluate electronic energies and nuclear gradients;
they do not calculate an initial or final molecular Hessian, frequencies, or an IRC.
A converged geometry is a **candidate transition state** until its stationary-point
character and connection to the intended reactant and product are established.

## QST2 and QST3

Supply optimized reactant and product structures with identical atoms in the
same order, charge, multiplicity, and electronic-state definition. OpenQP reads
the reactant from `geom` and the product from an XYZ file in Å. It aligns the
product by a proper rotation and translation; it never permutes atoms.

QST2 interpolates redundant internal coordinates at the midpoint. If the internal
back-transformation fails, the log explicitly identifies the Cartesian fallback.
QST3 additionally reads a supplied approximate transition-state structure.
Its geometry is aligned to the reactant and used as the starting point.

```text
rhf/sto-3g
ts(S0,search="qst2",product="product.xyz",maxit=50)
geom="reactant.xyz"
```

```text
rhf/sto-3g
ts(S0,search="qst3",product="product.xyz",guess="guess.xyz",maxit=50)
geom="reactant.xyz"
```

```python
from oqp.openqp import OpenQP
job = OpenQP().molecule(geometry="reactant.xyz", basis="sto-3g").hf()
job.workflow.ts(search="qst3", product="product.xyz", guess="guess.xyz", maxit=50)
job.run()
```

In sectioned input, use `[input] runtype=ts`, `[optimize] lib=oqp` and
`[oqp] ts_search=qst2|qst3`, `ts_product=product.xyz`, and, for QST3,
`ts_guess=guess.xyz`. Relative endpoint paths resolve against the input file.
Both searches require `init_hessian=model`. Frozen-distance constraints and
QM/MM are currently unsupported. Endpoints are not optimized automatically.

### Coordinate selection and inversion endpoints

The examples above leave `coordsys=auto`, which initially selects DLC for an
isolated molecule. Before constructing the model Hessian, QST2/QST3 check whether
the selected internal coordinates distinguish the two endpoints. Distinct
Cartesian structures can have identical internal coordinates: for example, the
two pyramidal NH3 inversion structures have the same bond lengths and angles.
In this case OpenQP automatically uses Cartesian coordinates for the search and
reports `DLC->CART(fallback)` in the coordinate label. This also applies to an
explicit internal-coordinate selection; endpoints that remain distinguishable
retain the selected internal coordinates.

The model Hessian is initialized in the chosen coordinates, consistently with
the transit tangent and gradient. This fallback does not evaluate a molecular
Hessian or frequencies. The engine example
`examples/OPT/NH3_RHF-HF_QST3_OQP.oqp` demonstrates the default selection with the
supplied NH3 endpoint and guess XYZ files; no `coordsys="cartesian"` override is
needed. Its three-step limit is a short execution example, not a convergence
criterion. Truly coincident Cartesian endpoints are still rejected.

### Search steps

The synchronous-transit direction follows the circle through the two endpoints
and the current structure (Peng–Schlegel Eq. 8), evaluated in the active working
coordinates. The first two steps ascend along that tangent. Steps three and four
retain tangent-only ascent when its estimated displacement exceeds 0.05 in atomic
units. Otherwise P-RFO follows the model-Hessian eigenvector with greatest tangent
overlap if that overlap exceeds 0.8, or the lowest eigenvalue. P-RFO takes over from
step five; after that step, the existing mode-overlap tracking continues. Native
trust-radius controls apply throughout. If a nonfinite internal step triggers
Cartesian recovery, the followed mode is converted and the previous internal
QST tangent is discarded; the next QST step recomputes it in Cartesian coordinates.
This implements the published STQN
strategy within OpenQP's optimizer; it is not a reproduction of Gaussian's defaults.

## Experimental model curvature

The default is `model_hessian=auto,hessian_update=auto`: supported isolated,
unconstrained H–Ar molecules use modified Lindh initial curvature with Bofill
updates for TS searches (BFGS for minimum searches). Unsupported cases retain
the constant model, and a calculated initial Hessian takes precedence. Explicit
`model_hessian=constant` restores the earlier model. GPR remains optional because
a molecular performance advantage has not been established for this implementation.

These controls are independent of the TS initial-guess method. QST2/QST3 use
reactant/product structures to determine the initial uphill direction; Lindh
sets the initial model Hessian; Bofill or the optional GPR correction updates
curvature as the search proceeds. Thus QST can use either model/update choice,
and both curvature controls also work with a single-guess P-RFO TS search or
ordinary minimum optimization. Selecting a Hessian model does not enable QST.

To additionally enable the energy/gradient-based local Gaussian process, set:

```text
rhf/sto-3g
ts(S0,search="qst3",product="product.xyz",guess="guess.xyz",model_hessian="lindh",hessian_update="gpr",gpr_history=8,gpr_length_scale=0.5,maxit=50)
geom="reactant.xyz"
```

The same options work for a minimum search:

```text
rhf/sto-3g
opt(S0,model_hessian="lindh",hessian_update="gpr",maxit=50)
geom="initial.xyz"
```

In sectioned input, keep `[input] runtype=optimize` or `ts`, and add:

```ini
[oqp]
init_hessian=model
model_hessian=lindh
hessian_update=gpr
gpr_history=8
gpr_length_scale=0.5
```

The Python API accepts the same names:

```python
job.workflow.ts(search="qst3", product="product.xyz", guess="guess.xyz",
                model_hessian="lindh", hessian_update="gpr",
                gpr_history=8, gpr_length_scale=0.5)
# For a minimum: job.workflow.optimize(model_hessian="lindh", hessian_update="gpr")
```

The modified Lindh model estimates initial curvature from the geometry and
covalent radii (H–Ar). It constructs Cartesian curvature first, so a QST
Cartesian fallback uses the same model. The local derivative Gaussian process
then uses the optimization's own energies and gradients in a bounded span of
recent Cartesian displacements. It corrects the current quasi-Newton model in
that span; it does not replace the rest of the approximate Hessian or take
steps using only a predicted energy and gradient. This is an experimental
combination, not a reproduction of a published full GPR TS optimizer.

The GPR history limit is 3–20 observations and the fixed length scale is
0.001–10 bohr (defaults 8 and 0.5 bohr). Insufficient data, uncertain curvature, or a failed fit leaves
BFGS/Bofill curvature in use, with a diagnostic in the log. The uncertainty
check uses the largest posterior-to-prior variance ratio over symmetric
Hessian components in the sampled subspace (limit 0.05); a well-sampled
transverse direction cannot mask an uncertain reaction direction. This is
a model-based rejection criterion, not a guarantee of curvature accuracy. A recovery attempt
starts a fresh history. No extra electronic evaluations or calculated molecular
Hessians are requested by either option. Neither model curvature nor its GPR
correction establishes the stationary-point order or supplies frequencies.

These options currently support only unconstrained native minimum and TS
searches, including QST2/QST3. Nondefault controls are rejected for frozen
distances, QM/MM, crossing searches, NEB, IRC, MEP, external optimizers, or an
initial Hessian calculated analytically or numerically. The example
`examples/OPT/NH3_RHF-HF_QST3_LINDH_GPR_OQP.oqp` demonstrates the controls with
three iterations and recovery disabled; it is not a molecular speed benchmark.
No convergence or speedup advantage is claimed. Compare actual energy/gradient
call counts only after confirming that searches reach the same candidate saddle.
See the [keyword definitions](../keywords/oqp.md#model_hessian) for defaults,
bounds, regularization, and element support.

## IDPP initialization for NEB

For a poorly known reaction path, a band calculation can be more informative
than a single candidate saddle search. `interpolation="idpp"` refines the initial
NEB band using image-dependent target pair distances before any electronic
band evaluation. Climbing-image NEB then runs on the requested electronic surface.

```text
rhf/sto-3g
neb(S0,product="product.xyz",images=7,interpolation="idpp",opt_ends=false,maxit=100)
geom="reactant.xyz"
```

In sectioned input use `[oqp] neb_interpolation=idpp`; the default is `linear`.
The Python API accepts `job.workflow.neb(interpolation="idpp")`, with product and
image count set through `job.settings.neb(product="product.xyz", nimage=7)`.

IDPP minimizes the sum of squared deviations from interpolated endpoint pair
distances, weighted by the inverse fourth power of the **current** distance.
The gradient includes the derivative of that weight. A fixed-endpoint NEB/FIRE
optimization uses this surrogate objective, without electronic energies or Hessians.
Near-coincident pairs are detected both at images and along the straight segments
between adjacent images. A smooth deterministic transverse displacement breaks
collinear exchange symmetry, including even image counts with no coincident
sampled image; endpoints remain fixed. A final segment check rejects unresolved
near-collisions even when the projected band force is small.
Coincident endpoints are rejected. If IDPP fails to converge within 1000 steps,
the calculation stops before electronic NEB and reports the failure.
The optimized surrogate band is available as `mol.neb_idpp_result`.

IDPP often improves Cartesian initial paths with atom crowding. It is an
initialization method, not evidence that NEB or QST will find the lowest barrier
or a particular mechanism. Compare candidate paths when multiple mechanisms are
plausible. This implementation is for nonperiodic molecular geometries; it does
not apply minimum-image distances or cell interpolation.

## References and alternatives

- [Peng and Schlegel, Isr. J. Chem. 33, 449–454 (1993)](https://doi.org/10.1002/ijch.199300051): synchronous transit plus quasi-Newton searches.
- [Smidstrup et al., J. Chem. Phys. 140, 214106 (2014)](https://arxiv.org/abs/1406.1512): IDPP and comparisons with linear interpolation.
- [Sharada et al., J. Chem. Theory Comput. 8, 5166–5174 (2012)](https://doi.org/10.1021/ct300659d): freezing-string searches with BFGS and no evaluated Hessian.
- [Zimmerman, J. Chem. Theory Comput. 9, 3043–3050 (2013)](https://doi.org/10.1021/ct400319w): growing-string searches in internal coordinates.
- [Heyden, Bell and Keil, J. Chem. Phys. 123, 224101 (2005)](https://doi.org/10.1063/1.2104507): improved dimer searches.

The latter methods are alternatives considered in the literature survey, not
additional workflows implemented here. Neither QST nor IDPP has a universal
convergence advantage across reactions.
