#!/usr/bin/env bash
# Entry point of the replication harness. Usage: ./replicate.sh check|plan|run|report|audit-port [options]
# The interpreter is $REPLICATE_PYTHON (default python3); it should be the analysis environment (env/requirements_freeze.txt).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${REPLICATE_PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
exec "$PY" -s -m replicate "$@"
