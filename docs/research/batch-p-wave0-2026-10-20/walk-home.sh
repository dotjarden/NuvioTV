#!/bin/bash
# Batch P Wave 0: the fixed Stage Home walk. 20 rows down, 20 up. Same for every build. (The rail is measured separately: on rc9 Menu at the Home root ejects the app.)
cd "$(dirname "$0")/../../.."
A=scripts/device/atv.sh
steps=""; for i in $(seq 20); do steps="$steps down sleep=0.6"; done
$A seq $steps | tail -1
steps=""; for i in $(seq 20); do steps="$steps up sleep=0.6"; done
$A seq $steps | tail -1
