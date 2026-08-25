#!/usr/bin/env bash
# Exercise the runner's exact signal-cleanup helpers against real child processes.
set -Eeuo pipefail

ROOT="$(cd -- "$(dirname -- "$BASH_SOURCE")/../../.." && pwd -P)"
RUNNER="$ROOT/experiments/g1/commands/20-g1-c-004.sh"
TEMPORARY="$(mktemp -d "${TMPDIR:-/tmp}/g1-c-004-signal-cleanup.XXXXXX")"
ARM_PID=""
ARM_PGID=""
SAMPLER_PID=""
HARNESS_PID=""

fallback_cleanup() {
  trap - EXIT
  if [[ "$HARNESS_PID" =~ ^[1-9][0-9]*$ ]]; then kill -KILL "$HARNESS_PID" 2>/dev/null || true; fi
  if [[ "$SAMPLER_PID" =~ ^[1-9][0-9]*$ ]]; then kill -KILL "$SAMPLER_PID" 2>/dev/null || true; fi
  if [[ "$ARM_PGID" =~ ^[1-9][0-9]*$ ]]; then kill -KILL -- "-$ARM_PGID" 2>/dev/null || true; fi
  if [[ "$ARM_PID" =~ ^[1-9][0-9]*$ ]]; then kill -KILL "$ARM_PID" 2>/dev/null || true; fi
  if [[ "$ARM_PID" =~ ^[1-9][0-9]*$ ]]; then wait "$ARM_PID" 2>/dev/null || true; fi
  if [[ "$SAMPLER_PID" =~ ^[1-9][0-9]*$ ]]; then wait "$SAMPLER_PID" 2>/dev/null || true; fi
  rm -rf "$TEMPORARY"
}
trap fallback_cleanup EXIT

sed -n '/BEGIN_SIGNAL_CLEANUP_HELPERS/,/END_SIGNAL_CLEANUP_HELPERS/p' "$RUNNER" >"$TEMPORARY/helpers.sh"

(
  # shellcheck source=/dev/null
  source "$TEMPORARY/helpers.sh"
  perl -MPOSIX -e 'my $ready = shift; setsid(); open my $out, ">", $ready or die $!; print {$out} "$$\n"; close $out; exec "sleep", "60"' "$TEMPORARY/arm-ready" &
  CURRENT_ARM_PID="$!"
  for _ in $(seq 1 100); do
    [[ -f "$TEMPORARY/arm-ready" ]] && break
    sleep 0.01
  done
  CURRENT_ARM_PGID="$CURRENT_ARM_PID"
  [[ "$(cat "$TEMPORARY/arm-ready")" == "$CURRENT_ARM_PID" ]]
  sleep 60 &
  CURRENT_SAMPLER_PID="$!"
  printf '%s\n' "$CURRENT_ARM_PID" >"$TEMPORARY/arm-pid"
  printf '%s\n' "$CURRENT_ARM_PGID" >"$TEMPORARY/arm-pgid"
  printf '%s\n' "$CURRENT_SAMPLER_PID" >"$TEMPORARY/sampler-pid"
  trap 'cleanup_active_processes; exit 0' TERM
  : >"$TEMPORARY/ready"
  while :; do sleep 0.1 & wait "$!"; done
) >"$TEMPORARY/harness.log" 2>&1 &
HARNESS_PID="$!"
for _ in $(seq 1 100); do
  [[ -f "$TEMPORARY/ready" ]] && break
  sleep 0.01
done
[[ -f "$TEMPORARY/ready" ]] || { cat "$TEMPORARY/harness.log" >&2; exit 1; }
ARM_PID="$(cat "$TEMPORARY/arm-pid")"
ARM_PGID="$(cat "$TEMPORARY/arm-pgid")"
SAMPLER_PID="$(cat "$TEMPORARY/sampler-pid")"
kill -TERM "$HARNESS_PID"
wait "$HARNESS_PID"
HARNESS_PID=""

if kill -0 "$SAMPLER_PID" 2>/dev/null; then printf 'sampler survived cleanup\n' >&2; exit 1; fi
if kill -0 -- "-$ARM_PGID" 2>/dev/null; then printf 'arm process group survived cleanup\n' >&2; exit 1; fi
printf 'G1-C-004 signal cleanup regression passed\n'
