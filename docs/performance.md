# Performance

OpenQP's performance knobs are ordinary **input keys** (no environment variables) bundled
behind a single opt-in preset, `[input] perf`, that acts as one accuracy↔speed dial.

```ini
[input]
perf = 1        # 0, 1, 2, or 3 (default 1; perf=-1 disables the preset)
```

## The four levels

| `perf` | Use it for | What it enables | Accuracy |
| --- | --- | --- | --- |
| **0** | strict reference / reproducibility | every accelerator off, every cutoff tightest | bit-reference (fixed thread count) |
| **1** | **recommended production** | exact, proven-helpful only: MRSF response cutoff `1e-8`, z-vector warm-start (+ always-on Fock digestion) | ≈ reference (≤ µEh) |
| **2** | faster, tiny degradation | `perf=1` + coarse-to-fine XC grid + gradient Schwarz cutoff `1e-8` | gradients within ~5×10⁻⁷ a.u.; SCF exact at convergence |
| **3** | aggressive, degradation allowed | looser cutoffs traded for speed: gradient `1e-7`, response `1e-6` | small, controlled (~few µeV on excitation energies) |

**`perf=1` is the default** (recommended production, exact). Set `perf=-1` to disable the preset
entirely (every knob at its control default). The levels were calibrated on a
CPU benchmark (MKL and Apple Accelerate) over HF/DFT/TDDFT/MRSF energies and MRSF gradients.

!!! note "Why some accelerators are not in any preset"
    On the CPU builds benchmarked, the XC Φ-cache, IncDFT, MRSF FP32 and progressive screening
    (`pscreen`) were performance-neutral
    to *negative* (FP32 was ~2× slower under MKL). No preset enables them; they remain available
    as explicit input keys (`xc_phi_cache`, `xc_incdft`, `fp32`) for regimes the CPU benchmark
    does not cover, e.g. GPU XC. Start at `perf=1` and raise it only if your own timing shows a gain.

## Individual input keys

Every knob is also a direct input key. Each defaults to `auto` (defer to the preset); an explicit
value **overrides** the preset.

| Section | Key | Meaning |
| --- | --- | --- |
| `[scf]` | `xc_c2f` | coarse-to-fine XC grid during the SCF descent (`on`/`off`/`auto`) |
| `[scf]` | `xc_phi_cache` | cache collocation Φ across SCF iterations — exact, opt-in (`on`/`off`/`auto`) |
| `[scf]` | `xc_incdft` | incremental DFT — experimental, opt-in (`on`/`off`/`auto`) |
| `[scf]` | `pscreen` | progressive integral/grid screening (+ `pscreen_cap`) |
| `[scf]` | `grad_cutoff` | Schwarz cutoff for the 2e-derivative gradient build (number or `auto`) |
| `[tdhf]` | `resp_cutoff` | 2e cutoff for the MRSF response build (number or `auto`) |
| `[tdhf]` | `fp32` | single-precision MRSF response digestion — opt-in (`on`/`off`/`auto`) |
| `[tdhf]` | `zv_warmstart` | reuse the previous step's z-vector as the CPHF seed — exact (`on`/`off`/`auto`) |

Precedence (low → high): control default → `perf` preset → explicit input key. For example,
production speed but keep the full XC grid and a tight response on one job:

```ini
[input]
perf = 2
[scf]
xc_c2f = off
[tdhf]
resp_cutoff = 5e-11
```

The resolved settings (and any warnings) are printed near the top of the run log:

```text
   Performance settings (perf = 2)
     scf.xc_c2f        = off       (input)
     scf.grad_cutoff   = 1.0d-8    (preset)
     tdhf.resp_cutoff  = 5e-11     (input)
     tdhf.zv_warmstart = on        (preset)
     ...
```

## Recommendations

- **HF / DFT / TDDFT / MRSF energies:** `perf=1` for exact production; `perf=2` to add the
  coarse-to-fine grid (helps large pure-functional DFT). Use `perf=3` when a few µeV on excitation
  energies is acceptable for ~10–20% more speed.
- **Gradients, geometry optimization, MD:** `perf=1` (z-vector warm-start is most effective across
  many nearby geometries) or `perf=2`. Avoid `perf=3` for MD through conical intersections.
- **Reference numbers and tight 2nd-order properties (IR/Raman/NMR):** `perf=0` or `perf=1`.

## Reproducibility

`perf=0` is the bitwise reference **for a fixed thread count**. The threaded Fock build uses a
dynamic-schedule reduction, so results are not bit-identical across thread counts at any level —
pin `OMP_NUM_THREADS` for strict reproducibility.
