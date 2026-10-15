#!/bin/bash
# NuvioTV device rig: refuse to walk unless the app is the one we are logging, foregrounded, in the
# Test profile. Run before every sequence that starts with a Select.
#   preflight.sh            exit 0 = ok, 1 = refuse (prints why)
# Checks: devicectl tunnel up; console stream alive and attached to the CURRENT app pid; the last
# "[ProfileSelect] selecting profile N" in the log is the Test profile (TEST_PROFILE_INDEX, default 3);
# writes a screenshot to $PREFLIGHT_SHOT (default /tmp/nuviotv-preflight.jpg) for a human/model read.
set -uo pipefail
CONF="${NUVIOTV_DEVICE_CONF:-$HOME/.config/nuviotv-device}"
# shellcheck disable=SC1091
source "$CONF/atv.env"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE="${NUVIOTV_BUNDLE:-com.youngchris29.NuvioTV}"
want="${TEST_PROFILE_INDEX:-3}"
fail() { echo "PREFLIGHT REFUSED: $*"; exit 1; }

xcrun devicectl device info details --device "$ATV_UDID" 2>/dev/null | grep -q "Tunnel IP" || fail "devicectl tunnel down (wait ~20 s and retry)"
pid="$(xcrun devicectl device info processes --device "$ATV_UDID" 2>/dev/null | awk '$2 ~ /NuvioTV\.app\/NuvioTV$/ {print $1}')"
[[ -n "$pid" ]] || fail "$BUNDLE is not running"
[[ -f "$CONF/console.pid" && -f "$CONF/console.pid.path" ]] || fail "no console stream (console.sh start)"
kill -0 "$(cat "$CONF/console.pid")" 2>/dev/null || fail "console stream process is dead (the app was relaunched outside the stream?)"
log="$(cat "$CONF/console.pid.path")"
logpid="$(grep -o -m1 "NuvioTV\[[0-9]*:" "$log" | head -1 | tr -dc '0-9')"
[[ -z "$logpid" || "$logpid" == "$pid" ]] || fail "console log follows pid $logpid but the app is pid $pid (relaunched by tvOS; console.sh start again)"
last="$(grep -o "selecting profile [0-9]*" "$log" | tail -1 | awk '{print $3}')"
[[ -n "$last" ]] || fail "no profile selected yet in this process (pick the Test profile first)"
[[ "$last" == "$want" ]] || fail "last profile selected is $last, not the Test profile ($want)"
shot="${PREFLIGHT_SHOT:-/tmp/nuviotv-preflight.jpg}"
tmp="$(mktemp -d)/p.png"
xcrun devicectl device capture screenshot --device "$ATV_UDID" --destination "$tmp" >/dev/null 2>&1 || fail "screenshot failed"
sips -s format jpeg -s formatOptions 80 -Z 960 "$tmp" --out "$shot" >/dev/null 2>&1; rm -f "$tmp"
echo "PREFLIGHT OK: app pid $pid, console pid $(cat "$CONF/console.pid") → $log, profile $last, screenshot $shot (read it: must show NuvioTV, not the tvOS home screen)"
