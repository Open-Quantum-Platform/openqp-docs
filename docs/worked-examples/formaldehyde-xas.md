# Formaldehyde: X-ray Absorption (Core Excitations)

X-ray absorption spectroscopy (XAS) excites an electron out of a 1s core
orbital. Each element absorbs in its own energy window (the K-edge), so the
spectrum is element-specific: carbon near 285 eV, oxygen near 530 eV. MRSF-TDDFT
can reach these core states directly with the `ixcore` option, without
computing the hundreds of valence states below them.

<div class="oqp-figs" markdown>
<figure markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<figcaption>Formaldehyde</figcaption>
</figure>
<figure markdown>
![pi* orbital](../assets/worked-examples/orb-hcho-side-lumo.png)
<figcaption>π*, the orbital that receives the core electron</figcaption>
</figure>
</div>

![Carbon and oxygen K-edge](../assets/worked-examples/plot-hcho-xas.svg)

## Copy and run

The carbon K-edge:

```text title="formaldehyde-xas-c.oqp"
mrsf(nstate=70)/bhhlyp/6-31g* energy(S0) tdhf(ixcore=2)
geom="""
C      0.000000     0.000000    -0.526342
O      0.000000     0.000000     0.676110
H      0.000000     0.937620    -1.119884
H      0.000000    -0.937620    -1.119884
"""
```

[Download formaldehyde-xas-c.oqp](inputs/formaldehyde-xas-c.oqp) ·
[formaldehyde-xas-o.oqp](inputs/formaldehyde-xas-o.oqp) (oxygen K-edge,
`tdhf(ixcore=1)`)

```bash
openqp formaldehyde-xas-c.oqp
```

- `tdhf(ixcore=N)` selects molecular orbital N as the core orbital. The orbitals
  are numbered by energy: orbital 1 is O 1s and orbital 2 is C 1s. OpenQP shifts
  the response equations so that excitations out of this orbital are found
  among the computed states.
- `nstate=70` leaves room for the valence states that are still computed;
  `energy(S0)` follows the repository XAS example.

Each run takes about 5 seconds.

## What you get

The transitions from S0 are listed after the excited-state summary table. For
the carbon K-edge:

```text
   S0 -> S53  283.882898        ...      0.0629
   S0 -> S54  284.616185        ...      0.0000
```

| Edge | Transition | Energy | Oscillator strength | Experiment |
| --- | --- | --- | --- | --- |
| C K-edge | C 1s → π\* | 283.88 eV | 0.063 | about 286.0 eV |
| O K-edge | O 1s → π\* | 525.48 eV | 0.026 | about 530.8 eV |

The same input for HCN ([hcn-xas-c.oqp](inputs/hcn-xas-c.oqp)) gives its
carbon 1s → π\* transition at 285.55 eV with an oscillator strength of 0.050,
the value quoted for the corresponding repository example.

## Reading the result

- **Each edge has one strong 1s → π\* line.** Like valence MRSF-TDDFT, the core
  states come from spin flips out of the high-spin reference; only the
  excitation from the core orbital into the LUMO (π\*) is a single excitation in
  this construction, so higher core-excited states appear with very small
  intensity.
- **The energies are 2–6 eV below experiment.** Linear-response core
  excitations with a hybrid functional and a small basis set are not expected
  to give absolute edge positions, and this calculation does not relax the
  orbitals around the core hole. The repository's
  [`examples/XAS`](https://github.com/Open-Quantum-Platform/openqp/tree/main/examples/XAS)
  folder also contains the ΔCHP-MRSF approach, which includes core-hole
  relaxation through `guess(swapmo=...)`, `scf(rstctmo=true)`, and `ixcore`.
- **The ordering of the edges is element-specific**: the 240 eV gap between the
  C and O lines is what makes XAS a probe of individual atoms.

## Try next

- Compute the nitrogen K-edge of HCN by selecting the N 1s orbital, which is
  orbital 1 in HCN.
- Use a basis set with core polarization functions, such as `cc-pcvdz`, and
  compare the edge positions.

See also: [MRSF-TDDFT](../workflows/mrsf-tddft.md),
[`tdhf` keywords](../keywords/tdhf.md).
