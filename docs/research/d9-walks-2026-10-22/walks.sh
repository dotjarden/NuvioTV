#!/bin/bash
# D9 (BUG-206) walks, 2026-10-22: one Animation Hitches recording per walk, Instruments launching the
# installed Release build with Steven's device-local settings as launch arguments. Same two phases as
# docs/research/wave3c-r0-2026-10-21/walks.sh (launch → human-read screenshot → walk), with two
# corrections learned the same day:
#   - Bool settings read through @AppStorage ignore YES/NO launch arguments and take 1/0, so the
#     earlier walks ran the trailer, ring and headings settings at Test 2's STORED values (the Detail
#     background trailer was ON during the BUG-206 hunt's Cinematic walks). The Bools below are 1/0.
#   - -detail_layout cinematic is explicit.
#
#   walks.sh launch <name> [extra launch args…]   → starts the recording, fronts the app, writes
#                                                   docs/research/d9-walks-2026-10-22/launch-<name>.png
#   walks.sh walk <name> detail                    → ONLY after the screenshot shows NuvioTV's Home in Test 2:
#                                                   rail → Search → Severance → series Detail → 10 down / 10 up
#   walks.sh abort <name>
set -u
cd "$(dirname "$0")/../../.."
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"; source "$CONF/atv.env"
R=docs/research/d9-walks-2026-10-22
A=scripts/device/atv.sh
PHASE="$1"; NAME="$2"; shift 2
TR="$HOME/Library/Logs/nuviotv-traces/${TRACE_PREFIX:-d9}-$NAME.trace"
LOG="$HOME/Library/Logs/nuviotv-traces/${TRACE_PREFIX:-d9}-$NAME.log"
STEVEN=(-detail_trailer_autoplay 0 -detail_trailer_background 0 -detail_layout cinematic
        -sidebar_style rail -rail_visibility hidden -rail_position corner -rail_labels shown
        -rail_style floating -ui_font system -accent_focus_ring 1 -focus_ring_poster_color 1
        -depth_rail_poster_color 1 -no_zoom_on_focus 0 -row_edge_fade off
        -show_catalog_details_in_headings 1 -settings_style default -detail_action_icons_only 0)
case "$PHASE" in
  launch)
    rm -rf "$TR"
    PID="$(xcrun devicectl device info processes --device "$ATV_UDID" 2>/dev/null | grep "NuvioTV.app/NuvioTV " | awk '{print $1}' | head -1)"
    if [ -n "$PID" ]; then xcrun devicectl device process signal --device "$ATV_UDID" --pid "$PID" --signal SIGKILL >/dev/null 2>&1; sleep 6; fi
    LIMIT="${LIMIT:-110s}"
    xcrun xctrace record --device "$ATV_UDID" --template 'Animation Hitches' --time-limit "$LIMIT" \
      --output "$TR" --launch -- com.youngchris29.NuvioTV "${STEVEN[@]}" "$@" > "$LOG" 2>&1 &
    echo $! > "$R/launch-$NAME.pid"
    sleep 15
    if grep -q "Timed out waiting for device" "$LOG"; then echo "LAUNCH FAILED (Instruments timed out)"; tail -2 "$LOG"; exit 2; fi
    timeout 40 "$A" launch com.youngchris29.NuvioTV >/dev/null 2>&1; sleep 4
    SHOT_SMALL=1 scripts/device/shot.sh "$R/launch-$NAME" | tail -1
    echo "LAUNCHED $(date -u +%H:%M:%SZ) — read the screenshot before 'walk'" ;;
  walk)
    WALK="$1"
    echo "WALK_T0 $(date +%s)"
    case "$WALK" in
      detail) docs/research/batch-p-wave0-2026-10-20/walk-detail.sh ;;
      home)   docs/research/batch-p-wave0-2026-10-20/walk-home.sh ;;
    esac
    while kill -0 "$(cat "$R/launch-$NAME.pid")" 2>/dev/null; do sleep 5; done
    tail -2 "$LOG"
    python3 -I docs/research/batch-p-wave0-2026-10-20/hitches.py "$TR"
    rm -rf "${TMPDIR:-/tmp}"/instruments*.ktrace ;;
  abort)
    kill "$(cat "$R/launch-$NAME.pid")" 2>/dev/null; sleep 2; rm -rf "$TR"; echo "aborted $NAME" ;;
esac
