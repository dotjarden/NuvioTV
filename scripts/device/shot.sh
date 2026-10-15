#!/bin/bash
# NuvioTV device rig: screenshot the Living Room Apple TV over devicectl (3840x2160 PNG, ~1.3 s).
#   shot.sh [name-or-path]      # default: docs/research/device-rig-<today>/shot-<HHMMSS>.png
# Prints the PNG path. Set SHOT_SMALL=1 to also write a 960-px-wide copy next to it (for reading).
set -euo pipefail
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"
# shellcheck disable=SC1091
source "$CONF/atv.env"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
arg="${1:-}"
if [[ -z "$arg" ]]; then
  dir="$ROOT/docs/research/device-rig-$(date +%F)"; mkdir -p "$dir"; out="$dir/shot-$(date +%H%M%S).png"
elif [[ "$arg" == */* || "$arg" == *.png ]]; then
  out="$arg"; [[ "$out" == *.png ]] || out="$out.png"; mkdir -p "$(dirname "$out")"
else
  dir="$ROOT/docs/research/device-rig-$(date +%F)"; mkdir -p "$dir"; out="$dir/$arg.png"
fi
xcrun devicectl device capture screenshot --device "$ATV_UDID" --destination "$out" >/dev/null
if [[ "${SHOT_SMALL:-0}" == 1 ]]; then sips -Z 960 "$out" --out "${out%.png}.small.png" >/dev/null; fi
echo "$out"
