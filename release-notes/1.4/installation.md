# Installation and OQP Studio

The planned OpenQP 1.4 distribution uses platform-specific engine binaries.
Select the binary for your operating system and architecture from the 1.4
release when it becomes available. Check the artifact and runtime requirements
against the signed release manifest before installing. Verify the signature
and file checksum, then check the minimum OS version listed for that artifact,
including its bundled dependencies.

The macOS arm64 feasibility bundle reports version 1.3.1 and includes
dependencies that declare macOS 26 as their minimum. Compatibility on M3
systems and the final 1.4 minimum OS are pending validation. Linux x86-64
on AWS will be tested separately.

## Concurrent compute budget

The planned default is 32 vCPU across concurrently running AWS calculations.
Set the thread count for each process according to its allocation, and count
all active job allocations toward the same budget. For example, two concurrent
jobs allocated 16 vCPU each use the full budget. Enforcement of the 32 vCPU
limit is pending validation.

For OQP Studio, use the engine version and platform artifact listed for the
corresponding Studio release. Studio's integration and the supported artifact
list are pending qualification. See the
[OQP Studio manual](https://www.openqp.org/manual/studio/) for general Studio
usage.

## Beta diagnostics

If you choose to share a beta diagnostic report, manually provide the engine
version, input and log files, elapsed runtime, and the restart outcome if you
attempted a restart.
