#!/bin/bash
# R0 Release walks, one after another. Summary lines → summary.txt (hitches.py output per run).
# After each Instruments session the devicectl tunnel drops for up to a minute ("Timed out waiting for
# device to boot"), so every run waits for the tunnel first and retries once if no trace was written.
cd "$(dirname "$0")/../../.."
source ~/.config/nuviotv-device/atv.env
R=docs/research/wave3c-r0-2026-10-21; W=$R/walks.sh; S=$R/summary.txt; T=$HOME/Library/Logs/nuviotv-traces
wait_tunnel() {
  for i in $(seq 18); do
    if timeout 25 xcrun devicectl device info details --device "$ATV_UDID" >/dev/null 2>&1; then return 0; fi
    sleep 10
  done
  echo "tunnel never came back" >> "$S"; return 1
}
run() {
  local name="$1"
  for attempt in 1 2 3; do
    wait_tunnel || return 1
    sleep "${GAP:-45}"   # Instruments' own tunnel needs longer than devicectl's after a session ends
    echo "== $name attempt $attempt $(date -u +%H:%M:%SZ)" >> "$S"; "$W" "$@" >> "$S" 2>&1; echo >> "$S"
    if [ -d "$T/r0-$name.trace" ]; then return 0; fi
  done
}
ONLY="${ONLY:-}"
want() { [ -z "$ONLY" ] || [[ " $ONLY " == *" $1 "* ]]; }
want detail-cinematic && run detail-cinematic detail -detail_layout cinematic -home_layout classic
want detail-classic && run detail-classic   detail -detail_layout classic   -home_layout classic
want home-classic-depth && run home-classic-depth   home -home_layout classic
want home-classic-depth2 && run home-classic-depth2  home -home_layout classic
want home-classic-nodepth && run home-classic-nodepth  home -home_layout classic -debug.homeNoCardDepth YES
want home-classic-nodepth2 && run home-classic-nodepth2 home -home_layout classic -debug.homeNoCardDepth YES
want home-stage-depth && run home-stage-depth   home -home_layout stage
want home-stage-depth2 && run home-stage-depth2  home -home_layout stage
want home-stage-nodepth && run home-stage-nodepth  home -home_layout stage -debug.homeNoCardDepth YES
want home-stage-nodepth2 && run home-stage-nodepth2 home -home_layout stage -debug.homeNoCardDepth YES
want picker && run picker picker -home_layout classic
if want rc7-detail-cinematic; then
  wait_tunnel; xcrun devicectl device install app --device "$ATV_UDID" ~/Claude/Projects/NuvioMobile-wave3/iosApp/build/rc7-app/NuvioTV.app >> "$S" 2>&1
  run rc7-detail-cinematic detail -detail_layout cinematic -home_layout classic
  wait_tunnel; xcrun devicectl device install app --device "$ATV_UDID" ~/Claude/Projects/NuvioMobile-wave3/iosApp/build/rel-app/NuvioTV.app >> "$S" 2>&1
fi
echo "ALL DONE $(date -u +%H:%M:%SZ)" >> "$S"
