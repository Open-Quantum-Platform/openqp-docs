# Calculation logs

The release candidate adds a timing table to the termination section when
module timing records are available. The table reports call counts, elapsed
wall time and process CPU time in seconds. The table total sums the listed
modules. The separate elapsed wall time reports the whole calculation.

For an explicitly confirmed successful workflow, the log reports
`OpenQP terminated normally.` An incomplete workflow can list its recorded
failures on lines beginning with `Incomplete:`. The presence of a termination
section or timing table alone does not confirm success.
