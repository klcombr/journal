#!/usr/bin/env bash
# Print a small report of the journal file passed (or the default one).
set -euo pipefail

FILE="${1:-${JOURNAL_FILE:-journal.md}}"

if [ ! -f "$FILE" ]; then
  echo "No journal found at: $FILE" >&2
  exit 1
fi

TOTAL=$(grep -c '^- ' "$FILE" || true)
DAYS=$(grep '^- ' "$FILE" | awk '{print $2}' | cut -c1-10 | sort -u | wc -l)

echo "File : $FILE"
echo "Entries : $TOTAL"
echo "Days logged : $DAYS"
