#!/bin/bash
# Batch P Wave 0: Detail walk on a SERIES: rail → Search → type $1 (default Severance) → down x4 lands on the Series row (the Top result prefers films) → Detail, then 10 down / 10 up.
cd "$(dirname "$0")/../../.."
A=scripts/device/atv.sh
$A seq menu sleep=1.5 down sleep=0.5 select sleep=2.5 text=${1:-Severance} sleep=5 down sleep=0.6 down sleep=0.6 down sleep=0.6 down sleep=0.6 select sleep=6 | tail -1
echo "DETAIL_T0 $(date +%s)"
steps=""; for i in $(seq 10); do steps="$steps down sleep=0.8"; done
$A seq $steps | tail -1
steps=""; for i in $(seq 10); do steps="$steps up sleep=0.8"; done
$A seq $steps | tail -1
