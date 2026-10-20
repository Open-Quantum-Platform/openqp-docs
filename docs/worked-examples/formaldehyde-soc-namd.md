# Formaldehyde: Intersystem Crossing by SOC Surface Hopping

Surface hopping with spin-orbit coupling (SOC-NAMD) lets a trajectory hop
between singlet and triplet states. This example starts one trajectory of
formaldehyde on S1 (¹nπ\*) and follows it for 150 fs. The molecule
pyramidalizes, hops to the ³nπ\* triplet T0 at 29 fs, and spends most of the
run on the triplet before it returns to S1.

!!! warning "Experimental, and needs a build with openqp#535"
    SOC-NAMD is still under development and must be treated as experimental
    (see [Ensembles and SOC-NAMD](../keywords/md-ensemble-soc.md)). OpenQP
    builds without
    [openqp#535](https://github.com/Open-Quantum-Platform/openqp/pull/535)
    stop this run at the first trajectory write after the singlet → triplet
    hop, with `ValueError: NAMD trajectory schema/model mismatch on append`.

<div class="oqp-figs" markdown>
<figure markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<figcaption>t = 0 fs, planar ground-state geometry, on S1</figcaption>
</figure>
<figure markdown>
![n orbital](../assets/worked-examples/orb-hcho-homo.png)
<figcaption>n (b2): the lone pair excited in S1 and T0</figcaption>
</figure>
<figure markdown>
![pi* orbital](../assets/worked-examples/orb-hcho-side-lumo.png)
<figcaption>π* (b1): the orbital that receives the electron</figcaption>
</figure>
</div>

## Copy and run

```text title="formaldehyde-soc-namd.oqp"
mrsf(nstate=3)/bhhlyp/6-31g* namd(S1,scheme=custom,tdc=npi,rescale=isotropic,thrshe=0.367493,frustrated=reflect,soc=true,soc_basis=mch) md(nstep=300,dt=0.5,temperature=300,seed=3)
geom="""
C      0.000000     0.000000    -0.526342
O      0.000000     0.000000     0.676110
H      0.000000     0.937620    -1.119884
H      0.000000    -0.937620    -1.119884
"""
```

[Download formaldehyde-soc-namd.oqp](inputs/formaldehyde-soc-namd.oqp)

```bash
openqp formaldehyde-soc-namd.oqp
```

- `mrsf(nstate=3)/bhhlyp/6-31g*`: three MRSF-TDDFT singlets (S0, S1, S2) and
  three triplets (T0, T1, T2), the same states as in the
  [SOC example](formaldehyde-soc.md).
- `soc=true,soc_basis=mch`: surface hopping among the 12 spin-pure (MCH)
  states, 3 singlets plus 3 × 3 triplet M_S sublevels, coupled by the SOC
  matrix elements. The force is the exact gradient of the active MCH state.
- `scheme=custom,tdc=npi,rescale=isotropic,thrshe=0.367493,frustrated=reflect`:
  overlap-based (NPI) time-derivative couplings and isotropic velocity
  rescaling. The named schemes with analytic couplings support same-spin NAMD
  only, so SOC-NAMD sets these four choices explicitly
  (see [`scheme=custom`](../keywords/md-schemes.md)).
- `md(nstep=300,dt=0.5,temperature=300,seed=3)`: 300 steps of 0.5 fs, initial
  velocities drawn from a 300 K Maxwell–Boltzmann distribution with a fixed
  random seed.

The run takes about 2.5 minutes with 4 threads.

## What you get

Each step prints one line. In SOC-MCH runs `active` gives the MCH basis index
and its state, `grad` the state whose gradient drives the nuclei, and
`pop[S]`/`pop[T]` the total singlet and triplet populations:

```text
   SOC-MCH-NAMD step     57  t=   28.500 fs  active=2:S1  E_tot=-114.26346330  ...  hop=False  ...  grad=S1  pop[S]=0.9792 ...
   SOC-MCH-NAMD step     58  t=   29.000 fs  active=4:T0(ms=-1)  E_tot=-114.26346919  ...  hop=True  ...  grad=T0  pop[S]=0.9580 pop[T]=0.0420
```

The trajectory file `formaldehyde-soc-namd.namd.trj` holds all 12 MCH state
energies, complex amplitudes, populations, coordinates, and velocities at every
step. It is read the same way as in the
[ethylene NAMD example](ethylene-namd.md#what-you-get); here
`state_energies` has 12 columns in the order S0, S1, S2, T0(−1, 0, +1),
T1(−1, 0, +1), T2(−1, 0, +1).

![State energies, triplet population, and pyramidalization along the trajectory](../assets/worked-examples/plot-formaldehyde-soc-namd.svg)

| Event | Reference trajectory |
| --- | --- |
| Initial kinetic temperature | 532 K (one random sample of the 300 K distribution) |
| Pyramidalization before the hop | 45° at 25 fs (0° at the start) |
| Hop S1 → T0(M_S = −1) | 29.0 fs, S1–T0 gap 0.31 eV |
| Time on T0 | 97.5 of 150 fs |
| Later hops | T0 → S1 at 119.5, 127.0 and 133.0 fs; S1 → T0 at 121.5 and 131.5 fs |
| Final state | S1 at 150 fs; singlet population 0.88 |
| Total-energy range over 150 fs | 2.1 × 10⁻⁴ hartree (0.006 eV) |
| Energy-conservation check | passed at all 301 steps |

## Reading the result

- **Pyramidalization comes first.** At the planar start the S1–T0 coupling is
  zero (El-Sayed's rule, see the [SOC example](formaldehyde-soc.md)), and the
  triplet population stays below 0.06 for the first 29 fs. S1 formaldehyde is
  pyramidal, and the out-of-plane angle reaches 45° within 25 fs. The hop to
  T0 happens at this distorted geometry.
- **S1 and T0 move together.** Both are nπ\* states, so the S1–T0 gap stays
  between 0.16 and 0.34 eV along the whole trajectory, while S0 oscillates by
  more than 3 eV with the C–O stretch and the pyramidalization.
- **The hop releases the gap as kinetic energy.** The isotropic rescaling
  conserves total energy, and the kinetic energy rises from 0.18 eV to
  0.55 eV across the hop step.
- **Populations follow the active state after the hop.** The triplet
  population jumps from 0.04 to above 0.7 within one step. This comes from the
  energy-based decoherence correction (`decoherence=edc`, the default), which
  damps the amplitudes of the states that are not active.
- **One trajectory is not a result.** Intersystem-crossing rates and triplet
  yields need an ensemble of trajectories; see
  [Ensembles and SOC-NAMD](../keywords/md-ensemble-soc.md).

## Try next

- Change `seed=3` to other values to run more trajectories; the time of the
  first hop changes from one trajectory to the next.
- Use `soc_basis=adiabatic` to propagate spin-adiabatic states. With
  `seed=3` and `nstep=80` that trajectory hops at 6.5, 23.5 and 38 fs and is
  on a mostly-triplet state (T0 weight 0.93) after the last hop. Its force
  uses the weighted-MCH approximation, which is why the
  [md keywords](../keywords/md-ensemble-soc.md#soc_basis) recommend `mch`
  for now.

See also: [md keywords](../keywords/md.md),
[Ensembles and SOC-NAMD](../keywords/md-ensemble-soc.md),
[Spin-Orbit Coupling](../workflows/soc.md).
