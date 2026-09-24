# Feedback and Scientific Issue Reports

OQP Studio is improved through reproducible reports from calculations and
interface use. Select **Help > Feedback and ideas** in Studio to open the public
[OpenQP Ideas discussion](https://github.com/Open-Quantum-Platform/openqp/discussions/categories/ideas).

Use a discussion for a proposed workflow, analysis method, visualization, or
manual improvement. A maintainer can convert a reproducible defect into the
canonical development issue without requiring the reporter to use the private
development system.

## Include in a report

- OQP Studio version and package type, such as standalone or with-engine;
- operating system and CPU architecture;
- bundled or local OpenQP engine identity and version;
- the smallest input and structure that reproduce the behavior;
- the exact action and the observed output or message;
- the scientifically expected behavior and, when relevant, a literature or
  method reference; and
- a sanitized calculation log or screenshot.

For a numerical discrepancy, also state method, functional, basis, charge,
multiplicity, target state, convergence settings, and units. For an
optimization or dynamics problem, include the last valid structure and the
relevant convergence or trajectory diagnostics.

## Protect sensitive data

Public discussions are visible to everyone. Remove unpublished structures,
credentials, private paths, personal information, license data, and proprietary
force-field parameters. If a minimal public example cannot be prepared, first
describe the problem without attaching the sensitive files.

## What happens next

Reports are triaged as documentation, Studio interface, OpenQP engine,
packaging, or scientific-method issues. The public discussion remains the place
for reporter follow-up; implementation work is tracked in the canonical OpenQP
development repositories. Release notes identify the version containing a
verified correction.
