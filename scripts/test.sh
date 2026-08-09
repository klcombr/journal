#!/usr/bin/env bash
# Run the test suite and report coverage-friendly summary.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== pytest =="
python -m pytest -q tests
