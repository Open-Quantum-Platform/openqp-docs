# Installation and OQP Studio

The planned OpenQP 1.4 distribution uses platform-specific engine binaries.
Select the binary for your operating system and architecture from the 1.4
release when it becomes available. Check the artifact and runtime requirements
against the signed release manifest before installing. Verify the signature
and file checksum, then check the minimum OS version listed for that artifact,
including its bundled dependencies.

The 1.4 beta bundle provides OpenMP parallel execution without an MPI
runtime. The relocated Linux beta executable used eight OpenMP threads
and one BLAS thread. It rejected an MPI request and a 33-thread request.

The earlier macOS arm64 feasibility bundle used version 1.3.1. Some of
its dependencies declare macOS 26 as their minimum. Compatibility on M3
systems and the final 1.4 minimum OS are pending validation. A Linux x86-64
1.4.0b1 standalone test bundle ran from a new location in a fresh glibc 2.28
container and completed initial energy and NPZ restart calculations through
both tested engine entry modes. Separate Linux native tests at one and 16
OpenMP threads covered MRSF gradients, analytic NAC for all pairs and three selected pairs,
and static HF/PBE QM/MM energies and NPZ restarts with the 6-31G basis.
The NAMD test passed its comparison of an uninterrupted 40-step (8 fs)
trajectory with a 20-step run resumed from its checkpoint through step 40.

The rebuilt Linux wheel passed the runtime library path audit. Actual
32 vCPU execution and AWS testing remain pending before production distribution.

The planned 1.4 bundle uses OpenMM's CPU platform with one thread for OpenMM
work. A missing CPU platform raises an error before a simulation starts.
The Linux standalone test observed a one-thread CPU context. Final bundle
qualification remains pending.

## Concurrent compute budget

The planned default ceiling for a single calculation is 32 vCPU. Set its
OpenMP thread count within its allocation. The AWS contract has a separate
aggregate limit of 32 vCPU across concurrently running independent jobs.
Two concurrent jobs allocated 16 vCPU each use the full aggregate budget.
The Linux beta test exercised rejection above the ceiling. A run at the
ceiling remains pending.

Set `omp_threads` to zero in an `.oqp` input with `input(omp_threads=0)`
to inherit the validated OpenMP environment. The command-line option
`--omp` requires a positive integer.

For OQP Studio, use the engine version and platform artifact listed for the
corresponding Studio release. With test-signed 1.4.0b1 bundles on macOS and
Linux, Studio API tests completed initial energy calculations and NPZ
restarts with identical energies on each platform. The macOS Studio UI
also showed the completed restart. Production distribution and the
supported artifact list are pending qualification. See the
[OQP Studio manual](https://www.openqp.org/manual/studio/) for general Studio
usage.

## Beta diagnostics

If you choose to share a beta diagnostic report, manually provide the engine
version, input and log files, elapsed runtime, and the restart outcome if you
attempted a restart.
