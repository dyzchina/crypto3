#!/usr/bin/env bash
# build.sh — xelatex 3-pass + bibtex
set -e
cd "$(dirname "$0")/../manuscript"
MAIN="main_eca_v01"

echo "=== pass 1 xelatex ==="
xelatex -interaction=nonstopmode "${MAIN}.tex" > /dev/null 2>&1 || true
echo "=== bibtex ==="
bibtex "${MAIN}" 2>&1 | tail -5
echo "=== pass 2 xelatex ==="
xelatex -interaction=nonstopmode "${MAIN}.tex" > /dev/null 2>&1 || true
echo "=== pass 3 xelatex ==="
xelatex -interaction=nonstopmode "${MAIN}.tex" 2>&1 | tail -3
echo
grep -oE "Output written on.*\.pdf \([0-9]+ pages\)" "${MAIN}.log" || true
grep -iE "! |error" "${MAIN}.log" | grep -viE "inputenc|dvipdfmx|font substitut" | head || true
