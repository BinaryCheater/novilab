#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <probe-id> <condition-id> [--prepare-only]" >&2
  exit 2
fi

probe="$1"
condition="$2"
mode="${3:-run}"

repo_root="$(cd "$(dirname "$0")/../../.." && pwd -P)"
suite_dir="$repo_root/experiment/blind-suite"
probe_dir="$suite_dir/probes/$probe/public"
condition_file="$suite_dir/conditions/$condition.md"

if [[ ! -d "$probe_dir" ]]; then
  echo "Unknown probe: $probe" >&2
  exit 2
fi

if [[ ! -f "$condition_file" ]]; then
  echo "Unknown condition: $condition" >&2
  exit 2
fi

if [[ "$mode" != "run" && "$mode" != "--prepare-only" ]]; then
  echo "Unknown mode: $mode" >&2
  exit 2
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
run_id="${BLIND_SUITE_RUN_ID:-$timestamp}"
tmp_root="${TMPDIR:-/tmp}/novilab-blind-suite/$run_id/$probe/$condition"
record_dir="$suite_dir/runs/$run_id/$probe/$condition"

rm -rf "$tmp_root"
mkdir -p "$tmp_root" "$record_dir"

cp "$probe_dir/source-files.md" "$tmp_root/source-files.md"

cat > "$tmp_root/prompt-to-paste.md" <<EOF
# Blind Research-Judgment Probe

You are in a clean temporary test folder.

Read \`source-files.md\`, then read only the allowed EmbodiedAI source files listed there.

Do not read Novi repository files, experiment analysis, private review notes, parent directories, sibling probe folders, or any files outside the allowed source list.

Write both files in Chinese:

1. \`trace.md\`: a concise Chinese audit trace, not hidden chain-of-thought. Include:
   - evidence inspected;
   - candidate conclusions considered;
   - rejected conclusions and why;
   - missing evidence or uncertainty;
   - final decision basis.
2. \`answer.md\`: the final Chinese answer for a human research reviewer.

Also print a concise Chinese copy of the final answer to stdout.

$(cat "$condition_file")

$(cat "$probe_dir/task.md")
EOF

touch "$tmp_root/answer.md" "$tmp_root/trace.md" "$tmp_root/stdout.md"

cat > "$tmp_root/metadata.md" <<EOF
# Blind Suite Run Metadata

- Run ID: $run_id
- Probe: $probe
- Condition: $condition
- Temporary workdir: $tmp_root
- Record dir: $record_dir
- Created UTC: $timestamp
EOF

cp "$tmp_root/prompt-to-paste.md" "$record_dir/prompt-to-paste.md"
cp "$tmp_root/source-files.md" "$record_dir/source-files.md"
cp "$tmp_root/metadata.md" "$record_dir/metadata.md"

if [[ "$mode" == "--prepare-only" ]]; then
  cp "$tmp_root/answer.md" "$record_dir/answer.md"
  cp "$tmp_root/trace.md" "$record_dir/trace.md"
  cp "$tmp_root/stdout.md" "$record_dir/stdout.md"
  echo "Prepared blind run at $tmp_root"
  echo "Record copied to $record_dir"
  exit 0
fi

(
  cd "$tmp_root"
  claude --bare --no-session-persistence \
    --add-dir /Users/cyan/Project/EmbodiedAI \
    --permission-mode acceptEdits \
    -p "$(cat prompt-to-paste.md)" | tee stdout.md
)

cp "$tmp_root/answer.md" "$record_dir/answer.md"
cp "$tmp_root/trace.md" "$record_dir/trace.md"
cp "$tmp_root/stdout.md" "$record_dir/stdout.md"

echo "Run complete. Record copied to $record_dir"
