#!/bin/bash
# Wave 3c R0/R1: one Animation Hitches recording per walk, Instruments launching the Release build with
# Steven's device-local settings as launch arguments (the synced ones — accent White, Card Depth
# Subtle/Soft/Full, Medium+, Rounded, Hide Titles, OLED — are already set in Test 2).
#   walks.sh <name> <walk> [extra launch args…]
#     walk = home   : walk-home.sh (20 down / 20 up on Home)
#            detail : walk-detail.sh (rail → Search → Severance → series Detail → 10 down / 10 up)
#            picker : Trending Movies → Animals → Play → the stream picker, 30 down / 30 up at 0.35 s
# Trace → ~/Library/Logs/nuviotv-traces/r0-<name>.trace; summary printed with hitches.py.
# The app auto-enters the remembered profile (Test 2 — confirm on the first Release launch of the day).
set -u
cd "$(dirname "$0")/../../.."
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"; source "$CONF/atv.env"
NAME="$1"; WALK="$2"; shift 2
A=scripts/device/atv.sh
TR="$HOME/Library/Logs/nuviotv-traces/r0-$NAME.trace"; rm -rf "$TR"
STEVEN=(-detail_trailer_autoplay NO -detail_trailer_background NO -sidebar_style rail -rail_visibility hidden
        -rail_position corner -rail_labels shown -rail_style floating -ui_font system -accent_focus_ring YES
        -focus_ring_poster_color YES -depth_rail_poster_color YES -no_zoom_on_focus NO -row_edge_fade off
        -show_catalog_details_in_headings YES -settings_style default -detail_action_icons_only NO)
LIMIT=80s; [[ "$WALK" == picker ]] && LIMIT=110s
xcrun xctrace record --device "$ATV_UDID" --template 'Animation Hitches' --time-limit "$LIMIT" \
  --output "$TR" --launch -- com.youngchris29.NuvioTV "${STEVEN[@]}" "$@" \
  > "$HOME/Library/Logs/nuviotv-traces/r0-$NAME.log" 2>&1 &
XT=$!
sleep 15
echo "WALK_T0 $(date +%s)"
case "$WALK" in
  home)
    docs/research/batch-p-wave0-2026-10-20/walk-home.sh ;;
  detail)
    docs/research/batch-p-wave0-2026-10-20/walk-detail.sh ;;
  picker)
    # Home row 4 = Trending Movies; Animals is the 7th card. Play opens the picker (Auto-Play Best is off in Test 2).
    $A seq down sleep=0.8 down sleep=0.8 down sleep=0.8 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.5 right sleep=0.8 select sleep=5 select sleep=8 | tail -1
    echo "PICKER_T0 $(date +%s)"
    steps=""; for i in $(seq 30); do steps="$steps down sleep=0.35"; done
    $A seq $steps | tail -1
    steps=""; for i in $(seq 30); do steps="$steps up sleep=0.35"; done
    $A seq $steps | tail -1
    $A seq menu sleep=1.5 menu sleep=1.5 | tail -1 ;;
esac
wait $XT
tail -2 "$HOME/Library/Logs/nuviotv-traces/r0-$NAME.log"
python3 -I docs/research/batch-p-wave0-2026-10-20/hitches.py "$TR"
