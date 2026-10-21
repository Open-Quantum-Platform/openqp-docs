# Ethylene: Coupling Between Two Geometries (NACME)

Surface-hopping dynamics needs the coupling between electronic states along
the trajectory. The NACME (nonadiabatic coupling matrix element) workflow
obtains it from two nearby geometries: it computes the overlaps of the
electronic states at the two structures and turns them into a time-derivative
coupling. This example takes two consecutive frames from the
[ethylene NAMD trajectory](ethylene-namd.md), 0.5 fs apart, just before the
hop to S0.

<div class="oqp-figs" markdown>
<figure markdown>
![Ethylene at the hop](../assets/worked-examples/mol-namd-1015.png)
<figcaption>Ethylene near the S1→S0 hop (t ≈ 101 fs)</figcaption>
</figure>
</div>

## Copy and run

```text title="ethylene-nacme.oqp"
mrsf(nstate=3)/bhhlyp/6-31g nacme(S0,S1)
geom2="""
C     -0.064618    -0.221999     0.675181
C      0.008847     0.342365    -0.693621
H     -0.897526     0.258489     1.326593
H      0.271183    -1.193629     1.028019
H     -0.000944    -0.618553    -1.099719
H      1.291351     0.120517    -1.035329
"""
geom="""
C     -0.063015    -0.217408     0.666522
C      0.006888     0.342791    -0.685095
H     -0.922484     0.251033     1.304645
H      0.320438    -1.208096     1.024800
H     -0.015385    -0.622076    -1.118494
H      1.285729     0.086223    -0.989812
"""
```

[Download ethylene-nacme.oqp](inputs/ethylene-nacme.oqp)

```bash
openqp ethylene-nacme.oqp
```

`nacme(S0,S1)` requests the coupling matrix; `geom2` is the earlier structure
(t = 100.5 fs) and `geom` the later one (t = 101.0 fs). Both are given inside
the input. The run takes about 4 seconds.

## What you get

The log prints the state overlaps between the two geometries, the derivative
coupling, the energy gaps, and the nonadiabatic coupling:

```text
   PyOQP: phase corrected state overlap (s_ij)
      0.82885303       0.55690871       0.00264817
     -0.54636930       0.82540781      -0.00484133
     -0.00118345      -0.01044068       0.99716901
   PyOQP: phase corrected derivative coupling (d_ij)
      0.00000000       0.55163901       0.00191581
     -0.55163901       0.00000000       0.00279967
     -0.00191581      -0.00279967       0.00000000
   PyOQP: state energy gap (e_ji)
      0.00000000       0.00834302       0.16127661
```

Rows and columns are S0, S1, S2. The printed coupling is
d_ij = (s_ij − s_ji)/(2Δt) with Δt = 1, so d is dimensionless: for example
d(S0,S1) = (0.55690871 + 0.54636930)/2 = 0.55163901. (The log header writes the
formula without the factor 2, but the printed values include it.) Divide by
the time step in atomic units (0.5 fs = 20.67 a.u.) to obtain the
time-derivative coupling.

| Quantity | Reference value |
| --- | --- |
| ⟨S0(t) \| S0(t+Δt)⟩ | 0.829 |
| ⟨S0(t) \| S1(t+Δt)⟩ | 0.557 |
| d(S0,S1) | 0.552 (0.0267 a.u.⁻¹ per 0.5 fs) |
| S1 − S0 gap | 0.0083 hartree (0.23 eV) |
| d(S1,S2) | 0.003 |

## Reading the result

- **The states mix strongly within 0.5 fs.** An overlap of 0.56 between S0 at
  one step and S1 at the next means that the electronic character changes
  substantially between the two frames; the trajectory is passing close to the
  S0/S1 intersection.
- **The coupling is large where the gap is small.** d(S0,S1) = 0.55 at a gap of
  0.23 eV, while S2, 4.4 eV higher, couples by only 0.003.
- This is the quantity a surface-hopping run evaluates at every step with the
  overlap-based coupling schemes (see
  [NAMD coupling schemes](../keywords/md-schemes.md)).

## Try next

- Compute the analytic NAC vector at one of the two geometries with
  `nac(S0,S1,type=analytical)`, as in the [MECI example](ethylene-meci.md), and
  compare its direction with the motion between the frames.

See also: [NACME](../workflows/nacme.md),
[ethylene NAMD](ethylene-namd.md).
