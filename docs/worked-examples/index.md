# Worked Examples

Each worked example is one small molecule, one complete `.oqp` input that you
can copy and run as it is, and the results that the run produces. The
coordinates are written inside the input, so no separate geometry file is
needed. Run the input, then compare your numbers with the reference values on
the page.

```bash
openqp water-scf.oqp
```

Every input on these pages can also be downloaded from the link under its code
block. With 2 to 4 CPU threads, each run takes between 2 seconds and 1 minute.

<div class="oqp-gallery" markdown>

<a class="oqp-card" href="water-scf/" markdown>
![Water](../assets/worked-examples/orb-water-side-homo.png)
<strong>Water energy and orbitals</strong>
<span>Total energy, orbital energies, HOMO and LUMO pictures, dipole moment, and atomic charges.</span>
</a>

<a class="oqp-card" href="formaldehyde-opt-freq/" markdown>
![Formaldehyde C=O stretch](../assets/worked-examples/mode-hcho-co-mode.png)
<strong>Geometry and vibrations</strong>
<span>Optimize formaldehyde, then compute harmonic frequencies, zero-point energy, and thermochemistry.</span>
</a>

<a class="oqp-card" href="formaldehyde-uv/" markdown>
![Formaldehyde pi* orbital](../assets/worked-examples/orb-hcho-side-lumo.png)
<strong>UV absorption (TDDFT)</strong>
<span>Excitation energies and oscillator strengths, and the orbitals behind the n→π* band.</span>
</a>

<a class="oqp-card" href="ethylene-twist/" markdown>
![Twisted ethylene](../assets/worked-examples/mol-ethylene-twisted.png)
<strong>Twisted ethylene (MRSF-TDDFT)</strong>
<span>S0, S1, and S2 along the C=C twist, where S0 becomes a diradical.</span>
</a>

<a class="oqp-card" href="formaldehyde-soc/" markdown>
![Formaldehyde](../assets/worked-examples/mol-hcho.png)
<strong>Spin-orbit coupling</strong>
<span>Singlet-triplet coupling matrix elements in cm⁻¹ and El-Sayed's rule.</span>
</a>

<a class="oqp-card" href="benzene-nmr/" markdown>
![Benzene](../assets/worked-examples/mol-benzene.png)
<strong>NMR chemical shifts</strong>
<span>GIAO shieldings of benzene and TMS, converted to ¹H and ¹³C chemical shifts.</span>
</a>

<a class="oqp-card" href="hcn-isomerization/" markdown>
![HCN transition state](../assets/worked-examples/mode-hcn-ts-mode.png)
<strong>Transition state and barrier</strong>
<span>Locate the HCN → HNC transition state, confirm one imaginary frequency, and compute the barrier.</span>
</a>

<a class="oqp-card" href="water-correlation/" markdown>
![Water](../assets/worked-examples/mol-water.png)
<strong>MP2 and CCSD(T) energies</strong>
<span>Correlation energies of water at the MP2 and CCSD(T) levels.</span>
</a>

</div>

## How the reference values were produced

All reference values on these pages come from running exactly the inputs shown,
with OpenQP 1.3.1 (GitHub `main`, commit `f5361a2`, 20 October 2026) on macOS
x86_64 with 2 to 8 OpenMP threads. Molecule and orbital pictures are snapshots
of the [OQP Studio](../studio/index.md) 3D viewer, made from the output files of
the same runs.

On another computer, SCF energies normally agree with the reference values to
about 10⁻⁶ hartree. Small differences in the last digits come from DFT
integration grids, thread counts, and convergence thresholds. They are not
errors.

Where an independent code was available, the reference values were also checked
against PySCF 2.13 at the same geometry and basis set. Each page states which
values were checked.

## Reading an OpenQP run

Every run writes these files beside the input:

| File | Contents |
| --- | --- |
| `<name>.log` | The full text output, including SCF iterations, orbital energies, and all requested properties. Each page quotes the relevant part. |
| `<name>_scf_*.molden` | Molecular orbitals in Molden format. Open it in OQP Studio Analysis, [OpenqpView](https://open-quantum-platform.github.io/OpenqpView/), Molden, or Avogadro to display orbitals. |
| `<name>.hess.json`, `<name>.freq.molden` | Written by Hessian runs: frequencies, normal modes, and thermochemistry data. Open the `.freq.molden` file to animate the vibrations. |
| `opt.xyz`, `opt_status.txt` | Written by geometry optimizations and transition-state searches: the final geometry and a table of the optimization steps. |

The end of every log has an `ENERGIES AND STATES` block, which is the quickest
place to read the final energies:

```text
   PyOQP LOG | ENERGIES AND STATES
   PyOQP: Final Energy
   ========================================================================
   PyOQP Energy unit:                 Hartree
   PyOQP electronic energies
   PyOQP state 0                            -76.3256993935
```

For the full input syntax, see [`.oqp` Input](../oqp-input.md). For larger
template decks, see the [repository examples](../examples/index.md).
