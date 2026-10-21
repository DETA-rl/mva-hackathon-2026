"""Replication harness for the MVA Hackathon 2026 analyses.

Commands (see README, section "Replicating this work"):
  check   preflight: OS, Python, packages, GPU, RAM, disk, input and rule hashes
  plan    the step graph (register IDs), with declared resources, inputs, outputs and dependencies
  run     execute the graph under resource guards; writes results/REPLICATION_REPORT.md and results.json
  report  rebuild the report from the last run state
  audit-port  verify that the ported analysis scripts differ from the as-run scripts only on logged lines
"""

__version__ = "1.0.0"
