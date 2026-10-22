#!/bin/bash
# Wave 3c R0/R1: one Animation Hitches recording per walk, Instruments launching the Release build with
# Steven's device-local settings as launch arguments (the synced ones — accent White, Card Depth
# Subtle/Soft/Full, Medium+, Rounded, Hide Titles, OLED — are already set in Test 2).
#
# TWO PHASES, so that no press goes out before a human-read screenshot confirms NuvioTV is in front
# (2026-10-22 01:45Z: an Instruments launch that did not bring the app forward let a whole walk press
# into another app):
#   walks.sh launch <name> [extra launch args…]   → starts the recording, waits 15 s, writes
#                                                   docs/research/wave3c-r0-2026-10-21/launch-<name>.png
#                                                   and exits (xctrace keeps running, pid in launch-<name>.pid)
#   walks.sh walk <name> <walk>                    → ONLY after the screenshot shows NuvioTV's Home in Test 2:
#                                                   runs the presses, waits for xctrace, prints the summary
#   walks.sh abort <name>                          → kills the recording without pressing anything
#     walk = home   : walk-home.sh (20 down / 20 up on Home)
#            detail : walk-detail.sh (rail → Search → Severance → series Detail → 10 down / 10 up)
#            picker : Trending Movies → Animals → Play → the stream picker, 30 down / 30 up at 0.35 s
set -u
cd "$(dirname "$0")/../../.."
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"; source "$CONF/atv.env"
R=docs/research/wave3c-r0-2026-10-21
A=scripts/device/atv.sh
PHASE="$1"; NAME="$2"; shift 2
TR="$HOME/Library/Logs/nuviotv-traces/${TRACE_PREFIX:-r0}-$NAME.trace"
LOG="$HOME/Library/Logs/nuviotv-traces/${TRACE_PREFIX:-r0}-$NAME.log"
STEVEN=(-detail_trailer_autoplay NO -detail_trailer_background NO -sidebar_style rail -rail_visibility hidden
        -rail_position corner -rail_labels shown -rail_style floating -ui_font system -accent_focus_ring YES
        -focus_ring_poster_color YES -depth_rail_poster_color YES -no_zoom_on_focus NO -row_edge_fade off
        -show_catalog_details_in_headings YES -settings_style default -detail_action_icons_only NO)
case "$PHASE" in
  launch)
    rm -rf "$TR"
    # 02:11Z: an Instruments --launch over a RUNNING instance came up behind the tvOS Home screen (the
    # Companion's LaunchApp then relaunches WITHOUT the args). Kill the app first, give tvOS a beat.
    PID="$(xcrun devicectl device info processes --device "$ATV_UDID" 2>/dev/null | grep "NuvioTV.app/NuvioTV " | awk '{print $1}' | head -1)"
    if [ -n "$PID" ]; then xcrun devicectl device process signal --device "$ATV_UDID" --pid "$PID" --signal SIGKILL >/dev/null 2>&1; sleep 6; fi
    LIMIT="${LIMIT:-110s}"
    xcrun xctrace record --device "$ATV_UDID" --template 'Animation Hitches' --time-limit "$LIMIT" \
      --output "$TR" --launch -- com.youngchris29.NuvioTV "${STEVEN[@]}" "$@" > "$LOG" 2>&1 &
    echo $! > "$R/launch-$NAME.pid"
    sleep 15
    if grep -q "Timed out waiting for device" "$LOG"; then echo "LAUNCH FAILED (Instruments timed out)"; tail -2 "$LOG"; exit 2; fi
    SHOT_SMALL=1 scripts/device/shot.sh "$R/launch-$NAME" | tail -1
    echo "LAUNCHED $(date -u +%H:%M:%SZ) — read the screenshot before 'walk'" ;;
  walk)
    WALK="$1"
    echo "WALK_T0 $(date +%s)"
    case "$WALK" in
      home)   docs/research/batch-p-wave0-2026-10-20/walk-home.sh ;;
      detail) docs/research/batch-p-wave0-2026-10-20/walk-detail.sh ;;
      picker)
        $A seq down sleep=0.8 down sleep=0.8 down sleep=0.8 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.8 select sleep=5 select sleep=8 | tail -1
        echo "PICKER_T0 $(date +%s)"
        steps=""; for i in $(seq 30); do steps="$steps down sleep=0.35"; done
        $A seq $steps | tail -1
        steps=""; for i in $(seq 30); do steps="$steps up sleep=0.35"; done
        $A seq $steps | tail -1
        $A seq menu sleep=1.5 menu sleep=1.5 | tail -1 ;;
    esac
    while kill -0 "$(cat "$R/launch-$NAME.pid")" 2>/dev/null; do sleep 5; done
    tail -2 "$LOG"
    python3 -I docs/research/batch-p-wave0-2026-10-20/hitches.py "$TR" ;;
  abort)
    kill "$(cat "$R/launch-$NAME.pid")" 2>/dev/null; sleep 2; rm -rf "$TR"; echo "aborted $NAME" ;;
esac
