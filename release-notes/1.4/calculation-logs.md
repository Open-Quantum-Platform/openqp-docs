# Calculation logs

The release candidate adds a timing table to the termination section when
module timing records are available. The table reports call counts, elapsed
wall time and process CPU time in seconds. The table total sums the listed
modules. The separate elapsed wall time reports the whole calculation.

## Termination status

For an explicitly confirmed successful workflow, the log reports
`OpenQP terminated normally.` An incomplete workflow can list its recorded
failures on lines beginning with `Incomplete:`. The presence of a termination
section or timing table alone does not confirm success.

When molecular data is saved, the final
[workflow status](result-files.md#workflow-status) in the NPZ or JSON result
uses the same completion decision as the log. For example, a geometry
optimization that reaches its iteration limit without converging can save a
result with `workflow.completed=false` and `workflow.status=incomplete`. Check
`workflow.reasons` or the termination section for the recorded reasons.

A TD response or TD Z-vector convergence failure stops the calculation with
a nonzero exit status. The failure message identifies which solve failed.

## MRSF response residuals

The MRSF Davidson log prints each residual as the squared Euclidean norm
‖r‖². It shows separate maxima for the reported roots and for all roots
tracked by the solver. The tracked-root maximum is diagnostic. The convergence
check uses the reported roots and any additional tracked roots that could
enter the reported set.

The [`tdhf.conv` reference](https://www.openqp.org/manual/keywords/tdhf/#conv)
defines the tolerance for ‖r‖². For example, a tolerance of `1e-6` corresponds
to a residual norm of `1e-3`.
