#!/usr/bin/env bash
# Build a local distributable wheel and print where it landed.
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf build dist *.egg-info
pip wheel . --no-deps -w dist >/dev/null
echo "Wheel(s) in dist/:"
ls -1 dist/
