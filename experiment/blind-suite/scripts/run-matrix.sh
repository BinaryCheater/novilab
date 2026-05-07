#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/../../.." && pwd -P)"
runner="$repo_root/experiment/blind-suite/scripts/run-one.sh"

mode="${1:-run}"

if [[ "$mode" != "run" && "$mode" != "--prepare-only" ]]; then
  echo "Usage: $0 [--prepare-only]" >&2
  exit 2
fi

export BLIND_SUITE_RUN_ID="${BLIND_SUITE_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"

probes=(
  q1-motion-structure
  q2-geometry-closure
  q3-physical-identity
  q4-identifiability
  q5-dense-verdict
  q6-failure-attribution
  q7-generalization
  next-prior-selection
  prototype-plan
  adversarial-scaling
)

conditions=(
  naive
  research-discipline
  structured-trace
)

echo "Blind suite run id: $BLIND_SUITE_RUN_ID"

for probe in "${probes[@]}"; do
  for condition in "${conditions[@]}"; do
    echo "==> $probe / $condition"
    "$runner" "$probe" "$condition" "$mode"
  done
done

echo "Matrix complete: $repo_root/experiment/blind-suite/runs/$BLIND_SUITE_RUN_ID"
