# Installation and OQP Studio

The planned OpenQP 1.4 distribution uses platform-specific engine binaries.
Select the binary for your operating system and architecture from the 1.4
release when it becomes available. Check the artifact and runtime requirements
against the signed release manifest before installing. Verify the signature
and file checksum, then check the minimum OS version listed for that artifact,
including its bundled dependencies.

The planned 1.4 beta bundle will provide OpenMP parallel execution without
an MPI runtime. An MPI request will report an explicit unsupported-mode
error. These behaviors remain pending engine validation.

The macOS arm64 feasibility bundle reports version 1.3.1 and includes
dependencies that declare macOS 26 as their minimum. Compatibility on M3
systems and the final 1.4 minimum OS are pending validation. A Linux x86-64
1.3.1 test bundle passed its signature check and ran in a fresh glibc 2.28
container. The final Linux build, its 32 vCPU behavior, and static QM/MM
initialization still require validation.

The planned 1.4 bundle uses OpenMM's CPU platform with one thread for OpenMM
work. A missing CPU platform raises an error before a simulation starts.
This behavior remains pending qualification in the final bundle.

## Concurrent compute budget

The planned default ceiling for a single calculation is 32 vCPU. Set its
OpenMP thread count within its allocation. The AWS contract has a separate
aggregate limit of 32 vCPU across concurrently running independent jobs.
Two concurrent jobs allocated 16 vCPU each use the full aggregate budget.
Enforcement of the per-calculation ceiling is pending engine validation.

Set `omp_threads` to zero in an `.oqp` input with `input(omp_threads=0)`
to inherit the validated OpenMP environment. The command-line option
`--omp` requires a positive integer.

For OQP Studio, use the engine version and platform artifact listed for the
corresponding Studio release. Studio's integration and the supported artifact
list are pending qualification. See the
[OQP Studio manual](https://www.openqp.org/manual/studio/) for general Studio
usage.

## Beta diagnostics

If you choose to share a beta diagnostic report, manually provide the engine
version, input and log files, elapsed runtime, and the restart outcome if you
attempted a restart.
