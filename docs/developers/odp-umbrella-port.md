# ODP Umbrella-Sampling Port

!!! info "Design and validation contract"
    ODP umbrella sampling is **not yet an OpenQP input feature**. This page
    defines the equations, separation of responsibilities, restart records,
    and acceptance tests for a future native Fortran implementation. It does
    not reserve final input-keyword names.

One-dimensional projection (ODP) converts a multidimensional collective
variable (CV) vector into a scalar reaction-progress coordinate suitable for
umbrella sampling. The method follows Baek and Choi's ODP formulation; see the
[published reference](../references.md#enhanced-sampling).

## Keep the physical controls separate

ODP, solvent containment, and temperature control solve different problems.
They must remain separately selectable and separately recorded.

| Control | Purpose | Part of ODP? |
| --- | --- | --- |
| Parallel ODP umbrella | Samples progress between reference CV vectors | Yes |
| Perpendicular restraint | Optionally limits excursions away from the reference line | Optional extension |
| Droplet boundary potential | Prevents finite, nonperiodic solvent from evaporating | No |
| Solute position/orientation restraint | Prevents unwanted drift or rotation | No |
| Thermostat | Generates an NVT rather than NVE trajectory | No |

A water-droplet boundary therefore must not be enabled merely by selecting
ODP. Conversely, ODP must work for gas-phase, periodic, droplet, NVE, and NVT
setups whenever the underlying force model supports those combinations.

## Coordinate definition

Let \(\mathbf X(\mathbf r)\) be the current CV vector, and let
\(\mathbf R\) and \(\mathbf P\) be its reactant and product references. Define

\[
L = \lVert \mathbf P-\mathbf R \rVert,
\qquad
\mathbf T = \frac{\mathbf P-\mathbf R}{L}.
\]

OpenQP should use the signed, dimensionless progress coordinate

\[
\xi(\mathbf r) =
\frac{(\mathbf X-\mathbf R)\mathbin{\cdot}\mathbf T}{L}.
\]

Thus \(\xi=0\) at the reactant reference and \(\xi=1\) at the product
reference. A signed projection deliberately permits sampling below zero and
above one and avoids a nondifferentiable absolute value at the reactant
reference.

The displacement perpendicular to the reference line is

\[
\mathbf X_\perp =
(\mathbf X-\mathbf R)
-[(\mathbf X-\mathbf R)\mathbin{\cdot}\mathbf T]\mathbf T
= \mathbf P_\perp(\mathbf X-\mathbf R),
\]

where \(\mathbf P_\perp=\mathbf I-\mathbf T\mathbf T^{\mathsf T}\).

All CV components must use an explicit, compatible metric. Mixing distances,
angles, or other units in a Euclidean norm without declared scaling is not
valid. The input and restart record must preserve that metric.

## Bias energy and analytic force

For window \(i\), the conservative bias is

\[
U_i = \frac{1}{2}k_{\parallel,i}(\xi-u_i)^2
+ \frac{1}{2}k_{\perp,i}\lVert\mathbf X_\perp\rVert^2,
\]

where the second term is optional. With the CV Jacobian
\(\mathbf J_X=\partial\mathbf X/\partial\mathbf r\), the atomic bias force is

\[
\mathbf F_i^{\mathrm{bias}} = -\mathbf J_X^{\mathsf T}
\left[
\frac{k_{\parallel,i}(\xi-u_i)}{L}\mathbf T
+ k_{\perp,i}\mathbf P_\perp(\mathbf X-\mathbf R)
\right].
\]

The production value and Jacobian kernels should be implemented in Fortran.
Python may prepare inputs and analyze records, but it must not be the
per-timestep force path.

## CV implementation rules

The initial native implementation should cover only CVs with fully derived,
continuous analytic Jacobians, such as bond distance, asymmetric distance
combinations, and angle coordinates. Every CV definition must state atom
ordering, units, periodic wrapping, and singular geometries.

Flexible definitions that change atom membership or select a minimum during a
trajectory require a separate continuity design. They must not silently switch
branches inside an umbrella window.

The legacy KNU-GAMESS ODP branch is useful as a behavior and file-format
reference, but not as source to transcribe verbatim. Finite-difference audits
of that branch expose normalization/Jacobian inconsistencies in at least an
asymmetric-distance path and an angle path. OpenQP must derive each Jacobian
from its implemented bias energy and pass independent numerical derivatives.

## Trajectory and restart records

Each packed trajectory record used for umbrella analysis should contain at
least:

- window identifier, step, time, and ensemble;
- \(\xi\), \(\mathbf X\), and \(\mathbf X_\perp\) or its norm;
- parallel and perpendicular bias energies;
- the unrestrained potential energy and the total conservative energy;
- thermostat work/heat or an extended/shadow energy when the selected
  thermostat defines one;
- any independent droplet-boundary or solute-restraint energies.

The restart state must preserve the CV definitions and ordering, CV metric,
\(\mathbf R\), \(\mathbf P\), window center, force constants, optional
perpendicular-restraint settings, and all ensemble state needed for a
bitwise-continuous continuation. Restarting must append to the same logical
trajectory without duplicating or dropping a saved step.

## Validation gates

ODP is ready for a production PR only after all of these gates pass:

1. Compare every analytic CV Jacobian and full atomic bias force with central
   finite differences of the same Fortran energy.
2. Test reactant, product, off-path, negative-progress, and beyond-product
   geometries, plus every declared singularity guard.
3. Verify zero net translation and zero net torque for biases built exclusively
   from internal, rotation-invariant CVs.
4. Check the native energy and force against an independent reference
   implementation over randomized nonsingular geometries.
5. In NVE, gate conservation using
   \(E_{\mathrm{tot}}=K+E_{\mathrm{QM/MM}}+U_{\mathrm{ODP}}\), plus every
   other enabled conservative restraint such as a droplet boundary.
6. In NVT, report the physical-energy exchange separately; do not apply the
   raw NVE drift gate to a thermostatted trajectory.
7. Stop safely before propagating coordinates when a CV, Jacobian, force,
   energy, or restart-consistency check is nonfinite or out of contract.
8. Demonstrate restart equivalence and recovery of umbrella histograms and
   free energies from packed trajectory records alone.

The ODP implementation, droplet model, and thermostat should receive separate
unit tests even if an integration example enables all three.
