#!/bin/bash
# NuvioTV device rig: launch the Debug device build with its console streamed to a log file.
#   console.sh start [log-path] [-- app args…]   # launches com.youngchris29.NuvioTV with --console
#   console.sh stop                              # ends the stream (the app keeps running)
#   console.sh tail [n]                          # last n lines of the current log
#   console.sh grep <pattern>                    # grep the current log
# Recipe from the 09-30 device walks: devicectl process launch --terminate-existing --console
# keeps stdout/NSLog lines UNTRUNCATED (the About pane's lineLimit(1) loses them). App args
# go after `--` (e.g. -- -debug.homeScrollProbe YES). The stream dies when the app exits.
set -euo pipefail
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"
# shellcheck disable=SC1091
source "$CONF/atv.env"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUNDLE="${NUVIOTV_BUNDLE:-com.youngchris29.NuvioTV}"
PIDFILE="$CONF/console.pid"
cmd="${1:-}"; shift || true
case "$cmd" in
  start)
    log=""; if [[ "${1:-}" != "--" && -n "${1:-}" ]]; then log="$1"; shift; fi
    [[ "${1:-}" == "--" ]] && shift
    if [[ -z "$log" ]]; then d="$ROOT/docs/research/device-rig-$(date +%F)"; mkdir -p "$d"; log="$d/console-$(date +%H%M%S).log"; fi
    mkdir -p "$(dirname "$log")"; echo "$log" > "$PIDFILE.path"
    nohup xcrun devicectl device process launch --device "$ATV_UDID" --terminate-existing --console "$BUNDLE" "$@" > "$log" 2>&1 &
    echo $! > "$PIDFILE"; echo "console → $log (pid $(cat "$PIDFILE"))" ;;
  stop)
    [[ -f "$PIDFILE" ]] && { kill "$(cat "$PIDFILE")" 2>/dev/null || true; rm -f "$PIDFILE"; }
    [[ -f "$PIDFILE.path" ]] && { cat "$PIDFILE.path"; rm -f "$PIDFILE.path"; } ;;
  tail) tail -n "${1:-40}" "$(cat "$PIDFILE.path")" ;;
  grep) grep -n -E "${1:?pattern}" "$(cat "$PIDFILE.path")" ;;
  *) sed -n 2,9p "$0"; exit 64 ;;
esac
