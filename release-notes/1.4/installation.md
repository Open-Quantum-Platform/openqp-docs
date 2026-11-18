# 1.4 installation and OQP Studio

## Release candidate installation

The planned OpenQP 1.4 distribution uses platform-specific engine binaries.
Select the binary for your operating system and architecture from the 1.4
release when it becomes available. Check the artifact and runtime requirements
against the signed release manifest before installing. Verify the signature
and file checksum, then check the minimum OS version listed for that artifact,
including its bundled dependencies.

OpenQP 1.4 excludes xTB and rejects inputs that request it. DFTB remains
available through the optional OpenQP-DFTB backend.

The 1.4 beta bundle provides OpenMP parallel execution without an MPI
runtime. The relocated Linux beta executable used eight OpenMP threads
and one BLAS thread. It rejected an MPI request and a 33-thread request.

The signed manifest for the current macOS arm64 1.4.0b1 test bundle declares
macOS 26.0 as the minimum for the bundle. The final minimum OS and M3
compatibility are pending validation. A Linux x86-64
1.4.0b1 standalone test bundle ran from a new location in a fresh glibc 2.28
container and completed initial energy and NPZ restart calculations through
both tested engine entry modes. Separate Linux native tests at one and 16
OpenMP threads covered MRSF gradients, analytic NAC for all pairs and three selected pairs,
and static HF/PBE QM/MM energies and NPZ restarts with the 6-31G basis.
The NAMD test passed its comparison of an uninterrupted 40-step (8 fs)
trajectory with a 20-step run resumed from its checkpoint through step 40.

The rebuilt Linux wheel passed the runtime library path audit. Scientific
outputs from the native wheel at 32 OpenMP threads passed independent
checks. The compiled standalone at 32 threads and AWS execution are
pending validation.

The planned 1.4 bundle uses OpenMM's CPU platform with one thread for OpenMM
work. A missing CPU platform raises an error before a simulation starts.
The Linux standalone test observed a one-thread CPU context. Final bundle
qualification remains pending.

## Concurrent compute budget

The planned default ceiling for a single calculation is 32 vCPU. Set its
OpenMP thread count within its allocation. The AWS contract has a separate
aggregate limit of 32 vCPU across concurrently running independent jobs.
Two concurrent jobs allocated 16 vCPU each use the full aggregate budget.
Linux native-wheel tests sampled a peak of 32 runnable threads for both
a single 32-thread job and two concurrent 16-thread jobs. Sampling can
miss brief overshoots. Studio enforcement of the shared budget across
independent jobs remains pending.

Set `omp_threads` to zero in an `.oqp` input with `input(omp_threads=0)`
to inherit the validated OpenMP environment. The command-line option
`--omp` requires a positive integer.

For OQP Studio, use the engine version and platform artifact listed for the
corresponding Studio release. With test-signed 1.4.0b1 bundles on macOS and
Linux, Studio API tests completed initial energy calculations and NPZ
restarts with identical energies on each platform. The macOS Studio UI
also showed the completed restart. Production distribution and the
supported artifact list are pending qualification. See the
[OQP Studio manual](studio/index.md) for general Studio
usage.

## Beta diagnostics

If you choose to share a beta diagnostic report, manually provide the engine
version, input and log files, elapsed runtime, and the restart outcome if you
attempted a restart.
