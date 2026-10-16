# Handoff: ML Fock matrices for MRSF-TDDFTB reference orbitals

Status at handoff (cloud session, 2026-10-16): package works end to end on
real OpenQP data; MRSF-TDDFTB numbers with ML orbitals have NOT been produced
yet because the openqp-dftb native library was not available there.

## Where things are
- Code: openqp-docs branch `mlfock-prototype`, directory `mlfock/` (latest commit f62594c).
  Read `mlfock/README.md` first. Tests: `pip install -e .[test]; pytest tests -q`.
- Injection path (already exists, do NOT reimplement): openqp-dftb
  `tools/simple_mrsf/` and `maybe_load_simple_mrsf_reference` in
  `src/openqp_dftb_capi.F90`, env `OPENQP_DFTB_SIMPLE_MRSF_REF=<ref.bin>`.
  `mlfock.extract.write_simple_mrsf_reference` writes that exact format
  (verified byte-compatible with `tools/simple_mrsf/extract_ref.py`).
- ML target = OpenQP Gaussian-basis ROKS matrices [F_eff, F_alpha, F_beta],
  learned as a delta over Hcore. Orbitals = eigh(F_eff, S). No projection to
  the DFTB basis is needed.
- Verified: AO conventions (p = x,y,z; Cartesian d = xx,yy,zz,xy,xz,yz with
  sqrt(3) cross terms; VEC_MO_A MO-major), rotation matrices vs OpenQP
  overlaps, water demo (40 train geometries: 0.40 eV orbital-energy RMSE,
  subspace fidelities > 0.998).

## Tasks, in order
1. Install: clone `mlfock-prototype`, `pip install -e .[test]`, run `pytest tests -q`
   (needs pyoqp; openqp-dftb library for step 3+). Report the counts.
2. Run `python examples/water_demo.py 40 10 200` and confirm the table in README.
3. THE KEY EXPERIMENT (needs openqp-dftb + parameter set OB2W0PT3):
   for one small molecule (water first, then a chromophore the user names),
   compute MRSF-TDDFTB S1/T1 (and oscillator strengths) with
   (a) native DFTB orbitals, (b) real ROKS reference via tools/simple_mrsf,
   (c) ML reference via `mlfock.predict.Orbitals.write_reference` +
   `mlfock.oqp_bridge.run_mrsf_tddftb_with_reference`,
   and compare all three with full all-electron MRSF-TDDFT (OpenQP, same
   functional/basis). Report a table. (c) close to (b) is the success criterion.
4. Scale data: 300-1000 frames from an MRSF trajectory of that molecule
   (`examples/generate_and_train.py traj.xyz records/ --train`); train 2-4 seeds
   for an ensemble; report orbital-energy RMSE, closed/SOMO/virtual fidelities,
   and the S1/T1 errors of (c) vs (b) on held-out frames.
5. Optional eSEN backbone (`pip install fairchem-core ase; huggingface-cli login`;
   `--backbone esen-sm-direct-all-omol --spin 3`). `tests/test_esen.py::test_real_esen_smoke`
   validates the l=1 ordering detection; report it.
6. On-the-fly: `mlfock.onthefly.OnTheFlyLearner` inside a short run; report
   oracle-call rate vs uncertainty tolerance.
7. Gradients: simple-MRSF rejects gradient requests. Scope what openqp-dftb
   needs for a gradient consistent with injected orbitals (needed for NAMD);
   do not implement without the user's go-ahead.
8. Write results up in the Overleaf project (git clone on this machine) as
   LaTeX tables; push.

## Rules
- Keep mlfock as its own package; do not integrate into the openqp-agent branch.
- Commit on `mlfock-prototype` (or a branch the user names); no model names in commits.
- Be explicit in reports about what was measured vs assumed.
